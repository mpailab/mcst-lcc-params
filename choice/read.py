#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
содержит функции считывания файлов статистики
"""

# External imports
from __future__ import division # деление как в питон 3, т.е. вместо 3 / 2 = 1 будет 3 / 2 = 1.5
from os import listdir

# Internal imports
from def_classes import *
import global_vars as gl


def task_list():
    return listdir(gl.FULL_STAT_PATH)

def proc_list(taskname, add_unexec_procs = gl.USE_FULL_STAT):
    """ Получение списка процедур спека.
        add_unexec_procs == False -> пересечение списков компилируемых и исполняемых процедур
        add_unexec_procs == True  -> список всех компилируемых процедур
    """
    if add_unexec_procs:
        tpath = gl.FULL_STAT_PATH + '/' + taskname
        list_procs = listdir(tpath)
    else:
        path = gl.PROC_LIST_PATH + '/' + taskname + '.txt'
        ffile = open(path)
        list_procs = []
        for strr in ffile:
            # удаляет символ перехода на новую строку из strr
            strr = strr[:-1]
            list_procs.append(strr)
        ffile.close()
    return list_procs

def proc(taskname, procname):
    procpath = gl.STAT_PATH_FOR_READ + '/' + taskname + '/' + procname
    return proc_read(procpath)

def icv_proc(taskname, procname):
    procpath = gl.STAT_PATH_FOR_READ + '/' + taskname + '/' + procname
    return icv_proc_read(procpath)

def proc_cnt_dic(taskname):
    """ Получение для спека taskname словаря: процедура -> вес
        Вес процедуры -- время работы процедуры в составе спека, выраженное в некоторых условных единицах
        Результат зависит от глобала USE_FULL_STAT
            используются ли все компилируемые или только те компилируемые процедуры, которые реально исполняются
    """
    proc_weight_dir = {}
    if gl.USE_FULL_STAT:
        for procname in proc_list(taskname):
            proc_weight_dir[procname] = gl.UNEXEC_PROC_WEIGHT
            
    ffile = open(gl.PROC_ORDER_PATH + '/' + taskname + '.txt')
    for string in ffile:
        proc_name, value = string.split()
        proc_weight_dir[proc_name] = float(value)
    ffile.close()
                
    return proc_weight_dir

def task_cnt(taskname, num = 1):
    """ Получение веса задачи.
        Вес задачи --- отношение времени исполнения ее небиблиотечных процедур к общему времени ее работы
    """
    path = gl.STATEXEC_PATH + '/' + taskname + '/' + 'run.' + str(num) + '.txt'
    ffile = open(path)
    plist = proc_list(taskname, add_unexec_procs = False)
    sum_all = 0
    sum_own = 0
    for string in ffile:
        array = string.split()
        weight = float(array[2])
        sum_all += weight
        procname = array[5]
        if procname in plist:
            sum_own += weight
    ffile.close()
    return sum_own / sum_all

def task_cnt_dic():
    tlist = task_list()
    task_cnt_dir = {}
    for taskname in tlist:
        task_cnt_dir[taskname] = task_cnt(taskname)
    return task_cnt_dir

def proc_read(procpath):
    proc = Proc()
    file = open(procpath + '/regions.txt')
    for strr in file:
        ## отрезаем от strr последний символ, который является символом перехода на новую строку
        strr = strr[:-1]
        if strr[0] == 'H':
            #В этом случае в strr содержится информация о регионе
            words = strr.split()
            hnum = words[0].split(':')[1] # номер головы региона
            if len(words) == 1:
                # В этом случае регион с номером hnum раньше не встречался
                proc.regions[hnum] = Region()
            elif words[1][0] == 'N':
                # В этом случае в strr записана характеристика добавляемого узла
                nodenum = words[1].split(':')[1]
                if hnum != nodenum:
                    # голову региона не будем добавлять в узлы
                    if not proc.regions[hnum].nodes.has_key(nodenum):
                        proc.regions[hnum].nodes[nodenum] = Node()
                    chname = words[2].split(':')[0]
                    if chname == 'v':
                        #костыль: в исходном файле должно быть 'v_cnt', а по факту 'v cnt'.
                        chname = 'v_cnt'
                        value = words[3].split(':')[1]
                    else:
                        value = words[2].split(':')[1]
                    proc.regions[hnum].nodes[nodenum].chars[chname] = value
            else:
                # В этом случае в строке strr записана характеристика региона
                name = words[1].split(':')[0]
                value = words[1].split(':')[1]
                proc.regions[hnum].chars[name] = value
        elif strr[0] == 'N':
            #В этом случае в strr содержится информация о характеристике узла
            num = strr.split()[0].split(':')[1]
            name = strr.split()[1].split(':')[0]
            value = strr.split()[1].split(':')[1]
            if name == 'type':
                #В этом случае узел с номером nodenum раньше не встречался
                proc.nodes[num] = Node()
            proc.nodes[num].chars[name] = value
        else:
            #В этом случае в strr содержится информация о характеристике процедуры
            name = strr.split(':')[0]
            value = strr.split(':')[1]
            proc.chars[name] = value
    file.close()
    return proc

def icv_proc_read(procpath):
    proc = Icv_Proc()
    file = open(procpath + '/if_conv.txt')
    for strr in file:
        # отрезаем от strr последний символ, который является символом перехода на новую строку
        strr = strr[:-1]
        if strr[0] == 'H':
            #В этом случае в strr содержится информация о регионе
            words = strr.split()
            hnum = words[0].split(':')[1] # номер головы региона
            reg_charname = words[1].split(':')[0]
            if reg_charname == 'E':
                # В этом случае в strr записана характеристика участка
                enum = words[1].split(':')[1]
                if not proc.regions[hnum].sects.has_key(enum):
                    proc.regions[hnum].sects[enum] = Node() # програмно участок ведет себя как класс Node
                chname = words[2].split(':')[0]
                value = words[2].split(':')[1]
                proc.regions[hnum].sects[enum].chars[chname] = value
            elif reg_charname == 'cnt':
                proc.regions[hnum] = Icv_Region()
                proc.regions[hnum].chars['cnt'] = words[1].split(':')[1]
            else:
                #тогда в strr содержится информация о характеристики региона
                proc.regions[hnum].chars[reg_charname] = words[1].split(':')[1]
        else:
            #В этом случае в strr содержится информация о характеристике процедуры
            words = strr.split(':')
            name = words[0]
            value = words[1]
            proc.chars[name] = value
    file.close()
    return proc

# DCS -----------------------------------------------------------------------------------------------------

def dcs_proc(taskname, procname, difference_from_levels = True):
    procpath = gl.STAT_PATH_FOR_READ + '/' + taskname + '/' + procname
    proc = [None] # proc[0] = None -> нет нулевого уровня оптимизации
    for lv in gl.DCS_LEVELS:
        proc.append(dcs_level(procpath, lv)) # proc[lv] -- результат оптимизации на уровне lv
    if difference_from_levels == True:
        for lv in gl.DCS_LEVELS[1:].__reversed__(): # перебираем все пары (уровень, предыдущий уровень), начиная с последнего уровня
            lv_pr = lv - 1
            #if (proc[lv_pr].n_num != proc[lv].n_num) or (proc[lv_pr].e_num != proc[lv].e_num) or (proc[lv_pr].l_num != proc[lv].l_num):
            #    print 'In ', taskname + '.' + procname + '.dcs_' + str(lv), 'difference in nums'
            proc[lv].nd_num -= proc[lv_pr].nd_num
            proc[lv].ed_num -= proc[lv_pr].ed_num
            proc[lv].ld_num -= proc[lv_pr].ld_num
            proc[lv].N -= proc[lv_pr].N
            proc[lv].E -= proc[lv_pr].E
            proc[lv].L -= proc[lv_pr].L
            #if (len(proc[lv].N) != proc[lv].nd_num) or (len(proc[lv].E) != proc[lv].ed_num) or (len(proc[lv].L) != proc[lv].ld_num):
            #    print 'In ', taskname + '.' + procname + '.dcs_' + str(lv), 'difference in lens'
            
            # Вычислим процент метвых узлов, дуг, циклов находимых на каждом уровне
            proc[lv].nd = proc[lv].nd_num / proc[lv].n_num
            proc[lv].ed = proc[lv].ed_num / proc[lv].e_num
            proc[lv].ld = proc[lv].ld_num / proc[lv].l_num
            #try:
                #proc[lv].nd = proc[lv].nd_num / proc[lv].n_num
            #except ZeroDivisionError:
                #proc[lv].nd = 0
            #try:
                #proc[lv].ed = proc[lv].ed_num / proc[lv].e_num
            #except ZeroDivisionError:
                #proc[lv].ed = 0
            #try:
                #proc[lv].ld = proc[lv].ld_num / proc[lv].l_num
            #except ZeroDivisionError:
                #proc[lv].ld = 0
    return proc

def dcs_level(procpath, lv):
    lvpath = procpath + '/dcs_' + str(lv) + '.txt'
    #print lvpath
    ffile = open(lvpath)
    
    strr = ffile.readline()[:-1]
    procname = strr.split(':')[1]
    
    strr = ffile.readline()[:-1]
    n_num = int(strr.split(':')[1])
    
    strr = ffile.readline()[:-1]
    e_num = int(strr.split(':')[1])
    
    strr = ffile.readline()[:-1]
    l_num = int(strr.split(':')[1])
    
    N = set()
    E = set()
    L = set()
    
    for strr in ffile:
        strr = strr[:-1]
        spl_end = strr.split()[1].split(':')
        key = spl_end[0]
        value = int(spl_end[1])
        if key == 'E':
            E.add(value)
        elif key == 'N':
            N.add(value)
        elif key == 'L':
            L.add(value)
        elif key == 'n_num':
            nd_num = value
        elif key == 'e_num':
            ed_num = value
        elif key == 'l_num':
            ld_num = value
    ffile.close()
    
    nd_num = len(N)
    ed_num = len(E)
    ld_num = len(L)
    
    return Dcs_level(procname, lv, n_num, e_num, l_num, nd_num, ed_num, ld_num, N, E, L)

if __name__ == '__main__':
    pass
