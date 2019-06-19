#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
import argparse, configargparse, os

#FIXME тут требуется подключение этих модулей?
#import sys
#from subprocess import Popen, PIPE

# Internal imports
import options

#########################################################################################
# Read script options

cmd_line_params = {}

parser = configargparse.ArgParser( prog = 'intsys',
                                   description='Запуск интеллектуальной системы для настройки параметров фаз regions, if_conv, dcs.',
                                   default_config_files=['./.config'],
                                   formatter_class=argparse.MetavarTypeHelpFormatter)

parser.add( '-c', '--config', type=str, is_config_file=True, help='конфигурационный файл')

parser.add( 'mode', type=str, choices=['data','find','stat','train'], 
            help='режимы работы ИС:\n'
                 'data  - получение данных для обучения;\n'
                 'find  - поиск оптимальных значений параметров;\n'
                 'stat  - печать имеющихся данных для обучения;\n'
                 'train - обучение ИС.')

parser.add( '--force', action='store_true', help='запуск метода имитации отжига')


for gl in options.list():

    if gl.isBool():
        assert(gl.default is not None)
        if gl.default:
            parser.add( '--no-' + gl.param, dest=gl.param, action='store_false', help=gl.help)
        else:
            parser.add( '--' + gl.param, action='store_true', help=gl.help)

    elif gl.isDisc():
        assert(gl.values is not None)
        assert(gl.default is not None)
        parser.add( '--' + gl.param, type=int, choices=gl.values, default=gl.default, 
                             help=gl.help + '; Values: %(choices)s; Default: %(default)s')

    elif gl.isInt():
        assert(gl.default is not None)
        parser.add( '--' + gl.param, type=int, default=gl.default, 
                             help=gl.help + '; Default: %(default)s')

    elif gl.isFloat():
        assert(gl.default is not None)
        if gl.values is None:
            parser.add( '--' + gl.param, type=float, default=gl.default, 
                                 help=gl.help + '; Default: %(default)s')
        else:
            assert(len(gl.values) == 1)
            parser.add( '--' + gl.param, type=float, default=gl.default, 
                                 help=gl.help + '; Values: ' + gl.values[0] + '; Default: %(default)s')

    elif gl.isFile() or gl.isDir():
        parser.add( '--' + gl.param, type=str, default=gl.default, help=gl.help)

    elif gl.isFormat():
        parser.add( '--' + gl.param, metavar=gl.format, type=str, default=gl.default, help=gl.help)

    else:
        raise Exception('unsupported type of the global variable ' + gl.param)

args = parser.parse_args()

#########################################################################################
# Initialize global variables

for param, value in vars(args).items():
    if options.exist(param):
        options.__dict__[options.var(param).name] = value

#########################################################################################
# Run intelligent system

import anneal, train

if args.mode == 'data':

    if args.clear:
        train.clear()

    if args.force:
        anneal.run()

    else:
        pass

elif args.mode == 'find':

    if args.force:
        anneal.run()

    else:
        pass

elif args.mode == 'stat':
    print('Warning! Режим stat пока не поддерживается.')
    pass

else: # args.mode == 'train'
    train.run()
