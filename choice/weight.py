#!/usr/bin/python3
# -*- coding: utf-8 -*-

""" содержит определения весов
"""

# Internal imports
import global_vars as gl
import read


if gl.UNEXEC_PROC_WEIGHT_SETUP == 1:
    def unexec_proc(taskname):
        """ минимум среди весов исполняемых процедур taskname
        """
        return min(read.weights_of_exec_procs(taskname).values())
    
elif gl.UNEXEC_PROC_WEIGHT_SETUP == 2:
    def unexec_proc(taskname):
        """ среднее арифметическое весов исполняемых процедур
        """
        tmp = read.weights_of_exec_procs(taskname).values()
        return sum(tmp) / len(tmp)
else:
    def unexec_proc(taskname):
        return gl.DEFAULT_WEIGHT_FOR_PROC


#--------------------------------------------
#--------------------------------------------
if gl.PROC_WEIGHT_SETUP == 1:
    def proc(w_proc):
        return w_proc
else:
    def proc(w_proc):
        return 1.
#--------------------------------------------
#--------------------------------------------
if gl.TASK_WEIGHT_SETUP == 1:    
    def task(w_task):
        return w_task
else:
    def task(w_task):
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
    for key in list(dic.keys()):
        dic[key] = dic[key] / norm_value
