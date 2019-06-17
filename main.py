#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
import argparse, os, sys
from subprocess import Popen, PIPE

# Internal imports
import globals

#########################################################################################
# Read script options

parser = argparse.ArgumentParser( prog = 'intsys',
                                  description='Запуск интеллектуальной системы для настройки параметров фаз regions, if_conv, dcs.',
                                  formatter_class=argparse.MetavarTypeHelpFormatter)

for gl in globals.list():

    if gl.isBool():
        if gl.default:
            parser.add_argument( '--' + gl.param, action='store_true', help=gl.help)
        else:
            parser.add_argument( '--no-' + gl.param, dest=gl.param, action='store_false', help=gl.help)

    elif gl.isDisc():
        assert(gl.values is not None)
        assert(gl.default is not None)
        parser.add_argument( '--' + gl.param, type=int, choices=gl.values, default=gl.default, action='store', 
                             help=gl.help + '; Values: %(choices)s; Default: %(default)s')

    elif gl.isInt():
        assert(gl.default is not None)
        parser.add_argument( '--' + gl.param, type=int, default=gl.default, action='store', 
                             help=gl.help + '; Default: %(default)s')

    elif gl.isFloat():
        assert(gl.default is not None)
        if gl.values is None:
            parser.add_argument( '--' + gl.param, type=float, default=gl.default, action='store', 
                                 help=gl.help + '; Default: %(default)s')
        else:
            assert(len(gl.values) == 1)
            parser.add_argument( '--' + gl.param, type=float, default=gl.default, action='store', 
                                 help=gl.help + '; Values: ' + gl.values[0] + '; Default: %(default)s')

    elif gl.isFile() or gl.isDir():
        parser.add_argument( '--' + gl.param, type=str, default=gl.default, action='store', help=gl.help)

    elif gl.isFormat():
        parser.add_argument( '--' + gl.param, metavar=gl.format, type=str, default=gl.default, action='store', help=gl.help)

    else:
        raise Exception('unsupported type of the global variable ' + gl.param)

args = parser.parse_args()

#########################################################################################
# Read config file

params = {}
if os.path.exists(args.config):
    with open(args.config, encoding='utf-8') as cfile:

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
            
            param, value = line.split('=', 1)
            param = param.strip() # обрезаем имя глобальной переменной от возможных лишних пробелов
            value = value.strip() # обрезаем пробельные символы с двух сторон

            if not globals.exist(param):
                print('Warning! There is not a parametor of IS with name : \'' + param + '\'')
                continue

            if param in params:
                print('Warning! Several definitions in the configuration file for parametor ' + param + '.')
                print('         The first value will be used.')
                continue
            
            gl = globals.var(param)
            if gl.isBool():
                if value in ('0', '1'):
                    params[param] = bool(int(value))
                else:
                    print('Warning! Incorrect value for bool parametor', param ,':', value)
                    print('         The set of valid values for', param, 'is {0, 1}')
                    print('         Default value for', param, 'will be used :', int(gl.default))
                    continue

            elif gl.isDisc():
                if value in gl.values:
                    params[param] = int(value)
                else:
                    print('Warning! Incorrect value for parametor', param ,':', value)
                    print('         The set of valid values for', param, 'is', gl.values)
                    print('         Default value for', param, 'will be used :', gl.default) 
                    continue

            elif gl.isInt():
                if value.isdigit():
                    params[param] = int(value)
                else:
                    print('Warning! Incorrect value for parametor', param ,':', value)
                    print('         The type of', param, 'is int')
                    print('         Default value for', param, 'will be used :', gl.default) 
                    continue

            elif gl.isFloat():
                try:
                    value = float(value)
                except ValueError:
                    print('Warning! Incorrect value for parametor', param ,':', value)
                    print('         The type of', param, 'is float')
                    print('         Default value for', param, 'will be used ', gl.default) 
                    continue
                params[param] = value

            elif gl.isFile():
                if os.path.isfile(value):
                    params[param] = value
                else:
                    print('Warning! Incorrect value for parametor', param ,':', value)
                    print('         File', value, 'does not exist')
                    print('         Default value for', param, 'will be used :', gl.default) 
                    continue

            elif gl.isDir():
                if os.path.exists(value):
                    params[param] = value
                else:
                    print('Warning! Incorrect value for parametor', param ,':', value)
                    print('         Directory', value, 'does not exist')
                    print('         Default value for', param, 'will be used :', gl.default) 
                    continue

            elif gl.isFormat():
                params[param] = value

            else:
                raise Exception('unsupported type of the global variable ' + gl.param)
else:
    print('Warning! Configuration file does not exist.')
    print('         Default values for all parametors of IS will be used.')

#########################################################################################
# Initialize global variables

def set_global (gl, value):
    globals.__dict__[gl.name] = value

for param, value in params.items():
    set_global(globals.var(param), value)

for param, value in vars(args).items():
    set_global(globals.var(param), value)

#########################################################################################
# Run intelligent system

import anneal

if __name__ == '__main__':
    anneal.run()
