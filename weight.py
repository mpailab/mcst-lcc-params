#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" содержит определения весов
"""

# Internal imports
import globals as gl
import read


if gl.UNEXEC_PROC_WEIGHT_SETUP == 1:
    def unexec_proc(exec_proc_weights):
        """ минимум среди весов исполняемых процедур taskname
        """
        return min(exec_proc_weights)
    
elif gl.UNEXEC_PROC_WEIGHT_SETUP == 2:
    def unexec_proc(exec_proc_weights):
        """ среднее арифметическое весов исполняемых процедур
        """
        return sum(exec_proc_weights) / len(exec_proc_weights)
else:
    def unexec_proc(exec_proc_weights):
        return gl.DEFAULT_WEIGHT_FOR_PROC

#--------------------------------------------
#--------------------------------------------
if gl.PROC_WEIGHT_SETUP == 1:
    def proc(proc_cnt, procname):
        return proc_cnt[procname]
else:
    def proc(proc_cnt, procname):
        return 1.
#--------------------------------------------
#--------------------------------------------

if   gl.TASK_WEIGHT_SETUP == 1:
    def task(taskname, sum_exec_proc_weights, comp_and_exec_proc_cnt, sumw_exec_proc_in_procs):
        """ Вес задачи считывается из внешнего файла """
        return read.task_cnt(taskname)
elif gl.TASK_WEIGHT_SETUP == 2:
    def task(taskname, sum_exec_proc_weights, comp_and_exec_proc_cnt, sumw_exec_proc_in_procs):
        """ Вес задачи --- отношение суммы весов ее компилируемых и исполняемых процедур к сумме весов всех ее процедур """
        weights = comp_and_exec_proc_cnt.values()
        return sum(weights) / sum_exec_proc_weights
elif gl.TASK_WEIGHT_SETUP == 3:
    def task(taskname, sum_exec_proc_weights, comp_and_exec_proc_cnt, sumw_exec_proc_in_procs):
        """ Вес задачи --- отношение суммы весов ее исполняемых оптимизируемых процедур  к сумме весов всех ее процедур"""
        return sumw_exec_proc_in_procs / sum_exec_proc_weights
else:
    def task(taskname, sum_exec_proc_weights, comp_and_exec_proc_cnt, sumw_exec_proc_in_procs):
        return 1.
#-------------------------------------------
#--------------------------------------------
if gl.NODE_WEIGHT_SETUP == 0:
    def node(n_cnt, v_cnt, max_cnt_in_proc):
        if n_cnt == 0:
            return 0.
        else:
            return 1.
elif gl.NODE_WEIGHT_SETUP == 1:
    def node(n_cnt, v_cnt, max_cnt_in_proc):
        return v_cnt
elif gl.NODE_WEIGHT_SETUP == 2:
    def node(n_cnt, v_cnt, max_cnt_in_proc):
        return n_cnt
elif gl.NODE_WEIGHT_SETUP == 3:
    def node(n_cnt, v_cnt, max_cnt_in_proc):
        if n_cnt == 0:
            return 0.
        else:
            return (v_cnt / n_cnt)
else:
    def node(n_cnt, v_cnt, max_cnt_in_proc):
        return 1.
#-------------------------------------------
#--------------------------------------------
if gl.REGN_WEIGHT_SETUP == 1:
    def regn(reg_cnt, rel_reg_cnt):
        return reg_cnt
elif gl.REGN_WEIGHT_SETUP == 2:
    def regn(reg_cnt, rel_reg_cnt):
        return rel_reg_cnt
else:
    def regn(reg_cnt, rel_reg_cnt):
        return 1.
#--------------------------------------------
#--------------------------------------------
if gl.SECT_WEIGHT_SETUP == 0:
    def icv_sect(sect_cnt):
        if sect_cnt == 0:
            return 0.
        else:
            return 1.
elif gl.SECT_WEIGHT_SETUP == 1:
    def icv_sect(sect_cnt):
        return sect_cnt
else:
    def icv_sect(sect_cnt):
        return 1.
#--------------------------------------------
#--------------------------------------------

if gl.ICV_REGN_WEIGHT_SETUP == 1:
    def icv_regn(reg_cnt, rel_reg_cnt):
        return reg_cnt
elif gl.ICV_REGN_WEIGHT_SETUP == 2:
    def icv_regn(reg_cnt, rel_reg_cnt):
        return rel_reg_cnt
else:
    def icv_regn(reg_cnt, rel_reg_cnt):
        return 1.
#--------------------------------------------
#--------------------------------------------

def normolize_to_percents(array, norm_value = None):
    if norm_value == None:
        norm_value = sum(array)
    return [100 * x / norm_value for x in array]

def normolize_dict(dic):
    norm_value = sum(dic.values())
    for key in dic.keys():
        dic[key] = dic[key] / norm_value
