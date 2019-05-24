﻿#!/usr/bin/python3
# -*- coding: utf-8 -*-
 
""" содержит инициализацию глобальных переменных для всего проекта
"""

##
# Модуль weight
##

""" Настройка выбора веса неисполняемой процедуры {0, 1, 2}
    0 -> DEFAULT_WEIGHT_FOR_PROC
    1 -> минимум среди всех весов исполняемых процедур
    2 -> среднее значение весов всех исполняемых процедур
"""
UNEXEC_PROC_WEIGHT_SETUP = 1

# Вес по-умолчанию, который присваевается каждой компилируемой, но неисполняемой процедуре
DEFAULT_WEIGHT_FOR_PROC = 1.

""" Конечный вес каждого узла фазы regions определяется формулой pr_norm(nd_norm(w_n * w_r) * w_p * w_t), где
    w_n -- начальный вес узла,
    w_r -- вес региона,
    nd_norm -- нормирование по всем узлам процедуры,
    w_p -- вес процедуры,
    w_t -- вес спека,
    pr_norm -- нормирование по всем расматриваемым процедурам (всех рассматриваемых спеков)
    
    Конечный вес сливаемого участка в фазе if_conv определяется формулой pr_norm(s_norm(w_s * w_ir) * w_p * w_t), где
    w_s -- начальный вес сливаемого участка
    w_ir -- вес региона, к которому относится сливаемый участок
    s_norm -- нормирование по всем сливаемым участкам процедуры
"""

""" Режим учета веса процедуры w_p: {0, 1}
    0 -> w_p = 1 (не учитывать вес процедуры)
    1 -> w_p -- временя работы процедуры в составе спека (ненормированное)
"""
PROC_WEIGHT_SETUP = 1

""" Режим учета веса спека w_t: {0, 1}
    0 -> w_t = 1 (не учитывать вес спека)
    1 -> w_t -- считывается из файла TASK_WEIGHT_PATH
    2 -> w_t -- отношение времени исполнения всех собственных (небиблиотечных) процедур спека к общему времени его работы
    3 -> w_t -- отношение времени исполнения оптимизируемых собственных (небиблиотечных) процедур спека к общему времени его работы
"""
TASK_WEIGHT_SETUP = 3

""" Режим определения начального веса узла w_n: {0, 1, 2, 3}
    0 -> w_n = 0, если счетчик узла во всей процедуре (n_cnt) равен нулю;
         w_n = 1, иначе
    1 -> w_n -- внутренний счетчик узла (v_cnt)
    2 -> w_n -- счетчик узла во всей процедуре (n_cnt) 
    3 -> w_n -- отношения внутреннего счетчика узла к счетчику узла во всей процедуре (v_cnt / n_cnt);
         однако если n_cnt = 0, то w_n полагается равным нулю
"""
NODE_WEIGHT_SETUP = 0

""" Режим учета веса региона w_r фазы regions: {0, 1, 2}
    0 -> w_r = 1 (не учитывать вес региона)
    1 -> w_r -- счетчик региона
    2 -> w_r -- счетчик региона, нормируемый по всем регионам в процедуре
"""
REGN_WEIGHT_SETUP = 0

""" Режим учета веса региона w_ir фазы if_conv: {0, 1, 2}
    0 -> w_ir = 1 (не учитывать вес региона)
    1 -> w_ir -- счетчик региона
    2 -> w_ir -- счетчик региона, нормируемый по всем регионам в процедуре
"""
ICV_REGN_WEIGHT_SETUP = 0

""" Режим учета веса сливаемого участка w_s: {0, 1}
    0 -> w_s = 1 (не учитывать вес сливаемого участка)
    1 -> w_s -- счетчик сливаемого участка
"""
SECT_WEIGHT_SETUP = 1


##
# Модуль read
##

# Каталог с файлами <specname>.txt
# Строка каждого файла <specname>.txt имеет вид: <procname> <weight>
# Допустим случай, когда у спека <specname> может не быть компилируемой процедуры <procname>
# Не все компилируемые процедуры спека <specname> обязаны присутствовать в файле <specname>.txt
PROC_WEIGHT_PATH = './spec/stat/exec'


# Файл с весами спеков
TASK_WEIGHT_PATH = './spec/stat/exec/spec_weights.txt'

# Принимать во внимание процедуры, для которых не заданы веса? {0, 1}
USE_ALL_PROCS_IN_STAT = True
# ? переименовать в USE_UNEXEC_PROCS_IN_STAT

# Каталог со статистикой компиляции спеков при значениях параметров оптимизирующих преобразований по-умолчанию
STAT_PATH = './spec/stat/comp_all/stat'

# Каталог, в который собирается статистика компиляции спеков во время работы ИС
DINUMIC_STAT_PATH = './spec/stat/comp_all/stat'

##
# Модуль stat_adaptation
##

# Учитывать при обработки статистики динамическое изменение числа операций в процедуре во время фазы regions? {0, 1}
DINUMIC_PROC_OPERS_NUM = False
# Учитывать при обработки статистики динамическое изменение числа операций в регионах процедуры во время фазы regions? {0, 1}
DINUMIC_REGN_OPERS_NUM = False


##
# dcs
##

# Номер последнего существующего уровня оптимизации фазы dcs
MAX_DCS_LEVEL = 4

# Полезность dcs оптимизации для процедуры определяется формулой:
# impotance = DCS_KOEF_NODE_IMPOTANCE * nd + DCS_KOEF_EDGE_IMPOTANCE * ed + DCS_KOEF_LOOP_IMPOTANCE * ld,
# где nd -- процент найденных мертвых узлов,
#     ed -- процент найденных мертвых циклов,
#     ld -- процент найденных мертвых циклов.
DCS_KOEF_NODE_IMPOTANCE = 1.
DCS_KOEF_EDGE_IMPOTANCE = 1.
DCS_KOEF_LOOP_IMPOTANCE = 1.

# Если полезность dcs оптимизации <= DSC_IMPOTANCE_LIMIT, то dcs оптимизация считается бесполезной
DSC_IMPOTANCE_LIMIT = 0.001

##
# Модуль analyse
##

# Каталог, в котором хранятся логи запусков оптимизации методом имитации отжига
RUN_LOGS_PATH = './result_from_real_data'

# Предполагаемая процентная величина погрешности определения времени исполнения, компиляции, объема потребляемой памяти, и т.п.
DEVIATION_PERCENT_OF_TcTeMemF = 0.01

##
# Опции сглаживания статистики (модуль smooth_stat)
##

# Сглаживать статистику? {0, 1}
SMOOTH_STAT = True
# Чем меньше следующие коэффиценты, тем сильнее сглаживание
ERF_KOEF_FOR_CONTINUOUS_PAR = 20. # коэффициент сглаживания для вещественных параметров
ERF_KOEF_FOR_DISCRETE_PAR = 0.5 # коэффициент сглаживания для целичисленных параметров

# Чем ниже следующие параметры, тем качественнее сглаживание
# Уменьшение следующих параметров может очень существенно замедлить сглаживание!
# Доля исходного веса, которая не будет участвовать в сглаживании
ZERO_LIMIT_FOR_ERF = 0.01
# Порог для абсолютных значений весов, веса ниже которого не будут сглаживаться
ZERO_LIMIT_FOR_WEIGHT = 0.001


##
# Модуль calculate_TcTeMem
##

# Путь до скрипта, который запускает компиляцию спека, и возвращает время компиляции
SCRIPT_COMP = './choice/run_comp.sh'
# Путь до скрипта, который запускает исполнение спека, и возвращает время исполнения
SCRIPT_EXEC = './choice/run_exec.sh'
# Путь до скрипта, который запускает компиляцию спека вместе со сбором статистики, и возвращает объем потребляемой памяти
SCRIPT_COMP_WITH_STAT = './choice/run_comp_with_stat.sh'


##
# Модуль draw
##

# Количество столбцов на генерируемых графиках
PAR_DIAG_COL_NUM = 100
# Отображать на экран генерируемые графики? {0, 1}
SHOW_FLAG = False
# Сохранять генерируемые графики? {0, 1}
SAVE_PIC_FLAG = True
# Каталог, в который будут сохраняться генерируемые графики
IMAGES_SAVE_MAIN_DIR = './images'
# Структура подкаталогов, в соответствии с которой будут распределяться сохраняемые графики {0, 1, 2}
# 0 -> нет подкаталогов
# 1 -> taskname/...
# 2 -> parname/...
SAVE_SUBDIR_STRUCTURE_MODE = 2
# Опция включает отрисовку на графиках результатов запуска оптимизации
DRAW_RUN_RESULTS_ON_GRAPHICS = True


##
# Модуль optimize
##

# Актуализировать статистику на каждом шаге метода отжига? {0, 1}
GAIN_STAT_ON_EVERY_OPTIMIZATION_STEP = True

""" Сохранять в оперативной памяти распределения весов для каждого нового набора параметров? {0, 1}
    Увеличивает скорость работы ИС, может привести к чрезмерному потреблению оперативной памяти
"""
PAR_DISTRIBUTION_DATABASE = True

# Начальное значение температуры: (0, 1]
START_TEMPERATURE = 0.5

# Закон убывания температуры: {0, 1, 2}
# 0 -> 1 / ln(n + 1)
# 1 -> 1 / n
# 2 -> alpha ^ n
TEMPERATURE_LAW_TYPE = 2
# значение alpha
ALPHA_IN_TEPMERATURE_LAW = 0.7

# Тип вероятностного распределения,
# определяющего выбор следующего состояния системы в зависимости от ее текущих состояния и температуры: {0, 1, 2, 3}
# 0 -> нормальное распределение
# 1 -> распределение для сверхбыстрого отжига
# 2 -> распределение Коши
# 3 -> равномерное распределение
DISTRIBUTION_LAW_TYPE = 1

""" Учитывать зависимоти параметров друг от друга? {0, 1}
    Параметр par1 зависит от par2, если при определенных значениях параметра par2,
    значение par1 никак не влияют на работу компилятора LCC.
    Если опция возведена, то зависимости параметров учитываются при прогнозировании
    насколько существенно может повлиять на работу компилятора изменение значений параметров
"""
USE_RELATIONS_OF_PARAMETORS = True

""" Минимизируемый функцонал имеет вид
    F(dT_c, dT_e, dV) = TIME_COMP_IMPOTANCE * dT_c + TIME_EXEC_IMPOTANCE * dT_e + MEMORY_IMPOTANCE * dV, где
    dT_c -- относительное увеличение времени компиляции,
    dT_e -- относительное увеличение времени исполнения,
    dV -- относительное увеличение объема потребляемой памяти.
    
    Однако, если выполняется одно из условий
    dT_c > 1 + COMP_TIME_INCREASE_ALLOWABLE_PERCENT,
    dT_e > 1 + EXEC_TIME_INCREASE_ALLOWABLE_PERCENT,
    dV > 1 + MEMORY_INCREASE_ALLOWABLE_PERCENT,
    то значение F(dT_c, dT_e, dV) полагается равным +бесконечности
"""
# Значения коэффицентов минимизируемого функционала
TIME_EXEC_IMPOTANCE = 5.
TIME_COMP_IMPOTANCE = 1.
MEMORY_IMPOTANCE = 1.
# Допустимый процент увеличения времени компиляции
COMP_TIME_INCREASE_ALLOWABLE_PERCENT = 0.25
# Допустимый процент увеличения времени исполнения
EXEC_TIME_INCREASE_ALLOWABLE_PERCENT = 0.05
# Допустимый процент увеличения объема потребляемой памяти
MEMORY_INCREASE_ALLOWABLE_PERCENT = 0.50

# Число итераций метода отжига
MAX_NUMBER_ITERATIONS = 10

# Максимальное число попыток выбора новых значений параметров для каждой итерации метода отжига
MAX_NUMBER_OF_ATTEMPTS_FOR_ITERATION = 10

# Уменьшать значение температуры после итераций, на которых не был осуществлен переход к лучшему значению? {0, 1}
DECREASE_TEMPERATURE_BEFORE_UNFORTUNATE_ITERATIONS = True

##
# Глобалы-опции
##


# Стратегия
# Синтаксис:
#        <стратегия>            ::= <группа параметров> | <стратегия>; <группа параметров>
#        <группа параметров>   ::= <параметр> | <группа параметров> <параметр>
OPTIMIZATION_STRATEGY = """ regn_max_proc_op_sem_size;
                            regn_opers_limit;
                            regn_heur1 regn_heur2 regn_heur3 regn_heur4;
                            ifconv_opers_num ifconv_calls_num ifconv_merge_heur
                        """
# Последовательная оптимизация? {0, 1}
# 0 -> независимая оптимизация по каждой группе в стратегии
# 1 -> последовательная оптимизация согласно стратегии
SEQ_OPTIMIZATION_WITH_STRATEGY = True


# Список оптимизируемых спеков
# Синтаксис:
#        <список спеков>   ::= <спек> | <список спеков>, <спек>
#        <спек>            ::= <имя спека> | <имя спека> : <список процедур>
#        <список процедур> ::= <процедура> | <список процедур> <процедура>
specs = """ 519.lbm,
            541.leela,
            508.namd,
            510.parest,
            521.wrf,
            505.mcf,
            549.fotonik3d,
            525.x264,
            544.nab,
            538.imagick,
            511.povray,
            503.bwaves,
            526.blender,
            523.xalancbmk,
            531.deepsjeng,
            548.exchange2,
            554.roms,
            500.perlbench,
            527.cam4,
            557.xz,
            502.gcc
        """
# Синхронная оптимизация? {0, 1}
# 0 -> независимая оптимизация каждого спека
# 1 -> синхранная оптимизация спеков
SYNCHRONOUS_OPTIMIZATION_FOR_SPECS = True

# Каталог, в котором формируется выходные файлы
OUTPUTDIR = "./doc/test_output"
# ! Надо сделать возможность не перезаписывать файлы
# REWRITE_OUTPUT_FILES = True
