#!/usr/bin/python
# -*- coding: utf-8 -*-

# External imports
import os, sys
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow import keras
from scipy import interpolate
from functools import reduce

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Internal imports
import options as gl
import specs
import strategy as strat

#########################################################################################
# Globals

# Default parameters
PARS = {
    'ifconv_calls_num'          : ( 0, 6),
    'ifconv_merge_heur'         : ( 1, 1.0),
    'ifconv_opers_num'          : ( 2, 200),
    'regn_disb_heur'            : ( 3, 9),
    'regn_heur1'                : ( 4, 0.037),
    'regn_heur2'                : ( 5, 0.06),
    'regn_heur3'                : ( 6, 0.03),
    'regn_heur4'                : ( 7, 0.0),
    'regn_heur_bal1'            : ( 8, 0.0),
    'regn_heur_bal2'            : ( 9, 0.0),
    'regn_max_proc_op_sem_size' : (10, 16000),
    'regn_opers_limit'          : (11, 2048),
    'regn_prob_heur'            : (12, 0.04),
    }
Np = len(PARS.keys())

# Default spec names
SPECS = [
    '500.perlbench',
    '502.gcc',
    '503.bwaves',
    '505.mcf',
    '508.namd',
    '510.parest',
    '511.povray',
    '519.lbm',
    '521.wrf',
    '523.xalancbmk',
    '525.x264',
    '526.blender',
    '527.cam4',
    '531.deepsjeng',
    '538.imagick',
    '541.leela',
    '544.nab',
    '548.exchange2',
    '549.fotonik3d',
    '554.roms',
    '557.xz'
    ]
Ns = len(SPECS)

# Objective function
def F (Tc,Te,V):
    return Tc + 5*Te + V

# Default value of objective function
FL = F(1.0,1.0,1.0)

#########################################################################################
# Read database

pars = = list(set(reduce(lambda x, y: x + y, strat.get())))
specs = specs.get().keys()
dataset = gl.TRAIN_DATA_DIR
interp = gl.DATA_INTERP
delta = gl.TRAIN_DELTA

class Spec:
    def __init__(self, name):
        self.name  = name
        self.procs = []

def read_proc (str):
    return list(map(float, str.split(' ')))

def read_eval (str):
    x = str.split(':')
    return (float(x[0]), F(float(x[1]), float(x[2]), float(x[3])))
    
Table = {}
for p in pars:
    Table[p] = [0,[]]

MAX_COUNTER = 0

# print('Read database:')
for name in specs:

    if not os.path.exists(dataset + '/Params/' + name + '.txt'):
        print('Warning: ' + dataset + '/Params does not contain ' + name + '.txt. Spec ' + '\'' + name + '\' will be omitted.')
        continue

    if not os.path.exists(dataset + '/Values/' + name + '.txt'):
        print('Warning: ' + dataset + '/Values does not contain ' + name + '.txt. Spec ' + '\'' + name + '\' will be omitted.')
        continue

    spec = Spec(name)
    sys.stdout.write('  ' + name + ' ... ')
    sys.stdout.flush()

    with open(dataset + '/Params/' + name + '.txt', 'r') as f:
        spec.procs = [read_proc(line.rstrip('\n')) for line in f]

    MAX_COUNTER = max(MAX_COUNTER, max(map(lambda x: x[0], spec.procs)))

    with open(dataset + '/Values/' + name + '.txt', 'r') as f:
        rows = [line.rstrip('\n') for line in f]
        while len(rows) < Np: rows.append('')
        for p in PARS.keys():
            i = PARS[p][0]
            if p in Table and rows[i] != '':
                vh = {}
                for x in map(read_eval, rows[i].split()):
                    if not (x[0] in vh) or x[1] < vh[x[0]]: vh[x[0]] = x[1]
                vs = list(vh.items())
                if any (x[1] < 7 for x in vs):
                    vs.append((PARS[p][1], FL))
                    vs.sort()
                    x = [ i for i, j in vs ]
                    y = [ j for i, j in vs ]
                    f = interpolate.interp1d(x, y, kind=interp, fill_value="extrapolate")
                    if Table[p][0] < vs[-1][0]: Table[p][0] = vs[-1][0]
                    Table[p][1].append([spec,f,x,y])

    sys.stdout.write('ok\n')

# for p in Table.keys():
#     if Table[p][1] != []:
#         print(p + ':')
#         x = np.arange(0, 1.01*Table[p][0], Table[p][0]/100)
#         for spec in Table[p][1]:
#             print(spec[0].name + ':')
#             y = spec[1](x)
#             plt.plot(x, y, '-', spec[2], spec[3], 'o')
#             plt.show()

#########################################################################################
# Train neural network

def run():
    print('Train neural network:')
    for p in Table.keys():

        sys.stdout.write('  ' + p + ' ... ')
        sys.stdout.flush()

        if Table[p][1] == []: 
            print('Not enough data available')
            continue

        data = []
        step = Table[p][0]/100
        mask = x = np.arange(0, 101*step, step)
        for ls in Table[p][1]:
            spec = ls[0]
            f = ls[1]
            val = FL - f(mask)
            if max(val) != 0:
                val = np.maximum(val / max (val), 0)
            for proc in spec.procs:
                if proc[0] != 0:
                    data.append((proc[1:], val * np.exp(proc[0] / MAX_COUNTER)))

        # print('Data size: ' + str(len(data)))

        np.random.shuffle(data)

        N = int(delta*len(data))

        train_X = np.array([ i for i, j in data[0:N] ])
        train_Y = np.array([ j for i, j in data[0:N] ])

        test_X = np.array([ i for i, j in data[N:] ])
        test_Y = np.array([ j for i, j in data[N:] ])

        model = keras.Sequential([keras.layers.Flatten(input_shape=(48,)),
                                keras.layers.Dense(50, activation='relu'),
                                keras.layers.Dense(50, activation='relu'),
                                keras.layers.Dense(101, activation='softmax')])
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
        # plt.plot(mask, test_Y[0], '-', mask, predictions[0], 'o')
        # plt.show()

        sys.stdout.write('ok (accuracy ' + str(test_acc) + ')\n')

        model.save(gl.MODEL_DIR + '/' + p + '_model.h5')
    
