#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
содержит характеристики параметров оптимизации компилятора LCC (фазы regions и if_conv)

Параметры фазы regions:
- regn_max_proc_op_sem_size,
- regn_opers_limit,
- regn_heur1,
- regn_heur2,
- regn_heur3,
- regn_heur4,
- regn_disb_heur,
- regn_heur_bal1,
- regn_heur_bal2,
- regn_prob_heur,
- disable_regions_nesting.

Параметры фазы if_conv:
- ifconv_opers_num,
- ifconv_calls_num,
- ifconv_merge_heur.

Параметры фазы dcs:
- dcs_kill,
- dcs_level.

Словарь val_type: параметр -> тип значения (int, float, bool)

Словарь default_value: параметр -> значение по-умолчанию

Список doub_kind содержит параметры фазы regions, значения которых не оказывают влияния на работу компилятора LCC при условии,
что запрещено дублирование узлов процедуры.

Список reg_unb содержит параметры фазы regions, которые отвечают за обработку несбалансированных схождений.

Список reg_depend_seq содержит параметры фазы regions, упорядоченные таким образом, что параметр par1 встречается в списке раньше чем par2
тогда и только тогда, когда par2 зависит от par1. Параметр par2 зависит от par1 (par1 может блокировать par2),
если при некоторых значениях параметра par1 параметр par2 не влияет на работу компилятора LCC.

Список reg_extend_regn_list состоит из параметров фазы regions, которые могут быть блокированы параметром regn_opers_limit.
По факту reg_extend_regn_list совпадает с reg_depend_seq.

Список reg_seq есть [regn_max_proc_op_sem_size, regn_opers_limit] + reg_depend_seq
Список req_seq содержит все параметры фазы regions.
Внутри списка reg_depend_seq параметр par1 встречается раньше чем par2 тогда и только тогда, когда par2 зависит от par1.
Список параметров из reg_depend_seq, которые зависят от regn_max_proc_op_sem_size, есть doub_kind.
Список параметров из reg_depend_seq, которые зависят от regn_opers_limit, есть reg_extend_regn_list.

Список icv_seq содержит все параметры фазы if_conv, упорядоченные таким образом,
что параметр par1 встречается раньше чем par2 тогда и только тогда, когда par2 зависит от par1.

Словарь index_in_reg_seq: параметр -> индекс в списке req_seq
Словарь index_in_icv_seq: параметр -> индекс в списке icv_seq

Каждый параметр фаз regions и if_conv определяет условие, невыполнение которого означает блокировку работы зависящих от него параметров.
Каждое такое условие имеет вид less_eq(x, pv), less(x, pv), gr_eq(x, pv), gr(x, pv),
где pv --- значение параметра, а x --- значение характеристики процедуры (региона, узла), отвечающей параметру.
Словарь cond задает cоответсвтие: параметр -> условие

'''

# External imports
import sys
from functools import reduce

# Подключаем модуль, хранящий значения параметров интеллектуальной системы
import options as gl

val_type = {
    'regn_max_proc_op_sem_size' : int,
    'regn_heur1' : float,
    'regn_heur2' : float,
    'regn_heur3' : float,
    'regn_heur4' : float,
    'regn_heur_bal1' : float,
    'regn_heur_bal2' : float,
    'regn_opers_limit' : int,
    'regn_prob_heur' : float,
    'regn_disb_heur' : int,
    'ifconv_merge_heur' : float,
    'ifconv_opers_num' : int,
    'ifconv_calls_num' : int,
    'disable_regions_nesting': bool,
    'dcs_kill': bool,
    'dcs_level': int
    }
    
_defaults = {
    'regn_max_proc_op_sem_size' : 16000,
    'regn_heur1' : 0.037,
    'regn_heur2' : 0.06,
    'regn_heur3' : 0.03,
    'regn_heur4' : 0.0,
    'regn_heur_bal1' : 0.0,
    'regn_heur_bal2' : 0.0,
    'regn_opers_limit' : 2048,
    'regn_prob_heur' : 0.04,
    'regn_disb_heur' : 9,
    'ifconv_merge_heur' : 1.0,
    'ifconv_opers_num' : 200,
    'ifconv_calls_num' : 6,
    'disable_regions_nesting' : True,
    'dcs_kill': False,
    'dcs_level': 0
    }

def set_defaults ():
    res = _defaults
    for pv in gl.PAR_DEFAULTS.split():
        l = pv.split(':')
        res[l[0]] = val_type[l[0]](l[1])
    return res

default_value = set_defaults()
    
_ranges = {
    'regn_max_proc_op_sem_size' : (0,50000),
    'regn_heur1' : (0.0,1.0),
    'regn_heur2' : (0.0,1.0),
    'regn_heur3' : (0.0,1.0),
    'regn_heur4' : (0.0,1.0),
    'regn_heur_bal1' : (0.0,1.0),
    'regn_heur_bal2' : (0.0,1.0),
    'regn_opers_limit' : (0,5000),
    'regn_prob_heur' : (0.0,1.0),
    'regn_disb_heur' : (0,15),
    'ifconv_merge_heur' : (0.0,2.0),
    'ifconv_opers_num' : (0,500),
    'ifconv_calls_num' : (0,10),
    'disable_regions_nesting' : (False,True),
    'dcs_kill': (False,True),
    'dcs_level': (0,4)
    }

def set_ranges ():
    res = _ranges
    for pr in gl.PAR_RANGES.split():
        l = pr.split(':')
        res[l[0]] = (val_type[l[0]](l[1]), val_type[l[0]](l[2]))
    return res

ranges = set_ranges()

# список параметров, связанных с дублированием узлов
doub_kind = [
    'disable_regions_nesting',
    'regn_heur2',
    'regn_heur3',
    'regn_heur4',
    ]
# при некоторых значениях параметра regn_max_proc_op_sem_size
# параметры из списка doub_kind не влияют на работу компилятора LCC.

# параметры, связанные с несбалансированными схождениями
reg_unb = [
    'regn_disb_heur',
    'regn_heur_bal1',
    'regn_heur_bal2',
    'regn_prob_heur'
    ]
# последовательность, составленная из некоторых параметров фазы regions (if_conv), упорядоченная таким образом, что
# par1 предшествует par2 :=
# при некоторых значениях параметра par1 параметр par2 не влияет на работу компилятора LCC;
# в этом случае говорим, что par2 зависит от par1, или par1 может блокировать par2.
reg_depend_seq = [
    'regn_heur1',
    'regn_heur2',
    'regn_heur3',
    'regn_heur4'
    ] + reg_unb
reg_seq = ['regn_max_proc_op_sem_size', 'regn_opers_limit'] + reg_depend_seq
tmp = []
for i in range(len(reg_seq)):
    tmp.append((reg_seq[i], i))
index_in_reg_seq = dict(tmp)

# параметры связанные с добавлением узлов в регион
reg_extend_regn_list = reg_depend_seq

icv_seq = [
    'ifconv_opers_num',
    'ifconv_calls_num',
    'ifconv_merge_heur'
    ]
tmp = []
for i in range(len(icv_seq)):
    tmp.append((icv_seq[i], i))
index_in_icv_seq = dict(tmp)

# pv --- значение параметра
# x --- значение характеристики процедуры (региона, узла), отвечающей параметру

def less_eq(x, pv): return x <= pv
def less(x, pv): return x < pv
def gr_eq(x, pv): return x >= pv
def gr(x, pv): return x >  pv


# условие того, что
# - узел не отвергается
# - дублирование не запрещается
# - слияние узла не встречает препятствий
# - лимит операций не превышен
# - и т. п.
cond = {
    'regn_max_proc_op_sem_size' : less_eq,
    'regn_heur1' : gr,
    'regn_heur2' : gr,
    'regn_heur3' : gr,
    'regn_heur4' : gr,
    'regn_heur_bal1' : gr,
    'regn_heur_bal2' : gr,
    'regn_opers_limit' : less_eq,
    'regn_prob_heur' : gr_eq,
    'regn_disb_heur' : gr,
    'ifconv_merge_heur' : less_eq,
    'ifconv_opers_num' : less_eq,
    'ifconv_calls_num' : less_eq
    }

# список параметров с конечным числом значений
dcs = ['dcs_kill', 'dcs_level']
nesting = ['disable_regions_nesting']


def strategy(strategy_in_line_format = gl.OPTIMIZATION_STRATEGY):
    """
        Преобразовать стратегию оптимизации из строкового формата в рабочий формат интеллектуальной системы
    """
    def print_format():
        print('The strategy must be in the next format :', end=' ')
        print('<group> [; <group>]')
        print('     where <group> is a string in the next format :', end=' ')
        print('<parname> [<parname>]')
    
    def par_filt(parname):
        if parname in val_type.keys() or parname == 'dcs':
            return True
        else:
            print('Warning! Unknown parametor of LCC in the strategy :', parname)
            print('         The unknown parametor \'' + parname + '\' will be ignored')
            return False
            
    def group_filt(group):
        if bool(group): # если группа параметров не пустая
            dcs_par_exist = reduce(lambda x, y: x or y, [parname in dcs + ['dcs'] for parname in group])
            nesting_par_exist = reduce(lambda x, y: x or y, [parname in nesting for parname in group])
            reg_or_icv_par_exist = reduce(lambda x, y: x or y, [parname in reg_seq + icv_seq for parname in group])
            if reg_or_icv_par_exist:
                if dcs_par_exist:
                    print('Warning! Wrong parametors group :', group)
                    print('         dcs-parametors must be in separated group')
                    print('         The wrong parametors group will be ignored :', group)
                    return False
                if nesting_par_exist:
                    print('Warning! Wrong parametors group :', group)
                    print('         parametor \'' + nesting[0] + '\' must be in separated group')
                    print('         The wrong parametors group will be ignored :', group)
                    return False
            else:
                if dcs_par_exist and nesting_par_exist:
                    print('Warning! Wrong parametors group :', group)
                    print('         dcs-parametors and parametor \'' + nesting[0] + '\' must be in separated groups')
                    print('         The wrong parametors group will be ignored :', group)
                    return False
            return True
        else:
            return False
    
    groups = strategy_in_line_format.split(';')
    result = list(filter(group_filt, [list(filter(par_filt, x.split())) for x in groups]))
    result.sort()
    
    if bool(result) == False: # если список пустой
        print('Error! The optimization strategy is empty')
        print('Posible reason: there is not any valid parametor of LCC in the strategy or')
        print('                all parametors group in the strategy are not valid')
        print_format()
        sys.exit()
    
    return result

def encode_strategy(strategy):
    """
        Преобразовать стратегию оптимизации из рабочего формата интеллектуальной системы в строковой формат 
    """
    return reduce(lambda x, y: x + '; ' + y, [reduce(lambda x, y: x + ' ' + y, group) for group in strategy])
    
def print_strategy(strategy, output = None):
    """
        Напечатать стратегию в красивом многострочном виде
    """
    for group in strategy:
        print('   ', reduce(lambda x, y: x + ', ' + y, group), file=output)


def specs(specs_in_string = gl.SPECS):
    """
        Преобразовать список спеков из строкового формата в рабочий формат интеллектуальной системы
    """
    # def print_format():
    #     print('The list of specs must be in the next format :', end=' ')
    #     print('<specname>[: <proclist>][, <specname>[: <proclist>]]')
    #     print('<proclist> format is :', end=' ')
    #     print('<procname> [<procname>]')
    
    result = {}
    for spec in specs_in_string.split(','):
        tmp = spec.split(':', 1)
        if len(tmp) == 1:
            specname = tmp[0]
            proclist = None
        else:
            specname, proclist = tmp[0], tmp[1]
            proclist = proclist.split()
            proclist.sort()
        specname = specname.strip()
        if not proclist:
            proclist = None
        if specname in result:
            print('Warning! There are several occurrences in the speclist for specname :', specname)
            print('         Only the first occurrence of', specname, 'will be used')
            continue
        result[specname] = proclist
    return result

def encode_specs(spec_procs):
    """
        Преобразовать спеки из рабочего формата в строковой формат
    """
    def sp_encode(xxx_todo_changeme):
        (specname, proclist) = xxx_todo_changeme
        if not proclist:
            return specname
        else:
            return specname + ': ' + reduce(lambda x, y: x + ' ' + y, proclist)
    return reduce(lambda x, y: x + ', ' + y, map(sp_encode, spec_procs.items()))

def print_specs(spec_procs, output = None):
    """
        Напечатать словарь spec_proсs в красивом многострочном виде
    """
    for specname, proclist in spec_procs.items():
        whitespace = '   '
        if proclist:
            print(whitespace, specname + ': ' + reduce(lambda x, y: x + ', ' + y, proclist), file=output)
        else:
            print(whitespace, specname, file=output)