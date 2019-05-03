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

def get_globals_names(types = None):
    '''
    Получение имен всех глобальных переменных проекта, тип данных которых находится среди types
    '''
    def filterfunc(objname, filertypes = types):
        if type(gl.__dict__[objname]) in types:
            return True
        else:
            return False
    if types != None:
        return filter(filterfunc, gl.__dict__.keys())
    else:
        return filter(lambda x: x[0] != '_', gl.__dict__.keys())

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


# Тесты.

s1 = set(get_globals_names([int, str, float, bool]))
s2 = set(get_globals_names())
print 'int, str, float, bool - without _:', s1 - s2
print 'without _ - int, str, float, bool:', s2 - s1


def print_dict(my_dict):
    print 'Start print --------------------------------'
    print 
    for item in my_dict.iteritems():
        if item[0][0] != '_':
            print item[0], '=', item[1]
        else:
            print item[0]

#print gl.__dict__['ZERO_LIMIT_FOR_ERF']
#gl.__dict__['ZERO_LIMIT_FOR_ERF'] = 0.2
#print gl.ZERO_LIMIT_FOR_ERF
#print_dict(gl.__dict__)
#print gl.__dict__['__package__']
#print gl.__dict__['__doc__']
#print print_dict(gl.__dict__['__builtins__'])
#print gl.__dict__['__file__']
#print gl.__dict__['__name__']
#print __name__


exit()
    
loc = locals()



#!!! names = opt.read.__dict__
# print_dict(names)

for item in loc.items():
    itype = type(item[1])
    if itype == int or itype == float or itype == bool or itype == str:
        pass
    else:
        print item[0], itype
