#!/usr/bin/python
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

# Соответсвтие level не используется
#level = {
    #'regn_max_proc_op_sem_size' : 'proc',
    #'regn_heur1' : 'node',
    #'regn_heur2' : 'node',
    #'regn_heur3' : 'node',
    #'regn_heur4' : 'node',
    #'regn_heur_bal1' : 'regn',
    #'regn_heur_bal2' : 'node',
    #'regn_opers_limit' : 'regn',
    #'regn_prob_heur' : 'node',
    #'regn_disb_heur' : 'node',
    #'ifconv_merge_heur' : 'sect',
    #'ifconv_opers_num' : 'sect',
    #'ifconv_calls_num' : 'sect',
    #'disable_regions_nesting': 'proc'
    #}

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

default_value = {
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
index_in_reg_seq = dict(map(None, reg_seq, range(len(reg_seq))))

# параметры связанные с добавлением узлов в регион
reg_extend_regn_list = reg_depend_seq

icv_seq = [
    'ifconv_opers_num',
    'ifconv_calls_num',
    'ifconv_merge_heur'
    ]
index_in_icv_seq = dict(map(None, icv_seq, range(len(icv_seq))))

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
