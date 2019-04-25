#!/usr/bin/python
# -*- coding: utf-8 -*-
 
"""
содержит инициализацию глобальных переменных для всего проекта
"""

#! Значения по-умолчанию для параметров будет считывать из компилятора сразу в модуль par


##
# Модуль weight
##

PROC_WEIGHT_SETUP = 1 # {0, 1}
TASK_WEIGHT_SETUP = 1 # {0, 1}
NODE_WEIGHT_SETUP = 0 # {0, 1, 2, 3}
REGN_WEIGHT_SETUP = 0 # {0, 1, 2}
SECT_WEIGHT_SETUP = 1 # {1, 0}
ICV_REGN_WEIGHT_SETUP = 0 # {0, 1, 2}

##
# Модуль read
##

# Каталог с файлами <specname>.txt
# В файле <specname>.txt для каждой процедуры спека <specname>, являющейся одновременно исполняемой и компилируемой,
# содержится общее время ее работы
PROC_ORDER_PATH = './spec/analyse/proc_order'

# Каталог с файлами <specname>.txt
# Каждый такой файл хранит пересечение списков компилируемых и исполняемых процедур спека <specname>
PROC_LIST_PATH = './spec/analyse/proc_list'

# Каталог, в котором содержится информация, о времени работы всех исполняемых процедур (но необязательно компилируемых)
# для каждого спека
STATEXEC_PATH = './spec/stat/exec'

# Вес, который присваевается каждой компилируемой, но неисполняемой процедуре
UNEXEC_PROC_WEIGHT = 1.

# Принимать во внимание компилируемые, но неисполняемые процедуры? {True, False}
USE_FULL_STAT = False

# Каталог со статистикой по всем компилируемым процедурам по всем спекам
FULL_STAT_PATH = './spec/stat/comp_all/stat'

# Каталог, из которой производиться считывание статистики
# Если мы решили сами собирать статистику, то надо выставить STAT_PATH_FOR_READ != FULL_STAT_PATH
STAT_PATH_FOR_READ = FULL_STAT_PATH

##
# Модуль stat_adaptation
##

# Учитывать при обработки статистики динамическое изменение числа операций в процедуре во время фазы regions
DINUMIC_PROC_OPERS_NUM = False
# Учитывать при обработки статистики динамическое изменение числа операций в регионах процедуры во время фазы regions
DINUMIC_REGN_OPERS_NUM = False


##
# dcs
##

# Номер последнего существующего уровня оптимизации фазы dcs
MAX_DCS_LEVEL = 4
# Cписко всех уровней оптимизации dcs, кроме нулевого
DCS_LEVELS = range(1, MAX_DCS_LEVEL + 1)

# Полезность dcs оптимизации для процедуры определяется формулой:
# impotance = DCS_KOEF_NODE_IMPOTANCE * nd + DCS_KOEF_EDGE_IMPOTANCE * ed + DCS_KOEF_LOOP_IMPOTANCE * ld,
# где nd -- процент найденных мертвых узлов,
#     ed -- процент найденных мертвых циклов,
#     ld -- процент найденных мертвых циклов.
DCS_KOEF_NODE_IMPOTANCE = 1
DCS_KOEF_EDGE_IMPOTANCE = 1
DCS_KOEF_LOOP_IMPOTANCE = 1

# Если полезность dcs оптимизации <= DSC_ZERO_LIMIT, то dcs оптимизация считается бесполезной
DSC_ZERO_LIMIT = 0.001

##
# Модуль analyse
##

# Каталог, в котором хранятся логи запусков метода имитации отжига
RUN_LOGS_PATH = './result_from_real_data'

# Предполагаемая процентная величина погрешности определения времени исполнения, компиляции, объема потребляемой памяти, и т.п.
DEVIATION_PERCENT_OF_TcTeMemF = 0.01

##
# Модуль smooth_stat
##

# Включение сглаживания статистики
SMOOTH_STAT = True

##
# Модуль optimize
##

USE_RELATIONS_OF_PARAMETORS = True
GAIN_STAT_ON_EVERY_OPTIMIZATION_STEP = True
