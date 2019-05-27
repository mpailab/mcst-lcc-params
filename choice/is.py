#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
import os, sys
from subprocess import Popen, PIPE
from functools import reduce
#try:
    ## Пробуем подключить библиотеку для отрисовки графики, которой нет в стандартной поставке python
    #import matplotlib.pyplot as plt
#except:
    #pass

# Подключаем модуль, хранящий значения параметров интеллектуальной системы
import global_vars as gl

# Путь по-умолчанию до конфигурационного файла
DEFAULT_CONFIGURE_FILE_PATH = './choice/.config'

## Считываем опции
# -o <outputdir> записывать вывод в файлы каталога (-) уже есть в конф. файле
# -c <pathname> путь до конфигурационного файла
# -a анализ логов (?)
# -d рисование диограмм (?)
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
        
    result = [x for x in gl.__dict__.keys() if x[0] != '_'] # игнорируем переменные, которые начинаются с символа '_'
    if types != None:
        return list(filter(filterfunc, result))
    else:
        return result

def read_configure(configure_file_path = DEFAULT_CONFIGURE_FILE_PATH):
    """
        Считать данные из конфигурационного файла
    """
    gnames = get_globals_names() # получаем имена всех глобальных переменных проекта
    
    if not os.path.exists(configure_file_path):
        print('There is not file:', configure_file_path)
        print('Warning! Configuration file was not found.')
        print('Default values for all parametors of IS will be used.')
        return {}
    else:
        print('Configuration file:', configure_file_path)
    
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
            print('Warning! Line in the configuration file is not in format \"parname = value\" :', end=' ')
            print('\'' + line + '\'')
            continue
        
        varname, value = line.split('=', 1)
        varname = varname.strip() # обрезаем имя глобальной переменной от возможных лишних пробелов
        if not varname in gnames:
            print('Warning! There is not a parametor of IS with name :', end=' ')
            print('\'' + varname + '\'')
            continue
        
        tvar = type(gl.__dict__[varname]) # получить тип переменной varname {bool, int, float, str}
        if tvar == bool:
            # {0, 1}
            value = value.strip() # обрезаем пробельные символы с двух сторон
            if value in ('0', '1'):
                value = bool(int(value))
                if varname in result:
                    print('Warning! Several definitions in the configuration file for parametor :', varname)
                    print('         The first value for parametor', varname ,'will be used :', int(result[varname]))
                    continue
                result[varname] = value
            else:
                print('Warning! Incorrect value for bool parametor', varname ,':', value)
                print('         The set of valid values for', varname, 'is {0, 1}')
                print('         Default value for', varname, 'will be used :', int(gl.__dict__[varname]))
                continue
        elif tvar == int:
            value = value.strip() # обрезаем пробельные символы с двух сторон
            if value.isdigit():
                value = int(value)
                if varname in result:
                    print('Warning! Several definitions in the configuration file for parametor :', varname)
                    print('         The first value for parametor', varname ,'will be used :', result[varname])
                    continue
                result[varname] = value
            else:
                print('Warning! Incorrect value for parametor', varname ,':', value)
                print('         The type of', varname, 'is int')
                print('         Default value for', varname, 'will be used :', gl.__dict__[varname]) 
                continue
        elif tvar == float:
            try:
                value = float(value)
            except ValueError:
                print('Warning! Incorrect value for parametor', varname ,':', value)
                print('         The type of', varname, 'is float')
                print('         Default value for', varname, 'will be used ', gl.__dict__[varname]) 
                continue
            if varname in result:
                    print('Warning! Several definitions in the configuration file for parametor :', varname)
                    print('         The first value for parametor', varname ,'will be used :', result[varname])
                    continue
            result[varname] = value
        elif tvar == str:
            value = value.lstrip()
            result[varname] = value
        else:
            try:
                value = tvar(value)
            except:
                print('Warning! Incorrect value for parametor', varname ,':', value)
                print('         The type of', varname, 'is', tvar)
                print('         Default value for', varname, 'will be used ', gl.__dict__[varname]) 
                continue
            if varname in result:
                    print('Warning! Several definitions in the configuration file for parametor :', varname)
                    print('         The first value for parametor', varname ,'will be used :', result[varname])
                    continue
            result[varname] = value
        
    return result

def change_globals(gval_dict):
    """
        Измененить значение глобальных переменных при помощи словаря gval_dict
        gval_dict : переменная -> новое значение
    """
    for varname, value in gval_dict.items():
        gl.__dict__[varname] = value # инициализация глобальной переменной новым значением
        
def print_globals(types = None):
    """
        Вывести на экран текущую конфигурацию параметров интеллектуальной системы
    """
    for var, val in gl.__dict__.items():
        if var[0] == '_':
            continue
        if types != None:
            if not type(val) in types:
                continue
        print(var, '=', val)
        

# Читаем конфигурационный файл
gval_dict = read_configure()
# Инициализацием глобальные переменные
change_globals(gval_dict)
# Выводим на экран значения глобальных переменных
# print_globals()
# ?Проверяем корректность значений глобальных переменных
# cheak_globals()

def cheak_globals():
    # надо проверить
    # для gl.specs:
    #    - все спеки из gl.specs содержатся в заданном пакете спеков
    #    - все указанные явно процедуры спеков в gl.specs действительно принадлежат этим спекам
    pass

# Все изменения глобальных переменных должны быть осуществелны до подключения следующих модулей.
# Подключаем модули ИС
import def_classes as dcl
import read as rd

import weight as wht
import stat_adaptation as adt
    
import smooth_stat as sth
import calculate_TcTeMem as clc
    
import optimize as opt
#import analyse as anl
#try:
    ## Импортирование модуля draw вызовет ошибку, если в системе нет необходимых библиотек (matplotlib для Python 2.7)
    #import draw as dr
    #draw_module_is_imported = True
#except:
    #draw_module_is_imported = False

def get_strategy(strategy_in_line_format):
    """
        Преобразовать стратегию оптимизации из строкового формата в рабочий формат интеллектуальной системы
    """
    def print_format():
        print('The strategy must be in the next format :', end=' ')
        print('<group> [; <group>]')
        print('     where <group> is a string in the next format :', end=' ')
        print('<parname> [<parname>]')
    
    def par_filt(parname):
        if parname in par.val_type.keys() or parname == 'dcs':
            return True
        else:
            print('Warning! Unknown parametor of LCC in the strategy :', parname)
            print('         The unknown parametor \'' + parname + '\' will be ignored')
            return False
            
    def group_filt(group):
        if bool(group): # если группа параметров не пустая
            dcs_par_exist = reduce(lambda x, y: x or y, [parname in par.dcs + ['dcs'] for parname in group])
            nesting_par_exist = reduce(lambda x, y: x or y, [parname in par.nesting for parname in group])
            reg_or_icv_par_exist = reduce(lambda x, y: x or y, [parname in par.reg_seq + par.icv_seq for parname in group])
            if reg_or_icv_par_exist:
                if dcs_par_exist:
                    print('Warning! Wrong parametors group :', group)
                    print('         dcs-parametors must be in separated group')
                    print('         The wrong parametors group will be ignored :', group)
                    return False
                if nesting_par_exist:
                    print('Warning! Wrong parametors group :', group)
                    print('         parametor \'' + par.nesting[0] + '\' must be in separated group')
                    print('         The wrong parametors group will be ignored :', group)
                    return False
            else:
                if dcs_par_exist and nesting_par_exist:
                    print('Warning! Wrong parametors group :', group)
                    print('         dcs-parametors and parametor \'' + par.nesting[0] + '\' must be in separated groups')
                    print('         The wrong parametors group will be ignored :', group)
                    return False
            return True
        else:
            return False
    
    groups = strategy_in_line_format.split(';')
    result = list(filter(group_filt, [list(filter(par_filt, x.split())) for x in groups]))
    
    if bool(result) == False: # если список пустой
        print('Error! The optimization strategy is empty')
        print('Posible reason: there is not any valid parametor of LCC in the strategy or')
        print('                all parametors group in the strategy are not valid')
        print_format()
        sys.exit()
    
    return result

def encode_strategy(strategy):
    """
        Преобразовать стратегию оптимизации из рабочего формата интеллектуальной системы в строковой формат 
    """
    return reduce(lambda x, y: x + '; ' + y, [reduce(lambda x, y: x + ' ' + y, group) for group in strategy])
    
def print_strategy(strategy, output = None):
    """
        Напечатать стратегию в красивом многострочном виде
    """
    for group in strategy:
        print('   ', reduce(lambda x, y: x + ', ' + y, group), file=output)

def get_specs(specs_in_string):
    """
        Преобразовать список спеков из строкового формата в рабочий формат интеллектуальной системы
    """
    def print_format():
        print('The list of specs must be in the next format :', end=' ')
        print('<specname>[: <proclist>][, <specname>[: <proclist>]]')
        print('<proclist> format is :', end=' ')
        print('<procname> [<procname>]')
    
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
        if specname in result:
            print('Warning! There are several occurrences in the speclist for specname :', specname)
            print('         Only the first occurrence of', specname, 'will be used')
            continue
        result[specname] = proclist
    return result

def encode_specs(spec_procs):
    """
        Преобразовать спеки из рабочего формата в строковой формат
    """
    def sp_encode(xxx_todo_changeme):
        (specname, proclist) = xxx_todo_changeme
        if not proclist:
            return specname
        else:
            return specname + ': ' + reduce(lambda x, y: x + ' ' + y, proclist)
    return reduce(lambda x, y: x + ', ' + y, map(sp_encode, spec_procs.items()))

def print_specs(spec_procs, output = None):
    """
        Напечатать словарь spec_proсs в красивом многострочном виде
    """
    for specname, proclist in spec_procs.items():
        whitespace = '   '
        if proclist:
            print(whitespace, specname + ': ' + reduce(lambda x, y: x + ', ' + y, proclist), file=output)
        else:
            print(whitespace, specname, file=output)


# if __name__ == '__main__':
    # надо далее все сделать под этим if-ом


if not gl.GAIN_STAT_ON_EVERY_OPTIMIZATION_STEP:
    # если мы сами не собираем статистику, то
    # следует убедиться, что в папке gl.STAT_PATH она присутствует для всех спеков и их процедур из gl.specs
    # если ее там нет в должном виде, то надо
    #       1 вариант -> выдать ошибку
    #       2 вариант -> собрать статистику в gl.STAT_PATH
    pass

# Получаем стратегию в рабочем формате, параллельно проверяя ее на корректность
strategy = get_strategy(gl.OPTIMIZATION_STRATEGY)
spec_procs = get_specs(gl.specs)
# !надо проверить, что спеки и процедуры в spec_procs взяты не с потолка

if not os.path.isdir(gl.OUTPUTDIR):
    print('Warning! There is not directory: ', gl.OUTPUTDIR)
    print('         The output directory is not given')
    print('         The output is on the screen')
    

if gl.SEQ_OPTIMIZATION_WITH_STRATEGY and gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
    print('Synchronous optimization of specs :')  # all
    print_specs(spec_procs)
    print('Successive optimization with the strategy :') # seq
    print_strategy(strategy)
    
    if os.path.isdir(gl.OUTPUTDIR):
        path = os.path.join(gl.OUTPUTDIR, 'all.seq.txt')
        # path = os.path.join(gl.OUTPUTDIR, str(spec_procs) + '.' + str(strategy) + '.txt')
        ffile = open(path, 'w', 0)
        
        print('Synchronous optimization of specs :', file=ffile)  # all
        print_specs(spec_procs, ffile)
        print('Successive optimization with the strategy :', file=ffile) # seq
        print_strategy(strategy, ffile)
        print('---------------------------------------------------------------------------', file=ffile)
    else:
        ffile = None
    
    try:
        opt.seq_optimize(spec_procs, strategy, output = ffile)
    except clc.ExternalScriptError as error:
        print('fail')
        print('An error by giving (t_c, t_e, m) from external script')
    #except KeyboardInterrupt:
        print()
        exit()
    else:
        print("ok")
elif gl.SEQ_OPTIMIZATION_WITH_STRATEGY and not gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
    print('Independent optimization for every spec in') # every_spec
    print_specs(spec_procs)
    print('Successive optimization with the strategy :') # seq
    print_strategy(strategy)
    
    for specname, proclist in spec_procs.items():
        print("---------------------------------------------------------------------------")
        print("Spec:", specname)
        
        if os.path.isdir(gl.OUTPUTDIR):
            path = os.path.join(gl.OUTPUTDIR, specname + '.seq.txt')
            # path = os.path.join(gl.OUTPUTDIR, str({specname: proclist}) + '.' + str(strategy) + '.txt')
            ffile = open(path, 'w', 0)
            
            print('Optimization of spec :', file=ffile)  # all
            print_specs({specname: proclist}, ffile)
            print('Successive optimization with the strategy :', file=ffile) # seq
            print_strategy(strategy, ffile)
            print('---------------------------------------------------------------------------', file=ffile)
        else:
            ffile = None
        
        try:
            opt.seq_optimize({specname: proclist}, strategy, output = ffile)
        except clc.ExternalScriptError as error:
            print('fail')
            print('An error by giving (t_c, t_e, m) from external script')
        #except KeyboardInterrupt:
            print()
            exit()
        else:
            print("ok")

elif not gl.SEQ_OPTIMIZATION_WITH_STRATEGY and gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
    print('Synchronous optimization of specs :')  # all
    print_specs(spec_procs)
    print('Independent optimization on every parametors group in the strategy :') # not seq
    print_strategy(strategy)
    
    dis_regpar = adt.get_dis_regpar(spec_procs)
    wht.normolize_dict(dis_regpar)
    dis_icvpar = adt.get_dis_icvpar(spec_procs)
    wht.normolize_dict(dis_icvpar)
    
    for parnames in strategy:
        print("---------------------------------------------------------------------------")
        print("Group:", parnames)
        if os.path.isdir(gl.OUTPUTDIR):
            path = os.path.join(gl.OUTPUTDIR, 'all.' + str(parnames) +'.txt') # ?
            # path = os.path.join(gl.OUTPUTDIR, str(spec_procs) + '.' + str(parnames) + '.txt')
            ffile = open(path, 'w', 0)
            
            print('Synchronous optimization of specs :', file=ffile)  # all
            print_specs(spec_procs, ffile)
            print('Optimization on the parametors group :', file=ffile)
            print_strategy([parnames], ffile)
            print('---------------------------------------------------------------------------', file=ffile)
        else:
            ffile = None
        
        is_dcs_pargroup = reduce(lambda x, y: x and y, [p in par.dcs or p == 'dcs' for p in parnames])
        is_nesting_pargroup = len(parnames) == 1 and parnames[0] in par.nesting
        
        try:
            if is_dcs_pargroup:
                opt.dcs_optimize(spec_procs, output = ffile)
            elif is_nesting_pargroup:
                opt.optimize_bool_par(spec_procs, parnames[0], output = ffile)
            else:
                opt.optimize(spec_procs, parnames, output = ffile, dis_regpar = dis_regpar, dis_icvpar = dis_icvpar)
        except clc.ExternalScriptError as error:
            print('fail')
            print('An error by giving (t_c, t_e, m) from external script')
        #except KeyboardInterrupt:
            print()
            exit()
        else:
            print("ok")
elif not gl.SEQ_OPTIMIZATION_WITH_STRATEGY and not gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
    print('Independent optimization for every spec in') # every_spec
    print_specs(spec_procs)
    print('Independent optimization on every parametors group in the strategy :') # not seq
    print_strategy(strategy)
    
    for specname, proclist in spec_procs.items():
        print("---------------------------------------------------------------------------")
        print("---------------------------------------------------------------------------")
        print("Spec:", specname)
        
        dis_regpar = adt.get_dis_regpar({specname : proclist})
        wht.normolize_dict(dis_regpar)
        dis_icvpar = adt.get_dis_icvpar({specname : proclist})
        wht.normolize_dict(dis_icvpar)
        
        for parnames in strategy:
            print("---------------------------------------------------------------------------")
            print("Group:", parnames)
            
            if os.path.isdir(gl.OUTPUTDIR):
                path = os.path.join(gl.OUTPUTDIR, specname + '.' + str(parnames) +'.txt')
                # path = os.path.join(gl.OUTPUTDIR, str({specname : proclist}) + '.' + str(parnames) + '.txt')
                ffile = open(path, 'w', 0)
                
                print('Optimization of the spec :', file=ffile)  # all
                print_specs({specname : proclist}, ffile)
                print('Optimization on the parametors group :', file=ffile)
                print_strategy([parnames], ffile)
                print('---------------------------------------------------------------------------', file=ffile)
            else:
                ffile = None
            
            is_dcs_pargroup = reduce(lambda x, y: x and y, [p in par.dcs or p == 'dcs' for p in parnames])
            is_nesting_pargroup = len(parnames) == 1 and parnames[0] in par.nesting
            try:
                if is_dcs_pargroup:
                    opt.dcs_optimize({specname : proclist}, output = ffile)
                elif is_nesting_pargroup:
                    opt.optimize_bool_par({specname : proclist}, parnames[0], output = ffile)
                else:
                    opt.optimize({specname : proclist}, parnames, output = ffile, dis_regpar = dis_regpar, dis_icvpar = dis_icvpar)
            except clc.ExternalScriptError as error:
                print('fail')
                print('An error by giving (t_c, t_e, m) from external script')
            #except KeyboardInterrupt:
                print()
                exit()
            else:
                print("ok")
        
