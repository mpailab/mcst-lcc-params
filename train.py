#!/usr/bin/python
# -*- coding: utf-8 -*-

# External imports
import os, sys, shutil
from functools import reduce
import numpy as np
import pickle

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Internal imports
import options as gl
import statistics as stat
import par, verbose, export

#########################################################################################
# Local variables and data structures

# Table of groups of parameters
PARS = {tuple(g) : 1 for g in par.strategy()}

# Table of specs
SPECS = par.specs()

# Dataset directory
DATA_DIR = gl.TRAIN_DATA_DIR
if DATA_DIR == None:
    verbose.error('Directory for train data was not defined')

# Clear database directory
def clear ():
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
        os.makedirs(DATA_DIR)

# Database structure
class DataBase:

    # Initiate database
    def __init__ (self):

        # Table of values
        # Format: spec -> procs -> (par_1,...,par_n) -> (val_1,...,val_n) -> [(t_c/t0_c, t_e/t0_e, v_mem/v0_mem), ... ]
        self.values = {}

        # Default values for current launch
        # Format : spec -> (t0_c, t0_e, v0_mem)
        self.default = {}
    
    # Load database from sourse
    def load (self, sourse = DATA_DIR):

        if gl.TRAIN_PURE:
            return

        if os.path.isdir(sourse):
            for spec in SPECS.keys():
                path = os.path.join(sourse, spec + '.bd')
                if os.path.isfile(path):
                    with open(path, 'rb') as f:
                        self.values[spec] = pickle.load(f)
    
    # Save database from sourse
    def save (self, sourse = DATA_DIR):

        if gl.TRAIN_PURE:
            return

        if not os.path.isdir(sourse):
            os.makedirs(sourse)
        
        for spec in self.values.keys():
            path = os.path.join(sourse, spec + '.bd')
            with open(path, 'wb') as f:
                pickle.dump(self.values[spec], f, 2)
                
    # Add value to database
    # Format of pv: {par_1 : val_1, ..., par_n : val_n}
    def add (self, spec, procs, pv, t_c, t_e, v_mem):

        if gl.TRAIN_PURE:
            return

        if not pv:
            self.default[spec] = (t_c, t_e, v_mem)

        else:
            k = () if procs is None else tuple(procs)
            p = list(pv.keys())
            p.sort()
            p = tuple(p)
            v = tuple(map(lambda x: pv[x], p))
            r = (t_c / self.default[spec][0], t_e / self.default[spec][1], v_mem / self.default[spec][2])
            
            if not spec in self.values:
                self.values[spec] = {}
                
            if not k in self.values[spec]:
                self.values[spec][k] = {}
                
            if not p in self.values[spec][k]:
                self.values[spec][k][p] = {}
                
            if not v in self.values[spec][k][p]:
                self.values[spec][k][p][v] = [r]
            else:
                self.values[spec][k][p][v].append(r)

# Database
DB = DataBase()
    
# Close database
def close ():
    DB.save()

# Percent of train data
DELTA = gl.TRAIN_DELTA

# Number of train steps
TRAIN_STEPS = gl.TRAIN_STEPS

# Train grid density
TRAIN_GRID = gl.TRAIN_GRID

# Collect grid density
COLLECT_GRID = gl.COLLECT_GRID

# Order of spline interpolation
INTERP = gl.TRAIN_INTERP

# List of available optimizers 
OPTIMIZERS = ['rmsprop', 'sgd', 'adagrad', 'adadelta', 'adam', 'adamax', 'nadam']

# Number of epochs
EPOCHS = gl.TRAIN_EPOCHS

# Batch size
BATCH = gl.TRAIN_BATCH

# Objective function
def F (x):
    return gl.TIME_COMP_IMPOTANCE * x[0] + gl.TIME_EXEC_IMPOTANCE * x[1] + gl.MEMORY_IMPOTANCE * x[2]

# Default value of objective function
FL = F((1.0,1.0,1.0))

# Create grid for values of group of parameters
def grid (group, ranges=par.ranges, steps=COLLECT_GRID):

    ax = []
    for parname in group:
        start, stop = ranges[parname]
        if par.types[parname] == bool:
            steps = 1
        elif par.types[parname] == int:
            d = stop - start
            steps = d if d < steps else steps
        ax.append(np.linspace(start, stop, num=steps+1, dtype=par.types[parname]))

    l = list(map(lambda x: x.flatten().tolist(), np.meshgrid(*ax, sparse=False, indexing='ij')))

    return list(zip(*l))

#########################################################################################
# Collect the raw data

def collect():

    import func

    def calculate (specs, pars):
        try:
            func.calculate_abs_values(specs, pars)
        except func.ExternalScriptError as error:
            raise KeyboardInterrupt(error)

    print('Collect the raw data')
    
    # Calculate default values
    calculate(SPECS, {})

    # Collect the raw data for current group of parameters
    for gr in PARS.keys():

        points = grid(gr)
        default = tuple([par.defaults[x] for x in gr])
        
        # Add data for default values of parameters
        for spec, procs in SPECS.items():
            t_c, t_e, v_mem = DB.default[spec]
            DB.add(spec, procs, dict(zip(gr, default)), t_c, t_e, v_mem)
        
        # Calculate values in points and store data
        for point in points:
            if point != default:
                calculate(SPECS, dict(zip(gr, point)))

#########################################################################################
# Train neural network

def average (l):
    return sum(l) / float(len(l))

def run ():
    
    DB.load()

    print('Train neural network')

    C = {}                       # Characters of procedures of specs
    R = {gr : {} for gr in PARS} # Ranges of parameters in every group
    D = {gr : [] for gr in PARS} # Specs data for every group
    cnt = 0                      # Maximal counter in all specs

    # Treat specs, read its characters and store data
    for spec in SPECS.keys():
        
        procs = SPECS[spec]

        # Read characters of procedures
        chars = stat.read_procs_chars(spec)
        weights = stat.read_procs_weights(spec)
        C[spec] = [ (weight, chars[proc]) for proc, weight in weights if proc in chars ]

        # Find maximal counter
        cnt = max(cnt, weights)

        # Store data for every group of parameters
        for gr in PARS.keys():
            
            procs_t = () if procs is None else tuple(procs)
            
            # Check that there is the raw data for given group of parameters
            if not spec in DB.values:
                continue
            if not procs_t in DB.values[spec]:
                continue
            if not gr in DB.values[spec][procs_t]:
                continue

            # Form list of the raw data
            vh = DB.values[spec][procs_t][gr]
            vs = [ (v, average(list(map(lambda x: F(x), vh[v])))) for v in vh.keys()]

            # Check that data is suitable
            if not any (x[1] < FL for x in vs):
                continue

            # Correct minimal and maximal values for every parameter in given group
            for x in vs:
                for i in range(0,len(gr)):
                    min_value = max_value = x[0][i]
                    if gr[i] in R[gr]:
                        if R[gr][gr[i]][0] < min_value:
                            min_value = R[gr][gr[i]][0]
                        if R[gr][gr[i]][1] > max_value:
                            max_value = R[gr][gr[i]][1]
                    R[gr][gr[i]] = (min_value, max_value)

            # Store data
            if len(gr) == 1:
                vs.sort()
            D[gr].append([spec, [ i for i, j in vs ], [ j for i, j in vs ]])

    from scipy.interpolate import interp1d, griddata

    # Train neural network for a given group of parameters
    models = []
    for gr in PARS.keys():

        # Check that data is not empty for a given group of parameters
        if D[gr] == []: 
            verbose.warning('Train for parameters ' + str(gr) + ' are impossible since not enough data available.')
            continue

        # Set interpolation method
        method = INTERP
        if method == 'quadratic' and len(gr) > 1:
            verbose.warning('Method \'quadratic\' can not be used for training data of parameters ' + str(gr) + ', method \'linear\' will be used.')
            method = 'linear'
        if method == 'cubic' and len(gr) > 2:
            verbose.warning('Method \'cubic\' can not be used for training data of parameters ' + str(gr) + ', method \'linear\' will be used.')
            method = 'linear'

        # Create grid for interpolation
        gridd = grid(gr, R[gr], TRAIN_GRID)

        # Fill data list
        data = []
        for spec, points, values in D[gr]:

            # Calculate interpolation function
            if len(gr) == 1:
                points = list(map(lambda x: x[0], points))
                f = interp1d(points, values, kind=method, axis=0, bounds_error=False, fill_value='extrapolate')
            else:
                f = lambda x: griddata(points, values, x, method=method)

            # Calculate interpolated values
            val = FL - f(gridd)

            # Normalize interpolated values
            if max(val) != 0:
                val = np.maximum(val / max (val), 0)

            # Store pairs of procedures characters and values normalized with respect to procedures counters
            for c in C[spec]:
                if c[0] != 0:
                    n_val = val * np.exp(c[0] / cnt)
                    n_val = [np.asscalar(x) for x in n_val]
                    data.append((c[1], n_val))

        N = int(DELTA * len(data))

        # Create a model of neural network
        from tensorflow import keras, get_logger
        get_logger().setLevel('ERROR') # make tensorflow more silent
        model = keras.Sequential([keras.layers.Flatten(input_shape=(48,)),
                                  keras.layers.Dense(int(len(gridd) / 2), activation='relu'),
                                  keras.layers.Dense(int(len(gridd) / 2), activation='relu'),
                                  keras.layers.Dense(len(gridd), activation='softmax')])
        
        acc_t = {}
        loss_t = {}
        for optimizer in OPTIMIZERS:

            # Set optimizer
            model.compile( optimizer=optimizer, loss='categorical_crossentropy', metrics=['categorical_accuracy'])

            opt_acc = []
            opt_loss = []
            
            for i in range(TRAIN_STEPS):

                # Randomize data
                np.random.shuffle(data)

                # Train model
                train_X = np.array([ i for i, j in data[0:N] ])
                train_Y = np.array([ j for i, j in data[0:N] ])
                model.fit(train_X, train_Y, epochs=EPOCHS, batch_size=BATCH, verbose=False)

                # Check model
                test_X = np.array([ i for i, j in data[N:] ])
                test_Y = np.array([ j for i, j in data[N:] ])
                loss, acc = model.evaluate(test_X, test_Y, verbose=False)

                opt_acc.append(acc)
                opt_loss.append(loss)

            acc_t[optimizer] = average(opt_acc)
            loss_t[optimizer] = average(opt_loss)

        max_acc = max(acc_t.values())
        min_loss = min([loss_t[op] for op in OPTIMIZERS if acc_t[op] == max_acc])
        best_opt = [op for op in OPTIMIZERS if acc_t[op] == max_acc and loss_t[op] == min_loss]

        # Set best optimizer
        model.compile( optimizer=best_opt[0], loss='categorical_crossentropy', metrics=['categorical_accuracy'])

        # Train model
        data_X = np.array([ i for i, j in data ])
        data_Y = np.array([ j for i, j in data ])
        model.fit(data_X, data_Y, epochs=EPOCHS, batch_size=BATCH, verbose=False)

        # Save model
        models.append((gr, gridd, model))

    # Write models
    export.write(models)

#########################################################################################
# Use neural network to find parameters values

# Поиск оптимальные значения параметров компилятора lcc
def find ():
    
    procs_chars = stat.read_procs_chars()
    procs_weights = stat.read_procs_weights()
    procs = [ proc for proc in procs_chars.keys() if proc in procs_weights.keys() ]
    chars = { proc : procs_chars[proc] for proc in procs }
    weights = { proc : procs_weights[proc] for proc in procs }
        
    pars_to_models = export.read()
    print('Optimal values of parameters')
    for gr in PARS.keys():

        model = pars_to_models[gr]
        val_grids = list(map(model.predict, chars))
        val_grid = np.average(val_grids, weights=np.array(weights))
        val = np.unravel_index(np.argmax(val_grid), val_grid.shape)

        for i in range(len(gr)):
            print(' ', gr[i], '=', val[i])
