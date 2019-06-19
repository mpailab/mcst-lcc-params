#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
import configargparse, os, sys

# Internal imports
import options

#########################################################################################
# Read script options

DEFAULT_CONFIG_FILE = './.config'
SETUP_CONFIG_FILE = './.setup_config'

class Formatter(configargparse.HelpFormatter):
    def _split_lines(self, text, width):
        import textwrap
        return [x for l in text.splitlines() for x in textwrap.wrap(l, width) ]

parser = configargparse.ArgParser( prog = 'intsys',
                                   description='Запуск интеллектуальной системы для настройки параметров фаз regions, if_conv, dcs.',
                                   formatter_class=Formatter,
                                   default_config_files=[DEFAULT_CONFIG_FILE, SETUP_CONFIG_FILE])


mode_group = parser.add_argument_group('Выбор режима работы ИС')
mode_group.add( 'mode', metavar='<mode>', type=str, choices=['data','find','stat','train'], 
                help='режим работы ИС. Values:\n'
                     ' data - получение данных для обучения;\n'
                     ' find - поиск оптимальных значений параметров;\n'
                     ' stat - печать имеющихся данных для обучения;\n'
                     'train - обучение ИС;\n'
                     'setup - установка значений параметров по умолчанию.')

parser.add( '-c', '--config', metavar='path', type=str, is_config_file=True, help='конфигурационный файл')
parser.add( '--force', action='store_true', help='запуск метода имитации отжига')

for mode in options.modes.keys():

    group = parser if mode == '' else parser.add_argument_group(options.modes[mode])
    for gl in options.list(mode):

        if gl.isBool():
            assert(gl.default is not None)
            if gl.default:
                group.add( '--no-' + gl.param, dest=gl.param, action='store_false', help=gl.help)
            else:
                group.add( '--' + gl.param, action='store_true', help=gl.help)

        elif gl.isDisc():
            assert(gl.values is not None)
            assert(gl.default is not None)
            group.add( '--' + gl.param, type=int, choices=gl.values, default=gl.default, 
                 help=gl.help + '; Values: %(choices)s; Default: %(default)s')

        elif gl.isDiscStr():
            assert(gl.values is not None)
            assert(gl.default is not None)
            group.add( '--' + gl.param, type=str, choices=gl.values, default=gl.default, 
                 help=gl.help + '; Values: %(choices)s; Default: %(default)s')

        elif gl.isInt():
            assert(gl.default is not None)
            group.add( '--' + gl.param, metavar='int', type=int, default=gl.default, 
                 help=gl.help + '; Default: %(default)s')

        elif gl.isFloat():
            assert(gl.default is not None)
            if gl.values is None:
                group.add( '--' + gl.param, metavar='float', type=float, default=gl.default, 
                     help=gl.help + '; Default: %(default)s')
            else:
                assert(len(gl.values) == 1)
                group.add( '--' + gl.param, metavar='float', type=float, default=gl.default, 
                     help=gl.help + '; Values: ' + gl.values[0] + '; Default: %(default)s')

        elif gl.isFile() or gl.isDir():
            group.add( '--' + gl.param, metavar='path', type=str, default=gl.default, help=gl.help)

        elif gl.isFormat():
            group.add( '--' + gl.param, metavar=gl.format, type=str, default=gl.default, help=gl.help)

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

if args.mode == 'setup':

    with open(SETUP_CONFIG_FILE, 'w') as f:
        f.write('# Configure default values of parameters\n\n')
        for gl in options.list('setup'):
            if not getattr(args, gl.param) == gl.default:
                f.write('# ' + gl.help + '\n')
                f.write(gl.param + ' = ' + str(getattr(args, gl.param)))

    sys.exit()

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
            train.find()

    elif args.mode == 'stat':
        print('Warning! Режим stat пока не поддерживается.')
        pass

    else: # args.mode == 'train':
        train.run()

except KeyboardInterrupt:
    os.chdir(PWD)
    train.close()
