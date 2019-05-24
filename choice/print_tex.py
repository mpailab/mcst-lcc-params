#!/usr/bin/python
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

print get_globals_names()
exit()
my_gl_vars = []


outputdir = './doc/tex_patterns/all/'
for varname in get_globals_names():
    ofile = open(outputdir + varname + '.tex', 'w')
    #ofile = None
    print >> ofile, get_tex_pattern(varname)
