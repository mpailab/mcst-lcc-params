#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
import os, sys
from sys import maxsize
from math import erf

# Internal imports
import options as gl
import par, verbose


class StaticticError(gl.IntsysError):
    def __init__(self, error, proc):
        self.error = error
        self.proc = proc
    
    def __str__(self):
        return 'An error by reading statictic for proc %r : %s' % (self.proc, self.error)


#########################################################################################
# Чтение статистики компилируемых процедур

# Выбор каталога, из которого будет считываться статистика
if gl.INHERIT_STAT:
    STAT_PATH_FOR_READ = gl.STAT_PATH
else:
    STAT_PATH_FOR_READ = gl.DINUMIC_STAT_PATH

class Regions (object):
            
    class Node (object):
            
        def __init__(self, init):
            self.pcnt = float(init[0])
            self.rcnt = float(init[1])
            self.senter = int(init[2])
            self.popers_num = int(init[3])
            self.ropers_num = int(init[4])
            self.unbal = int(init[5]) if len(init) > 5 else 0
            if self.unbal:
                self.unbal_sh_alt = float(init[5])

    class Region (object):
            
        def __init__(self, init):
            self.cnt = float(init[0])
            self.opers_num = int(init[1])
            self.nodes = [ Regions.Node(x.split('-')) for x in init[2:] ]

    class Proc (object):
            
        def __init__(self, name, init):
            self.name = name
            self.max_cnt = float(init[0])
            self.opers_num = int(init[1])
            self.regions = [ Regions.Region(x.split(':')) for x in init[2:] ]

class IfConv (object):

    class ESB (object):
            
        def __init__(self, init):
            self.cnt = float(init[0])
            self.opers_num = int(init[1])
            self.calls_num = int(init[2])
            self.merge = int(len(init) > 3)
            if self.merge:
                self.btime = float(init[3])
                self.atime = float(init[4])
                self.heur = float(init[5])

    class Region (object):
            
        def __init__(self, init):
            self.cnt = float(init[0])
            self.esbs = [ IfConv.ESB(x.split('-')) for x in init[1:] ]

    class Proc (object):
            
        def __init__(self, name, init):
            self.name = name
            self.regions = [ IfConv.Region(x.split(':')) for x in init ]

class DCS (object):
            
    def __new__(self, name, init):
        return self.Proc(name, init)

    class Level (object):
            
        def __init__(self, init):
            self.nodes_num = int(init[1])
            self.edges_num = int(init[2])
            self.loops_num = int(init[3])

    class Proc (object):
            
        def __init__(self, name, init):
            self.name = name
            self.nodes_num = int(init[0])
            self.edges_num = int(init[1])
            self.loops_num = int(init[2])
            self.level = { int(y[0]) : DCS.Level(y[1:]) for x in init for y in [x.split(':')] }

def read_stat (taskname, procs, phase):
    stat_dir = os.path.join(STAT_PATH_FOR_READ, taskname)
    with open(os.path.join(stat_dir, phase + '.txt')) as file:
        procs_stat = { x[0] : x[1:] for l in file.read().splitlines()
                                    for x in [l.split('#')] }
        return { k : procs_stat.get(k) for k in procs }

def read_regions_stat (taskname, procs,):
    return read_stat(taskname, procs, 'regions')

def read_ifconv_stat (taskname, procs):
    return read_stat(taskname, procs, 'if_conv')

def read_dcs_stat (taskname, procs):
    return read_stat(taskname, procs, 'dcs')

# Считывает статистику компиляции фазы dcs процедуры procname задачи taskname (для всех уровней dcs-оптимизации)
def get_dcs_proc(taskname, procname, stat, difference_from_levels = True):
    proc = DCS.Proc(procname, stat)
    if difference_from_levels == True:
        for lv in range(2, gl.MAX_DCS_LEVEL + 1): # перебираем все пары (уровень, предыдущий уровень), начиная с последнего уровня
            lv_pr = lv - 1
            proc.level[lv].nodes_num -= proc.level[lv_pr].nodes_num
            proc.level[lv].edges_num -= proc.level[lv_pr].edges_num
            proc.level[lv].loops_num -= proc.level[lv_pr].loops_num
            
            # Вычислим процент метвых узлов, дуг, циклов находимых на каждом уровне
            proc.level[lv].nd = proc.level[lv].nd_num / proc.nodes_num if proc.nodes_num else 0
            proc.level[lv].ed = proc.level[lv].ed_num / proc.edges_num if proc.edges_num else 0
            proc.level[lv].ld = proc.level[lv].ld_num / proc.loops_num if proc.loops_num else 0
    return proc

#########################################################################################
# Поучение распределений характеристик компилируемых процедур

# Формирует множество компилируемых процедур задачи taskname,
# т.е. таких процедур, которые фигурируют в статистике компиляции задачи taskname
def comp_procs_list(taskname):
    return os.listdir(os.path.join(STAT_PATH_FOR_READ, taskname))

# Считывает файл, в котором задаются веса для процедур задачи taskname
def weights_of_exec_procs(taskname, weight_file = None):
    res = {}
    if weight_file is None:
        weight_file =  os.path.join(gl.PROC_WEIGHT_PATH, taskname + '.txt')
    with open(weight_file) as rfile:
        for line in rfile:
            sp_line = line.split()
            procname = sp_line[0]
            try:
                w_proc = float(sp_line[1])
            except ValueError:
                print('Warning! Incorrect weight for proc ' + procname, ':', sp_line[1])
            else:
                res[procname] = w_proc
    return res

# Получение веса задачи taskname из внешнего файла
def task_cnt(taskname):
    if not os.path.exists(gl.TASK_WEIGHT_PATH):
        print('There is not file :', gl.TASK_WEIGHT_PATH)
        print('Warning! The file with information of task weights was not found.')
        print('         The weight of task', taskname, 'will be equal to :', 1.)
        return 1.
    res = {}
    with open(gl.TASK_WEIGHT_PATH) as rfile:
        for line in rfile:
            sp_line = line.split()
            task = sp_line[0]
            try:
                w_task = float(sp_line[1])
            except ValueError:
                if task == taskname:
                    print('Warning! Incorrect weight for spec ' + taskname, ':', sp_line[1])
                    print('         The weight of task', taskname, 'will be equal to :', 1.)
                    return 1.
            res[task] = w_task
    if taskname in res:
        return res[taskname]
    else:
        print('The file with information of task weights :', gl.TASK_WEIGHT_PATH)
        print('Warning! There is not weight of task :', taskname)
        print('         The weight of task', taskname, 'will be equal to :', 1.)
        return 1.

# Возвращает тройку: 1) procs - итератор процедур задачи taskname
#                    2) для всех процедур из procs словарь proc_cnt : процедура -> ее вес 
#                    3) вес задачи taskname
# procs определяется аргументом proc_list и глобальной переменной gl.USE_UNEXEC_PROCS_IN_STAT.
# Всего возможно 4 значения для procs:
#     - procs = все компилируемые и исполняемые процедуры (proc_list == None и gl.USE_UNEXEC_PROCS_IN_STAT == False)
#     - procs = все компилируемые процедуры               (proc_list == None и gl.USE_UNEXEC_PROCS_IN_STAT == True)
#     - procs = proc_list                                 (proc_list != None и gl.USE_UNEXEC_PROCS_IN_STAT == True)
#     - procs = все исполняемые процедуры из proc_list    (proc_list != None и gl.USE_UNEXEC_PROCS_IN_STAT == False)
def get_procs_and_weights(taskname, proc_list):
    exec_proc_cnt = weights_of_exec_procs(taskname)
    
    exec_proc_weights = list(exec_proc_cnt.values())
    sum_exec_proc_weights = sum(exec_proc_weights)
    default_unexec_proc_weight = unexec_proc_weight(exec_proc_weights)
    
    
    comp_proc_set = set(comp_procs_list(taskname))
    comp_and_exec_proc_cnt = {}
    for procname in exec_proc_cnt:
        if procname in comp_proc_set:
            comp_and_exec_proc_cnt[procname] = exec_proc_cnt[procname]

    proc_cnt = None
    sumw_exec_proc_in_procs = None
    if proc_list == None:
        if gl.USE_UNEXEC_PROCS_IN_STAT:
            procs = comp_proc_set # procs -- все компилируемые процедуры
        else:
            procs = comp_and_exec_proc_cnt.keys()
            proc_cnt = comp_and_exec_proc_cnt # procs -- все компилируемые и исполняемые процедуры
            sumw_exec_proc_in_procs = sum(comp_and_exec_proc_cnt.values())
    else:
        if not gl.USE_UNEXEC_PROCS_IN_STAT:
            procs = set(procs).intersection(set(comp_and_exec_proc_cnt.keys())) # procs -- все исполняемые процедуры из всех заданных
            proc_cnt = {pr : comp_and_exec_proc_cnt[pr] for pr in procs}
            sumw_exec_proc_in_procs = sum(proc_cnt.values())
        else:
            procs = proc_list # procs -- все заданные процедуры
    
    if proc_cnt == None or sumw_exec_proc_in_procs == None:
        proc_cnt = {}
        sumw_exec_proc_in_procs = 0
        for procname in procs:
            if procname in comp_and_exec_proc_cnt:
                tmp_weight = exec_proc_cnt[procname]
                proc_cnt[procname] = tmp_weight
                sumw_exec_proc_in_procs += tmp_weight
            else:
                proc_cnt[procname] = default_unexec_proc_weight
    normolize_dict(proc_cnt)
    
    w_task = task_weight(taskname, sum_exec_proc_weights, comp_and_exec_proc_cnt, sumw_exec_proc_in_procs)
    
    return iter(procs), proc_cnt, w_task

# Формирует суммарное распределение параметров по статистике компиляции процедур procs_dic
# на основе распределения параметров для каждой процедуры.
# Распределение параметров для каждой процедуры получается при помощи функции get_dis_par_for_proc.
# Если normolize_mode == True, то полученное распределение нормируется.
def get_dis_par(procs_dic, read_stat, get_dis_par_for_proc, normolize_mode = True):
    dis_par = {}
    for taskname, proc_list in procs_dic.items():
        procs, proc_cnt, w_task = get_procs_and_weights(taskname, proc_list)
        stat = read_stat(taskname, procs)
        for procname in procs:
            w_proc = proc_weight(proc_cnt, procname)
            dis_par_proc = get_dis_par_for_proc(taskname, procname, stat[procname])
            sum_tmp = sum(dis_par_proc.values())
            if sum_tmp == 0:
                continue
            for key in dis_par_proc.keys():
                dis_par_proc[key] = (dis_par_proc[key] / sum_tmp) * w_proc * w_task

            # Объединяем словари в один
            for key in dis_par_proc.keys():
                if key in dis_par:
                    dis_par[key] += dis_par_proc[key]
                else:
                    dis_par[key] = dis_par_proc[key]

    if normolize_mode:
        normolize_dict(dis_par)
    return dis_par
    
def get_unnorm_dis_regpar_for_proc(taskname, procname, stat):
    """
        Формирует распределение параметров фазы regions по статистике компиляции процедуры procname задачи taskname
        Полученное распределение не нормируется
    """
    dis_par = {}
    try:
        proc = Regions.Proc(procname, stat)
    except Exception as error:
        raise StaticticError(error, procname)
    proc_max_cnt = proc.max_cnt
    if not gl.DINUMIC_PROC_OPERS_NUM:
        proc_opers_num = proc.opers_num # regn_max_proc_op_sem_size
    if proc_max_cnt == 0:
        return {}
    sum_reg_cnt = sum([regn.cnt for regn in proc.regions], 0)
    for regn in proc.regions:
        reg_cnt = regn.cnt
        if not gl.DINUMIC_REGN_OPERS_NUM:
            reg_opers_num = regn.opers_num # regn_opers_limit
        rel_reg_cnt = reg_cnt / sum_reg_cnt
        w_regn = regn_weight(reg_cnt, rel_reg_cnt)
        for node in regn.nodes:
            try:
                n_cnt = node.pcnt
                s_enter = node.senter
                v_cnt = node.rcnt
                w = node_weight(n_cnt, v_cnt, proc_max_cnt) * w_regn
                key = []
                if gl.DINUMIC_PROC_OPERS_NUM:
                    proc_opers_num = node.popers_num # regn_max_proc_op_sem_size
                key.append(proc_opers_num)
                if gl.DINUMIC_REGN_OPERS_NUM:
                    reg_opers_num = node.ropers_num # regn_opers_limit
                key.append(reg_opers_num)
                r_cnt = node.rcnt / regn.cnt  # regn_heur1
                key.append(r_cnt)
                if s_enter:
                    key.append(r_cnt)                # regn_heur2
                    o_cnt = node.rcnt / node.pcnt    # regn_heur3
                    key.append(o_cnt)
                    p_cnt = node.rcnt / proc.max_cnt # regn_heur4
                    key.append(p_cnt)
                else:
                    key.append(maxsize) # на узел без бокового входа параметры regn_heur2, regn_heur3, regn_heur4
                    key.append(maxsize) # не оказывают влияния
                    key.append(maxsize)
                if node.unbal:
                    p = node.unbal                # regn_disb_heur
                    key.append(p)
                    p = reg_cnt / proc_max_cnt    # regn_heur_bal1
                    key.append(p)
                    p = n_cnt / proc_max_cnt      # regn_heur_bal2
                    key.append(p)
                    p = node.chars.unbal_sh_alt   # regn_prob_heur
                    key.append(p)
                else:
                    key.append(None)
                    key.append(None) # regn_heur_bal1, regn_heur_bal2 имеют смысл только,
                    key.append(None) # если мы определили несбалансированное схождение
                    key.append(None)
            except KeyError as error:
                verbose.warning('In %s %s -> %s' % (taskname, procname, error), verbose.err)
                continue
            except ValueError as error:
                verbose.warning('In %s %s -> %s' % (taskname, procname, error), verbose.err)
                continue
                    
            key = tuple(key)
            if key in dis_par:
                dis_par[key] += w
            else:
                dis_par[key] = w
                
    return dis_par

def get_unnorm_dis_icvpar_for_proc(taskname, procname, stat):
    """
        Формирует распределение параметров фазы if_conv по статистике компиляции процедуры procname задачи taskname
        Полученное распределение не нормируется
    """
    dis_par = {}
    try:
        icv_proc = Regions.Proc(procname, stat)
    except Exception as error:
        raise StaticticError(error, procname)
    sum_reg_cnt = 0
    for regn in icv_proc.regions:
        sum_reg_cnt += regn.cnt'
    if sum_reg_cnt == 0:
        return {}
    for regn in icv_proc.regions:
        reg_cnt = regn.cnt
        rel_reg_cnt = reg_cnt / sum_reg_cnt
        w_regn = icv_regn_weight(reg_cnt, rel_reg_cnt)
        for sect in regn.esbs:
            sect_cnt = sect.cnt
            w = icv_sect_weight(sect_cnt) * w_regn
            key = []
            o_num = sect.opers_num # ifconv_opers_num
            c_num = sect.calls_num # ifconv_calls_num
            key.append(o_num)
            key.append(c_num)
            if sect.merge:
                t_a = sect.atime
                t_b = sect.btime
                d_heur = sect.heur
                if t_b != 0:
                    p = t_a / t_b - d_heur # ifconv_merge_heur
                else:
                    if t_a == 0:
                        p = None # пользуемся тем, что None < pv для любого pv
                    else:
                        p = maxsize # считаем что maxsize > pv для любого возможного значения для pv
                key.append(p)
            else:
                key.append(None)
                # не знаю, что делать в этом случае. Этот случай бывает, когда sect не сливается из-за o_num и с_num и т.п.?
            
            key = tuple(key)
            if key in dis_par:
                dis_par[key] += w
            else:
                dis_par[key] = w
    return dis_par


def get_dis_regpar(procs_dic, normolize_mode = True):
    """
        Формирует суммарное распределение параметров фазы regions по статистики компиляции процедур procs_dic.
        Если normolize_mode == True, то полученное распределение нормируется.
    """
    return get_dis_par(procs_dic, read_regions_stat, get_unnorm_dis_regpar_for_proc, normolize_mode)

def get_dis_icvpar(procs_dic, normolize_mode = True):
    """
        Формирует суммарное распределение параметров фазы if_conv по статистики компиляции процедур procs_dic.
        Если normolize_mode == True, то полученное распределение нормируется.
    """
    return get_dis_par(procs_dic, read_ifconv_stat, get_unnorm_dis_icvpar_for_proc, normolize_mode)

def get_value_par(procs_dic, reg_parnames, icv_parnames, dis_regpar, dis_icvpar):
    """
        Для каждого параметра parname из списков reg_parnames и icv_parnames
        формирует распределение, упорядоченное по возможным значениям параметра parname.
        
        reg_parnames --- список некоторых параметров фазы regions
        icv_parnames --- список некоторых параметров фазы if_conv
        dis_regpar --- распределение параметров фазы regions
        dis_icvpar --- распределение параметров фазы if_conv
    """
    
    if len(reg_parnames) != 0:
        # получаем все узлы фазы regions процедур из procs_dic в неупорядоченном виде
        value_regpar = list(dis_regpar.keys())
    if len(icv_parnames) != 0:
        value_icvpar = list(dis_icvpar.keys())
       
    value_par = {}
    for parname in reg_parnames:
        value_one_regpar = list(value_regpar)
        i = par.index_in_reg_seq[parname]
        value_one_regpar.sort(key = lambda x: -1 if x[i] is None else x[i])
        value_par[parname] = value_one_regpar

    for parname in icv_parnames:
        value_one_icvpar = list(value_icvpar)
        i = par.index_in_icv_seq[parname]
        value_one_icvpar.sort(key = lambda x: -1 if x[i] is None else x[i])
        value_par[parname] = value_one_icvpar
    
    #надо просеять некоторые value_par[parname] от maxsize и None в своей координате (par.index_in_reg_seq[parname])
    for parname in ['regn_heur2', 'regn_heur3', 'regn_heur4']:
        if parname in reg_parnames:
            coord = par.index_in_reg_seq[parname]
            while value_par[parname] and value_par[parname][-1][coord] == maxsize: # maxsize > x, где 0 <= x <= 1.
                value_par[parname].pop()
    for parname in par.reg_unb:
        if parname in reg_parnames:
           coord = par.index_in_reg_seq[parname]
           # пользуемся тем, что None < x для любого x. Так как массив value_par[parname] упорядочен, то все None будут в начале.
           while value_par[parname] and value_par[parname][0][coord] == None:
               value_par[parname].pop(0)
    for parname in ['ifconv_merge_heur']:
        if parname in icv_parnames:
            coord = par.index_in_icv_seq[parname]
            while value_par[parname] and value_par[parname][0][coord] == None:
               value_par[parname].pop(0)
            while value_par[parname] and value_par[parname][-1][coord] == maxsize:
                value_par[parname].pop()
    
    return value_par

def get_dcs_proc_dis(dcs_proc,
                    koef_node_impotance = gl.DCS_KOEF_NODE_IMPOTANCE,
                    koef_edge_impotance = gl.DCS_KOEF_EDGE_IMPOTANCE,
                    koef_loop_impotance = gl.DCS_KOEF_LOOP_IMPOTANCE):
    """
        Определяет значимость каждого уровня оптимизации фазы dcs процедуры dcs_proc
    """
    pdis = [0] # значимость 0 уровня dcs-оптимизации (отсутствие dcs-оптимизации) полагаем равным нулю
    dcs_levels = range(1, gl.MAX_DCS_LEVEL + 1)
    for lv in dcs_levels:
        # процент мертвых узлов, выявленных на уровне lv оптимизации и не выявленных на предыдущих уровнях оптимизации
        nd = dcs_proc.level[lv].nodes_num / dcs_proc.nodes_num
        # процент мертвых ребер, выявленных на уровне lv оптимизации и не выявленных на предыдущих уровнях оптимизации
        ed = dcs_proc.level[lv].edges_num / dcs_proc.edges_num
        # процент мертвых циклов, выявленных на уровне lv оптимизации и не выявленных на предыдущих уровнях оптимизации
        ld = dcs_proc.level[lv].loops_num / dcs_proc.loops_num
        # значимость уровня lv dcs-оптимизации для данной процедуры
        impotance = koef_node_impotance * nd + koef_edge_impotance * ed + koef_loop_impotance * ld
        pdis.append(impotance)
    return pdis
    
def get_dcs_dis(procs_dic,
                koef_node_impotance = gl.DCS_KOEF_NODE_IMPOTANCE,
                koef_edge_impotance = gl.DCS_KOEF_EDGE_IMPOTANCE,
                koef_loop_impotance = gl.DCS_KOEF_LOOP_IMPOTANCE):
    """
        Определяет значимость каждого уровня оптимизации фазы dcs в среднем для всех процедур из procs_dic
    """
    dcs_levels = range(1, gl.MAX_DCS_LEVEL + 1)
    dis = [0] * (gl.MAX_DCS_LEVEL + 1)
    sum_w_task = 0
    for taskname, proc_list in procs_dic.items():

        procs, proc_cnt, w_task = get_procs_and_weights(taskname, proc_list)
        stat = read_dcs_stat(taskname, procs)
        sum_w_task += w_task
        
        tdis = [0] * (gl.MAX_DCS_LEVEL + 1)
        for procname in procs:
            proc = DCS.Proc(procname, stat[procname])
            for lv in range(2, gl.MAX_DCS_LEVEL + 1): # перебираем все пары (уровень, предыдущий уровень), начиная с последнего уровня
                lv_pr = lv - 1
                proc.level[lv].nodes_num -= proc.level[lv_pr].nodes_num
                proc.level[lv].edges_num -= proc.level[lv_pr].edges_num
                proc.level[lv].loops_num -= proc.level[lv_pr].loops_num

            pdis = get_dcs_proc_dis(proc,
                                    koef_node_impotance = koef_node_impotance,
                                    koef_edge_impotance = koef_edge_impotance,
                                    koef_loop_impotance = koef_loop_impotance)
            
            w_proc = proc_weight(proc_cnt, procname)
            
            for lv in dcs_levels:
                tdis[lv] += w_proc * pdis[lv]
        
        for lv in dcs_levels:
            dis[lv] += w_task * tdis[lv]
            
    for lv in dcs_levels:
        dis[lv] /= sum_w_task
    
    return dis


#########################################################################################
# Module check_stat

def check(specs = gl.SPECS):
    
    if STAT_PATH_FOR_READ == None:
        verbose.error('The statictic was not defined')

    for specname, proclist in specs.items():
        specpath = os.path.join(STAT_PATH_FOR_READ, specname)
        if not os.path.exists(specpath):
            verbose.error('There is not statictic for task %r.' % specname)
        if proclist == None:
            proclist = os.listdir(specpath)
        for procname in proclist:
            path = os.path.join(specpath, procname)
            if not os.path.exists(path):
                verbose.error('There is not statictic for proc %r of task %r.' % (procname, specname))
                
            path_reg = os.path.join(path, 'regions.txt')
            if not os.path.exists(path_reg):
                verbose.error('Incorrect statictic for proc %r of task %r. There is not file %r.' % (procname, specname, path_reg))
                
            path_icv = os.path.join(path, 'if_conv.txt')
            if not os.path.exists(path_icv):
                verbose.error('Incorrect statictic for proc %r of task %r. There is not file %r.' % (procname, specname, path_icv))
                
            dcs_levels = range(1, gl.MAX_DCS_LEVEL + 1)
            for lv in dcs_levels:
                lv_file = 'dcs_' + str(lv) + '.txt'
                path_lv = os.path.join(path, lv_file)
                if not os.path.exists(path_lv):
                    verbose.error('Incorrect statictic for proc %r of task %r. There is not file %r.' % (procname, specname, path_lv))
        
    if gl.PROC_WEIGHT_PATH == None:
        verbose.error('Weights for procs of specs was not defined')
        
    for specname in specs.keys():
        path = os.path.join(gl.PROC_WEIGHT_PATH, specname + '.txt')
        if not os.path.exists(path):
            verbose.error('There is not file with weights for proc of spec  %r : %r.' % (specname, path))
        
    if gl.TASK_WEIGHT_SETUP == 1:
        if gl.TASK_WEIGHT_PATH == None:
            verbose.error('Weights for specs was not defined')


#########################################################################################
# Module weight

if gl.UNEXEC_PROC_WEIGHT_SETUP == 1:
    def unexec_proc_weight(exec_proc_weights):
        """ минимум среди весов исполняемых процедур taskname
        """
        return min(exec_proc_weights)
    
elif gl.UNEXEC_PROC_WEIGHT_SETUP == 2:
    def unexec_proc_weight(exec_proc_weights):
        """ среднее арифметическое весов исполняемых процедур
        """
        return sum(exec_proc_weights) / len(exec_proc_weights)
else:
    def unexec_proc_weight(exec_proc_weights):
        return gl.DEFAULT_WEIGHT_FOR_PROC

#--------------------------------------------
#--------------------------------------------
if gl.PROC_WEIGHT_SETUP == 1:
    def proc_weight(proc_cnt, procname):
        return proc_cnt[procname]
else:
    def proc_weight(proc_cnt, procname):
        return 1.
#--------------------------------------------
#--------------------------------------------

if   gl.TASK_WEIGHT_SETUP == 1:
    def task_weight(taskname, sum_exec_proc_weights, comp_and_exec_proc_cnt, sumw_exec_proc_in_procs):
        """ Вес задачи считывается из внешнего файла """
        return task_cnt(taskname)
elif gl.TASK_WEIGHT_SETUP == 2:
    def task_weight(taskname, sum_exec_proc_weights, comp_and_exec_proc_cnt, sumw_exec_proc_in_procs):
        """ Вес задачи --- отношение суммы весов ее компилируемых и исполняемых процедур к сумме весов всех ее процедур """
        weights = comp_and_exec_proc_cnt.values()
        return sum(weights) / sum_exec_proc_weights
elif gl.TASK_WEIGHT_SETUP == 3:
    def task_weight(taskname, sum_exec_proc_weights, comp_and_exec_proc_cnt, sumw_exec_proc_in_procs):
        """ Вес задачи --- отношение суммы весов ее исполняемых оптимизируемых процедур  к сумме весов всех ее процедур"""
        return sumw_exec_proc_in_procs / sum_exec_proc_weights
else:
    def task_weight(taskname, sum_exec_proc_weights, comp_and_exec_proc_cnt, sumw_exec_proc_in_procs):
        return 1.
#-------------------------------------------
#--------------------------------------------
if gl.NODE_WEIGHT_SETUP == 0:
    def node_weight(n_cnt, v_cnt, max_cnt_in_proc):
        if n_cnt == 0:
            return 0.
        else:
            return 1.
elif gl.NODE_WEIGHT_SETUP == 1:
    def node_weight(n_cnt, v_cnt, max_cnt_in_proc):
        return v_cnt
elif gl.NODE_WEIGHT_SETUP == 2:
    def node_weight(n_cnt, v_cnt, max_cnt_in_proc):
        return n_cnt
elif gl.NODE_WEIGHT_SETUP == 3:
    def node_weight(n_cnt, v_cnt, max_cnt_in_proc):
        if n_cnt == 0:
            return 0.
        else:
            return (v_cnt / n_cnt)
else:
    def node_weight(n_cnt, v_cnt, max_cnt_in_proc):
        return 1.
#-------------------------------------------
#--------------------------------------------
if gl.REGN_WEIGHT_SETUP == 1:
    def regn_weight(reg_cnt, rel_reg_cnt):
        return reg_cnt
elif gl.REGN_WEIGHT_SETUP == 2:
    def regn_weight(reg_cnt, rel_reg_cnt):
        return rel_reg_cnt
else:
    def regn_weight(reg_cnt, rel_reg_cnt):
        return 1.
#--------------------------------------------
#--------------------------------------------
if gl.SECT_WEIGHT_SETUP == 0:
    def icv_sect_weight(sect_cnt):
        if sect_cnt == 0:
            return 0.
        else:
            return 1.
elif gl.SECT_WEIGHT_SETUP == 1:
    def icv_sect_weight(sect_cnt):
        return sect_cnt
else:
    def icv_sect_weight(sect_cnt):
        return 1.
#--------------------------------------------
#--------------------------------------------

if gl.ICV_REGN_WEIGHT_SETUP == 1:
    def icv_regn_weight(reg_cnt, rel_reg_cnt):
        return reg_cnt
elif gl.ICV_REGN_WEIGHT_SETUP == 2:
    def icv_regn_weight(reg_cnt, rel_reg_cnt):
        return rel_reg_cnt
else:
    def icv_regn_weight(reg_cnt, rel_reg_cnt):
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

#########################################################################################
# Module smooth_stat


def cerf(x):
    '''
    Функция сглаживания для параметров с вещественными значениями
    '''
    return erf(x * gl.ERF_KOEF_FOR_CONTINUOUS_PAR)
def derf(x):
    '''
    Функция сглаживания для параметров со значениями в int
    '''
    return erf(x * gl.ERF_KOEF_FOR_DISCRETE_PAR)

def get_erf(parname):
    '''
    Получить функцию сглаживания для параметра parname
    '''
    if par.types[parname] == int:
        return derf
    if par.types[parname] == float:
        return cerf
    if par.types[parname] == bool:
        raise BaseException('There is not smooth for bool parametors')

class Block:
    '''
    Блок элементов упорядоченного по некоторому признаку массива, равных по этому признаку
    '''
    def __init__(self, val, wsum, num, p_left, p_right):
        self.val = val # значение одинакового признака для всех элементов блока
        self.wsum = wsum # сумма весов всех элементов блока
        self.num = num # порядковый номер блока в упорядоченном массиве
        self.pl = p_left # номер первого элемента блока в упорядоченном массиве
        self.pr = p_right # номер последнего элемента блока в упорядоченном массиве + 1
        
class ItrBlocks:
    '''
    Итератор, который перебирает все блоки по степени их удаленности от некоторого заданного блока 
    '''
    def __iter__(self):
        return self
    
    def __init__(self, bl_center, blocks):
        self.bl_center = bl_center
        self.bl_left = bl_center
        self.bl_right = bl_center
        self.blk = blocks
        
    def see_left(self):
        lnum = self.bl_left.num
        if lnum != 0:
            return self.blk[lnum - 1]
        else:
            return None
    
    def see_right(self):
        rnum = self.bl_right.num
        if rnum != len(self.blk) - 1:
            return self.blk[rnum + 1]
        else:
            return None
        
    def __next__(self):
        cand_left =  self.see_left()
        cand_right = self.see_right()
        if cand_left == None:
            if cand_right == None:
                raise StopIteration
            else:
                self.bl_right = cand_right
                right_dist = abs(cand_right.val - self.bl_center.val)
                return (cand_right,), right_dist
        else:
            if cand_right == None:
                self.bl_left = cand_left
                left_dist = abs(cand_left.val - self.bl_center.val)
                return (cand_left,), left_dist
            else:
                left_dist = abs(cand_left.val - self.bl_center.val)
                right_dist = abs(cand_right.val - self.bl_center.val)
                if left_dist < right_dist:
                    self.bl_left = cand_left
                    return (cand_left,), left_dist
                if left_dist > right_dist:
                    self.bl_right = cand_right
                    return (cand_right,), right_dist
                # если дошли сюда, то left_dist == right_dist, и двигаемся сразу в оба направления
                self.bl_left = cand_left
                self.bl_right = cand_right
                return (cand_left, cand_right), left_dist

def return_weights(pr, sdis, bls, array, w_dis):
    '''
    Процедура уменьшает на процент pr веса элементов блоков bls массива array
    Результирующее распределение весов записывается в sdis
    '''
    for bl in bls:
        for pos in range(bl.pl, bl.pr):
            key = array[pos]
            sdis[key] += pr * w_dis[key]

def give_weight(weight_value, sdis, bls, array):
    '''
    Процедура распределяет вес weight_value на элементы блоков bls массива array
    sdis --- форимируемое распределение весов
    '''
    # считаем число элементов во всех блоках
    w_del = 0.
    for bl in bls:
        w_del += bl.pr - bl.pl
    # распределеляем weight_value равномерно по всем блокам
    for bl in bls:
        for pos in range(bl.pl, bl.pr):
            key = array[pos]
            sdis[key] += weight_value / w_del
        
def get_blocks(array, coord, w_dis):
    '''
    Функция blocks разрезает на блоки массив array, упорядоченный по принципу: a[i] < a[j], если a[i][coord] < a[j][coord].
    '''
    blocks = []
    if len(array) == 0:
        raise BaseException('array is empty')
    el = array[0]
    val_bl = el[coord]
    wsum = w_dis[el]
    bl_cnt = 0
    p_left = 0
    for pos in range(1, len(array)):
        el = array[pos]
        val = el[coord]
        w_el = w_dis[el]
        if val == val_bl:
            wsum += w_el
        else:
            bl = Block(val_bl, wsum, bl_cnt, p_left, pos)
            blocks.append(bl)
            val_bl = val
            wsum = w_el
            bl_cnt += 1
            p_left = pos
    else:
        bl = Block(val_bl, wsum, bl_cnt, p_left, pos + 1)
        blocks.append(bl)
    return blocks

def smooth_dis(array, coord, w_dis, erff):
    '''
    array --- массив векторов одинаковой длины, упорядоченный по координате coord,
    w_dis --- отображение, которое каждому элементу массива array, сопоставляет некоторое число (вес)
    Функция smooth_dis возвращает "сглаживание" w_dis,
    в котором вес каждого элемента массива array частично распределяется на соседние элементы.
    Распределение веса зависит от удаленности элементов массива array по координате coord,
    и определяется функцией erff.
    '''
    sdis = {}
    for key in w_dis.keys():
        sdis[key] = 0.
        
    blocks = get_blocks(array, coord, w_dis)
    for bl_center in blocks:
        w_amount = bl_center.wsum
        # если распределяемый вес маленький, то распределять нечего
        if w_amount < gl.ZERO_LIMIT_FOR_WEIGHT:
            return_weights(1, sdis, (bl_center,), array, w_dis)
            sdis[key] = w_amount
            continue
        itr_blocks = ItrBlocks(bl_center, blocks) # итератор, который перебирает все блоки по удаленности их от bl_center
        bls = (bl_center,)
        er_dist = erff(0)
        for bls_next, dist_next in itr_blocks:
            er_dist_next = erff(dist_next)
            pr = er_dist_next - er_dist # доля веса блока bl_center, которая будет распределена на блоки bls
            
            # распределяем долю веса bl_center на элементы блоков bls
            give_weight(pr * w_amount, sdis, bls, array)
            
            pr_rest = 1 - er_dist_next
            # если доля оставшегося для распределения веса пренебрежимо мала, то прерываем распределение веса
            if pr_rest < gl.ZERO_LIMIT_FOR_ERF:
                # тут тоже надо вернуть вес?
                # return_weights(pr_rest, sdis, (bl_center,), array, w_dis)
                break
            # если абсолютное значение оставшегося для распределения веса мало, то прекращаем распределение веса
            if w_amount * pr_rest < gl.ZERO_LIMIT_FOR_WEIGHT:
                return_weights(pr_rest, sdis, (bl_center,), array, w_dis)
                break
            
            bls = bls_next
            er_dist = er_dist_next
        else:
            pr = 1 - er_dist 
            # распределяем оставшеюся долю веса bl_center на самый удаленный от bl_center блок
            give_weight(pr * w_amount, sdis, bls, array)
            
    return sdis

def get_sm_dis(value_par, reg_parnames, icv_parnames, dis_regpar, dis_icvpar, pure_stat = gl.PURE_STAT):
    # dis_regpar и dis_icvpar должны быть уже нормированы
    sm_dis = {}
    if pure_stat:
        for parname in reg_parnames:
            sm_dis[parname] = dis_regpar
        for parname in icv_parnames:
            sm_dis[parname] = dis_icvpar
    else:
        for parname in reg_parnames:
            erff = get_erf(parname)
            coord = par.index_in_reg_seq[parname]
            if value_par[parname]:
                sm_dis[parname] = smooth_dis(value_par[parname], coord, dis_regpar, erff)
            else:
                sm_dis[parname] = dis_regpar
        for parname in icv_parnames:
            erff = get_erf(parname)
            coord = par.index_in_icv_seq[parname]
            if value_par[parname]:
                sm_dis[parname] = smooth_dis(value_par[parname], coord, dis_icvpar, erff)
            else:
                sm_dis[parname] = dis_icvpar
    return sm_dis
