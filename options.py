#!/usr/bin/python3
# -*- coding: utf-8 -*-
 
# Глобальные переменные

# Режимы работы ИС
modes = {
    ''       : 'Основная группа параметров',
    'anneal' : 'Группа параметров для настройки метода имитации отжига',
    'stat'   : 'Группа параметров для обработки статистики задач/процедур',
    'train'  : 'Группа параметров для настроки обучение ИС',
    'func'   : 'Группа параметров для настроки оптимизируемого функционала',
    'setup'  : 'Установка значений по умолчанию параметров оптимизирующих преобразований'
    }

# Информационная структура глобальной переменной
class Global:
     def __init__ (self, name, param, help, type, values, format, default, mode = ''):
          self.name    = name    # имя глобала
          self.param   = param   # имя параметра, соответствующего глобалу
          self.help    = help    # описание глобала
          self.type    = type    # тип глобала
          self.values  = values  # возможные значения глобала
          self.format  = format  # формат значения глобала
          self.default = default # значение по умолчанию
          # mode -> setup, train, anneal, stat, func
          self.mode    = mode    # режим ИС

     def isBool (self):
          return self.type == 'bool'

     def isDisc (self):
          return self.type == 'disc'
     
     def isDiscStr (self):
          return self.type == 'disc_str'
     
     def isInt (self):
          return self.type == 'int'

     def isFloat (self):
          return self.type == 'float'

     def isFile (self):
          return self.type == 'path_to_file'

     def isDir (self):
          return self.type == 'path_to_dir'

     def isFormat (self):
          return self.type == 'format'

# Таблица глабольных переменных: {param -> Global}
GL = {}

def list (mode = ''):
     return [x for x in GL.values() if x.mode == mode]

def exist (param):
     return param in GL

def var (param):
     return GL[param]

#########################################################################################
# Настройка весов
# 
# Конечный вес каждого узла фазы regions определяется формулой pr_norm(nd_norm(w_n * w_r) * w_p * w_t), где
# w_n -- начальный вес узла,
# w_r -- вес региона,
# nd_norm -- нормирование по всем узлам процедуры,
# w_p -- вес процедуры,
# w_t -- вес спека,
# pr_norm -- нормирование по всем расматриваемым процедурам (всех рассматриваемых спеков)
# 
# Конечный вес сливаемого участка в фазе if_conv определяется формулой pr_norm(s_norm(w_s * w_ir) * w_p * w_t), где
# w_s -- начальный вес сливаемого участка
# w_ir -- вес региона, к которому относится сливаемый участок
# s_norm -- нормирование по всем сливаемым участкам процедуры

# Настройка веса неисполняемой процедуры {0, 1, 2}
# 0 -> DEFAULT_WEIGHT_FOR_PROC
# 1 -> минимум среди всех весов исполняемых процедур
# 2 -> среднее значение весов исполняемых процедур
UNEXEC_PROC_WEIGHT_SETUP = 1
GL['w_unexec'] = Global(
     'UNEXEC_PROC_WEIGHT_SETUP', 'w_unexec',
     ('вес неисполняемых процедур:'
      ' 0 - вес по-умолчанию,'
      ' 1 - минимум среди всех весов исполняемых процедур,'
      ' 2 - среднее значение весов исполняемых процедур'),
     'disc', ['0', '1', '2'], None,
     UNEXEC_PROC_WEIGHT_SETUP, 'stat'
)

# Вес по-умолчанию, который присваевается компилируемой, но неисполняемой процедуре
DEFAULT_WEIGHT_FOR_PROC = 1.0
GL['w_default'] = Global(
     'DEFAULT_WEIGHT_FOR_PROC', 'w_default',
     'вес по-умолчанию, который присваивается компилируемой, но неисполняемой процедуре',
     'float', None, None,
     DEFAULT_WEIGHT_FOR_PROC, 'stat'
)

# Режим учета веса спека w_t: {0, 1, 2, 3}
# 0 -> w_t = 1 (не учитывать вес спека)
# 1 -> w_t -- считывается из файла TASK_WEIGHT_PATH
# 2 -> w_t -- отношение времени исполнения всех собственных (небиблиотечных) процедур спека к общему времени его работы
# 3 -> w_t -- отношение времени исполнения оптимизируемых собственных (небиблиотечных) процедур спека к общему времени его работы
TASK_WEIGHT_SETUP = 3
GL['w_task'] = Global(
     'TASK_WEIGHT_SETUP', 'w_task',
     ('режим учета весов задач при обработке статистики работы компилятора LCC:'
      ' 0 - не учитывать вес,'
      ' 1 - считывается из файла,'
      ' 2 - отношение времени исполнения всех процедур задачи к общему времени его исполнения),'
      ' 3 - отношение времени исполнения оптимизируемых процедур задачи к общему времени его исполнения'),
     'disc', ['0', '1', '2', '3'], None,
     TASK_WEIGHT_SETUP, 'stat'
)

# Режим учета веса процедуры w_p: {0, 1}
# 0 -> w_p = 1 (не учитывать вес процедуры)
# 1 -> w_p -- временя работы процедуры в составе спека (ненормированное)
PROC_WEIGHT_SETUP = 1
GL['w_proc'] = Global(
     'PROC_WEIGHT_SETUP', 'w_proc',
     ('режим учета весов процедур при обработке статистики работы компилятора LCC:'
      ' 0 - не учитывать вес процедуры,'
      ' 1 - временя работы процедуры в составе спека'),
     'disc', ['0', '1'], None,
     PROC_WEIGHT_SETUP, 'stat'
)

# Режим определения начального веса узла w_n: {0, 1, 2, 3}
# 0 -> w_n = 0, если счетчик узла во всей процедуре (n_cnt) равен нулю;
#      w_n = 1, иначе
# 1 -> w_n -- внутренний счетчик узла (v_cnt)
# 2 -> w_n -- счетчик узла во всей процедуре (n_cnt) 
# 3 -> w_n -- отношения внутреннего счетчика узла к счетчику узла во всей процедуре (v_cnt / n_cnt);
#      однако если n_cnt = 0, то w_n полагается равным нулю
NODE_WEIGHT_SETUP = 0
GL['w_node'] = Global(
     'NODE_WEIGHT_SETUP', 'w_node',
     ('режим определения начального веса узлов регионов фазы regions при обработке статистики работы компилятора LCC:'
      ' 0 - вес равен 0 если счетчик узла в процедуре равен нулю и 1 иначе,'
      ' 1 - вес равен внутреннему счетчику узла в регионе,'
      ' 2 - вес равен счетчику узла во всей процедуре,'
      ' 3 - вес равен отношению внутреннего счетчика узла к счетчику узла во всей процедуре (0 если счетчик узла в процедуре равен нулю)'),
     'disc', ['0', '1', '2', '3'], None,
     NODE_WEIGHT_SETUP, 'stat'
)

# Режим учета веса региона w_r фазы regions: {0, 1, 2}
# 0 -> w_r = 1 (не учитывать вес региона)
# 1 -> w_r -- счетчик региона
# 2 -> w_r -- счетчик региона, нормируемый по всем регионам в процедуре
REGN_WEIGHT_SETUP = 0
GL['w_regn'] = Global(
     'REGN_WEIGHT_SETUP', 'w_regn',
     ('режим учета весов регионов фазы regions при обработке статистики работы компилятора LCC:'
      ' 0 - не учитывать вес региона,'
      ' 1 - вес равен счетчику головы региона'
      ' 2 - вес равен счетчику головы региона, нормируемый по всем регионам в процедуре'),
     'disc', ['0', '1', '2'], None,
     REGN_WEIGHT_SETUP, 'stat'
)

# Режим учета веса региона w_ir фазы if_conv: {0, 1, 2}
# 0 -> w_ir = 1 (не учитывать вес региона)
# 1 -> w_ir -- счетчик региона
# 2 -> w_ir -- счетчик региона, нормируемый по всем регионам в процедуре
ICV_REGN_WEIGHT_SETUP = 0
GL['w_icv_regn'] = Global(
     'ICV_REGN_WEIGHT_SETUP', 'w_icv_regn',
     ('режим учета весов регионов фазы if_conv при обработке статистики работы компилятора LCC:'
      ' 0 - не учитывать вес региона,'
      ' 1 - вес равен счетчику головы региона'
      ' 2 - вес равен счетчику головы региона, нормируемый по всем регионам в процедуре'),
     'disc', ['0', '1', '2'], None,
     ICV_REGN_WEIGHT_SETUP, 'stat'
)

# Режим учета веса сливаемого участка w_s: {0, 1}
# 0 -> w_s = 1 (не учитывать вес сливаемого участка)
# 1 -> w_s -- счетчик сливаемого участка
SECT_WEIGHT_SETUP = 1
GL['w_sect'] = Global(
     'SECT_WEIGHT_SETUP', 'w_sect',
     ('режим учета весов сливаемых участков фазы if_conv при обработке статистики работы компилятора LCC'
      ' 0 - не учитывать вес сливаемого участка,'
      ' 1 - вес равен счетчику головы сливаемого участка'),
     'disc', ['0', '1'], None,
     SECT_WEIGHT_SETUP, 'stat'
)

#########################################################################################
# Считывание файлов статистики

# Каталог с файлами <specname>.txt, задающими веса для процедур спека <specname>
# Строка каждого файла <specname>.txt имеет вид: <procname> <weight>
# Допустим случай, когда у спека <specname> может не быть компилируемой процедуры <procname>
# Не все компилируемые процедуры спека <specname> обязаны присутствовать в файле <specname>.txt
PROC_WEIGHT_PATH = None
GL['dir_w_proc'] = Global(
     'PROC_WEIGHT_PATH', 'dir_w_proc',
     'путь до каталога с файлами, определяющими веса процедур',
     'path_to_dir', None, None,
     PROC_WEIGHT_PATH, 'stat'
)

# Файл, в котором задаются веса спеков
# Используется, если TASK_WEIGHT_SETUP = 1
TASK_WEIGHT_PATH = None
GL['file_w_task'] = Global(
     'TASK_WEIGHT_PATH', 'file_w_task',
     'путь к файлу, из которого считываются веса задач',
     'path_to_file', None, None,
     TASK_WEIGHT_PATH, 'stat'
)

# Учитывать статистику компиляции неисполняемых процедур (т.е. процедур, для которых не заданы веса)? {0, 1}
USE_UNEXEC_PROCS_IN_STAT = False
GL['use_unexec'] = Global(
     'USE_UNEXEC_PROCS_IN_STAT', 'use_unexec',
     'обработка статистики компиляции неисполняемых процедур',
     'bool', ['0', '1'], None,
     USE_UNEXEC_PROCS_IN_STAT, 'stat'
)

# Каталог со статистикой компиляции спеков при значениях параметров оптимизирующих преобразований по-умолчанию
STAT_PATH = None
GL['stat'] = Global(
     'STAT_PATH', 'stat',
     'путь каталогу со статистикой компиляции, собранной при значениях параметров оптимизирующих преобразований по-умолчанию',
     'path_to_dir', None, None,
     STAT_PATH, 'stat'
)

# Каталог, в который собирается статистика компиляции спеков во время работы ИС
DINUMIC_STAT_PATH = None
GL['din_stat'] = Global(
     'DINUMIC_STAT_PATH', 'din_stat',
     'путь каталогу, в котором ИС собирает статистику компиляции',
     'path_to_dir', None, None,
     DINUMIC_STAT_PATH, 'stat'
)

#########################################################################################
# Обработка статистики

# Учитывать при обработки статистики динамическое изменение числа операций в процедуре во время фазы regions? {0, 1}
DINUMIC_PROC_OPERS_NUM = False
GL['din_proc'] = Global(
     'DINUMIC_PROC_OPERS_NUM', 'din_proc',
     'учет динамического изменения числа операций в процедуре во время компиляции на фазе regions',
     'bool', ['0', '1'], None,
     DINUMIC_PROC_OPERS_NUM, 'stat'
)

# Учитывать при обработки статистики динамическое изменение числа операций в регионах процедуры во время фазы regions? {0, 1}
DINUMIC_REGN_OPERS_NUM = False
GL['din_regn'] = Global(
     'DINUMIC_REGN_OPERS_NUM', 'din_regn',
     'включает учет динамического изменения числа операций в регионах во время компиляции на фазе regions',
     'bool', ['0', '1'], None,
     DINUMIC_REGN_OPERS_NUM, 'stat'
)

#########################################################################################
# Фаза dcs

# Номер последнего существующего уровня оптимизации фазы dcs
MAX_DCS_LEVEL = 4
GL['max_dcs_level'] = Global(
     'MAX_DCS_LEVEL', 'max_dcs_level',
     'номер последнего существующего уровня оптимизации фазы dcs',
     'int', None, None,
     MAX_DCS_LEVEL, 'setup'
)

# Полезность dcs оптимизации для процедуры определяется формулой:
# impotance = DCS_KOEF_NODE_IMPOTANCE * nd + DCS_KOEF_EDGE_IMPOTANCE * ed + DCS_KOEF_LOOP_IMPOTANCE * ld,
# где nd -- процент найденных мертвых узлов,
#     ed -- процент найденных мертвых дуг,
#     ld -- процент найденных мертвых циклов.
DCS_KOEF_NODE_IMPOTANCE = 1.0
GL['dcs_node'] = Global(
     'DCS_KOEF_NODE_IMPOTANCE', 'dcs_node',
     'коэффициент мертвых узлов в формуле полезности dcs-оптимизации',
     'float', None, None,
     DCS_KOEF_NODE_IMPOTANCE, 'anneal'
)
DCS_KOEF_EDGE_IMPOTANCE = 1.0
GL['dcs_edge'] = Global(
     'DCS_KOEF_EDGE_IMPOTANCE', 'dcs_edge',
     'коэффициент мертвых дуг в формуле полезности dcs-оптимизации',
     'float', None, None,
     DCS_KOEF_EDGE_IMPOTANCE, 'anneal'
)
DCS_KOEF_LOOP_IMPOTANCE = 1.0
GL['dcs_loop'] = Global(
     'DCS_KOEF_LOOP_IMPOTANCE', 'dcs_loop',
     'коэффициент мертвых циклов в формуле полезности dcs-оптимизации',
     'float', None, None,
     DCS_KOEF_LOOP_IMPOTANCE, 'anneal'
)

# Если полезность dcs оптимизации <= DSC_IMPOTANCE_LIMIT, то dcs оптимизация считается бесполезной
DSC_IMPOTANCE_LIMIT = 0.001
GL['dcs_limit'] = Global(
     'DSC_IMPOTANCE_LIMIT', 'dcs_limit',
     'порог для значений полезности dcs-оптимиизации',
     'float', None, None,
     DSC_IMPOTANCE_LIMIT, 'anneal'
)

#########################################################################################
# 

# Каталог, в котором хранятся логи запусков оптимизации методом имитации отжига
#RUN_LOGS_PATH = './logs'
#GL['logs'] = Global(
     #'RUN_LOGS_PATH', 'logs',
     #'каталог, в котором хранятся логи запусков',
     #'path_to_dir', None, None,
     #RUN_LOGS_PATH
#)

# Предполагаемая процентная величина погрешности определения времени исполнения, компиляции, объема потребляемой памяти, и т.п.
#DEVIATION_PERCENT_OF_TcTeMemF = 0.01
#GL['inaccuracy'] = Global(
     #'DEVIATION_PERCENT_OF_TcTeMemF', 'inaccuracy',
     #'величина погрешности',
     #'float', ['(0, 1)'], None,
     #DEVIATION_PERCENT_OF_TcTeMemF
#)

#########################################################################################
# Сглаживание статистики

# Сглаживать статистику? {0, 1}
SMOOTH_STAT = True
GL['smooth'] = Global(
     'SMOOTH_STAT', 'smooth',
     'сглаживание распределений, получаемых по статистике работы компилятора LCC',
     'bool', ['0', '1'], None,
     SMOOTH_STAT, 'stat'
)

# Чем меньше следующие коэффиценты, тем сильнее сглаживание
ERF_KOEF_FOR_CONTINUOUS_PAR = 20.0 # коэффициент сглаживания для вещественных параметров
GL['erf_cont'] = Global(
     'ERF_KOEF_FOR_CONTINUOUS_PAR', 'erf_cont',
     'коэффициент сглаживания распределений параметров оптимизирующих преобразований вещественного типа',
     'float', None, None,
     ERF_KOEF_FOR_CONTINUOUS_PAR, 'stat'
)
ERF_KOEF_FOR_DISCRETE_PAR = 0.5 # коэффициент сглаживания для целичисленных параметров
GL['erf_disc'] = Global(
     'ERF_KOEF_FOR_DISCRETE_PAR', 'erf_disc',
     'коэффициент сглаживания распределений параметров оптимизирующих преобразований целочисленного типа',
     'float', None, None,
     ERF_KOEF_FOR_DISCRETE_PAR, 'stat'
)

# Чем ниже следующие параметры, тем качественнее сглаживание
# Уменьшение следующих параметров может очень существенно замедлить сглаживание!
# Доля исходного веса, которая не будет участвовать в сглаживании
ZERO_LIMIT_FOR_ERF = 0.01
GL['erf_limit'] = Global(
     'ZERO_LIMIT_FOR_ERF', 'erf_limit',
     'доля для сглаживаемых весов, которая не будет участвовать в сглаживании',
     'float', ['(0, 1)'], None,
     ZERO_LIMIT_FOR_ERF, 'stat'
)

# Порог для абсолютных значений весов, веса ниже которого не будут сглаживаться
ZERO_LIMIT_FOR_WEIGHT = 0.001
GL['weight_limit'] = Global(
     'ZERO_LIMIT_FOR_WEIGHT', 'weight_limit',
     'порог для абсолютных значений весов, веса ниже которого не сглаживаются',
     'float', ['(0, 1)'], None,
     ZERO_LIMIT_FOR_WEIGHT, 'stat'
)

#########################################################################################
# Модуль optimize

# Использовать собранную статистику компилятора LCC в не зависимости от значений параметров оптимизирующих преобразований? {0, 1}
INHERIT_STAT = False
GL['inherit'] = Global(
     'INHERIT_STAT', 'inherit',
     'использовать собранную статистику компилятора LCC в не зависимости от значений параметров оптимизирующих преобразований',
     'bool', ['0', '1'], None,
     INHERIT_STAT
)

# Сохранять в оперативной памяти распределения весов для каждого нового набора параметров? {0, 1}
# Увеличивает скорость работы ИС, может привести к чрезмерному потреблению оперативной памяти
PAR_DISTRIBUTION_DATABASE = True
GL['database'] = Global(
     'PAR_DISTRIBUTION_DATABASE', 'database',
     'хранение в оперативной памяти всех распределений, получаемых по статистике работы компилятора LCC',
     'bool', ['0', '1'], None,
     PAR_DISTRIBUTION_DATABASE, 'anneal'
)

# Начальное значение температуры: (0, 1]
START_TEMPERATURE = 0.5
GL['start_temp'] = Global(
     'START_TEMPERATURE', 'start_temp',
     'начальное значение температуры в методе имитации отжига',
     'float', ['(0, 1]'], None,
     START_TEMPERATURE, 'anneal'
)

# Закон убывания температуры: {0, 1, 2}
# 0 -> 1 / ln(n + 1)
# 1 -> 1 / n
# 2 -> alpha ^ n
TEMPERATURE_LAW_TYPE = 2
GL['temp_law'] = Global(
     'TEMPERATURE_LAW_TYPE', 'temp_law',
     ('задает закон убывания температуры в методе имитации отжига: '
      ' 0 - функция f(n) = 1 / ln(n + 1)'
      ' 1 - функция f(n) = 1 / n'
      ' 2 - функция f(n) = alpha ^ n'),
     'disc', ['0', '1', '2'], None,
     TEMPERATURE_LAW_TYPE, 'anneal'
)

# значение alpha
ALPHA_IN_TEPMERATURE_LAW = 0.7
GL['alpha'] = Global(
     'ALPHA_IN_TEPMERATURE_LAW', 'alpha',
     'значение параметра alpha в законе убывания температуры для метода имитации отжига',
     'float', ['(0, 1)'], None,
     ALPHA_IN_TEPMERATURE_LAW, 'anneal'
)

# Тип вероятностного распределения,
# определяющего выбор следующего состояния системы в зависимости от ее текущих состояния и температуры: {0, 1, 2, 3}
# 0 -> нормальное распределение
# 1 -> распределение для сверхбыстрого отжига
# 2 -> распределение Коши
# 3 -> равномерное распределение
DISTRIBUTION_LAW_TYPE = 1
GL['distr_law'] = Global(
     'DISTRIBUTION_LAW_TYPE', 'distr_law',
     ('задает тип вероятностного распределения, определяющего выбор очередного кандидата для параметров оптимизирующих преобразований на каждом шаге метода имитации отжига'
      ' 0 - нормальное распределение,'
      ' 1 - распределение для сверхбыстрого отжига,'
      ' 2 - распределение Коши,'
      ' 3 - равномерное распределение'),
     'disc', ['0', '1', '2', '3'], None,
     DISTRIBUTION_LAW_TYPE, 'anneal'
)

# Учитывать зависимоти параметров друг от друга? {0, 1}
# Параметр par1 зависит от par2, если при определенных значениях параметра par2,
# значение par1 никак не влияют на работу компилятора LCC.
# Если опция возведена, то зависимости параметров учитываются при прогнозировании
# насколько существенно может повлиять на работу компилятора изменение значений параметров
USE_RELATIONS_OF_PARAMETORS = True
GL['relations'] = Global(
     'USE_RELATIONS_OF_PARAMETORS', 'relations',
     'использование зависимостей параметров оптимизирующих параметров друг от друга',
     'bool', ['0', '1'], None,
     USE_RELATIONS_OF_PARAMETORS, 'anneal'
)

# Минимизируемый функцонал имеет вид
# F(dT_c, dT_e, dV) = TIME_COMP_IMPOTANCE * dT_c + TIME_EXEC_IMPOTANCE * dT_e + MEMORY_IMPOTANCE * dV, где
# dT_c -- относительное увеличение времени компиляции,
# dT_e -- относительное увеличение времени исполнения,
# dV -- относительное увеличение объема потребляемой памяти.

# Однако, если выполняется одно из условий
# dT_c > 1 + COMP_TIME_INCREASE_ALLOWABLE_PERCENT,
# dT_e > 1 + EXEC_TIME_INCREASE_ALLOWABLE_PERCENT,
# dV > 1 + MEMORY_INCREASE_ALLOWABLE_PERCENT,
# то значение F(dT_c, dT_e, dV) полагается равным +бесконечности

# Значения коэффицентов минимизируемого функционала
TIME_EXEC_IMPOTANCE = 5.0
GL['F_exec'] = Global(
     'TIME_EXEC_IMPOTANCE', 'F_exec',
     'значение множителя при члене относительного увеличении времени исполнения в минимизируемом функционале',
     'float', None, None,
     TIME_EXEC_IMPOTANCE, 'func'
)
TIME_COMP_IMPOTANCE = 1.0
GL['F_comp'] = Global(
     'TIME_COMP_IMPOTANCE', 'F_comp',
     'значение множителя при члене относительного увеличении времени компиляции в минимизируемом функционале',
     'float', None, None,
     TIME_COMP_IMPOTANCE, 'func'
)
MEMORY_IMPOTANCE = 1.0
GL['F_mem'] = Global(
     'MEMORY_IMPOTANCE', 'F_mem',
     'значение множителя при члене относительного увеличении объема потребляемой компилятором памяти в минимизируемом функционале',
     'float', None, None,
     MEMORY_IMPOTANCE, 'func'
)

# Допустимый процент увеличения времени компиляции
COMP_TIME_INCREASE_ALLOWABLE_PERCENT = 0.25
GL['comp_limit'] = Global(
     'COMP_TIME_INCREASE_ALLOWABLE_PERCENT', 'comp_limit',
     'задает допустимое относительное замедление времени компиляции',
     'float', None, None,
     COMP_TIME_INCREASE_ALLOWABLE_PERCENT, 'func'
)

# Допустимый процент увеличения времени исполнения
EXEC_TIME_INCREASE_ALLOWABLE_PERCENT = 0.05
GL['exec_limit'] = Global(
     'EXEC_TIME_INCREASE_ALLOWABLE_PERCENT', 'exec_limit',
     'задает допустимое относительное замедление времени исполнения',
     'float', None, None,
     EXEC_TIME_INCREASE_ALLOWABLE_PERCENT, 'func'
)

# Допустимый процент увеличения объема потребляемой памяти
MEMORY_INCREASE_ALLOWABLE_PERCENT = 0.50
GL['mem_limit'] = Global(
     'MEMORY_INCREASE_ALLOWABLE_PERCENT', 'mem_limit',
     'задает допустимое относительное увеличение объема памяти, потребляемой при компиляции',
     'float', None, None,
     MEMORY_INCREASE_ALLOWABLE_PERCENT, 'func'
)

# Число итераций метода отжига
MAX_NUMBER_ITERATIONS = 10
GL['iter_num'] = Global(
     'MAX_NUMBER_ITERATIONS', 'iter_num',
     'число шагов применения метода имитации отжига',
     'int', None, None,
     MAX_NUMBER_ITERATIONS, 'anneal'
)

# Максимальное число попыток выбора новых значений параметров для каждой итерации метода отжига
MAX_NUMBER_OF_ATTEMPTS_FOR_ITERATION = 10
GL['attempts_num'] = Global(
     'MAX_NUMBER_OF_ATTEMPTS_FOR_ITERATION', 'attempts_num',
     'максимальное число попыток выбора очередного кандидата для параметров оптимизирующих преобразований на каждом шаге применения метода имитации отжига',
     'int', None, None,
     MAX_NUMBER_OF_ATTEMPTS_FOR_ITERATION, 'anneal'
)

# Уменьшать значение температуры после итераций, на которых не был осуществлен переход к лучшему значению? {0, 1}
DECREASE_TEMPERATURE_BEFORE_UNFORTUNATE_ITERATIONS = True
GL['decrease_temp'] = Global(
     'DECREASE_TEMPERATURE_BEFORE_UNFORTUNATE_ITERATIONS', 'decrease_temp',
     'уменьшение температуры после неудачных шагов применения метода имитации отжига',
     'bool', ['0', '1'], None,
     DECREASE_TEMPERATURE_BEFORE_UNFORTUNATE_ITERATIONS, 'anneal'
)

#########################################################################################
# Параметры запуска ИС

# Стратегия
# Синтаксис:
#   <стратегия>         ::= <группа параметров> | <стратегия>; <группа параметров>
#   <группа параметров> ::= <параметр> | <группа параметров> <параметр>
OPTIMIZATION_STRATEGY = None
GL['strategy'] = Global(
     'OPTIMIZATION_STRATEGY', 'strategy',
     'стратегия оптимизации, согласно с которой ИС осуществляет подборку параметров оптимизирующих преобразований',
     'format', None, '<parname> [<parname>] [; <parname> [<parname>]]',
     OPTIMIZATION_STRATEGY
)

# Последовательная оптимизация? {0, 1}
# 0 -> независимая оптимизация по каждой группе в стратегии
# 1 -> последовательная оптимизация согласно стратегии
SEQ_OPTIMIZATION_WITH_STRATEGY = True
GL['seq'] = Global(
     'SEQ_OPTIMIZATION_WITH_STRATEGY', 'seq',
     ('характер оптимизации по отношению к заданной параметром strategy стратегии оптимизации:'
      ' 0 - независимая оптимизация по каждой группе в стратегии'
      ' 1 - последовательная оптимизация согласно стратегии'),
     'bool', ['0', '1'], None,
     SEQ_OPTIMIZATION_WITH_STRATEGY, 'anneal'
)


# Список оптимизируемых задач
# Синтаксис:
#   <список задач>    ::= <задача> | <список задач>, <задача>
#   <задача>          ::= <имя задачи> | <имя задачи> : <список процедур>
#   <список процедур> ::= <процедура> | <список процедур> <процедура>
SPECS = None
GL['specs'] = Global(
     'SPECS', 'specs',
     'список задач, для которых ИС должна осуществлять подборку параметров оптимизирующих преобразований',
     'format', None, '<specname>[: <procname> [<procname>]] [, <specname>[: <procname> [<procname>]]]',
     SPECS
)

# Синхронная оптимизация? {0, 1}
# 0 -> независимая оптимизация каждого спека
# 1 -> синхранная оптимизация спеков
SYNCHRONOUS_OPTIMIZATION_FOR_SPECS = True
GL['sync'] = Global(
     'SYNCHRONOUS_OPTIMIZATION_FOR_SPECS', 'sync',
     ('характер оптимизации по отношению к заданному параметром specs списку задач:'
      ' 0 - независимая оптимизация каждой задачи'
      ' 1 - синхранная оптимизация задач'),
     'bool', ['0', '1'], None,
     SYNCHRONOUS_OPTIMIZATION_FOR_SPECS
)

# Каталог, в котором формируются выходные файлы
#OUTPUTDIR = "."
#GL['output'] = Global(
     #'OUTPUTDIR', 'output',
     #'каталог, в котором ИС формирует свои выходные файлы',
     #'path_to_dir', None, None,
     #OUTPUTDIR
#)

# Задает степень подробности вывода на экран во время работы ИС.
VERBOSE = 0
GL['verbose'] = Global(
     'VERBOSE', 'verbose',
     'степень подробности вывода информации на экран во время работы ИС',
     'disc', ['0', '1', '2'], None,
     VERBOSE
)

# Перезаписывать выходные файлы? {0, 1}
# 0 -> имена для выходных файлов будут подбираться таким образом, чтобы не перезаписывать выходные файлы от предыдущих запусков
# 1 -> выходные файлы от предыдущих запусков могут быть перезаписаны
#ALLOW_REWRITE_OUTPUT_FILES = False
#GL['rewrite'] = Global(
     #'ALLOW_REWRITE_OUTPUT_FILES', 'rewrite',
     #'режим перезаписи выходных файлов',
     #'bool', ['0', '1'], None,
     #ALLOW_REWRITE_OUTPUT_FILES
#)


#########################################################################################
# Модуль обучения ИС

# Удаляются все накопленные данные для обучения
TRAIN_PROC_CHARS = None
GL['proc_chars'] = Global(
     'TRAIN_PROC_CHARS', 'proc_chars',
     'характеристики процедур, для которых необходимо найти оптимальные значения параметров компилятора lcc. Данные задаются в следующем формате:\n'
     '<procs> = <proc> | <proc> <procs>\n'
     '<proc>  = <weight>;<nodes>;<loops>;<doms>;<pdoms>\n'
     '<weight> - вес процедуры\n'
     '<nodes> = <node> | <node>,<nodes>\n'
     '<node>  = <num>:<type>:<cnt>:<o_num>:<c_num>:<l_num>:<s_num>\n'
     '<num>   - номер узла управляющего графа\n'
     '<type>  - его тип (одно из значений Simple, If, Return, Start, Stop, Switch, Hyper, Jump, Tmp)\n'
     '<o_num> - число всех операций в нём\n'
     '<c_num> - число операций вызова в нём\n'
     '<l_num> - число операций чтения в нём\n'
     '<s_num> - число операций записи в нём\n'
     '<loops> = <loop> | <loop>,<loops>\n'
     '<loop>  = <num>:<ovl>:<red>\n'
     '<num>   - номер цикла управляющего графа\n'
     '<ovl>   - признак накрученного цикла (0 или 1)\n'
     '<red>   - признак сводимого цикла (0 или 1)\n'
     '<(p)doms>  = <(p)dom_height>,<(p)dom_width>,<(p)dom_succs>\n'
     '<(p)dom_height> - высота дерева (пост)доминаторов\n'
     '<(p)dom_width>  - ширина дерева (пост)доминаторов\n'
     '<(p)dom_succs>  - максимальное ветвление вершин в дереве (пост)доминаторов',
     'format', None, '<procs>',
     TRAIN_PROC_CHARS
)

# Удаляются все накопленные данные для обучения
TRAIN_CLEAR = False
GL['clear'] = Global(
     'TRAIN_CLEAR', 'clear',
     'удаление всех накопленных данных для обучения',
     'bool', ['0', '1'], None,
     TRAIN_CLEAR
)

# Накапливать ли данные для обучения?
TRAIN_PURE = False
GL['pure'] = Global(
     'TRAIN_PURE', 'pure',
     'не накопливать данные для обучения',
     'bool', ['0', '1'], None,
     TRAIN_PURE
)

# Каталог, в котором расположены данные для обучения ИС
TRAIN_DATA_DIR = './train/data'
GL['tr_dir'] = Global(
     'TRAIN_DATA_DIR', 'tr_dir',
     'каталог с данными для обучения ИС',
     'path_to_dir', None, None,
     TRAIN_DATA_DIR
)

# Каталог, в котором сохранаяются обученные искусственные нейронные сети для каждого параметра
TRAIN_MODEL_DIR = '.'
GL['model_dir'] = Global(
     'TRAIN_MODEL_DIR', 'model_dir',
     'каталог c предобученными искусственными нейронными сетями',
     'path_to_dir', None, None,
     TRAIN_MODEL_DIR, 'train'
)

# Доля данных, выделяемая для обучения искусственной нейронной сети
TRAIN_DELTA = 0.5
GL['delta'] = Global(
     'TRAIN_DELTA', 'delta',
     'доля данных, выделяемая для обучения искусственной нейронной сети',
     'float', None, None,
     TRAIN_DELTA, 'train'
)

# Размер сетки для интерполяции данных
TRAIN_GRID = 100
GL['grid'] = Global(
     'TRAIN_GRID', 'grid',
     'размер сетки для интерполяции данных',
     'float', None, None,
     TRAIN_GRID, 'train'
)

# Метод интерполяции данных
TRAIN_INTERP = 'linear'
GL['interp'] = Global(
     'TRAIN_INTERP', 'interp',
     'метод интерполяции данных',
     'disc_str', ['linear', 'cubic'], None,
     TRAIN_INTERP, 'train'
)

#########################################################################################
# Подсчёт времени компиляции, исполнения и потребления памяти

# Путь до bash-скрипта для инициализации скрипта SCRIPT_RUN_CMP
SCRIPT_INIT_CMP = None
GL['init_cmp'] = Global(
     'SCRIPT_INIT_CMP', 'init_cmp',
     'bash-скрипт для инициализации скрипта SCRIPT_RUN_CMP. Имеет формат:\n'
     '  SCRIPT_INIT_CMP <dist_dir>\n'
     'где <dist_dir> - директория, в которой будет запущен скрипт SCRIPT_RUN_CMP и куда необходимо скопировать все необходимые для этого исходники',
     'path_to_file', None, None,
     SCRIPT_INIT_CMP
)

# Путь до bash-скрипта для запуска задач на компиляцию и/или исполнение
SCRIPT_RUN_CMP = None
GL['run_cmp'] = Global(
     'SCRIPT_RUN_CMP', 'run_cmp',
     'bash-скрипт для запуска задач на компиляцию и/или исполнение. Имеет формат:\n'
     '  SCRIPT_RUN_CMP <-comp|-exec|-stat> <-suite <pack_name>> [-run <test_name>] <-base|-peak> [-old|-new] [-opt <opt_list>] <-server <machine_name>>\n'
     'где -comp   - режим рапуска на компиляцию\n'
     '    -exec   - режим рапуска на исполнение\n'
     '    -stat   - режим рапуска на получение статистики\n'
     '    -suite  - выбор специфического бэнчмарка\n'
     '    -run    - выбор специфических задач\n'
     '    -base   - базовый режим запуска компилятора lcc\n'
     '    -peak   - пиковый режим запуска компилятора lcc\n'
     '    -old    - запуск OLD версии компилятора lcc\n'
     '    -old    - запуск NEW версии компилятора lcc\n'
     '    -opt    - параметры компилятора lcc\n'
     '    -server - машина, на которой следует произвести запуск\n'
     'Скрипт должен в конце своей работы выдать на экран:\n'
     '  время компиляции (в режиме -comp),\n'
     '  время исполнения (в режиме -exec),\n'
     '  максимальный объем памяти, затраченный компилятором lcc (в режиме -stat).\n'
     'Других сообщений на экран выводится не должно.',
     'path_to_file', None, None,
     SCRIPT_RUN_CMP
)

# Путь до скрипта, который запускает компиляцию спека, и возвращает время компиляции
SCRIPT_COMP = None
GL['comp_scr'] = Global(
     'SCRIPT_COMP', 'comp_scr',
     'скрипт, который запускает компиляцию задачи, и возвращает время компиляции',
     'path_to_file', None, None,
     SCRIPT_COMP
)

# Путь до скрипта, который запускает исполнение спека, и возвращает время исполнения
SCRIPT_EXEC = None
GL['exec_scr'] = Global(
     'SCRIPT_EXEC', 'exec_scr',
     'скрипт, который запускает исполнение задачи, и возвращает время исполнения',
     'path_to_file', None, None,
     SCRIPT_EXEC
)

# Путь до скрипта, который запускает компиляцию спека вместе со сбором статистики, и возвращает объем потребляемой памяти
SCRIPT_COMP_WITH_STAT = None
GL['stat_scr'] = Global(
     'SCRIPT_COMP_WITH_STAT', 'stat_scr',
     'скрипт, который запускает компиляцию задачи вместе со сбором статистики, и возвращает объем потребляемой памяти',
     'path_to_file', None, None,
     SCRIPT_COMP_WITH_STAT
)

#########################################################################################
# Модуль par

# Значения по-умолчанию для параметров компилятора lcc
PAR_DEFAULTS = ''
GL['par_defaults'] = Global(
     'PAR_DEFAULTS', 'par_defaults',
     'значения по-умолчанию для параметров компилятора lcc',
     'format', None, '<par_name>:<value> ... <par_name>:<value>',
     PAR_DEFAULTS, 'setup'
)

# Диапазоны значений параметров компилятора lcc
PAR_RANGES = ''
GL['par_ranges'] = Global(
     'PAR_RANGES', 'par_ranges',
     'диапазоны значений параметров компилятора lcc',
     'format', None, '<par_name>:<min>:<max> ... <par_name>:<min>:<max>',
     PAR_RANGES, 'setup'
)

#########################################################################################
# Модуль net

points_num = 5
GL['points_num'] = Global(
     'points_num', 'points_num',
     'задает число точек в сетке',
     'int', None, None,
     points_num, 'train'
)

#########################################################################################
# Модуль draw

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

GREAN_DOTS = False
