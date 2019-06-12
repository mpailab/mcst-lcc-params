#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
    содержит преобразования пользовательских имен параметров ИС в имена внутренних переменных
"""

import global_vars as gl

# brief_name -> (fullname, discription, type, values, format, default_value)
data = {
    'specs' : ('SPECS',
        'задает список задач, для которых ИС должна осуществлять подборку параметров оптимизирующих преобразований',
        'format',
        None,
        '<specname>[: <procname> [<procname>]] [, <specname>[: <procname> [<procname>]]]',
        gl.__dict__['SPECS'] ),

    'sync' : ('SYNCHRONOUS_OPTIMIZATION_FOR_SPECS',
        'определяет характер оптимизации (синхронная или независимая) по отношению к заданному параметром specs списку задач',
        'bool',
        ['0', '1'], None,
        int(gl.__dict__['SYNCHRONOUS_OPTIMIZATION_FOR_SPECS']) ),

    'seq' : ('SEQ_OPTIMIZATION_WITH_STRATEGY',
        'определяет характер оптимизации (последовательная или обособленная) по отношению к заданной параметром strategy стратегии оптимизации',
        'bool',
        ['0', '1'], None,
        int(gl.__dict__['SEQ_OPTIMIZATION_WITH_STRATEGY']) ),

    'strategy' : ('OPTIMIZATION_STRATEGY',
        'задает стратегию оптимизации, согласно с которой ИС осуществляет подборку параметров оптимизирующих преобразований',
        'format',
        None,
        '<parname> [<parname>] [; <parname> [<parname>]]',
        gl.__dict__['OPTIMIZATION_STRATEGY'] ),

    'every' : ('GAIN_STAT_ON_EVERY_OPTIMIZATION_STEP',
        'включает пересчет статистики, собираемой компилятором LCC, при изменении значений параметров оптимизирующих преобразований',
        'bool',
        ['0', '1'], None,
        int(gl.__dict__['GAIN_STAT_ON_EVERY_OPTIMIZATION_STEP']) ),

    'start_temp' : ('START_TEMPERATURE',
        'задает начальное значение температуры',
        'float',
        ['(0, 1]'], None,
        gl.__dict__['START_TEMPERATURE'] ),

    'temp_law' : ('TEMPERATURE_LAW_TYPE',
        'задает закон убывания температуры',
        'disc',
        ['0', '1', '2'], None,
        gl.__dict__['TEMPERATURE_LAW_TYPE'] ),

    'alpha' : ('ALPHA_IN_TEPMERATURE_LAW',
        'задает значение параметра alpha в законе убывания температуры',
        'float',
        ['(0, 1)'], None,
        gl.__dict__['ALPHA_IN_TEPMERATURE_LAW'] ),

    'distr_law' : ('DISTRIBUTION_LAW_TYPE',
        'задает тип вероятностного распределения, определяющего выбор очередного кандидата для параметров оптимизирующих преобразований на каждом шаге метода имитации отжига',
        'disc',
        ['0', '1', '2', '3'], None,
        gl.__dict__['DISTRIBUTION_LAW_TYPE'] ),

    'relations' : ('USE_RELATIONS_OF_PARAMETORS',
        'включает использование зависимостей параметров оптимизирующих параметров друг от друга',
        'bool',
        ['0', '1'], None,
        int(gl.__dict__['USE_RELATIONS_OF_PARAMETORS']) ),

    'F_exec' : ('TIME_EXEC_IMPOTANCE',
        'задает значение множителя при члене относительного увеличении времени исполнения в минимизируемом функционале',
        'float', None, None,
        gl.__dict__['TIME_EXEC_IMPOTANCE'] ),

    'F_comp' : ('TIME_COMP_IMPOTANCE',
        'задает значение множителя при члене относительного увеличении времени компиляции в минимизируемом функционале',
        'float', None, None,
        gl.__dict__['TIME_COMP_IMPOTANCE'] ),

    'F_mem' : ('MEMORY_IMPOTANCE',
        'задает значение множителя при члене относительного увеличении объема, потребляемой компилятором памяти, в минимизируемом функционале',
        'float', None, None,
        gl.__dict__['MEMORY_IMPOTANCE'] ),

    'comp_limit' : ('COMP_TIME_INCREASE_ALLOWABLE_PERCENT',
        'задает допустимое относительное замедление времени компиляции',
        'float', None, None,
        gl.__dict__['COMP_TIME_INCREASE_ALLOWABLE_PERCENT'] ),

    'exec_limit' : ('EXEC_TIME_INCREASE_ALLOWABLE_PERCENT',
        'задает допустимое относительное замедление времени исполнения',
        'float', None, None,
        gl.__dict__['EXEC_TIME_INCREASE_ALLOWABLE_PERCENT'] ),

    'mem_limit' : ('MEMORY_INCREASE_ALLOWABLE_PERCENT',
        'задает допустимое относительное увеличение объема памяти, потребляемой при компиляции',
        'float', None, None,
        gl.__dict__['MEMORY_INCREASE_ALLOWABLE_PERCENT'] ),

    'iter_num' : ('MAX_NUMBER_ITERATIONS',
        'задает число шагов применения метода имитации отжига',
        'int', None, None,
        gl.__dict__['MAX_NUMBER_ITERATIONS'] ),

    'attempts_num' : ('MAX_NUMBER_OF_ATTEMPTS_FOR_ITERATION',
        'задает максимальное число попыток выбора очередного кандидата для параметров оптимизирующих преобразований на каждом шаге применения метода имитации отжига',
        'int', None, None,
        gl.__dict__['MAX_NUMBER_OF_ATTEMPTS_FOR_ITERATION'] ),

    'decrease_temp' : ('DECREASE_TEMPERATURE_BEFORE_UNFORTUNATE_ITERATIONS',
        'включает уменьшение температуры после неудачных шагов применения метода имитации отжига',
        'bool', ['0', '1'], None,
        int(gl.__dict__['DECREASE_TEMPERATURE_BEFORE_UNFORTUNATE_ITERATIONS']) ),

    'max_dcs_level' : ('MAX_DCS_LEVEL',
        'задает номер последнего существующего уровня оптимизации фазы dcs',
        'int', None, None,
        gl.__dict__['MAX_DCS_LEVEL'] ),

    'dcs_loop' : ('DCS_KOEF_LOOP_IMPOTANCE',
        'задает коэффициент мертвых циклов в формуле полезности dcs-оптимизации',
        'float', None, None,
        gl.__dict__['DCS_KOEF_LOOP_IMPOTANCE'] ),

    'dcs_edge' : ('DCS_KOEF_EDGE_IMPOTANCE',
        'задает коэффициент мертвых ребер в формуле полезности dcs-оптимизации',
        'float', None, None,
        gl.__dict__['DCS_KOEF_EDGE_IMPOTANCE'] ),

    'dcs_node' : ('DCS_KOEF_NODE_IMPOTANCE',
        'задает коэффициент мертвых узлов в формуле полезности dcs-оптимизации',
        'float', None, None,
        gl.__dict__['DCS_KOEF_NODE_IMPOTANCE'] ),

    'dcs_limit' : ('DSC_IMPOTANCE_LIMIT',
        'задает порог для значений полезности dcs-оптимиизации',
        'float', None, None,
        gl.__dict__['DSC_IMPOTANCE_LIMIT'] ),

    'smooth' : ('SMOOTH_STAT',
        'включает режим сглаживания распределений, получаемых по статистике работы компилятора LCC',
        'bool', ['0', '1'], None,
        int(gl.__dict__['SMOOTH_STAT']) ),

    'erf_disc' : ('ERF_KOEF_FOR_DISCRETE_PAR',
        'задает коэффициент сглаживания распределений параметров оптимизирующих преобразований целочисленного типа',
        'float', None, None,
        gl.__dict__['ERF_KOEF_FOR_DISCRETE_PAR'] ),

    'erf_cont' : ('ERF_KOEF_FOR_CONTINUOUS_PAR',
        'задает коэффициент сглаживания распределений параметров оптимизирующих преобразований вещественного типа',
        'float', None, None,
        gl.__dict__['ERF_KOEF_FOR_CONTINUOUS_PAR'] ),

    'erf_limit' : ('ZERO_LIMIT_FOR_ERF',
        'задает долю для сглаживаемых весов, которая не будет участвовать в сглаживании',
        'float', 
        ['(0, 1)'], None,
        gl.__dict__['ZERO_LIMIT_FOR_ERF'] ),

    'weight_limit' : ('ZERO_LIMIT_FOR_WEIGHT',
        'задает порог для абсолютных значений весов, веса ниже которого не сглаживаются',
        'float',
        ['(0, 1)'], None,
        gl.__dict__['ZERO_LIMIT_FOR_WEIGHT'] ),

    'w_task' : ('TASK_WEIGHT_SETUP',
        'задает режим учета весов задач при обработке статистики работы компилятора LCC',
        'disc',
        ['0', '1', '2', '3'], None,
        gl.__dict__['TASK_WEIGHT_SETUP'] ),

    'w_proc' : ('PROC_WEIGHT_SETUP',
        'задает режим учета весов процедур при обработке статистики работы компилятора LCC',
        'disc',
        ['0', '1'], None,
        gl.__dict__['PROC_WEIGHT_SETUP'] ),

    'w_unexec' : ('UNEXEC_PROC_WEIGHT_SETUP',
        'задает настройку весов неисполняемых процедур',
        'disc', ['0', '1', '2'], None,
        gl.__dict__['UNEXEC_PROC_WEIGHT_SETUP'] ),

    'w_default' : ('DEFAULT_WEIGHT_FOR_PROC',
        'задает вес по-умолчанию, который присваивается компилируемой, но неисполняемой процедуре',
        'float', None, None,
        gl.__dict__['DEFAULT_WEIGHT_FOR_PROC'] ),

    'w_regn' : ('REGN_WEIGHT_SETUP',
        'задает режим учета весов регионов фазы regions при обработке статистики работы компилятора LCC',
        'disc', ['0', '1', '2'], None,
        gl.__dict__['REGN_WEIGHT_SETUP'] ),

    'w_node' : ('NODE_WEIGHT_SETUP',
        'задает режим определения начального веса узлов регионов фазы regions при обработке статистики работы компилятора LCC',
        'disc', ['0', '1', '2', '3'], None,
        gl.__dict__['NODE_WEIGHT_SETUP'] ),

    'w_icv_regn' : ('ICV_REGN_WEIGHT_SETUP',
        'задает режим учета весов регионов фазы if\_conv при обработке статистики работы компилятора LCC',
        'disc', ['0', '1', '2'], None,
        gl.__dict__['ICV_REGN_WEIGHT_SETUP'] ),

    'w_sect' : ('SECT_WEIGHT_SETUP',
        'задает режим учета весов сливаемых участков фазы if\_conv при обработке статистики работы компилятора LCC',
        'disc', ['0', '1'], None,
        gl.__dict__['SECT_WEIGHT_SETUP'] ),

    'use_unexec' : ('USE_UNEXEC_PROCS_IN_STAT',
        'включает обработку статистики компиляции неисполняемых процедур',
        'bool', ['0', '1'], None,
        int(gl.__dict__['USE_UNEXEC_PROCS_IN_STAT']) ),

    'din_regn' : ('DINUMIC_REGN_OPERS_NUM',
        'включает учет динамического изменения числа операций в регионах во время компиляции на фазе regions',
        'bool', ['0', '1'], None,
        int(gl.__dict__['DINUMIC_REGN_OPERS_NUM']) ),

    'din_proc' : ('DINUMIC_PROC_OPERS_NUM',
        'включает учет динамического изменения числа операций в процедуре во время компиляции на фазе regions',
        'bool', ['0', '1'], None,
        int(gl.__dict__['DINUMIC_PROC_OPERS_NUM']) ),

    'file_w_task' : ('TASK_WEIGHT_PATH',
        'задает путь к файлу, из которого считываются веса задач',
        'path_to_file', None, None,
        gl.__dict__['TASK_WEIGHT_PATH'] ),

    'stat' : ('STAT_PATH',
        'задает путь каталогу со статистикой компиляции, собранной при значениях параметров оптимизирующих преобразований по-умолчанию',
        'path_to_dir', None, None,
        gl.__dict__['STAT_PATH'] ),

    'din_stat' : ('DINUMIC_STAT_PATH',
        'задает путь каталогу, в котором ИС собирает статистику компиляции',
        'path_to_dir', None, None,
        gl.__dict__['DINUMIC_STAT_PATH'] ),

    'dir_w_proc' : ('PROC_WEIGHT_PATH',
        'задает путь до каталога с файлами, определяющими веса процедур',
        'path_to_dir', None, None,
        gl.__dict__['PROC_WEIGHT_PATH'] ),

    'database' : ('PAR_DISTRIBUTION_DATABASE',
        'включает хранение в оперативной памяти всех распределений, получаемых по статистике работы компилятора LCC',
        'bool', ['0', '1'], None,
        int(gl.__dict__['PAR_DISTRIBUTION_DATABASE']) ),

    'output' : ('OUTPUTDIR',
        'задает каталог, в котором ИС формирует свои выходные файлы',
        'path_to_dir', None, None,
        gl.__dict__['OUTPUTDIR'] ),

    'rewrite' : ('ALLOW_REWRITE_OUTPUT_FILES',
        'включает режим перезаписи выходных файлов',
        'bool',
        ['0', '1'], None,
        int(gl.__dict__['ALLOW_REWRITE_OUTPUT_FILES']) ),
    
    'tr_dir' : ('TRAIN_DATA_DIR',
        'задает каталог, в котором расположены данные для переобучения ИС',
        'path_to_dir', None, None,
        gl.__dict__['TRAIN_DATA_DIR'] ),
    
    'tr_data' : ('TRAIN_DATA_SETUP',
        'настройка сбора данных перед обучением',
        'disc',
        ['0', '1', '2'], None,
        gl.__dict__['TRAIN_DATA_SETUP'] ),
    
    'verbose' : ('VERBOSE',
        'задает степень подробности вывода на экран во время работы ИС',
        'disc',
        ['0', '1', '2'], None,
        gl.__dict__['VERBOSE'] ),
    }

def gen_sed_script():
    llist = list(data.items())
    # сортировка по длине полных имен, нужно, чтобы в начале были длинные имена а потом короткие
    llist.sort(key = lambda x: len(x[1][0]), reverse = True) 
    for key, item in llist:
        pattern = item[0].replace('_', '\\\\_')
        sub = key.replace('_', '\\\\_')
        print('s/' + pattern + '/' + sub + '/g')

# gen_sed_script()
