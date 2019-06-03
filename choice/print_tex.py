#!/usr/bin/python3
# -*- coding: utf-8 -*-

import global_vars as gl

def get_globals_names(types = None):
    """ Получить имена всех глобальных переменных проекта, [тип данных которых находится среди types]
    """
    def filterfunc(objname):
        if type(gl.__dict__[objname]) in types:
            return True
        else:
            return False
        
    result = filter(lambda x: x[0] != '_', gl.__dict__.keys()) # игнорируем переменные, которые начинаются с символа '_'
    if types != None:
        return filter(filterfunc, result)
    else:
        return result

def gtype(varname):
    return type(gl.__dict__[varname]) # получить тип переменной varname {bool, int, float, str}
def ptype(t):
    if t == bool:
        return 'Булевый (0/1)'
    elif t == int:
        return 'Целочисленный'
    elif t == float:
        return 'Вещественный'
    else:
        return ''

def get_tex_pattern(varname):
    pvarname = varname.replace('_', '\\_')
    t = gtype(varname)
    val = gl.__dict__[varname]
    if t == bool:
        val = int(val)
    res = r"""\subsection*{}
\addcontentsline{toc}{subsection}{""" + pvarname + r"""}
\subsection*{""" + pvarname + r"""}
\subsubsection*{Тип параметра}
""" + ptype(t) + r"""
\subsubsection*{По умолчанию}

По-умолчанию значение этого параметра равно """ + str(val).replace('_', '\\_') + r"""
\subsubsection*{Описание}


\newpage
"""
    return res

gnames = """
\input{SPECS}
\input{SYNCHRONOUS_OPTIMIZATION_FOR_SPECS}
\input{SEQ_OPTIMIZATION_WITH_STRATEGY}
\input{OPTIMIZATION_STRATEGY}
\input{GAIN_STAT_ON_EVERY_OPTIMIZATION_STEP}
\input{START_TEMPERATURE}
\input{TEMPERATURE_LAW_TYPE}
\input{ALPHA_IN_TEPMERATURE_LAW}
\input{DISTRIBUTION_LAW_TYPE}
\input{USE_RELATIONS_OF_PARAMETORS}
\input{TIME_EXEC_IMPOTANCE}
\input{TIME_COMP_IMPOTANCE}
\input{MEMORY_IMPOTANCE}
\input{COMP_TIME_INCREASE_ALLOWABLE_PERCENT}
\input{EXEC_TIME_INCREASE_ALLOWABLE_PERCENT}
\input{MEMORY_INCREASE_ALLOWABLE_PERCENT}
\input{MAX_NUMBER_ITERATIONS}
\input{MAX_NUMBER_OF_ATTEMPTS_FOR_ITERATION}
\input{DECREASE_TEMPERATURE_BEFORE_UNFORTUNATE_ITERATIONS}
\input{MAX_DCS_LEVEL}
\input{DCS_KOEF_LOOP_IMPOTANCE}
\input{DCS_KOEF_EDGE_IMPOTANCE}
\input{DCS_KOEF_NODE_IMPOTANCE}
\input{DSC_IMPOTANCE_LIMIT}
\input{SMOOTH_STAT}
\input{ERF_KOEF_FOR_DISCRETE_PAR}
\input{ERF_KOEF_FOR_CONTINUOUS_PAR}
\input{ZERO_LIMIT_FOR_ERF}
\input{ZERO_LIMIT_FOR_WEIGHT}
\input{TASK_WEIGHT_SETUP}
\input{PROC_WEIGHT_SETUP}
\input{UNEXEC_PROC_WEIGHT_SETUP}
\input{DEFAULT_WEIGHT_FOR_PROC}
\input{REGN_WEIGHT_SETUP}
\input{NODE_WEIGHT_SETUP}
\input{ICV_REGN_WEIGHT_SETUP}
\input{SECT_WEIGHT_SETUP}
\input{USE_UNEXEC_PROCS_IN_STAT}
\input{DINUMIC_REGN_OPERS_NUM}
\input{DINUMIC_PROC_OPERS_NUM}
""".split('\\input{')[1:]
gnames = map(lambda x: x[:-2], gnames)

gnames_plus = ['TASK_WEIGHT_PATH', 'STAT_PATH', 'DINUMIC_STAT_PATH', 'PROC_WEIGHT_PATH', 'PAR_DISTRIBUTION_DATABASE', 'OUTPUTDIR', 'ALLOW_REWRITE_OUTPUT_FILES']

def print_brief_pars_desc(gnames, output = None):
    rdir = './doc/global describtion/'
    #print("\\begin{itemize}",file=output)
    for var in gnames:
        rfile = open(rdir + var + '.tex', 'r')
        pvar = var.replace('_', '\\_')
        text = rfile.read() 
        desc = text.split('\\subsection*{' + pvar + '}')[1].split('\\subsubsection*{Тип параметра}')[0].strip()
        ptype = text.split('\\subsubsection*{Тип параметра}')[1].split('\\subsubsection*{По умолчанию}')[0].strip()
        print('\\item', pvar, '\\\\', file = output)
        if ptype[-1] == '.':
            dot = ''
        else:
            dot = '.'
        print('Тип:', ptype[0].lower() + ptype[1:] + dot, file = output)
        print(desc, file = output)
        rfile.close()
    #print("\\end{itemize}",file=output)

def print_python_dict(gnames, tab = '    '):
    rdir = './doc/global describtion/'
    #print("\\begin{itemize}",file=output)
    i = 0
    for var in gnames:
        rfile = open(rdir + var + '.tex', 'r')
        pvar = var.replace('_', '\\_')
        text = rfile.read() 
        desc = text.split('\\subsection*{' + pvar + '}')[1].split('\\subsubsection*{Тип параметра}')[0].strip().replace('\n', ' ')
        ptype = text.split('\\subsubsection*{Тип параметра}')[1].split('\\subsubsection*{По умолчанию}')[0].strip()
        
        def without_dot(word):
            if word[-1] == '.':
                return word[:-1]
            else:
                return word
        def default_val(var):
            val = gl.__dict__[var]
            if type(val) != bool:
                return 'gl.__dict__[\'' + var + '\']'
            else:
                return 'int(gl.__dict__[\'' + var + '\'])'
        i += 1
        def values(var, ptype):
            val = gl.__dict__[var]
            tmp = without_dot(ptype).replace('$', '').split(':')
            if type(val) == bool:
                return "['0', '1']"
            elif len(tmp) == 2 and i >= 6:
                if type(val) == float:
                    return str([str(tmp[-1]).strip()])
                else:
                    return str(list(map(lambda x: x.strip(),  tmp[-1].split(','))))
            else:
                return 'None'
        
        tab2 = tab * 2
        print(tab + '\'' + str(i) + '\'', ': (\'' + var + '\'', end=',\n')
        print(tab2 + '\'' + without_dot(desc).lower() + '\'', end=',\n')
        print(tab2 + '\'' + ptype.lower() + '\'', end=', ')
        print(values(var, ptype), end=', ') # возможные значения
        print('None', end=',\n') # формат
        print(tab2 + default_val(var), end = ' ') # значение по-умолчанию
        print('),')
        print()
        rfile.close()


def get_globals_names(types = None):
    """ Получить имена всех глобальных переменных проекта, [тип данных которых находится среди types]
    """
    def filterfunc(objname):
        if type(gl.__dict__[objname]) in types:
            return True
        else:
            return False
        
    result = [x for x in gl.__dict__.keys() if x[0] != '_'] # игнорируем переменные, которые начинаются с символа '_'
    if types != None:
        return list(filter(filterfunc, result))
    else:
        return result

print_python_dict(list(gnames) + gnames_plus)
