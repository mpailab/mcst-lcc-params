#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Настройка вывода на экран различных категорий информации

# External imports
from os import devnull
import sys, textwrap

# Internal imports
import options as gl

devnull = open(devnull, 'w')
width = 100

## Виды информации, выводимой на экнан
## если = devnull -> не печатать на экран
## если = None -> печатать на экран

# F(...) = ...
F = devnull

# ./.../run.sh ....
runs = devnull

# The best (t_c, t_e, mem) is ...
optval = devnull

# Сообщения об ошибках
err = None

# Прочее
default = devnull

if gl.VERBOSE == 0:
    optval = None
    
if gl.VERBOSE == 1:
    optval = None
    F = None
    гuns = None
    
if gl.VERBOSE >= 2:
    F = None
    runs = None
    optval = None
    err = None
    default = None

def warning (str):
    print('Warning!', '\n         '.join(textwrap.wrap(str, width - 9)))

def error (str):
    print('Error!', '\n       '.join(textwrap.wrap(str, width - 7)))
    sys.exit()
