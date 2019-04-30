#!/usr/bin/python
# -*- coding: utf-8 -*-

# External imports
import os, sys
from subprocess import Popen, PIPE
try:
    # пробуем подключить библиотеку для отрисовки графики, которой нет в стандартной поставке python
    import matplotlib.pyplot as plt
except:
    pass

# Internal imports
import global_vars as gl

# Расположение конфигурационного файла
DEFAULT_CONFIGURE_FILE_PATH = './bin/configuration.txt'

def read_configure(configure_file_path = DEFAULT_CONFIGURE_FILE_PATH):
    '''
    Считывание данных из конфигурационного файла
    '''
    if not os.path.exists(configure_file_path):
        print 'There is not file:', configure_file_path
        print 'Warning! Configuration file was not found.'
        print 'Default values for all parametors of intellectual system will be used.'
        return []
    
    pass

# Читаем конфигурационный файл и инициализацием глобальные переменные
read_configure()
# Проверяем корректность значений глобальных переменных
#cheak_globals()
   
# Импортировать модули надо начинать с модулей низкого уровня и заканчивать модулями высокого уровня.
# Непосредственно после импортирования каждого модуля следует изменять его глобальные переменные в соответствии с конфигурационным файлом.
# Если модуль высокого уровня импотрирует модуль низкого уровня через from ___ import *,
# то необходимо, чтобы все глобальные переменные модуля низкого уровня уже были приведены в соответствие с конфигурационным файлом.
# Иначе значения глобальных переменных могут сохранить в некоторых местах программы свое значение по-умолчанию

# Подключаем модули ИС
import def_classes as dcl
import weight as wht
import par

import read as rd
import stat_adaptation as adt
    
import smooth_stat as sth
import calculate_TcTeMem as clc
    
import optimize as opt
import analyse as anl
    
try:
    # Импортирование модуля draw вызовет ошибку, если в системе нет необходимых библиотек (matplotlib для Python 2.7)
    import draw as dr
    import_draw_module = True
except:
    import_draw_module = False

print import_draw_module

exit()

def print_dict(my_dict):
    print 'Start print --------------------------------'
    for item in my_dict.iteritems():
        print item[0]
    
loc = locals()

#!!! names = opt.read.__dict__
# print_dict(names)

for item in loc.items():
    itype = type(item[1])
    if itype == int or itype == float or itype == bool or itype == str:
        pass
    else:
        print item[0], itype
