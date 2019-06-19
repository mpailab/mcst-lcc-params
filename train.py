#!/usr/bin/python
# -*- coding: utf-8 -*-

# External imports
import os, sys, shutil
from functools import reduce
import matplotlib.pyplot as plt
import numpy as np
import pickle
import tensorflow as tf
from tensorflow import keras
from scipy import interpolate

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Internal imports
import options as gl
import read
import specs
import strategy

# Table of groups of parameters
PARS = {tuple(g) : 1 for g in strategy.get()}

# Table of specs
SPECS = specs.get()

# Dataset directory
DATA_DIR = gl.TRAIN_DATA_DIR

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

    def w_loads_num (self):
        return self.loads_num * self.counter

    def loads_density (self):
        return self.loads_num / self.opers_num

    def w_stores_num (self):
        return self.stores_num * self.counter

    def stores_density (self):
        return self.stores_num / self.opers_num

class Loop:
    def __init__ (self, n, ovl, red):
        self.number = n    # номер цикла
        self.is_ovl = ovl  # признак накрученного цикла
        self.is_red = red  # признак сводимиго цикла

class Proc:
    def __init__ (self, name, t, ns, ls, ds, ps):
        self.name = name           # имя процедуры
        self.ticks = t             # число тактов исполнения процедуры
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
            return reduce(lambda a, n: a + n.calls_density(), self.nodes, 0) / self.max_cnt()
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
            return reduce(lambda a, n: a + n.loads_density(), self.nodes, 0) / self.max_cnt()
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
            return reduce(lambda a, n: a + n.stores_density(), self.nodes, 0) / self.max_cnt()
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

NODE_TYPE = {
    "Simple" : 0,
    "If"     : 1,
    "Return" : 2,
    "Start"  : 3,
    "Stop"   : 4,
    "Switch" : 5,
    "Hyper"  : 6,
    "Jump"   : 7,
    "Tmp"    : 8
    }

CHARS = [
    (  0, "Число тактов исполнения процедуры", lambda p: p.ticks),
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
    def __init__ (self, spec):

        # Spec name
        self.spec = spec

        # List of characters
        self.chars = []

        # Table of values
        # Format: procs -> (par_1,...,par_n) -> (val_1,...,val_n) -> [(t_c/t0_c, t_e/t0_e, v_mem/v0_mem), ... ]
        self.values = {}

        # Default values for current launch
        # Format : (t0_c, t0_e, v0_mem)
        self.default = None

        # Load default database
        self.load()
    
    # Load database from sourse
    def load (self, sourse = DATA_DIR):

        if os.path.exists(sourse):
            path = os.path.join(sourse, self.spec + '.bat')
            if os.path.isfile(path):
                with open(path, 'rb') as f:
                    self.values = pickle.load(f)
    
    # Save database from sourse
    def save (self, sourse = DATA_DIR):

        if not os.path.exists(sourse):
            os.makedirs(sourse)
            
        if bool(self.values):
            path = os.path.join(sourse, self.spec + '.bat')
            with open(path, 'wb') as f:
                pickle.dump(self.values, f, 2)
                
    # Add value to database
    # Format of pv: {par_1 : val_1, ..., par_n : val_n}
    def add (self, procs, pv, t_c, t_e, v_mem):

        if bool(pv):
            # TODO Add default values of parameters to database
            self.default = (t_c, t_e, v_mem)

        else:
            k = () if procs is None else tuple(procs)
            p = list(pv.keys())
            p.sort()
            p = tuple(p)
            v = tuple(map(lambda x: pv[x], p))
            r = (t_c / self.default[0], t_e / self.default[1], v_mem / self.default[2])
            
            if k in self.values and p in self.values[k] and v in self.values[k][p]:
                self.values[k][p][v].append(r)
            else:
                self.values[k][p][v] = [r]

    # Read characters of procedures
    def read (self, procs):
        
        proc_order = read.weights_of_exec_procs(self.spec)

        for name in procs:

            proc_info = read.proc(self.spec, name)

            t = proc_order[name] if name in proc_order else 0.0

            nodes = []
            for n in proc_info.nodes:
                node = proc_info.nodes[n]
                nodes.append(Node(int(n), 
                                  NODE_TYPE[node['type']], 
                                  float(node['cnt']), 
                                  int(node['o_num']), 
                                  int(node['c_num']), 
                                  int(node['l_num']), 
                                  int(node['s_num'])))

            loops = []
            for l in proc_info.loops:
                loop = proc_info.loops[l]
                loops.append(Loop(int(l), 
                                  bool(loop['ovl']), 
                                  bool(loop['red'])))

            proc = Proc(name, t, nodes, loops,
                        [int(proc_info.chars['dom_height']),
                         int(proc_info.chars['dom_weight']),
                         int(proc_info.chars['dom_succs'])],
                        [int(proc_info.chars['pdom_height']),
                         int(proc_info.chars['pdom_weight']),
                         int(proc_info.chars['pdom_succs'])])

            self.chars.append(list(map(lambda x: float(calc(x, proc)), CHARS)))


# Database
DB = {spec : DataBase(spec) for spec in SPECS.keys()}
    
# Close database
def close ():
    map(lambda spec: DB[spec].save(), SPECS.keys())

# Models directory
MODEL_DIR = gl.TRAIN_MODEL_DIR

# Order of spline interpolation
INTERP = gl.TRAIN_INTERP

# Grid density
GRID = gl.TRAIN_GRID

# Percent of train data
DELTA = gl.TRAIN_DELTA

# Objective function
def F (x):
    return gl.TIME_COMP_IMPOTANCE * x[0] + gl.TIME_EXEC_IMPOTANCE * x[1] + gl.MEMORY_IMPOTANCE * x[2]

# Default value of objective function
FL = F((1.0,1.0,1.0))

def average (l):
    return sum(l) / float(len(l))

def grid (dim, x):
    if dim == 1:
        return np.mgrid[0 : x[0] + GRID : GRID]
        
    elif dim == 2:
        return np.mgrid[0 : x[0] + GRID : GRID, 0 : x[1] + GRID : GRID]
        
    elif dim == 3:
        return np.mgrid[0 : x[0] + GRID : GRID, 0 : x[1] + GRID : GRID, 0 : x[2] + GRID : GRID]
        
    elif dim == 4:
        return np.mgrid[0 : x[0] + GRID : GRID, 0 : x[1] + GRID : GRID, 0 : x[2] + GRID : GRID, 0 : x[3] + GRID : GRID]
        
    elif dim == 5:
        return np.mgrid[0 : x[0] + GRID : GRID, 0 : x[1] + GRID : GRID, 0 : x[2] + GRID : GRID, 0 : x[3] + GRID : GRID, 0 : x[4] + GRID : GRID]
        
    else:
        print("Error! Can't train a neural network. The dimension of a group of parameters is too large.")
        sys.exit()

def run (): 

    Table = {}
    for p in PARS.keys():
        Table[p] = [tuple([0 for x in p]),[]]

    cnt = 0

    for spec in SPECS.keys():

        procs = SPECS[spec]

        # Read characters of procedures
        DB[spec].read(procs)

        # Find maximal counter
        cnt = max(cnt, max(map(lambda x: x[0], DB[spec].chars)))

        for p in PARS.keys():
            if p in DB[spec].values[tuple(procs)]:
                vh = DB[spec].values[tuple(procs)][p]
                vs = [ (v, average(list(map(lambda x: F(x), vh[v])))) for v in vh.keys()]
                if any (x[1] < FL for x in vs):
                    for x in vs:
                        for i in range(0,len(x[0])):
                            if Table[p][0][i] < x[0][i]: 
                                Table[p][0][i] = x[0][i]
                    x = [ i for i, j in vs ]
                    y = [ j for i, j in vs ]
                    Table[p][1].append([spec,x,y])

    for p in Table.keys():

        if Table[p][1] == []: 
            print('Warning! Train for params', p, 'are impossible since not enough data available.')
            continue

        data = []
        grid = grid(len(p), Table[p][0])
        for ls in Table[p][1]:
            spec = ls[0]
            val = FL - interpolate.griddata(ls[1], ls[2], grid, method=INTERP)
            if max(val) != 0:
                val = np.maximum(val / max (val), 0)
            for c in DB[spec].chars:
                if c[0] != 0:
                    data.append((c[1:], val * np.exp(c[0] / cnt)))

        np.random.shuffle(data)

        N = int(DELTA * len(data))

        train_X = np.array([ i for i, j in data[0:N] ])
        train_Y = np.array([ j for i, j in data[0:N] ])

        test_X = np.array([ i for i, j in data[N:] ])
        test_Y = np.array([ j for i, j in data[N:] ])

        model = keras.Sequential([keras.layers.Flatten(input_shape=(48,)),
                                keras.layers.Dense(int(GRID / 2), activation='relu'),
                                keras.layers.Dense(int(GRID / 2), activation='relu'),
                                keras.layers.Dense(GRID + 1, activation='softmax')])
        model.compile( #optimizer='rmsprop',
                    #optimizer='sgd',
                    #optimizer='adagrad',
                    #optimizer='adadelta',
                    #optimizer='adam',
                    #optimizer='adamax',
                    optimizer='nadam',
                    loss='categorical_crossentropy',
                    metrics=['categorical_accuracy'])

        model.fit(train_X, train_Y, epochs=100, batch_size=100, verbose=False)
        test_loss, test_acc = model.evaluate(test_X, test_Y, verbose=False)

        # predictions=model.predict(test_X)
        # print(predictions[0])
        # print(test_Y[0])
        # plt.plot(grid, test_Y[0], '-', grid, predictions[0], 'o')
        # plt.show()

        model.save(MODEL_DIR + '/' + p + '_model.h5')
    