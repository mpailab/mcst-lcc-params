#!/usr/bin/python3
# -*- coding: utf-8 -*-
 
# Глобальные переменные

# External imports
import os

class IntsysError(Exception):
    pass

PARAMS = {
    'regn_max_proc_op_sem_size' : (int, 16000, (0,50000)),
    'regn_heur1' : (float, 0.037, (0.0,1.0)),
    'regn_heur2' : (float, 0.06, (0.0,1.0)),
    'regn_heur3' : (float, 0.03, (0.0,1.0)),
    'regn_heur4' : (float, 0.0, (0.0,1.0)),
    'regn_heur_bal1' : (float, 0.0, (0.0,1.0)),
    'regn_heur_bal2' : (float, 0.0, (0.0,1.0)),
    'regn_opers_limit' : (int, 2048, (0,5000)),
    'regn_prob_heur' : (float, 0.04, (0.0,1.0)),
    'regn_disb_heur' : (int, 9, (0,15)),
    'ifconv_merge_heur' : (float, 1.0, (0.0,2.0)),
    'ifconv_opers_num' : (int, 200, (0,500)),
    'ifconv_calls_num' : (int, 6, (0,10)),
    'disable_regions_nesting': (bool, True, (False,True)),
    'dcs_kill': (bool, False, (False,True)),
    'dcs_level': (int, 0, (0,4))
    }

NODE_TYPE = {
    "Simple" : 0,
    "If"     : 1,
    "Return" : 2,
    "Start"  : 3,
    "Stop"   : 4,
    "Switch" : 5,
    "Hyper"  : 6,
    "Jump"   : 7,
    "Tmp"    : 8
    }

def dir (line):
     line = line.strip('"')
     if not os.path.isdir(line):
          raise ValueError
     return os.path.abspath(line)

def path (line):
     from re import search, escape
     line = line.strip('"')
     path = os.path.normpath(line)
     if not search(r'[^A-Za-z0-9_\-' + escape(os.path.sep) + ']', path) is None:
          raise ValueError
     return os.path.abspath(line)

def file (line):
     line = line.strip('"')
     if not os.path.isfile(line):
          raise ValueError
     return os.path.abspath(line)

# Parse string of the format '<name>'
def name (line):
     line = line.strip('"')
     if line == '':
          raise ValueError
     if len(line.split()) > 1:
          raise ValueError
     return line

# Parse string of the format '<parname> [<parname>] [; <parname> [<parname>]]'
def strategy (line):
     line = line.strip('"')
     line = str(line)
     if line == '':
          raise ValueError
     lines = line.split(';')
     pars = []
     for l in lines:
          group = [x for x in l.split() if x in PARAMS]
          if not group:
               raise ValueError
          group.sort()
          pars.append(tuple(group))
     return pars

# Parse string of the format '<specname>[: <procname> [<procname>]] [, <specname>[: <procname> [<procname>]]]'
def specs (line):
     line = line.strip('"')
     if line == '':
          raise ValueError
     lines = line.split(',')
     specs = {}
     for l in lines:
          if l == '':
               raise ValueError
          spec = l.split(':')
          if len(spec) > 2:
               raise ValueError
          name = spec[0].strip()
          if name == '':
               raise ValueError
          if name in specs:
               print('Warning! There are several occurrences in the speclist for specname :', name)
               print('         Only the first occurrence of', name, 'will be used.')
               continue
          procs = None
          if len(spec) == 2:
               procs = spec[1].split()
               if not procs:
                    raise ValueError
               procs.sort()
          specs[name] = procs
     return specs

def node_type (line):
     if line in NODE_TYPE:
          raise ValueError
     return NODE_TYPE[line]

# Parse string of the format '<procs>', где
# '<procs> = <proc> | <proc> <procs>\n'
# '<proc>  = <weight>;<nodes>;<loops>;<doms>;<pdoms>\n'
# '<weight> - вес процедуры\n'
# '<nodes> = <node> | <node>,<nodes>\n'
# '<node>  = <num>:<type>:<cnt>:<o_num>:<c_num>:<l_num>:<s_num>\n'
# '<num>   - номер узла управляющего графа\n'
# '<type>  - его тип (одно из значений Simple, If, Return, Start, Stop, Switch, Hyper, Jump, Tmp)\n'
# '<o_num> - число всех операций в нём\n'
# '<c_num> - число операций вызова в нём\n'
# '<l_num> - число операций чтения в нём\n'
# '<s_num> - число операций записи в нём\n'
# '<loops> = <loop> | <loop>,<loops>\n'
# '<loop>  = <num>:<ovl>:<red>\n'
# '<num>   - номер цикла управляющего графа\n'
# '<ovl>   - признак накрученного цикла (0 или 1)\n'
# '<red>   - признак сводимого цикла (0 или 1)\n'
# '<(p)doms>  = <(p)dom_height>,<(p)dom_width>,<(p)dom_succs>\n'
# '<(p)dom_height> - высота дерева (пост)доминаторов\n'
# '<(p)dom_width>  - ширина дерева (пост)доминаторов\n'
# '<(p)dom_succs>  - максимальное ветвление вершин в дереве (пост)доминаторов'
def proc_chars (line):
     lines = line.strip('"').split()
     if not lines:
          raise ValueError
     procs = []
     for l in lines:
          proc = l.split(';')
          if len(proc) != 5 or any (x == '' for x in proc):
               raise ValueError
          weight = float(proc[0])
          nodes = []
          for node in proc[1].split(','):
               ps = node.split(':')
               if len(ps) != 7 or any (x == '' for x in ps):
                    raise ValueError
               nodes.append((int(ps[0]), node_type(ps[1]), float(ps[3]), int(ps[4]), int(ps[5]), int(ps[6]), int(ps[7])))
          loops = []
          for loop in proc[2].split(','):
               ps = loop.split(':')
               if len(ps) != 3 or any (x == '' for x in ps):
                    raise ValueError
               loops.append((int(ps[0]), bool(ps[1]), bool(ps[3])))
          doms = []
          for dom in proc[3].split(','):
               ps = dom.split(':')
               if len(ps) != 3 or any (x == '' for x in ps):
                    raise ValueError
               doms.append((int(ps[0]), int(ps[1]), int(ps[3])))
          pdoms = []
          for pdom in proc[3].split(','):
               ps = pdom.split(':')
               if len(ps) != 3 or any (x == '' for x in ps):
                    raise ValueError
               pdoms.append((int(ps[0]), int(ps[1]), int(ps[3])))
          procs.append((weight, nodes, loops, doms, pdoms))
     return procs

# Parse string of the format '<par_name>:<value> ... <par_name>:<value>'
def defaults (line, allpars = True):
     lines = line.strip('"').split()
     if not lines:
          raise ValueError
     pars = {x : PARAMS[x][1] for x in PARAMS} if allpars else {}
     for l in lines:
          d = l.split(':')
          if len(d) != 2 or any (x == '' for x in d) or not d[0] in PARAMS:
               raise ValueError
          pars[d[0]] = PARAMS[d[0]][0](d[1])
     return pars
 
def starts (line):
     return defaults(line, allpars = False)

# Parse string of the format '<par_name>:<min>:<max> ... <par_name>:<min>:<max>'
def ranges (line):
     lines = line.strip('"').split()
     if not lines:
          raise ValueError
     pars = {x : PARAMS[x][2] for x in PARAMS}
     for l in lines:
          d = l.split(':')
          if len(d) != 3 or any (x == '' for x in d) or not d[0] in PARAMS:
               raise ValueError
          pars[d[0]] = (PARAMS[d[0]][0](d[1]), PARAMS[d[0]][0](d[2]))
     return pars

# Режимы работы ИС
modes = {
    ''       : 'Основная группа параметров',
    'anneal' : 'Группа параметров для настройки метода имитации отжига',
    'stat'   : 'Группа параметров для обработки статистики задач/процедур',
    'train'  : 'Группа параметров для настроки обучение ИС',
    'func'   : 'Группа параметров для настроки оптимизируемого функционала',
    'find'   : 'Группа параметров для настроки поиска оптимальных значений параметров компилятора lcc',
    'script' : 'Группа параметров для запуска задач на компиляцию и исполнение',
    'setup'  : 'Установка значений по умолчанию параметров компилятора lcc'
    }

# Информационная структура глобальной переменной
class Global:
     def __init__ (self, name, param, help, type, values, format, parser, default, mode = ''):
          self.name    = name    # имя глобала
          self.param   = param   # имя параметра, соответствующего глобалу
          self.help    = help    # описание глобала
          self.type    = type    # тип глобала
          self.values  = values  # возможные значения глобала
          self.format  = format  # формат значения глобала
          self.parser  = parser
          self.default = default # значение по умолчанию
          assert(mode in modes)
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
     'disc', [0, 1, 2], None, int,
     UNEXEC_PROC_WEIGHT_SETUP, 'stat'
)

# Вес по-умолчанию, который присваевается компилируемой, но неисполняемой процедуре
DEFAULT_WEIGHT_FOR_PROC = 1.0
GL['w_default'] = Global(
     'DEFAULT_WEIGHT_FOR_PROC', 'w_default',
     'вес по-умолчанию, который присваивается компилируемой, но неисполняемой процедуре',
     'float', None, None, float,
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
     'disc', [0, 1, 2, 3], None, int,
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
     'disc', [0, 1], None, int,
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
     'disc', [0, 1, 2, 3], None, int,
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
     'disc', [0, 1, 2], None, int,
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
     'disc', [0, 1, 2], None, int,
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
     'disc', [0, 1], None, int,
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
     'path_to_dir', None, None, dir,
     PROC_WEIGHT_PATH, 'stat'
)

# Файл, в котором задаются веса спеков
# Используется, если TASK_WEIGHT_SETUP = 1
TASK_WEIGHT_PATH = None
GL['file_w_task'] = Global(
     'TASK_WEIGHT_PATH', 'file_w_task',
     'путь к файлу, из которого считываются веса задач',
     'path_to_file', None, None, file,
     TASK_WEIGHT_PATH, 'stat'
)

# Учитывать статистику компиляции неисполняемых процедур (т.е. процедур, для которых не заданы веса)? {0, 1}
USE_UNEXEC_PROCS_IN_STAT = False
GL['use_unexec'] = Global(
     'USE_UNEXEC_PROCS_IN_STAT', 'use_unexec',
     'обработка статистики компиляции неисполняемых процедур',
     'bool', None, None, None,
     USE_UNEXEC_PROCS_IN_STAT, 'stat'
)

# Каталог со статистикой компиляции спеков при значениях параметров оптимизирующих преобразований по-умолчанию
STAT_PATH = None
GL['stat'] = Global(
     'STAT_PATH', 'stat',
     'путь каталогу со статистикой компиляции, собранной при значениях параметров оптимизирующих преобразований по-умолчанию',
     'path_to_dir', None, None, dir,
     STAT_PATH, 'stat'
)

#########################################################################################
# Обработка статистики

# Учитывать при обработки статистики динамическое изменение числа операций в процедуре во время фазы regions? {0, 1}
DINUMIC_PROC_OPERS_NUM = False
GL['din_proc'] = Global(
     'DINUMIC_PROC_OPERS_NUM', 'din_proc',
     'учет динамического изменения числа операций в процедуре во время компиляции на фазе regions',
     'bool', None, None, None,
     DINUMIC_PROC_OPERS_NUM, 'stat'
)

# Учитывать при обработки статистики динамическое изменение числа операций в регионах процедуры во время фазы regions? {0, 1}
DINUMIC_REGN_OPERS_NUM = False
GL['din_regn'] = Global(
     'DINUMIC_REGN_OPERS_NUM', 'din_regn',
     'включает учет динамического изменения числа операций в регионах во время компиляции на фазе regions',
     'bool', None, None, None,
     DINUMIC_REGN_OPERS_NUM, 'stat'
)

#########################################################################################
# Фаза dcs

# Номер последнего существующего уровня оптимизации фазы dcs
MAX_DCS_LEVEL = 4
GL['max_dcs_level'] = Global(
     'MAX_DCS_LEVEL', 'max_dcs_level',
     'номер последнего существующего уровня оптимизации фазы dcs',
     'int', None, None, int,
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
     'float', None, None, float,
     DCS_KOEF_NODE_IMPOTANCE, 'anneal'
)
DCS_KOEF_EDGE_IMPOTANCE = 1.0
GL['dcs_edge'] = Global(
     'DCS_KOEF_EDGE_IMPOTANCE', 'dcs_edge',
     'коэффициент мертвых дуг в формуле полезности dcs-оптимизации',
     'float', None, None, float,
     DCS_KOEF_EDGE_IMPOTANCE, 'anneal'
)
DCS_KOEF_LOOP_IMPOTANCE = 1.0
GL['dcs_loop'] = Global(
     'DCS_KOEF_LOOP_IMPOTANCE', 'dcs_loop',
     'коэффициент мертвых циклов в формуле полезности dcs-оптимизации',
     'float', None, None, float,
     DCS_KOEF_LOOP_IMPOTANCE, 'anneal'
)

# Если полезность dcs оптимизации <= DSC_IMPOTANCE_LIMIT, то dcs оптимизация считается бесполезной
DSC_IMPOTANCE_LIMIT = 0.001
GL['dcs_limit'] = Global(
     'DSC_IMPOTANCE_LIMIT', 'dcs_limit',
     'порог для значений полезности dcs-оптимиизации',
     'float', None, None, float,
     DSC_IMPOTANCE_LIMIT, 'anneal'
)

#########################################################################################
# 

# Каталог, в котором хранятся логи запусков оптимизации методом имитации отжига
#RUN_LOGS_PATH = './logs'
#GL['logs'] = Global(
     #'RUN_LOGS_PATH', 'logs',
     #'каталог, в котором хранятся логи запусков',
     #'path_to_dir', None, None, dir,
     #RUN_LOGS_PATH
#)

# Предполагаемая процентная величина погрешности определения времени исполнения, компиляции, объема потребляемой памяти, и т.п.
#DEVIATION_PERCENT_OF_TcTeMemF = 0.01
#GL['inaccuracy'] = Global(
     #'DEVIATION_PERCENT_OF_TcTeMemF', 'inaccuracy',
     #'величина погрешности',
     #'float', ['(0, 1)'], None, float,
     #DEVIATION_PERCENT_OF_TcTeMemF
#)

#########################################################################################
# Сглаживание статистики

# Сглаживать статистику? {0, 1}
PURE_STAT = False
GL['pure_stat'] = Global(
     'PURE_STAT', 'pure_stat',
     'не использовать сглаживание распределений, получаемых по статистике работы компилятора lcc',
     'bool', None, None, None,
     PURE_STAT, 'stat'
)

# Чем меньше следующие коэффиценты, тем сильнее сглаживание
ERF_KOEF_FOR_CONTINUOUS_PAR = 20.0 # коэффициент сглаживания для вещественных параметров
GL['erf_cont'] = Global(
     'ERF_KOEF_FOR_CONTINUOUS_PAR', 'erf_cont',
     'коэффициент сглаживания распределений параметров оптимизирующих преобразований вещественного типа',
     'float', None, None, float,
     ERF_KOEF_FOR_CONTINUOUS_PAR, 'stat'
)
ERF_KOEF_FOR_DISCRETE_PAR = 0.5 # коэффициент сглаживания для целичисленных параметров
GL['erf_disc'] = Global(
     'ERF_KOEF_FOR_DISCRETE_PAR', 'erf_disc',
     'коэффициент сглаживания распределений параметров оптимизирующих преобразований целочисленного типа',
     'float', None, None, float,
     ERF_KOEF_FOR_DISCRETE_PAR, 'stat'
)

# Чем ниже следующие параметры, тем качественнее сглаживание
# Уменьшение следующих параметров может очень существенно замедлить сглаживание!
# Доля исходного веса, которая не будет участвовать в сглаживании
ZERO_LIMIT_FOR_ERF = 0.01
GL['erf_limit'] = Global(
     'ZERO_LIMIT_FOR_ERF', 'erf_limit',
     'доля для сглаживаемых весов, которая не будет участвовать в сглаживании',
     'float', ['(0, 1)'], None, float,
     ZERO_LIMIT_FOR_ERF, 'stat'
)

# Порог для абсолютных значений весов, веса ниже которого не будут сглаживаться
ZERO_LIMIT_FOR_WEIGHT = 0.001
GL['weight_limit'] = Global(
     'ZERO_LIMIT_FOR_WEIGHT', 'weight_limit',
     'порог для абсолютных значений весов, веса ниже которого не сглаживаются',
     'float', ['(0, 1)'], None, float,
     ZERO_LIMIT_FOR_WEIGHT, 'stat'
)

#########################################################################################
# Модуль optimize

# Значения параметров компилятора lcc, в окрестности которых осуществляется поиск
# Если не заданы, то поиск осуществляется в окрестности значений параметров по-умолчанию
PAR_START = {}
GL['par_start'] = Global(
     'PAR_START', 'par_start',
     'значения параметров компилятора lcc, в окрестности которых осуществляется поиск',
     'format', None, '<par_name>:<value> ... <par_name>:<value>', starts,
     PAR_START, 'anneal'
)

# Использовать собранную статистику компилятора LCC в не зависимости от значений параметров оптимизирующих преобразований? {0, 1}
INHERIT_STAT = False
GL['inherit'] = Global(
     'INHERIT_STAT', 'inherit',
     'всегда использовать предварительно собранную статистику компилятора LCC',
     'bool', None, None, None,
     INHERIT_STAT, 'anneal'
)

# Ограничение на использование памяти
# Если True, то в оперативной памяти не сохраняются распределения весов для каждого нового набора параметров
MEM_RESTRICTION = False
GL['mem_restr'] = Global(
     'MEM_RESTRICTION', 'mem_restr',
     'ограничение на использование памяти',
     'bool', None, None, None,
     MEM_RESTRICTION, 'anneal'
)

# Начальное значение температуры: (0, 1]
START_TEMPERATURE = 0.5
GL['start_temp'] = Global(
     'START_TEMPERATURE', 'start_temp',
     'начальное значение температуры в методе имитации отжига',
     'float', ['(0, 1]'], None, float,
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
     'disc', [0, 1, 2], None, int,
     TEMPERATURE_LAW_TYPE, 'anneal'
)

# значение alpha
ALPHA_IN_TEPMERATURE_LAW = 0.7
GL['alpha'] = Global(
     'ALPHA_IN_TEPMERATURE_LAW', 'alpha',
     'значение параметра alpha в законе убывания температуры для метода имитации отжига',
     'float', ['(0, 1)'], None, float,
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
     'disc', [0, 1, 2, 3], None, int,
     DISTRIBUTION_LAW_TYPE, 'anneal'
)

# Учитывать зависимоти параметров друг от друга? {0, 1}
# Параметр par1 зависит от par2, если при определенных значениях параметра par2,
# значение par1 никак не влияют на работу компилятора LCC.
# Если опция возведена, то зависимости параметров учитываются при прогнозировании
# насколько существенно может повлиять на работу компилятора изменение значений параметров
UNRELATED_PARAMS = False
GL['unrelated'] = Global(
     'UNRELATED_PARAMS', 'unrelated',
     'считать параметры компилятора lcc независимыми друг от друга',
     'bool', None, None, None,
     UNRELATED_PARAMS, 'anneal'
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
     'float', None, None, float,
     TIME_EXEC_IMPOTANCE, 'func'
)
TIME_COMP_IMPOTANCE = 1.0
GL['F_comp'] = Global(
     'TIME_COMP_IMPOTANCE', 'F_comp',
     'значение множителя при члене относительного увеличении времени компиляции в минимизируемом функционале',
     'float', None, None, float,
     TIME_COMP_IMPOTANCE, 'func'
)
MEMORY_IMPOTANCE = 1.0
GL['F_mem'] = Global(
     'MEMORY_IMPOTANCE', 'F_mem',
     'значение множителя при члене относительного увеличении объема потребляемой компилятором памяти в минимизируемом функционале',
     'float', None, None, float,
     MEMORY_IMPOTANCE, 'func'
)

# Допустимый процент увеличения времени компиляции
COMP_TIME_INCREASE_ALLOWABLE_PERCENT = 0.25
GL['comp_limit'] = Global(
     'COMP_TIME_INCREASE_ALLOWABLE_PERCENT', 'comp_limit',
     'задает допустимое относительное замедление времени компиляции',
     'float', None, None, float,
     COMP_TIME_INCREASE_ALLOWABLE_PERCENT, 'func'
)

# Допустимый процент увеличения времени исполнения
EXEC_TIME_INCREASE_ALLOWABLE_PERCENT = 0.05
GL['exec_limit'] = Global(
     'EXEC_TIME_INCREASE_ALLOWABLE_PERCENT', 'exec_limit',
     'задает допустимое относительное замедление времени исполнения',
     'float', None, None, float,
     EXEC_TIME_INCREASE_ALLOWABLE_PERCENT, 'func'
)

# Допустимый процент увеличения объема потребляемой памяти
MEMORY_INCREASE_ALLOWABLE_PERCENT = 0.50
GL['mem_limit'] = Global(
     'MEMORY_INCREASE_ALLOWABLE_PERCENT', 'mem_limit',
     'задает допустимое относительное увеличение объема памяти, потребляемой при компиляции',
     'float', None, None, float,
     MEMORY_INCREASE_ALLOWABLE_PERCENT, 'func'
)

# Число итераций метода отжига
MAX_NUMBER_ITERATIONS = 10
GL['iter_num'] = Global(
     'MAX_NUMBER_ITERATIONS', 'iter_num',
     'число шагов применения метода имитации отжига',
     'int', None, None, int,
     MAX_NUMBER_ITERATIONS, 'anneal'
)

# Максимальное число попыток выбора новых значений параметров для каждой итерации метода отжига
MAX_NUMBER_OF_ATTEMPTS_FOR_ITERATION = 10
GL['attempts_num'] = Global(
     'MAX_NUMBER_OF_ATTEMPTS_FOR_ITERATION', 'attempts_num',
     'максимальное число попыток выбора очередного кандидата для параметров оптимизирующих преобразований на каждом шаге применения метода имитации отжига',
     'int', None, None, int,
     MAX_NUMBER_OF_ATTEMPTS_FOR_ITERATION, 'anneal'
)

# Уменьшать значение температуры после итераций, на которых не был осуществлен переход к лучшему значению? {0, 1}
TEMP_MODE = 0
GL['temp_mode'] = Global(
     'TEMP_MODE', 'temp_mode',
     'режим изменения температуры после неудачных шагов применения метода имитации отжига: 0 - уменьшать температуру, 1 - сохранять той же',
     'disc', [0, 1], None, int,
     TEMP_MODE, 'anneal'
)

#########################################################################################
# Параметры запуска ИС

# Стратегия
# Синтаксис:
#   <стратегия>         ::= <группа параметров> | <стратегия>; <группа параметров>
#   <группа параметров> ::= <параметр> | <группа параметров> <параметр>
OPTIMIZATION_STRATEGY = []
GL['strategy'] = Global(
     'OPTIMIZATION_STRATEGY', 'strategy',
     'стратегия оптимизации, согласно с которой ИС осуществляет подборку параметров оптимизирующих преобразований',
     'format', None, '<parname> [<parname>] [; <parname> [<parname>]]', strategy,
     OPTIMIZATION_STRATEGY
)

# Последовательная оптимизация
SEQ_OPTIMIZATION_WITH_STRATEGY = False
GL['seq'] = Global(
     'SEQ_OPTIMIZATION_WITH_STRATEGY', 'seq',
     'последовательная оптимизация групп параметров, определенных стратегией (задается параметром strategy)',
     'bool', None, None, None,
     SEQ_OPTIMIZATION_WITH_STRATEGY, 'anneal'
)


# Список оптимизируемых задач
# Синтаксис:
#   <список задач>    ::= <задача> | <список задач>, <задача>
#   <задача>          ::= <имя задачи> | <имя задачи> : <список процедур>
#   <список процедур> ::= <процедура> | <список процедур> <процедура>
SPECS = {}
GL['specs'] = Global(
     'SPECS', 'specs',
     'список задач, для которых ИС должна осуществлять подборку параметров оптимизирующих преобразований',
     'format', None, '<specname>[: <procname> [<procname>]] [, <specname>[: <procname> [<procname>]]]', specs,
     SPECS
)

# Каталог, в котором формируются выходные файлы
#OUTPUTDIR = "."
#GL['output'] = Global(
     #'OUTPUTDIR', 'output',
     #'каталог, в котором ИС формирует свои выходные файлы',
     #'path_to_dir', None, None, dir,
     #OUTPUTDIR
#)

# Задает степень подробности вывода на экран во время работы ИС.
VERBOSE = 0
GL['verbose'] = Global(
     'VERBOSE', 'verbose',
     'степень подробности вывода информации на экран во время работы ИС',
     'disc', [0, 1, 2, 3], None, int,
     VERBOSE
)

# Перезаписывать выходные файлы? {0, 1}
# 0 -> имена для выходных файлов будут подбираться таким образом, чтобы не перезаписывать выходные файлы от предыдущих запусков
# 1 -> выходные файлы от предыдущих запусков могут быть перезаписаны
#ALLOW_REWRITE_OUTPUT_FILES = False
#GL['rewrite'] = Global(
     #'ALLOW_REWRITE_OUTPUT_FILES', 'rewrite',
     #'режим перезаписи выходных файлов',
     #'bool', None, None, None,
     #ALLOW_REWRITE_OUTPUT_FILES
#)


#########################################################################################
# Модуль обучения ИС

# Характеистики процедур, для которых необходимо найти оптимальные значения параметров
TRAIN_PROC_CHARS = []
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
     'format', None, '<procs>', proc_chars,
     TRAIN_PROC_CHARS, 'find'
)

# Каталог с статистикой процедур, для которых необходимо найти оптимальные значения параметров
TRAIN_PROC_CHARS_DIR = None
GL['proc_chars_dir'] = Global(
     'TRAIN_PROC_CHARS_DIR', 'proc_chars_dir',
     'каталог со статистикой процедур, для которых необходимо найти оптимальные значения параметров компилятора lcc',
     'path_to_dir', None, None, dir,
     TRAIN_PROC_CHARS_DIR, 'find'
)

# Файл с весами процедур, для которых необходимо найти оптимальные значения параметров компилятора lcc
TRAIN_PROC_WEIGHTS = None
GL['proc_weights'] = Global(
     'TRAIN_PROC_WEIGHTS', 'proc_weights',
     'файл с весами процедур, для которых необходимо найти оптимальные значения параметров компилятора lcc',
     'path_to_file', None, None, file,
     TRAIN_PROC_WEIGHTS, 'find'
)

# Удаляются все накопленные данные для обучения
TRAIN_CLEAR = False
GL['clear'] = Global(
     'TRAIN_CLEAR', 'clear',
     'удаление всех накопленных данных для обучения',
     'bool', None, None, None,
     TRAIN_CLEAR, 'train'
)

# Накапливать ли данные для обучения?
TRAIN_PURE = False
GL['pure'] = Global(
     'TRAIN_PURE', 'pure',
     'не накапливать данные для обучения',
     'bool', None, None, None,
     TRAIN_PURE, 'train'
)

# Каталог, в котором расположены данные для обучения ИС
TRAIN_DATA_DIR = None
GL['tr_dir'] = Global(
     'TRAIN_DATA_DIR', 'tr_dir',
     'каталог с данными для обучения ИС',
     'path_to_dir', None, None, path,
     TRAIN_DATA_DIR, 'train'
)

# Каталог, в котором сохранаяются обученные искусственные нейронные сети для каждого параметра
TRAIN_MODEL_DIR = None
GL['model_dir'] = Global(
     'TRAIN_MODEL_DIR', 'model_dir',
     'каталог c предобученными искусственными нейронными сетями',
     'path_to_dir', None, None, path,
     TRAIN_MODEL_DIR, 'train'
)

# Доля данных, выделяемая для обучения искусственной нейронной сети
TRAIN_DELTA = 0.5
GL['delta'] = Global(
     'TRAIN_DELTA', 'delta',
     'доля данных, выделяемая для обучения искусственной нейронной сети',
     'float', None, None, float,
     TRAIN_DELTA, 'train'
)

# Число попыток для обучения модели искусственной нейронной сети
TRAIN_STEPS = 5
GL['tr_steps'] = Global(
     'TRAIN_STEPS', 'tr_steps',
     'число попыток для обучения модели искусственной нейронной сети',
     'int', None, None, int,
     TRAIN_STEPS, 'train'
)

# Число эпох обучения модели искусственной нейронной сети
TRAIN_EPOCHS = 100
GL['epochs'] = Global(
     'TRAIN_EPOCHS', 'epochs',
     'число эпох обучения модели искусственной нейронной сети',
     'int', None, None, int,
     TRAIN_EPOCHS, 'train'
)

# Размер пакета данных в обучении модели искусственной нейронной сети
TRAIN_BATCH = 100
GL['batch'] = Global(
     'TRAIN_BATCH', 'batch',
     'размер пакета данных в обучении модели искусственной нейронной сети',
     'int', None, None, int,
     TRAIN_BATCH, 'train'
)

# Размер сетки для интерполяции данных
TRAIN_GRID = 100
GL['train_grid'] = Global(
     'TRAIN_GRID', 'train_grid',
     'размер сетки для интерполяции данных',
     'int', None, None, int,
     TRAIN_GRID, 'train'
)

COLLECT_GRID = 5
GL['collect_grid'] = Global(
     'COLLECT_GRID', 'collect_grid',
     'размер сетки для получения данных',
     'int', None, None, int,
     COLLECT_GRID, 'train'
)

# Метод интерполяции данных
TRAIN_INTERP = 'linear'
GL['interp'] = Global(
     'TRAIN_INTERP', 'interp',
     'метод интерполяции данных:\n'
     #' nearest   - значение ближайшей точки из выборки (доступен для любой группы параметров)\n'
     ' linear    - интерполяция линейными сплайнами (доступен для любой группы параметров)\n'
     ' quadratic - интерполяция квадратичными сплайнами (доступен для групп из одного параметра)\n'
     ' cubic     - интерполяция кубическими сплайнами (доступен для групп из одного и двух параметров)\n',
     'disc_str', ['linear', 'quadratic', 'cubic'], None, name,
     TRAIN_INTERP, 'train'
)

#########################################################################################
# Подсчёт времени компиляции, исполнения и потребления памяти

# Путь до bash-скрипта для инициализации скрипта SCRIPT_CMP_RUN
SCRIPT_CMP_INIT = None
GL['cmp_init'] = Global(
     'SCRIPT_CMP_INIT', 'cmp_init',
     'bash-скрипт для инициализации скрипта cmp_run. Имеет формат:\n'
     '  cmp_init <dist_dir>\n'
     'где <dist_dir> - директория, в которой будет запущен скрипт cmp_run и куда необходимо скопировать все необходимые для этого исходники',
     'path_to_file', None, None, file,
     SCRIPT_CMP_INIT, 'script'
)

# Путь до bash-скрипта для запуска задач на компиляцию и/или исполнение
SCRIPT_CMP_RUN = None
GL['cmp_run'] = Global(
     'SCRIPT_CMP_RUN', 'cmp_run',
     'bash-скрипт для запуска задач на компиляцию и/или исполнение. Имеет формат:\n'
     '  cmp_run <-comp|-exec|-stat> -suite <pack_name> -spec <test_name> <-base|-peak> -opt <opt_list> -dir <path> -server <machine_name> -prof <profile>\n'
     'где -comp   - режим запуска на компиляцию\n'
     '    -exec   - режим запуска на исполнение\n'
     '    -stat   - режим запуска на получение статистики\n'
     '    -suite  - выбор специфического бэнчмарка\n'
     '    -spec   - выбор специфических задач\n'
     '    -base   - базовый режим запуска компилятора lcc\n'
     '    -peak   - пиковый режим запуска компилятора lcc\n'
     '    -opt    - параметры компилятора lcc\n'
     '    -dir    - директория, в которой сохраняется статистика\n'
     '    -server - машина, на которой следует произвести запуск\n'
     '    -prof   - директория, в которой сохраняются профили исполняемых процедур.'
     ' Профиль задачи <test_name> сохраняется в файле <test_name>.txt и имеет формат [<proc_name> <number>\\n],'
     ' где <number> - среднее арифметическое числа вызовов процедуры <proc_name> по врем запускам задачи <test_name> на исполнение\n'
     'Скрипт должен в конце своей работы выдать на экран:\n'
     '  время компиляции (в режиме -comp),\n'
     '  время исполнения (в режиме -exec),\n'
     '  максимальный объем памяти, затраченный компилятором lcc (в режиме -stat).\n'
     'Других сообщений на экран выводится не должно.',
     'path_to_file', None, None, file,
     SCRIPT_CMP_RUN, 'script'
)

# Режимы запуска задач на компиляцию/исполнение
CMP_MODES = {'comp':1, 'exec':1, 'stat':1}

# Выбор специфического бэнчмарка
CMP_SUITE = None
GL['cmp_suite'] = Global(
     'CMP_SUITE', 'cmp_suite',
     'выбор специфического бэнчмарка (значение параметра определяется внешним скриптом SCRIPT_RUN_CMP)',
     'format', None, '<pack_name>', name,
     CMP_SUITE, 'script'
)

# Каталог, в который собирается статистика компиляции спеков во время работы ИС
DINUMIC_STAT_PATH = None
GL['cmp_stat'] = Global(
     'DINUMIC_STAT_PATH', 'cmp_stat',
     'директория, в которую внешний скрипт сохраняет статистику',
     'path_to_dir', None, None, path,
     DINUMIC_STAT_PATH, 'script'
)

# Режим запуска задач на компиляцию
COMP_MODE = 'base'
GL['comp_mode'] = Global(
     'COMP_MODE', 'comp_mode',
     'режим запуска задач на компиляцию',
     'disc_str', ['base', 'peak'], None, name,
     COMP_MODE, 'script'
)

# Машина, на которой следует компилировать задачи
COMP_SERVER = None
GL['comp_srv'] = Global(
     'COMP_SERVER', 'comp_srv',
     'машина, на которой следует компилировать задачи',
     'format', None, '<machine_name>', name,
     COMP_SERVER, 'script'
)

# Машина, на которой следует исполнять задачи
EXEC_SERVER = None
GL['exec_srv'] = Global(
     'EXEC_SERVER', 'exec_srv',
     'машина, на которой следует исполнять задачи',
     'format', None, '<machine_name>', name,
     EXEC_SERVER, 'script'
)

#########################################################################################
# Модуль par

# Значения по-умолчанию для параметров компилятора lcc
PAR_DEFAULTS = {x : PARAMS[x][1] for x in PARAMS}
GL['par_defaults'] = Global(
     'PAR_DEFAULTS', 'par_defaults',
     'значения по-умолчанию для параметров компилятора lcc',
     'format', None, '<par_name>:<value> ... <par_name>:<value>', defaults,
     PAR_DEFAULTS, 'setup'
)

# Диапазоны значений параметров компилятора lcc
PAR_RANGES = {x : PARAMS[x][2] for x in PARAMS}
GL['par_ranges'] = Global(
     'PAR_RANGES', 'par_ranges',
     'диапазоны значений параметров компилятора lcc',
     'format', None, '<par_name>:<min>:<max> ... <par_name>:<min>:<max>', ranges,
     PAR_RANGES, 'setup'
)
