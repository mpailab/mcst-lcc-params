#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
import configargparse, os, sys

# Internal imports
import options

#########################################################################################
# Read script options

parser = configargparse.ArgParser( prog = 'intsys',
                                   description='Запуск интеллектуальной системы для настройки параметров фаз regions, if_conv, dcs.',
                                   default_config_files=['./.config', './.setup_config'])

parser.add( '-c', '--config', type=str, is_config_file=True, help='конфигурационный файл')
parser.add( '--force', action='store_true', help='запуск метода имитации отжига')

subparsers = parser.add_subparsers(help='режим работы ИС')

parser_data = subparsers.add_parser('data', help='получение данных для обучения')
parser_data.set_defaults(mode='data')

parser_find = subparsers.add_parser('find', help='поиск оптимальных значений параметров')
parser_find.set_defaults(mode='find')

parser_stat = subparsers.add_parser('stat', help='печать имеющихся данных для обучения')
parser_stat.set_defaults(mode='stat')

parser_train = subparsers.add_parser('train', help='обучение ИС')
parser_train.set_defaults(mode='train')

parser_setup = subparsers.add_parser('setup', help='установка значений параметров по умолчанию ИС')
parser_setup.set_defaults(mode='setup')

parsers = {
    ''      : parser,
    'data'  : parser_data,
    'find'  : parser_find,
    'stat'  : parser_stat,
    'train' : parser_train,
    'setup' : parser_setup
    }

for mode in parsers.keys():

    add = parsers[mode].add
    for gl in options.list(mode):

        if gl.isBool():
            assert(gl.default is not None)
            if gl.default:
                add( '--no-' + gl.param, dest=gl.param, action='store_false', help=gl.help)
            else:
                add( '--' + gl.param, action='store_true', help=gl.help)

        elif gl.isDisc():
            assert(gl.values is not None)
            assert(gl.default is not None)
            add( '--' + gl.param, type=int, choices=gl.values, default=gl.default, 
                 help=gl.help + '; Values: %(choices)s; Default: %(default)s')

        elif gl.isDiscStr():
            assert(gl.values is not None)
            assert(gl.default is not None)
            add( '--' + gl.param, type=str, choices=gl.values, default=gl.default, 
                 help=gl.help + '; Values: %(choices)s; Default: %(default)s')

        elif gl.isInt():
            assert(gl.default is not None)
            add( '--' + gl.param, metavar='int', type=int, default=gl.default, 
                 help=gl.help + '; Default: %(default)s')

        elif gl.isFloat():
            assert(gl.default is not None)
            if gl.values is None:
                add( '--' + gl.param, metavar='float', type=float, default=gl.default, 
                     help=gl.help + '; Default: %(default)s')
            else:
                assert(len(gl.values) == 1)
                add( '--' + gl.param, metavar='float', type=float, default=gl.default, 
                     help=gl.help + '; Values: ' + gl.values[0] + '; Default: %(default)s')

        elif gl.isFile() or gl.isDir():
            add( '--' + gl.param, metavar='path', type=str, default=gl.default, help=gl.help)

        elif gl.isFormat():
            add( '--' + gl.param, metavar=gl.format, type=str, default=gl.default, help=gl.help)

        else:
            raise Exception('unsupported type of the global variable ' + gl.param)

args = parser.parse_args()

#########################################################################################
# Initialize global variables

for param, value in vars(args).items():
    if options.exist(param):
        options.__dict__[options.var(param).name] = value

#########################################################################################
# Checking global variables
if options.dv_dcs_level > options.MAX_DCS_LEVEL:
    print('Error! default value for parametor dcs_level more then MAX_DCS_LEVEL')
    sys.exit()
for gl in options.list():
    gval = options.__dict__[gl.name]
    if gval == None:
        print ('Error! The value of parametor', gl.param, 'was not defined')
        sys.exit()
    if gl.isFile() or gl.isDir():
        if not os.path.exists(options.__dict__[gl.name]):
            print('Error! Wrong value for parametor', gl.param, ':', gl.default)
            print('       Incorrect path :', gl.default)
            sys.exit()

#########################################################################################
# Run intelligent system

import anneal, train, net

# каталог, из которого запущен процесс
PWD = os.getcwd()

try:
    if args.mode == 'data':

        if args.clear:
            train.clear()

        if args.force:
            anneal.run()

        else:
            net.run()

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

except KeyboardInterrupt:
    os.chdir(PWD)
    train.close()
