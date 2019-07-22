#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Настройка вывода на экран различных категорий информации

# External imports
from os import devnull
import sys, textwrap

# Internal imports
import options as gl

devnull = open(devnull, 'w')
width = 90

# Режимы вывода сообщений на экран
silent = None                                 # Минимальная печать сообщений
screen = None if gl.VERBOSE > 0 else devnull  # Обычная печать сообщений
trace  = None if gl.VERBOSE > 1 else devnull  # Трассировка событий (создание/удаление файлов, чтение/запись статистики и т.п.)
debug  = None if gl.VERBOSE > 2 else devnull  # Подробная печать сообщений, необходимых для отладки

## Виды информации, выводимой на экнан
## если = devnull -> не печатать на экран
## если = None -> печатать на экран

# F(...) = ...
F = debug
# ./.../run.sh ....
runs = debug

if gl.SEQ_OPTIMIZATION_WITH_STRATEGY:
    optval = screen
    groupname = screen
else:
    optval = silent
    groupname = silent


# Сообщения об ошибках
err = silent

# Прочее
default = debug

def warning (str, output = None):
    print('Warning:', '\n         '.join([x for y in str.split('\n') for x in textwrap.wrap(y, width - 9)]), file = output)

def error (str, output = None):
    print('Error:', '\n       '.join([x for y in str.split('\n') for x in textwrap.wrap(y, width - 7)]), file = output)
    sys.exit()

def undef (option, output = None):
    error('no parameter for --%s option' % option)
