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
# Опции сглаживания статистики (модуль smooth_stat)
##

# Включение сглаживания статистики
SMOOTH_STAT = True
# Чем меньше следующие коэффиценты, тем сильнее сглаживание
ERF_KOEF_FOR_CONTINUOUS_PAR = 20 # коэффициент сглаживания для вещественных параметров
ERF_KOEF_FOR_DISCRETE_PAR = 0.5 # коэффициент сглаживания для целичисленных параметров
# Порог, значения ниже которого отбрасываются, при определении доли оставшегося для распределения веса
ZERO_LIMIT_FOR_ERF = 0.01
# Веса ниже следующего значения не будут сглаживаться
ZERO_LIMIT_FOR_WEIGHT = 0.001


##
# Модуль calculate_TcTeMem
##

SCRIPT_COMP = './choice/run_comp.sh'
SCRIPT_EXEC = './choice/run_exec.sh'
# SCRIPT_COMP_WITH_STAT компилирует, собирает статистику и печатает объем затраченной памяти
SCRIPT_COMP_WITH_STAT = './choice/run_comp_with_stat.sh'


##
# Модуль draw
##

# количество столбцов на диаграммах
PAR_DIAG_COL_NUM = 100
# Опция включает отображение на экран всех генерируемых графиков
SHOW_FLAG = False
# Если опция включена, то генерируемые графики будут сохраняться
SAVE_PIC_FLAG = True
# Путь до каталога, в который будут сохраняться генерируемые графики
IMAGES_SAVE_MAIN_DIR = './images'
# Опция определяет структуру подкаталогов, в соответствии с которой будут распределяться сохраняемые графики
# 0 -> нет подкаталогов
# 1 -> taskname/...
# 2 -> parname/...
SAVE_SUBDIR_STRUCTURE_MODE = 2
# Опция включает отрисовку на графиках результатов запуска оптимизации
DRAW_RUN_RESULTS_ON_GRAPHICS = True


##
# Модуль optimize
##

# Хранить в оперативной памяти, вычисленные на предыдущих шагах оптимизации распределения? {True, False}
PAR_DISTRIBUTION_DATABASE = True

# Начальное значение температуры
START_TEMPERATURE = 0.5 # Range of temperature: (0, 1].

# Закон убывания температуры: {0, 1, 2}
# 0 -> 1 / ln(n + 1)
# 1 -> 1 / n
# 2 -> alpha ^ n
TEMPERATURE_LAW_TYPE = 2
# значение alpha
ALPHA_IN_TEPMERATURE_LAW = 0.7
# Тип вероятностного распределения, определяющего выбор следующего состояния системы в зависимости от ее текущих состояния и температуры
# {0, 1, 2, 3}
# 0 -> нормальное распределение
# 1 -> распределение для сверхбыстрого отжига
# 2 -> распределение Коши
# 3 -> равномерное распределение
DISTRIBUTION_LAW_TYPE = 1

USE_RELATIONS_OF_PARAMETORS = True
GAIN_STAT_ON_EVERY_OPTIMIZATION_STEP = True
KOEF_TIME_EXEC_IMPOTANCE = 5
MAX_NUMBER_ITERATIONS = 10
MAX_NUMBER_OF_ATTEMPTS_FOR_ITERATION = 10
# Уменьшать значение температуры после итераций, на которых не был осуществлен переход к лучшему значению
DECREASE_TEMPERATURE_BEFORE_UNFORTUNATE_ITERATIONS = True
COMP_TIME_INCREASE_ALLOWABLE_PERCENT = 0.25
EXEC_TIME_INCREASE_ALLOWABLE_PERCENT = 0.05
MEMEMORY_INCREASE_ALLOWABLE_PERCENT = 0.50
