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
DEFAULT_CONFIGURE_FILE_PATH = './choice/configuration.txt'

def get_globals_names(types = None):
    """ Получение имен всех глобальных переменных проекта, [тип данных которых находится среди types]
    """
    def filterfunc(objname):
        if type(gl.__dict__[objname]) in types:
            return True
        else:
            return False
        
    result = filter(lambda x: x[0] != '_', gl.__dict__.keys())
    if types != None:
        return filter(filterfunc, result)
    else:
        return result

def read_configure(configure_file_path = DEFAULT_CONFIGURE_FILE_PATH):
    '''
    Считывание данных из конфигурационного файла и инициализация глобальных переменных
    '''
    gnames = get_globals_names() # получаем имена всех глобальных переменных проекта
    def gtype(gname):
        """ Получить по имени глобальной переменной тип ее данных
        """
        return type(gl.__dict__[gname])
    
    if not os.path.exists(configure_file_path):
        print 'There is not file:', configure_file_path
        print 'Warning! Configuration file was not found.'
        print 'Default values for all parametors of IS will be used.'
        return 0
    else:
        print 'Read configuration file:', configure_file_path
    
    cfile = open(configure_file_path)
    for line in cfile:
        line = line[:-1] # откусываем от строки последний символ (символ перехода на новую строку)
        line = line.split('#', 1)[0] # все, начиная с символа '#' в строке считаем комментарием
        # игнорируем пустые строки
        if line == '':
            continue
        # игнорируем строки, состоящие из любого числа любых пробельных символов
        if line.isspace():
            continue
        
        # строки без присваивания игнорируем
        if not '=' in line:
            print 'Warning! Line in configuration file is not in format \"parname = value\" :',
            print '\'' + line + '\''
            continue
        
        varname, value = line.split('=', 1)
        varname = varname.strip() # обрезаем имя глобальной переменной от возможных лишних пробелов
        if not varname in gnames:
            print 'Warning! There is not parametor of IS with name :',
            print '\'' + varname + '\''
            continue
        
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


exit()

# globals_names = get_globals_names([int, str, float, bool])
globals_names = get_globals_names([str])
for gname in globals_names:
    print gname, '=', gl.__dict__[gname]

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
