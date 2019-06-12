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
        
# ?Что сильнее опции или конфигурационный файл?
# Читаем конфигурационный файл
gval_dict = read_configure()
# Редактируем gval_dict на основе переданных is.py опций и аргументов
pass
# Инициализацием глобальные переменные словарем gval_dict
change_globals(gval_dict)
# Выводим на экран значения глобальных переменных
# print_globals()
# ?Проверяем корректность значений глобальных переменных
# cheak_globals()

def cheak_globals():
    # надо проверить
    # для gl.SPECS:
    #    - все спеки из gl.SPECS содержатся в заданном пакете спеков
    #    - все указанные явно процедуры спеков в gl.SPECS действительно принадлежат этим спекам
    #    - в списке процедур в gl.SPECS не повторяются дважды одна и та же процедура
    # для gl.PROC_WEIGHT_PATH:
    #    - может быть задан дважды вес для одной и тойже процедуры
    # для gl.TASK_WEIGHT_PATH:
    #    - может быть задан дважды вес для одной и тойже задачи
    pass

# Все изменения глобальных переменных должны быть осуществелны до подключения следующих модулей.
# Подключаем модули ИС
import specs
import strategy as strat
import train_data as tr_data

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

def close_annealing():
    tr_data.data.write_to_files()
    tr_data.data.write_to_screen()
    exit()

def run_annealing():
    """
        Запуск ИС в подрежиме "метод имитации отжига"
    """
    if not gl.GAIN_STAT_ON_EVERY_OPTIMIZATION_STEP:
        # если мы сами не собираем статистику, то
        # следует убедиться, что в папке gl.STAT_PATH она присутствует для всех спеков и их процедур из gl.SPECS
        # если ее там нет в должном виде, то надо
        #       1 вариант -> выдать ошибку
        #       2 вариант -> собрать статистику в gl.STAT_PATH
        pass

    # Получаем стратегию в рабочем формате, параллельно проверяя ее на корректность
    strategy = strat.get(gl.OPTIMIZATION_STRATEGY)
    spec_procs = specs.get(gl.SPECS)
    # !надо проверить, что спеки и процедуры в spec_procs взяты не с потолка

    if not os.path.isdir(gl.OUTPUTDIR):
        print('Warning! There is not directory: ', gl.OUTPUTDIR)
        print('         The output directory is not given')
        print('         The output is on the screen')
        

    if gl.SEQ_OPTIMIZATION_WITH_STRATEGY and gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
        print('Synchronous optimization of specs :')  # all
        specs.fprint(spec_procs)
        print('Successive optimization with the strategy :') # seq
        strat.fprint(strategy)
        
        if os.path.isdir(gl.OUTPUTDIR):
            filename = 'all.seq'
            # filename = str(spec_procs) + '.' + str(strategy)
            path = os.path.join(gl.OUTPUTDIR, filename + '.txt')
            if not gl.ALLOW_REWRITE_OUTPUT_FILES:
                num = 0
                while os.path.exists(path):
                    path = os.path.join(gl.OUTPUTDIR, filename + '_' + str(num) + '.txt')
                    num += 1
            ffile = open(path, 'w')
            print('Output to :', path)
            
            print('Synchronous optimization of specs :', file=ffile)  # all
            specs.fprint(spec_procs, ffile)
            print('Successive optimization with the strategy :', file=ffile) # seq
            strat.fprint(strategy, ffile)
            print('---------------------------------------------------------------------------', file=ffile)
        else:
            ffile = None
        
        try:
            opt.seq_optimize(spec_procs, strategy, output = ffile)
        except clc.ExternalScriptError as error:
            print('fail')
            print('An error by giving (t_c, t_e, m) from external script')
        except KeyboardInterrupt:
            print()
            close_annealing()
        else:
            print("ok")
    elif gl.SEQ_OPTIMIZATION_WITH_STRATEGY and not gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
        print('Independent optimization for every spec in') # every_spec
        specs.fprint(spec_procs)
        print('Successive optimization with the strategy :') # seq
        strat.fprint(strategy)
        
        for specname, proclist in spec_procs.items():
            print("---------------------------------------------------------------------------")
            print("Spec:", specname)
            
            if os.path.isdir(gl.OUTPUTDIR):
                filename = specname + '.seq'
                # filename = str({specname: proclist}) + '.' + str(strategy)
                path = os.path.join(gl.OUTPUTDIR, filename + '.txt')
                if not gl.ALLOW_REWRITE_OUTPUT_FILES:
                    num = 0
                    while os.path.exists(path):
                        path = os.path.join(gl.OUTPUTDIR, filename + '_' + str(num) + '.txt')
                        num += 1
                ffile = open(path, 'w')
                print('Output to :', path)
                
                print('Optimization of spec :', file=ffile)  # all
                specs.fprint({specname: proclist}, ffile)
                print('Successive optimization with the strategy :', file=ffile) # seq
                strat.fprint(strategy, ffile)
                print('---------------------------------------------------------------------------', file=ffile)
            else:
                ffile = None
            
            try:
                opt.seq_optimize({specname: proclist}, strategy, output = ffile)
            except clc.ExternalScriptError as error:
                print('fail')
                print('An error by giving (t_c, t_e, m) from external script')
            except KeyboardInterrupt:
                print()
                close_annealing()
            else:
                print("ok")

    elif not gl.SEQ_OPTIMIZATION_WITH_STRATEGY and gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
        print('Synchronous optimization of specs :')  # all
        specs.fprint(spec_procs)
        print('Independent optimization on every parametors group in the strategy :') # not seq
        strat.fprint(strategy)
        
        dis_regpar = adt.get_dis_regpar(spec_procs)
        dis_icvpar = adt.get_dis_icvpar(spec_procs)
        
        for parnames in strategy:
            print("---------------------------------------------------------------------------")
            print("Group:", parnames)
            if os.path.isdir(gl.OUTPUTDIR):
                filename = 'all.' + str(parnames)
                # filename = str(spec_procs) + '.' + str(parnames)
                path = os.path.join(gl.OUTPUTDIR, filename + '.txt')
                if not gl.ALLOW_REWRITE_OUTPUT_FILES:
                    num = 0
                    while os.path.exists(path):
                        path = os.path.join(gl.OUTPUTDIR, filename + '_' + str(num) + '.txt')
                        num += 1
                ffile = open(path, 'w')
                print('Output to :', path)
                
                print('Synchronous optimization of specs :', file=ffile)  # all
                specs.fprint(spec_procs, ffile)
                print('Optimization on the parametors group :', file=ffile)
                strat.fprint([parnames], ffile)
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
            except KeyboardInterrupt:
                print()
                close_annealing()
            else:
                print("ok")
    elif not gl.SEQ_OPTIMIZATION_WITH_STRATEGY and not gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
        print('Independent optimization for every spec in') # every_spec
        specs.fprint(spec_procs)
        print('Independent optimization on every parametors group in the strategy :') # not seq
        strat.fprint(strategy)
        
        for specname, proclist in spec_procs.items():
            print("---------------------------------------------------------------------------")
            print("---------------------------------------------------------------------------")
            print("Spec:", specname)
            
            dis_regpar = adt.get_dis_regpar({specname : proclist})
            dis_icvpar = adt.get_dis_icvpar({specname : proclist})
            
            for parnames in strategy:
                print("---------------------------------------------------------------------------")
                print("Group:", parnames)
                
                if os.path.isdir(gl.OUTPUTDIR):
                    filename = specname + '.' + str(parnames)
                    # filename = str({specname : proclist}) + '.' + str(parnames)
                    path = os.path.join(gl.OUTPUTDIR, filename + '.txt')
                    if not gl.ALLOW_REWRITE_OUTPUT_FILES:
                        num = 0
                        while os.path.exists(path):
                            path = os.path.join(gl.OUTPUTDIR, filename + '_' + str(num) + '.txt')
                            num += 1
                    ffile = open(path, 'w')
                    print('Output to :', path)
                    
                    print('Optimization of the spec :', file=ffile)  # all
                    specs.fprint({specname : proclist}, ffile)
                    print('Optimization on the parametors group :', file=ffile)
                    strat.fprint([parnames], ffile)
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
                except KeyboardInterrupt:
                    print()
                    close_annealing()
                else:
                    print("ok")
    close_annealing()

if __name__ == '__main__':
    run_annealing()
