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


import global_vars as gl

# Расположение конфигурационного файла
DEFAULT_CONFIGURE_FILE_PATH = './choice/configuration.txt'

## Считываем опции
# -c <pathname> путь до конфигурационного файла
# -a анализ логов
# -d рисование диограмм
# -s поиск оптимального значений параметра при помощи метода отжига
# --<parname of IS>='new_value' новое значение для глобальной переменной
pass
# Что сильнее опции или конфигурационный файл?


import par
# Считываем значения по-умолчанию для параметров par.default_value
pass



def get_globals_names(types = None):
    """ Получение имен всех глобальных переменных проекта, [тип данных которых находится среди types]
    """
    def filterfunc(objname):
        if type(gl.__dict__[objname]) in types:
            return True
        else:
            return False
        
    result = filter(lambda x: x[0] != '_', gl.__dict__.keys()) # игнорируем переменные, которые начинаются с символа '_'
    if types != None:
        return filter(filterfunc, result)
    else:
        return result

def read_configure(configure_file_path = DEFAULT_CONFIGURE_FILE_PATH):
    '''
    Считывание данных из конфигурационного файла
    '''
    gnames = get_globals_names() # получаем имена всех глобальных переменных проекта
    
    if not os.path.exists(configure_file_path):
        print 'There is not file:', configure_file_path
        print 'Warning! Configuration file was not found.'
        print 'Default values for all parametors of IS will be used.'
        return {}
    else:
        print 'Read configuration file:', configure_file_path
    
    cfile = open(configure_file_path)
    result = {}
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
            print 'Warning! Line in the configuration file is not in format \"parname = value\" :',
            print '\'' + line + '\''
            continue
        
        varname, value = line.split('=', 1)
        varname = varname.strip() # обрезаем имя глобальной переменной от возможных лишних пробелов
        if not varname in gnames:
            print 'Warning! There is not a parametor of IS with name :',
            print '\'' + varname + '\''
            continue
        
        tvar = type(gl.__dict__[varname]) # получить тип переменной varname {bool, int, float, str}
        if tvar == bool:
            # {0, 1}
            value = value.strip() # обрезаем пробельные символы с двух сторон
            if value in ('0', '1'):
                value = bool(value)
                if result.has_key(varname):
                    print 'Warning! Several definitions in the configuration file for parametor :', varname
                    print '         The first value for parametor', varname ,'will be used :', int(result[varname])
                    continue
                result[varname] = value
            else:
                print 'Warning! Incorrect value for bool parametor', varname ,':', value
                print '         The set of valid values for', varname, 'is {0, 1}'
                print '         Default value for', varname, 'will be used :', int(gl.__dict__[varname])
                continue
        elif tvar == int:
            value = value.strip() # обрезаем пробельные символы с двух сторон
            if value.isdigit():
                value = int(value)
                if result.has_key(varname):
                    print 'Warning! Several definitions in the configuration file for parametor :', varname
                    print '         The first value for parametor', varname ,'will be used :', result[varname]
                    continue
                result[varname] = value
            else:
                print 'Warning! Incorrect value for parametor', varname ,':', value
                print '         The type of', varname, 'is int'
                print '         Default value for', varname, 'will be used :', gl.__dict__[varname] 
                continue
        elif tvar == float:
            try:
                value = float(value)
            except ValueError:
                print 'Warning! Incorrect value for parametor', varname ,':', value
                print '         The type of', varname, 'is float'
                print '         Default value for', varname, 'will be used ', gl.__dict__[varname] 
                continue
            if result.has_key(varname):
                    print 'Warning! Several definitions in the configuration file for parametor :', varname
                    print '         The first value for parametor', varname ,'will be used :', result[varname]
                    continue
            result[varname] = value
        elif tvar == str:
            value = value.lstrip()
            result[varname] = value
        else:
            try:
                value = tvar(value)
            except:
                print 'Warning! Incorrect value for parametor', varname ,':', value
                print '         The type of', varname, 'is', tvar
                print '         Default value for', varname, 'will be used ', gl.__dict__[varname] 
                continue
            if result.has_key(varname):
                    print 'Warning! Several definitions in the configuration file for parametor :', varname
                    print '         The first value for parametor', varname ,'will be used :', result[varname]
                    continue
            result[varname] = value
        
    return result

def change_globals(gval_dict):
    """
        Изменение значений глобальных переменных при помощи словаря gval_dict
        gval_dict : переменная -> ее новое значение
    """
    for varname, value in gval_dict.iteritems():
        gl.__dict__[varname] = value # инициализация глобальной переменной новым значением
        
def print_globals(types = None):
    """
        Печать текущей конфигурации проекта
    """
            
        
    for var, val in gl.__dict__.iteritems():
        if var[0] == '_':
            continue
        if types != None:
            if not type(val) in types:
                continue
        print var, '=', val
        
        
# Читаем конфигурационный файл и инициализацием глобальные переменные
gval_dict = read_configure()
change_globals(gval_dict)
print_globals([str])
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
