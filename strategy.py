#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
from functools import reduce

# Подключаем модуль, хранящий значения параметров интеллектуальной системы
import options as gl
import par

def get(strategy_in_line_format = gl.OPTIMIZATION_STRATEGY):
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
    result.sort()
    
    if bool(result) == False: # если список пустой
        print('Error! The optimization strategy is empty')
        print('Posible reason: there is not any valid parametor of LCC in the strategy or')
        print('                all parametors group in the strategy are not valid')
        print_format()
        sys.exit()
    
    return result

def encode(strategy):
    """
        Преобразовать стратегию оптимизации из рабочего формата интеллектуальной системы в строковой формат 
    """
    return reduce(lambda x, y: x + '; ' + y, [reduce(lambda x, y: x + ' ' + y, group) for group in strategy])
    
def fprint(strategy, output = None):
    """
        Напечатать стратегию в красивом многострочном виде
    """
    for group in strategy:
        print('   ', reduce(lambda x, y: x + ', ' + y, group), file=output)
