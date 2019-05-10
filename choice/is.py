#!/usr/bin/python
# -*- coding: utf-8 -*-

# External imports
import os, sys
from subprocess import Popen, PIPE
try:
    # Пробуем подключить библиотеку для отрисовки графики, которой нет в стандартной поставке python
    import matplotlib.pyplot as plt
except:
    pass

# Подключаем модуль, хранящий значения параметров интеллектуальной системы
import global_vars as gl

# Путь по-умолчанию до конфигурационного файла
DEFAULT_CONFIGURE_FILE_PATH = './choice/configuration.txt'

## Считываем опции
# -o <outputdir> записывать вывод в файлы каталога
# -c <pathname> путь до конфигурационного файла
# -a анализ логов
# -d рисование диограмм
# -s поиск оптимального значений параметра при помощи метода отжига
# -h печать краткой справки
# --<parname of IS>='new_value' новое значение для глобальной переменной
pass
# ?Что сильнее опции или конфигурационный файл?

# Подключаем модуль, содержащий данные о параметрах оптимизационных преобразований компилятора
import par
# Считываем значения по-умолчанию для параметров оптимизационных преобразований в par.default_value
pass


def get_globals_names(types = None):
    """ Получить имена всех глобальных переменных проекта, [тип данных которых находится среди types]
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
    """
        Считать данные из конфигурационного файла
    """
    gnames = get_globals_names() # получаем имена всех глобальных переменных проекта
    
    if not os.path.exists(configure_file_path):
        print 'There is not file:', configure_file_path
        print 'Warning! Configuration file was not found.'
        print 'Default values for all parametors of IS will be used.'
        return {}
    else:
        print 'Configuration file:', configure_file_path
    
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
                value = bool(int(value))
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
        Измененить значение глобальных переменных при помощи словаря gval_dict
        gval_dict : переменная -> новое значение
    """
    for varname, value in gval_dict.iteritems():
        gl.__dict__[varname] = value # инициализация глобальной переменной новым значением
        
def print_globals(types = None):
    """
        Вывести на экран текущую конфигурацию параметров интеллектуальной системы
    """
    for var, val in gl.__dict__.iteritems():
        if var[0] == '_':
            continue
        if types != None:
            if not type(val) in types:
                continue
        print var, '=', val
        
# Читаем конфигурационный файл
gval_dict = read_configure()
# Инициализацием глобальные переменные
print 'gl.DINUMIC_PROC_OPERS_NUM = ', gl.DINUMIC_PROC_OPERS_NUM
change_globals(gval_dict)
print 'gl.DINUMIC_PROC_OPERS_NUM = ', gl.DINUMIC_PROC_OPERS_NUM
# Выводим на экран значения глобальных переменных
# print_globals()
# Проверяем корректность значений глобальных переменных
# cheak_globals()


# Все изменения глобальных переменных должны быть осуществелны до подключения следующих модулей.
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
    draw_module_is_imported = True
except:
    draw_module_is_imported = False

def get_strategy(strategy_in_line_format, print_strategy = False):
    """
        Преобразовать стратегию оптимизации из строкового формата в рабочий формат интеллектуальной системы
    """
    def print_format():
        print 'The strategy must be in the next format :',
        print '<group> [; <group>]'
        print '     where <group> is a string in the next format :',
        print '<parname> [<parname>]'
    
    def par_filt(parname):
        if parname in par.val_type.keys() or parname == 'dcs':
            return True
        else:
            print 'Warning! Unknown parametor of LCC in the strategy :', parname
            print '         The unknown parametor \'' + parname + '\' will be ignored'
            return False
            
    def group_filt(group):
        if bool(group): # если группа параметров не пустая
            dcs_par_exist = reduce(lambda x, y: x or y, [parname in par.dcs + ['dcs'] for parname in group])
            nesting_par_exist = reduce(lambda x, y: x or y, [parname in par.nesting for parname in group])
            reg_or_icv_par_exist = reduce(lambda x, y: x or y, [parname in par.reg_seq + par.icv_seq for parname in group])
            if reg_or_icv_par_exist:
                if dcs_par_exist:
                    print 'Warning! Wrong parametors group :', group
                    print '         dcs-parametors must be in separated group'
                    print '         The wrong parametors group will be ignored :', group
                    return False
                if nesting_par_exist:
                    print 'Warning! Wrong parametors group :', group
                    print '         parametor \'' + par.nesting[0] + '\' must be in separated group'
                    print '         The wrong parametors group will be ignored :', group
                    return False
            else:
                if dcs_par_exist and nesting_par_exist:
                    print 'Warning! Wrong parametors group :', group
                    print '         dcs-parametors and parametor \'' + par.nesting[0] + '\' must be in separated groups'
                    print '         The wrong parametors group will be ignored :', group
                    return False
            return True
        else:
            return False
    
    groups = strategy_in_line_format.split(';')
    result = filter(group_filt, map(lambda x: filter(par_filt, x.split()), groups))
    
    if bool(result) == False: # если список пустой
        print 'Error! The optimization strategy is empty'
        print 'Posible reason: there is not any valid parametor of LCC in the strategy or'
        print '                all parametors group in the strategy are not valid'
        print_format()
        sys.exit()
    
    if print_strategy:
        print 'Using optimization strategy: '
        print '   ', reduce(lambda x, y: x + '; ' + y, map(lambda group: reduce(lambda x, y: x + ' ' + y, group), result))
            
    
    return result

def get_specs(specs_in_string):
    """
        Преобразовать список спеков из строкового формата в рабочий формат интеллектуальной системы
    """
    def print_format():
        print 'The list of specs must be in the next format :',
        print '<specname>[: <proclist>][, <specname>[: <proclist>]]'
        print '<proclist> format is :',
        print '<procname> [<procname>]'
    
    result = {}
    for spec in specs_in_string.split(','):
        tmp = spec.split(':', 1)
        if len(tmp) == 1:
            specname = tmp[0]
            proclist = None
        else:
            specname, proclist = tmp[0], tmp[1]
            proclist = proclist.split()
        specname = specname.strip()
        if not proclist:
            proclist = None
        if result.has_key(specname):
            print 'Warning! There are several occurrences in the speclist for specname :', specname
            print '         Only the first occurrence of', specname, 'will be used'
            continue
        result[specname] = proclist
    return result

strategy = get_strategy(gl.OPTIMIZATION_STRATEGY)
spec_procs = get_specs(gl.specs)
# !надо проверить, что спеки и процедуры в spec_procs взяты не с потолка

if not os.path.isdir(gl.OUTPUTDIR):
    print 'Warning! There is not directory: ', gl.OUTPUTDIR
    print '         The output directory is not given'
    print '         The output will be on the screen'
    

if gl.SEQ_OPTIMIZATION_WITH_STRATEGY and gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
    print 'Synchronous optimization of specs', spec_procs # all
    print 'Successive optimization with the strategy', strategy # seq
    
    if os.path.isdir(gl.OUTPUTDIR):
        path = os.path.join(gl.OUTPUTDIR, 'all.seq.txt')
        # path = os.path.join(gl.OUTPUTDIR, str(spec_procs) + '.' + str(strategy) + '.txt')
        ffile = open(path, 'w', 0)
    else:
        ffile = None
    
    try:
        opt.seq_optimize(spec_procs, strategy, output = ffile)
    except clc.ExternalScriptError as error:
        print 'fail'
        print 'Error by attempt of giving (t_c, t_e, m) in external script'
    else:
        print "ok"
elif gl.SEQ_OPTIMIZATION_WITH_STRATEGY and not gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
    print 'Independent optimization for every spec in', spec_procs # every_spec
    print 'Successive optimization with the strategy', strategy # seq
    
    for specname, proclist in spec_procs.iteritems():
        print "---------------------------------------------------------------------------"
        print "Spec procs:", specname,
        if not proclist:
            print
        else:
            print ':', proclist
