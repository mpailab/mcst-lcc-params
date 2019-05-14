#!/usr/bin/python
# -*- coding: utf-8 -*-

# External imports
import os, sys
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

# Internal imports
import options

# Default compiler options
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

def F (Tc,Te,V):
    return Tc + 5*Te + V

# Read script options
opts = options.read(sys.argv[1:], PARS.keys(), SPECS)

class Spec:
    def __init__(self, name):
        self.name  = name
        self.procs = []

def read_proc (str):
    return str.split(':')

def read_eval (str):
    x = str.split(':')
    return (float(x[0]), F(float(x[1]), float(x[2]), float(x[3])))
    
Table = {}
for p in opts.pars:
    Table[p] = [0,[]]

print('Spec initialization:')
for name in opts.specs:

    if not os.path.exists(opts.dataset + '/Params/' + name + '.txt'):
        print('Warning: ' + opts.dataset + '/Params does not contain ' + name + '.txt. Spec ' + '\'' + name + '\' will be omitted.')
        continue

    if not os.path.exists(opts.dataset + '/Values/' + name + '.txt'):
        print('Warning: ' + opts.dataset + '/Values does not contain ' + name + '.txt. Spec ' + '\'' + name + '\' will be omitted.')
        continue

    spec = Spec(name)
    sys.stdout.write(name + ' ... ')

    with open(opts.dataset + '/Params/' + name + '.txt', 'r') as f:
        spec.procs = list(map(read_proc, f.read()))

    with open(opts.dataset + '/Values/' + name + '.txt', 'r') as f:
        rows = [line.rstrip('\n') for line in f]
        while len(rows) < Np: rows.append('')
        for p in PARS.keys():
            i = PARS[p][0]
            if p in Table and rows[i] != '':
                vh = {}
                for x in map(read_eval, rows[i].split()):
                    if not (x[0] in vh) or x[1] < vh[x[0]]: vh[x[0]] = x[1]
                vs = vh.items()
                if any (x[1] < 7 for x in vs):
                    vs.append((PARS[p][1], F(1.0,1.0,1.0)))
                    vs.sort()
                    x = [ i for i, j in vs ]
                    y = [ j for i, j in vs ]
                    f = interpolate.interp1d(x, y, kind=opts.interp, fill_value="extrapolate")
                    if Table[p][0] < vs[-1][0]: Table[p][0] = vs[-1][0]
                    Table[p][1].append((spec,f,x,y))

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



# for spec in os.listdir(data_set + '/Params'):
#     if int(spec[0])
#     with open(data_set + '/Params', 'w') as f:
#         f.write("\n".join(map(desc, params)))



# class Spec:
#     def __init__(self, name, ps, vs):
#         self.name   = name   # имя задачи
#         self.params = ps     # параметры процедур задачи
#         self.values = vs     # относительные изменения времени компиляции, исполнения и потребляемой памяти по параметрам компиляции


# import numpy as np
# f=[]
# g=open('502.gcc.txt','r')
# f.append(g)
# g=open('549.fotonik3d.txt','r')
# f.append(g)
# g=open('548.exchange2.txt','r')
# f.append(g)
# g=open('538.imagick.txt','r')
# f.append(g)
# g=open('531.deepsjeng.txt','r')
# f.append(g)
# g=open('527.cam4.txt','r')
# f.append(g)
# g=open('525.x264.txt','r')
# f.append(g)
# g=open('523.xalancbmk.txt','r')
# f.append(g)
# g=open('521.wrf.txt','r')
# f.append(g)
# g=open('519.lbm.txt','r')
# f.append(g)
# g=open('511.povray.txt','r')
# f.append(g)
# g=open('510.parest.txt','r')
# f.append(g)
# g=open('508.namd.txt','r')
# f.append(g)
# g=open('505.mcf.txt','r')
# f.append(g)
# g=open('503.bwaves.txt','r')
# f.append(g)
# g=open('500.perlbench.txt','r')
# f.append(g)

# import pandas as pd
# pr=[]
# for i in range(16):
#     g=pd.read_table(f[i],sep=' ',header=None,names=[0,1,2,3,4,5,6,7,8,9,10,11,12],lineterminator='\n')
#     pr.append(g)

# pr1=[]
# for i in range (16):
#     pr1.append([])
#     for j in range (12):
#         pr1[i].append([])
#         for k in range (12):
#             pr1[i][j].append([])
#             for l in range (4):
#                 pr1[i][j][k].append([])
# for i in range (16):
#     for j in range (12):
#         for k in range (12):
#             for l in range (4):
#                 pr1[i][j][k][l]=0

# for i in range (16):
#     for j in range (12):
#         for k in range (12):
#             if (type(pr[i][j][k])==str):
#                 for l in range (4):
#                     pr1[i][j][k][l]=float(pr[i][j][k].split(":")[l])

# def Func(Tc,Tc0,Te,Te0,V,V0):
#     x=(Tc/Tc0)+5*(Te/Te0)+(V/V0)
#     return x

# start=[]
# num=[]
# for j in range (16) :
#     start.append(Func(pr1[j][1][0][1],pr1[j][0][0][1],pr1[j][1][0][2],pr1[j][0][0][2],pr1[j][1][0][3],pr1[j][0][0][3]))
#     num.append(0)
# print(start)

# for l in range (16) :
#     for i in range (12):
#         for j in range (12):
#             if (pr1[l][j][i][1]!=0)&(pr1[l][j][i][2]!=0)&(pr1[l][j][i][3]!=0):
#                 if (Func(pr1[l][j][i][1],pr1[l][0][i][1],pr1[l][j][i][2],pr1[l][0][i][2],pr1[l][j][i][3],pr1[l][0][i][3])<start[l]):
#                     start[l]=Func(pr1[l][j][i][1],pr1[l][0][i][1],pr1[l][j][i][2],pr1[l][0][i][2],pr1[l][j][i][3],pr1[l][0][i][3])
#                     num[l]=i
# print(num)

# pr2=[]
# for i in range(16):
#     g=pd.read_table(f[i],sep=' ',header=None,names=[i  for i in range (49)],lineterminator='\n')
#     pr2.append(g)

# pr3=[]
# for i in range (16):
#     pr3.append([])
#     for j in range (len(pr2[i][0])):
#         pr3[i].append([])
#         for k in range (49):
#             pr3[i][j].append([])

# for i in range (16):
#     for j in range (49):
#         for k in range (len(pr2[i][j])):
#             pr3[i][k][j]=float( pr2[i][j][k] )

# c=[]
# Inter=[] 
# for k in range (16):
#     c.append([])
# for k in range (16) :
#     for i in range (12) :
#         if (pr1[k][i][1][1]!=0)&(pr1[k][i][1][2]!=0)&(pr1[k][i][1][3]!=0):
#                 c[k].append([])
#                 for j in range (2):
#                     c[k][i].append([])
#                 c[k][i][0]=pr1[k][i][1][0]
#                 c[k][i][1]=Func(pr1[k][i][1][1],pr1[k][0][1][1],pr1[k][i][1][2],pr1[k][0][1][2],pr1[k][i][1][3],pr1[k][0][1][3])

#     c[k].sort()
# d=[]
# for k in range (16):
#     d.append([])
# for k in range (16):
#     d[k].append([c[k][0][0],c[k][0][1]])
#     for i in range (len(c[k])-1):
#         if (c[k][i+1][0]!=c[k][i][0]):
#             d[k].append([c[k][i+1][0],c[k][i+1][1]])


# a=[]
# b=[]
# for k in range (16):
#     a.append([])
#     b.append([])
# for k in range (16):
#     h=(d[k][len(d[k])-1][0]-d[k][0][0])/len(d[k])*0.05
#     if (d[k][0][1]<7):
#         a[k].append(d[k][0][0]-h)
#         if (d[k][1][1]>7):
#             k1=(d[k][0][1]-d[k][1][1])/(d[k][0][0]-d[k][1][0])
#             k2=d[k][0][1]-k1*d[k][0][0]
#             x=(7-k2)/k1
#             if (x<d[k][0][0]+h):
#                 b[k].append(x)
#             else :
#                 b[k].append(d[k][0][0]+h)
#         else :
#                 b[k].append(d[k][0][0]+h)         
    
#     for i in range (len(d[k])-2) :
#         if (d[k][i+1][1]<7):
#             if (d[k][i+2][1]>7):
#                 k1=(d[k][i+1][1]-d[k][i+2][1])/(d[k][i+1][0]-d[k][i+2][0])
#                 k2=d[k][i+1][1]-k1*d[k][i+1][0]
#                 x=(7-k2)/k1
#                 if (x<d[k][i+1][0]+h):
#                     b[k].append(x)
#                 else :
#                     b[k].append(d[k][i+1][0]+h)
#             else :
#                 b[k].append(d[k][i+1][0]+h)
#             if (d[k][i][1]>7):
#                 k1=(d[k][i+1][1]-d[k][i][1])/(d[k][i+1][0]-d[k][i][0])
#                 k2=d[k][i+1][1]-k1*d[k][i+1][0]
#                 x=(7-k2)/k1
#                 if (x>d[k][i+1][0]-h):
#                     a[k].append(x)
#                 else :
#                     a[k].append(d[k][i+1][0]-h)  
#             else :
#                 a[k].append(d[k][i+1][0]-h) 
        
#     if (d[k][len(d[k])-1][1]<7):
#         b[k].append(d[k][len(d[k])-1][0]+h)
#         if (d[k][len(d[k])-2][1]>7):
#             k1=(d[k][len(d[k])-1][1]-d[k][len(d[k])-2][1])/(d[k][len(d[k])-1][0]-d[k][len(d[k])-2][0])
#             k2=d[k][len(d[k])-1][1]-k1*d[k][len(d[k])-1][0]
#             x=(7-k2)/k1
#             if (x>d[k][len(d[k])-1][0]-h):
#                 a[k].append(x)
#             else :
#                 a[k].append(d[k][len(d[k])-1][0]-h)  
#         else :
#                 a[k].append(d[k][len(d[k])-1][0]-h)     

# lev=[]
# prav=[]
# for k in range (16):
#     lev.append([])
#     prav.append([])
# for k in range (16): 
#     if (len(a[k])>0):
#         lev[k].append(a[k][0])
#         for i in range (len(a[k])-1):
#             if (b[k][i]<a[k][i+1]):
#                 prav[k].append(b[k][i])
#                 lev[k].append(a[k][i+1])
#         prav[k].append(b[k][len(b[k])-1])

# aut=[]
# for k in range (16) :
#     for i in range (len(lev[k])) :
#         aut.append(lev[k][i])
#         aut.append(prav[k][i])
# aut.sort()

# otr=[]
# zad=[]
# m=0
# for l in range (len(aut) - 1):
#     for k in range (16): 
#         for j in range (len(lev[k])) :
#             tmp=[]
#             if (aut[l]>=lev[k][j])&(aut[l+1]<=prav[k][j]):
#                 tmp.append(aut[l])
#                 tmp.append(aut[l+1])
#                 if tmp in otr:
#                     zad[m-1].append(k)
#                 else:
#                     zad.append([])
#                     otr.append(tmp)
#                     zad[m].append(k)
#                     m+=1

# p=np.zeros(16)
# for i in range (16):
#     for j in range (len(zad)):
#         if i in zad[j]:
#             p[i]+=(otr[j][1]-otr[j][0])

# train_X=[]
# train_Y=[]
# m=0
# s=0
# for i in range (16):
#     for j in range (len(pr3[i])):
#         if (pr3[i][j][0]!=0):
#             m=0
#             vect=[]
#             for k in range (len(otr)): 
#                 vect.append(0)
#             for k in range (len(otr)):
#                 if i in zad[k]:
#                     vect[k]=(otr[k][1]-otr[k][0])/p[i]
#             for k in range (len(vect)):
#                 if vect[k]==0:
#                     m+=1
#             if (m!=len(vect)):
#                 train_Y.append(vect)
#                 train_X.append(pr3[i][j])

# for i in range (len(train_X)):
#     train_X[i]=np.array(train_X[i])
#     train_Y[i]=np.array(train_Y[i])

# real_X=[]
# real_Y=[]
# index=[]
# for i in range (len(train_X)):
#     index.append(i)
# index=np.array(index)
# np.random.shuffle(index)
# for i in range (len(train_X)):
#     real_X.append(train_X[index[i]])
#     real_Y.append(train_Y[index[i]])

# train_X2=[]
# train_Y2=[]
# test_X2=[]
# test_Y2=[]
# for i in range (len(real_X)-1500):
#     train_X2.append(real_X[i])
#     train_Y2.append(real_Y[i])
# for i in range (1500):
#     test_X2.append(real_X[i+len(real_X)-1500])
#     test_Y2.append(real_Y[i+len(real_X)-1500])

# train_X2=np.array(train_X2)
# train_Y2=np.array(train_Y2)
# test_X2=np.array(test_X2)
# test_Y2=np.array(test_Y2)
# print(train_X2.shape,train_Y2.shape,test_X2.shape,test_Y2.shape)

# import tensorflow as tf
# from tensorflow import keras
# model = keras.Sequential([keras.layers.Flatten(input_shape=(49,)),
#                               keras.layers.Dense(40, activation=tf.nn.relu),
#                               keras.layers.Dense(39, activation=tf.nn.softmax)])
# model.compile(optimizer=tf.train.GradientDescentOptimizer(learning_rate=0.05),loss='categorical_crossentropy',metrics=['categorical_accuracy'])
# model.fit(train_X2, train_Y2, epochs=100)
# test_loss, test_acc = model.evaluate(test_X2, test_Y2)
# print('Test accuracy:', test_acc)

# predictions=model.predict(test_X2)
# print(predictions[1330])
# print(test_Y2[1330])
# print(predictions[1499])