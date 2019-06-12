#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
from functools import reduce

# Подключаем модуль, хранящий значения параметров интеллектуальной системы
import global_vars as gl


def get(specs_in_string = gl.SPECS):
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

def encode(spec_procs):
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

def fprint(spec_procs, output = None):
    """
        Напечатать словарь spec_proсs в красивом многострочном виде
    """
    for specname, proclist in spec_procs.items():
        whitespace = '   '
        if proclist:
            print(whitespace, specname + ': ' + reduce(lambda x, y: x + ', ' + y, proclist), file=output)
        else:
            print(whitespace, specname, file=output)
