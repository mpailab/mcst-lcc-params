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

class Node:
    def __init__ (self, n, t, c, on, cn, ln, sn):
        self.number     = n     # номер узла
        self.type       = t     # тип узла
        self.counter    = c     # счётчик узла
        self.opers_num  = on    # число операций в узле
        self.calls_num  = cn    # число операций вызова в узле
        self.loads_num  = ln    # число операций чтения в узле
        self.stores_num = sn    # число операций записи в узле

    def w_opers_num (self):
        return self.opers_num * self.counter

    def w_calls_num (self):
        return self.calls_num * self.counter

    def calls_density (self):
        return self.calls_num / self.opers_num

    def w_calls_density (self):
        return self.w_calls_num() / self.opers_num

    def w_loads_num (self):
        return self.loads_num * self.counter

    def loads_density (self):
        return self.loads_num / self.opers_num

    def w_loads_density (self):
        return self.w_loads_num() / self.opers_num

    def w_stores_num (self):
        return self.stores_num * self.counter

    def stores_density (self):
        return self.stores_num / self.opers_num

    def w_stores_density (self):
        return self.w_stores_num() / self.opers_num

class Loop:
    def __init__ (self, n, ovl, red):
        self.number = n    # номер цикла
        self.is_ovl = ovl  # признак накрученного цикла
        self.is_red = red  # признак сводимиго цикла

class Proc:
    def __init__ (self, name, w, ns, ls, ds, ps):
        self.name = name           # имя процедуры
        self.weight = w            # вес процедуры
        self.nodes = ns            # узлы процедуры
        self.loops = ls            # циклы процедуры
        self.dom_height  = ds[0]   # высота дерева доминаторов
        self.dom_weight  = ds[1]   # ширина дерева доминаторов
        self.dom_branch  = ds[2]   # максимальное ветвление вершины в дереве доминаторов
        self.pdom_height = ps[0]   # высота дерева постдоминаторов
        self.pdom_weight = ps[1]   # ширина дерева постдоминаторов
        self.pdom_branch = ps[2]   # максимальное ветвление вершины в дереве постдоминаторов

    def opers_num (self):
        return reduce(lambda a, n: a + n.opers_num, self.nodes, 0)

    def w_opers_num (self):
        if self.max_cnt():
            return reduce(lambda a, n: a + n.w_opers_num(), self.nodes, 0) / self.max_cnt()
        else:
            return 0

    def max_opers_num (self):
        return reduce(max, map(lambda n: n.opers_num, self.nodes), 0)

    def aver_opers_num (self):
        return self.opers_num() / self.nodes_num()

    def w_aver_opers_num (self):
        return self.w_opers_num() / self.nodes_num()

    def calls_num (self):
        return reduce(lambda a, n: a + n.calls_num, self.nodes, 0)

    def w_calls_num (self):
        if self.max_cnt():
            return reduce(lambda a, n: a + n.w_calls_num(), self.nodes, 0) / self.max_cnt()
        else:
            return 0

    def max_calls_num (self):
        return reduce(max, map(lambda n: n.calls_num, self.nodes), 0)

    def aver_calls_num (self):
        return self.calls_num() / self.nodes_num()

    def w_aver_calls_num (self):
        return self.w_calls_num() / self.nodes_num()

    def calls_density (self):
        return reduce(lambda a, n: a + n.calls_density(), self.nodes, 0)

    def w_calls_density (self):
        if self.max_cnt():
            return reduce(lambda a, n: a + n.w_calls_density(), self.nodes, 0) / self.max_cnt()
        else:
            return 0

    def max_calls_density(self):
        return reduce(max, map(lambda n: n.calls_density(), self.nodes), 0)

    def aver_calls_density(self):
        return self.calls_density() / self.nodes_num()

    def w_aver_calls_density(self):
        return self.w_calls_density() / self.nodes_num()

    def loads_num (self):
        return reduce(lambda a, n: a + n.loads_num, self.nodes, 0)

    def w_loads_num (self):
        if self.max_cnt():
            return reduce(lambda a, n: a + n.w_loads_num(), self.nodes, 0) / self.max_cnt()
        else:
            return 0

    def max_loads_num (self):
        return reduce(max, map(lambda n: n.loads_num, self.nodes), 0)

    def aver_loads_num (self):
        return self.loads_num() / self.nodes_num()

    def w_aver_loads_num (self):
        return self.w_loads_num() / self.nodes_num()

    def loads_density (self):
        return reduce(lambda a, n: a + n.loads_density(), self.nodes, 0)

    def w_loads_density (self):
        if self.max_cnt():
            return reduce(lambda a, n: a + n.w_loads_density(), self.nodes, 0) / self.max_cnt()
        else:
            return 0

    def max_loads_density(self):
        return reduce(max, map(lambda n: n.loads_density(), self.nodes), 0)

    def aver_loads_density(self):
        return self.loads_density() / self.nodes_num()

    def w_aver_loads_density(self):
        return self.w_loads_density() / self.nodes_num()

    def stores_num (self):
        return reduce(lambda a, n: a + n.stores_num, self.nodes, 0)

    def w_stores_num (self):
        if self.max_cnt():
            return reduce(lambda a, n: a + n.w_stores_num(), self.nodes, 0) / self.max_cnt()
        else:
            return 0

    def max_stores_num (self):
        return reduce(max, map(lambda n: n.stores_num, self.nodes), 0)

    def aver_stores_num (self):
        return self.stores_num() / self.nodes_num()

    def w_aver_stores_num (self):
        return self.w_stores_num() / self.nodes_num()

    def stores_density (self):
        return reduce(lambda a, n: a + n.stores_density(), self.nodes, 0)

    def w_stores_density (self):
        if self.max_cnt():
            return reduce(lambda a, n: a + n.w_stores_density(), self.nodes, 0) / self.max_cnt()
        else:
            return 0

    def max_stores_density(self):
        return reduce(max, map(lambda n: n.stores_density(), self.nodes), 0)

    def aver_stores_density(self):
        return self.stores_density() / self.nodes_num()

    def w_aver_stores_density(self):
        return self.w_stores_density() / self.nodes_num()

    def nodes_num (self):
        return len(self.nodes)

    def w_nodes_num (self):
        if self.max_cnt():
            return reduce(lambda a, n: a + n.counter, self.nodes, 0) / self.max_cnt()
        else:
            return 0

    def loops_num (self):
        return len(self.loops)

    def ovl_loops_num (self):
        return len([l for l in self.loops if l.is_ovl])

    def irr_loops_num (self):
        return len([l for l in self.loops if not l.is_red])

    def max_cnt (self):
        return reduce(max, map(lambda n: n.counter, self.nodes), 0)

    def aver_cnt (self):
        return reduce(lambda a, n: a + n.counter, self.nodes, 0) / self.nodes_num()

CHARS = [
    (  0, "Вес процедуры", lambda p: p.weight),
    (  1, "Число операций", Proc.opers_num),
    (  2, "Взвешенное число операций", Proc.w_opers_num),
    (  3, "Максимальное число операций в узле", Proc.max_opers_num),
    (  4, "Среднее число операций в узле", Proc.aver_opers_num),
    (  5, "Взвешенное среднее число операций в узле", Proc.w_aver_opers_num),

    (  6, "Число операций вызова", Proc.calls_num),
    (  7, "Взвешенное число операций вызова", Proc.w_calls_num),
    (  8, "Максимальное число операций вызова в узле", Proc.max_calls_num),
    (  9, "Среднее число операций вызова в узле", Proc.aver_calls_num),
    ( 10, "Взвешенное среднее число операций вызова в узле", Proc.w_aver_calls_num),
    ( 11, "Плотность операций вызова", Proc.calls_density),
    ( 12, "Взвешенная плотность операций вызова", Proc.w_calls_density),
    ( 13, "Максимальная плотность операций вызова в узле", Proc.max_calls_density),
    ( 14, "Средняя плотность операций вызова в узле", Proc.aver_calls_density),
    ( 15, "Взвешенная средняя плотность операций вызова в узле", Proc.w_aver_calls_density),

    ( 16, "Число операций чтения", Proc.loads_num),
    ( 17, "Взвешенное число операций чтения", Proc.w_loads_num),
    ( 18, "Максимальное число операций чтения в узле", Proc.max_loads_num),
    ( 19, "Среднее число операций чтения в узле", Proc.aver_loads_num),
    ( 20, "Взвешенное среднее число операций чтения в узле", Proc.w_aver_loads_num),
    ( 21, "Плотность операций чтений", Proc.loads_density),
    ( 22, "Взвешенная плотность операций вызова", Proc.w_loads_density),
    ( 23, "Максимальная плотность операций вызова в узле", Proc.max_loads_density),
    ( 24, "Средняя плотность операций вызова в узле", Proc.aver_loads_density),
    ( 25, "Взвешенная средняя плотность операций вызова в узле", Proc.w_aver_loads_density),

    ( 26, "Число операций записи", Proc.stores_num),
    ( 27, "Взвешенное число операций записи", Proc.w_stores_num),
    ( 28, "Максимальное число операций записи в узле", Proc.max_stores_num),
    ( 29, "Среднее число операций записи в узле", Proc.aver_stores_num),
    ( 30, "Взвешенное среднее число операций записи в узле", Proc.w_aver_stores_num),
    ( 31, "Плотность операций записи", Proc.stores_density),
    ( 32, "Взвешенная плотность операций вызова", Proc.w_stores_density),
    ( 33, "Максимальная плотность операций вызова в узле", Proc.max_stores_density),
    ( 34, "Средняя плотность операций вызова в узле", Proc.aver_stores_density),
    ( 35, "Взвешенная средняя плотность операций вызова в узле", Proc.w_aver_stores_density),

    ( 36, "Число узлов", Proc.nodes_num),
    ( 37, "Взвешенное число узлов", Proc.w_nodes_num),

    ( 38, "Число циклов", Proc.loops_num),
    ( 39, "Число накрученных циклов", Proc.ovl_loops_num),
    ( 40, "Число несводимых циклов", Proc.irr_loops_num),

    ( 41, "Максимальный счётчик", Proc.max_cnt),
    ( 42, "Средний счётчик", Proc.aver_cnt),

    ( 43, "Высота дерева доминаторов", lambda p: p.dom_height),
    ( 44, "Ширина дерева доминаторов", lambda p: p.dom_weight),
    ( 45, "Максимальное ветвление вершин в дереве доминаторов", lambda p: p.dom_branch),

    ( 46, "Высота дерева постдоминаторов", lambda p: p.pdom_height),
    ( 47, "Ширина дерева постдоминаторов", lambda p: p.pdom_weight),
    ( 48, "Максимальное ветвление вершин в дереве постдоминаторов", lambda p: p.pdom_branch),
]

def desc (param):
    return "{:>3} : {:>1}".format(param[0], param[1])

def calc (param, proc):
    f = param[2]
    return f(proc)

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

# Models directory
MODEL_DIR = gl.TRAIN_MODEL_DIR

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

# Read characters of procedures
def read_procs (spec, procs, stat_dir = None, weight_file = None):
    
    procs_and_weights = stat.get_procs_and_weights(spec, procs)
    procs = procs_and_weights[0]
    proc_order = procs_and_weights[1]

    res = []
    for proc in procs:

        proc_info = stat.get_proc(spec, proc, stat_dir)
        
        w_proc = stat.proc_weight(proc_order, proc)

        nodes = []
        for n in proc_info.nodes:
            node = proc_info.nodes[n]
            nodes.append(Node(int(n),
                                gl.NODE_TYPE[node.chars['type']], 
                                float(node.chars['cnt']), 
                                int(node.chars['o_num']), 
                                int(node.chars['c_num']), 
                                int(node.chars['l_num']), 
                                int(node.chars['s_num'])))

        loops = []
        for l in proc_info.loops:
            loop = proc_info.loops[l]
            loops.append(Loop(int(l), 
                                bool(loop['ovl']), 
                                bool(loop['red'])))

        res.append(Proc(proc, w_proc, nodes, loops,
                        [int(proc_info.chars['dom_height']),
                            int(proc_info.chars['dom_weight']),
                            int(proc_info.chars['dom_succs'])],
                        [int(proc_info.chars['pdom_height']),
                            int(proc_info.chars['pdom_weight']),
                            int(proc_info.chars['pdom_succs'])]))
    return res

def proc_to_chars (proc):
    return list(map(lambda x: float(calc(x, proc)), CHARS))

def to_chars (procs):
    return list(map(proc_to_chars, procs))
    
def read_proc_chars (spec, procs, stat_dir = None, weight_file = None):
    return to_chars(read_procs(spec, procs, stat_dir, weight_file))

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
    
    # Check statistics correctness
    stat.check(SPECS)

    print('Train neural network')

    C = {}                       # Characters of procedures of specs
    R = {gr : {} for gr in PARS} # Ranges of parameters in every group
    D = {gr : [] for gr in PARS} # Specs data for every group
    cnt = 0                      # Maximal counter in all specs

    # Treat specs, read its characters and store data
    for spec in SPECS.keys():
        
        procs = SPECS[spec]

        # Read characters of procedures
        C[spec] = read_proc_chars(spec, procs)

        # Find maximal counter
        cnt = max(cnt, max(map(lambda x: x[0], C[spec])))

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
                    data.append((c[1:], val * np.exp(c[0] / cnt)))

        N = int(DELTA * len(data))

        # Create a model of neural network
        from tensorflow import keras
        model = keras.Sequential([keras.layers.Flatten(input_shape=(48,)),
                                  keras.layers.Dense(int(len(gridd) / 2), activation='relu'),
                                  keras.layers.Dense(int(len(gridd) / 2), activation='relu'),
                                  keras.layers.Dense(len(gridd), activation='softmax')])
        
        acc = []
        loss = []
        for optimizer in OPTIMIZERS:

            # Set optimizer
            model.compile( optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['categorical_accuracy'])

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

            acc.append(average(opt_acc))
            loss.append(average(opt_loss))

        max_acc = max(acc)
        min_loss = min([x for i in range(OPTIMIZERS) for x in loss if x == loss[i] and acc[i] == max_acc])
        best_opt = [i for i in range(OPTIMIZERS) if acc[i] == max_acc and loss[i] == min_loss]

        # Set best optimizer
        model.compile( optimizer=best_opt[0], loss='sparse_categorical_crossentropy', metrics=['categorical_accuracy'])

        # Train model
        model.fit([i for i, j in data], [j for i, j in data], epochs=EPOCHS, batch_size=BATCH, verbose=False)

        # Save model
        model.save(os.path.join(MODEL_DIR, gr + '_model.h5'))
        models.append((model, gridd, gr))

    # Write models in c code
    export.write(models)

#########################################################################################
# Use neural network to find parameters values

# Поиск оптимальные значения параметров компилятора lcc
def find ():

    if not gl.TRAIN_PROC_CHARS and gl.TRAIN_PROC_CHARS_DIR is None:
        verbose.error('Нет характеристик процедур, для которых необходимо найти оптимальные значения параметров компилятора lcc.')

    if gl.TRAIN_PROC_CHARS and not gl.TRAIN_PROC_CHARS_DIR is None:
        verbose.warning('Одновременно указаны характеристики процедур и каталог со статистикой процедур, '
                        'для которых необходимо найти оптимальные значения параметров компилятора lcc. '
                        'Будут использованы характеристики процедур, заданные опцией --proc_chars.')

    if gl.TRAIN_PROC_CHARS:
        chars = to_chars([Proc( 'tmp', p[0], [Node(*n) for n in  p[1]], [Loop(*l) for l in  p[2]], p[3], p[4]) for p in gl.TRAIN_PROC_CHARS])

    else:
        procs = [x[1] for x in os.walk(gl.TRAIN_PROC_CHARS_DIR)]

        for proc in procs:
            stat_file = os.path.join(gl.TRAIN_PROC_CHARS_DIR, proc, 'regions.txt')
            if not os.path.isfile(stat_file):
                verbose.error('Incorrect statictic for proc %r. There is not file %r.' % (proc, stat_file))
        
        if gl.TRAIN_PROC_WEIGHTS is None:
            verbose.error('Weights for procs was not defined. There is not file %r.' % gl.TRAIN_PROC_WEIGHTS)

        chars = read_proc_chars('tmp', procs, gl.TRAIN_PROC_CHARS_DIR, gl.TRAIN_PROC_WEIGHTS)
        

    from tensorflow import keras

    print('Optimal values of parameters')
    for p in PARS.keys():

        model = keras.models.load_model(os.path.join(MODEL_DIR, p + '_model.h5'))
        val_grids = [model.predict(p[1:]) for p in chars]
        val_grid = np.average(val_grids, weights=np.array([p[0] for p in chars]))
        val = np.unravel_index(np.argmax(val_grid), val_grid.shape)

        for i in range(len(p)):
            print(' ', p[i], '=', val[i])
