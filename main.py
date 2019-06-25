#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
import configargparse, os, sys

# Internal imports
import options

#########################################################################################
# Read script options

DEFAULT_CONFIG_FILE = './.config'

class Formatter(configargparse.HelpFormatter):
    def _split_lines(self, text, width):
        import textwrap
        return [x for l in text.splitlines() for x in textwrap.wrap(l, width) ]

# class DirAction(configargparse.Action):
#     def __call__(self, parser, namespace, values, option_string=None):
#         if not os.path.exists(values):
#             raise ValueError('nargs for store actions must be > 0; if you '
#                              'have nothing to store, actions such as store '
#                              'true or store const may be more appropriate')
#         if const is not None and nargs != OPTIONAL:
#             raise ValueError('nargs must be %r to supply const' % OPTIONAL)
#         setattr(namespace, self.dest, values)

parser = configargparse.ArgParser( prog = 'intsys',
                                   description='Запуск интеллектуальной системы для настройки параметров фаз regions, if_conv, dcs.',
                                   formatter_class=Formatter,
                                   default_config_files=[DEFAULT_CONFIG_FILE])


mode_group = parser.add_argument_group('Выбор режима работы ИС')
mode_group.add( 'mode', metavar='<mode>', type=str, choices=['data','find','stat','train'], 
                help='режим работы ИС. Values:\n'
                     ' data - получение данных для обучения;\n'
                     ' find - поиск оптимальных значений параметров;\n'
                     ' stat - печать имеющихся данных для обучения;\n'
                     'train - обучение ИС.')

parser.add( '-c', '--config', metavar='path', type=str, is_config_file=True, help='конфигурационный файл')
parser.add( '--force', action='store_true', help='запуск метода имитации отжига')

for mode in options.modes.keys():

    group = parser if mode == '' else parser.add_argument_group(options.modes[mode])
    for gl in options.list(mode):

        if gl.isBool():
            assert(gl.default is False)
            group.add( '--' + gl.param, action='store_true', help=gl.help)

        elif gl.isDisc():
            assert(gl.values is not None)
            assert(gl.default is not None)
            group.add( '--' + gl.param, type=gl.parser, choices=gl.values, default=gl.default, 
                 help=gl.help + '; Values: %(choices)s; Default: %(default)s')

        elif gl.isDiscStr():
            assert(gl.values is not None)
            assert(gl.default is not None)
            group.add( '--' + gl.param, type=gl.parser, choices=gl.values, default=gl.default, 
                 help=gl.help + '; Values: %(choices)s; Default: %(default)s')

        elif gl.isInt():
            assert(gl.default is not None)
            group.add( '--' + gl.param, metavar='int', type=gl.parser, default=gl.default, 
                 help=gl.help + '; Default: %(default)s')

        elif gl.isFloat():
            assert(gl.default is not None)
            if gl.values is None:
                group.add( '--' + gl.param, metavar='float', type=gl.parser, default=gl.default, 
                     help=gl.help + '; Default: %(default)s')
            else:
                assert(len(gl.values) == 1)
                group.add( '--' + gl.param, metavar='float', type=gl.parser, default=gl.default, 
                     help=gl.help + '; Values: ' + gl.values[0] + '; Default: %(default)s')

        elif gl.isDir():
            group.add( '--' + gl.param, metavar='path', type=gl.parser, default=gl.default, help=gl.help)

        elif gl.isFile():
            group.add( '--' + gl.param, metavar='path', type=gl.parser, default=gl.default, help=gl.help)

        elif gl.isFormat():
            group.add( '--' + gl.param, metavar=gl.format, type=gl.parser, default=gl.default, help=gl.help)

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
    
import verbose

if options.SPECS is None:
    verbose.error('Specs list was not defined')
    
if options.OPTIMIZATION_STRATEGY is None:
    verbose.error('Optimization strategy was not defined')
    
if args.force or args.mode == 'data':

    # все глобалы раздела script должны быть не None
    for gl in options.list(mode = 'script'):
        gval = options.__dict__[gl.name]
        if gval == None:
            verbose.error('The value of parametor \'' + gl.param + '\' was not defined')

#########################################################################################
# Run intelligent system

# каталог, из которого запущен процесс
PWD = os.getcwd()

try:
    if args.mode == 'data':

        if args.clear:
            from train import clear
            clear()

        if args.force:
            import anneal
            anneal.run()

        else:
            import train
            train.collect()

    elif args.mode == 'find':

        if args.force:
            import anneal
            anneal.run()

        else:
            import train
            train.find()

    elif args.mode == 'stat':
        verbose.warning('Режим \'stat\' пока не поддерживается.')
        pass

    else: # args.mode == 'train':
        import train
        train.run()

except KeyboardInterrupt:
    os.chdir(PWD)
    train.close()
