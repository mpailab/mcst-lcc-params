#!/usr/bin/python3
# -*- coding: utf-8 -*-

from functools import reduce
import sys, os

import options as gl

ptype = { 'disc' : 'Дискретный.',
          'float' : 'Вещественный',
          'path_to_dir' : 'Текстовая строка',
          'path_to_file' : 'Текстовая строка',
          'bool' : 'Булевый (0/1)',
          'int' : 'Целочисленный',
          'format' : 'Текстовая строка следующего формата:',
          'disc_str' : 'Дискретный'
        }

def print_in_tex_format(gv, output = sys.stdout):
    
    orig_stdout = sys.stdout
    sys.stdout = output
    
    pv = gv.param.replace('_', '\\_')
    des = gv.help.capitalize() + '.'
    tv = ptype[gv.type]
    
    print('\\addcontentsline{toc}{subsection}{ (%s)}' % pv)
    print('\\subsection*{ (%s)}' % pv)
    print('\index{%s}' % pv)
    
    print()
    print(des)
    
    print('\\paragraph*{Тип параметра}')
    print(tv)
    if gv.isDisc() or gv.isDiscStr():
        vals = reduce(lambda x, y: '%s, %s' % (x, y), gv.values)
        print('Возможные значения: %s'% vals)
    if gv.isFormat():
        print(gv.format)
    # Следующий формат: ...
    
    print('\\paragraph*{По умолчанию}')
    if gv.default == None:
        print('Значение по-умолчанию для этого параметра не задано')
    else:
        if gv.isBool():
            deff = int(gv.default)
        else:
            deff = gv.default
        print('По-умолчанию значение этого параметра равно %r' % deff)
    
    print('\\paragraph*{Описание}')
    print(des)


    #При определенных условиях максимальное число шагов применения метода имитации отжига может быть
    #больше чем iter\_num, но не больше чем $3\:\cdot$~iter\_num.
    
    sys.stdout = orig_stdout
    
gvs = list(gl.GL.values())
modes = gl.modes
for mode, desc in gl.modes.items():
    print('\chapter{%s}' % desc)
    for gv in gvs:
        if gv.mode == mode:
            print('\\input{./%s/%s}' % (gv.mode, gv.name))
            dirr = './doc/tex_patterns/%s' % gv.mode
            if not os.path.exists(dirr):
                os.makedirs(dirr)
            name = '%s.tex' % gv.name
            path = os.path.join(dirr, name)
            with open(path, 'w') as f:
                #print_in_tex_format(gv, output = f)
                pass
    print()
