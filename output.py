#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" 
    содержит настройки вывода на экран различных категорий информации
"""

from os import devnull
devnull = open(devnull, 'w')

import options as gl



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

