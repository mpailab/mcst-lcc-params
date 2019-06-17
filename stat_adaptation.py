#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
from sys import maxsize

# Internal imports
import globals as gl
import par, read, weight

def add_dic(dic, dic_plus):
    """
        Объединяет словари dic и dic_plus в один и записывает результат в dic.
        Если в словарях dic и dic_plus содержится один и тот же ключ key,
        то в результирующем словаре ключу key будет соответствовать значение dic[key] + dic_plus[key]
    """
    for key in dic_plus.keys():
        if key in dic:
            dic[key] += dic_plus[key]
        else:
            dic[key] = dic_plus[key]

def get_procs_and_weights(taskname, proc_list):
    """
        Возвращает тройку: 1) procs - итератор процедур задачи taskname
                           2) для всех процедур из procs словарь proc_cnt : процедура -> ее вес 
                           3) вес задачи taskname
        procs определяется аргументом proc_list и глобальной переменной gl.USE_UNEXEC_PROCS_IN_STAT.
        Всего возможно 4 значения для procs:
            - procs = все компилируемые и исполняемые процедуры (proc_list == None и gl.USE_UNEXEC_PROCS_IN_STAT == False)
            - procs = все компилируемые процедуры               (proc_list == None и gl.USE_UNEXEC_PROCS_IN_STAT == True)
            - procs = proc_list                                 (proc_list != None и gl.USE_UNEXEC_PROCS_IN_STAT == True)
            - procs = все исполняемые процедуры из proc_list    (proc_list != None и gl.USE_UNEXEC_PROCS_IN_STAT == False)
    """
    exec_proc_cnt = read.weights_of_exec_procs(taskname)
    
    exec_proc_weights = list(exec_proc_cnt.values())
    sum_exec_proc_weights = sum(exec_proc_weights)
    default_unexec_proc_weight = weight.unexec_proc(exec_proc_weights)
    
    
    comp_proc_set = set(read.comp_procs_list(taskname))
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
    weight.normolize_dict(proc_cnt)
    
    w_task = weight.task(taskname, sum_exec_proc_weights, comp_and_exec_proc_cnt, sumw_exec_proc_in_procs)
    
    return iter(procs), proc_cnt, w_task

def get_dis_par(procs_dic, get_dis_par_for_proc, normolize_mode = True):
    """
        Формирует суммарное распределение параметров по статистики компиляции процедур procs_dic
        на основе распределения параметров для каждой процедуры.
        Распределение параметров для каждой процедуры получается при помощи функции get_dis_par_for_proc.
        Если normolize_mode == True, то полученное распределение нормируется.
    """
    dis_par = {}
    for taskname, proc_list in procs_dic.items():
        procs, proc_cnt, w_task = get_procs_and_weights(taskname, proc_list)
        for procname in procs:
            w_proc = weight.proc(proc_cnt, procname)
            dis_par_proc = get_dis_par_for_proc(taskname, procname)
            sum_tmp = sum(dis_par_proc.values())
            if sum_tmp == 0:
                continue
            for key in dis_par_proc.keys():
                dis_par_proc[key] = (dis_par_proc[key] / sum_tmp) * w_proc * w_task
            add_dic(dis_par, dis_par_proc)
    if normolize_mode:
        weight.normolize_dict(dis_par)
    return dis_par


def get_dis_regpar(procs_dic, normolize_mode = True):
    """
        Формирует суммарное распределение параметров фазы regions по статистики компиляции процедур procs_dic.
        Если normolize_mode == True, то полученное распределение нормируется.
    """
    return get_dis_par(procs_dic, get_unnorm_dis_regpar_for_proc, normolize_mode)

def get_dis_icvpar(procs_dic, normolize_mode = True):
    """
        Формирует суммарное распределение параметров фазы if_conv по статистики компиляции процедур procs_dic.
        Если normolize_mode == True, то полученное распределение нормируется.
    """
    return get_dis_par(procs_dic, get_unnorm_dis_icvpar_for_proc, normolize_mode)
    
def get_unnorm_dis_regpar_for_proc(taskname, procname):
            """
                Формирует распределение параметров фазы regions по статистике компиляции процедуры procname задачи taskname
                Полученное распределение не нормируется
            """
            dis_par = {}
            proc = read.proc(taskname, procname)
            proc_max_cnt = float(proc.chars['max_cnt'])
            if not gl.DINUMIC_PROC_OPERS_NUM:
                proc_opers_num = int(proc.chars['opers_num']) # regn_max_proc_op_sem_size
            if proc_max_cnt == 0:
                return {}
            sum_reg_cnt = 0
            for regn in proc.regions.values():
                sum_reg_cnt += float(regn.chars['cnt'])
            for regn in proc.regions.values():
                reg_cnt = float(regn.chars['cnt'])
                if not gl.DINUMIC_REGN_OPERS_NUM:
                    reg_opers_num = int(regn.chars['opers_num']) # regn_opers_limit
                rel_reg_cnt = reg_cnt / sum_reg_cnt
                w_regn = weight.regn(reg_cnt, rel_reg_cnt)
                for node in regn.nodes.values():
                    if 'n_cnt' in node.chars:
                        if 's_enter' in node.chars:
                            s_enter = int(node.chars['s_enter'])
                        else:
                            continue
                        n_cnt = float(node.chars['n_cnt'])
                        v_cnt = float(node.chars['v_cnt'])
                        w = weight.node(n_cnt, v_cnt, proc_max_cnt) * w_regn
                        key = []
                        if gl.DINUMIC_PROC_OPERS_NUM:
                            proc_opers_num = int(proc.chars['proc_opers_num']) # regn_max_proc_op_sem_size
                        key.append(proc_opers_num)
                        if gl.DINUMIC_REGN_OPERS_NUM:
                            reg_opers_num = int(regn.chars['regn_opers_num']) # regn_opers_limit
                        key.append(reg_opers_num)               
                        r_cnt = float(node.chars['r_cnt'])      # regn_heur1
                        key.append(r_cnt)
                        if s_enter:
                            key.append(r_cnt)                       # regn_heur2
                            o_cnt = float(node.chars['o_cnt'])      # regn_heur3
                            key.append(o_cnt)
                            p_cnt = float(node.chars['p_cnt'])      # regn_heur4
                            key.append(p_cnt)
                        else:
                            key.append(maxsize) # на узел без бокового входа параметры regn_heur2, regn_heur3, regn_heur4
                            key.append(maxsize) # не оказывают влияния
                            key.append(maxsize)
                        if 'unb_max_dep' in node.chars and 'unb_sh_alt_prob' in node.chars:
                            p = int(node.chars['unb_max_dep']) - int(node.chars['unb_min_dep']) # regn_disb_heur
                            key.append(p)
                            p = reg_cnt / proc_max_cnt                                          # regn_heur_bal1
                            key.append(p)
                            p = n_cnt / proc_max_cnt                                            # regn_heur_bal2
                            key.append(p) 
                            p = float(node.chars['unb_sh_alt_prob'])                            # regn_prob_heur
                            key.append(p)
                        else:
                            key.append(None)
                            key.append(None) # regn_heur_bal1, regn_heur_bal2 имеют смысл только,
                            key.append(None) # если мы определили несбалансированное схождение
                            key.append(None)
                                
                        key = tuple(key)
                        if key in dis_par:
                            dis_par[key] += w
                        else:
                            dis_par[key] = w
            return dis_par

def get_unnorm_dis_icvpar_for_proc(taskname, procname):
            """
                Формирует распределение параметров фазы if_conv по статистике компиляции процедуры procname задачи taskname
                Полученное распределение не нормируется
            """
            dis_par = {}
            icv_proc = read.icv_proc(taskname, procname)
            sum_reg_cnt = 0
            for regn in icv_proc.regions.values():
                sum_reg_cnt += float(regn.chars['cnt'])
            if sum_reg_cnt == 0:
                return {}
            for _, regn in icv_proc.regions.items():
                reg_cnt = float(regn.chars['cnt'])
                rel_reg_cnt = reg_cnt / sum_reg_cnt
                w_regn = weight.icv_regn(reg_cnt, rel_reg_cnt)
                for sect in regn.sects.values():
                    sect_cnt = float(sect.chars['cnt'])
                    w = weight.icv_sect(sect_cnt) * w_regn
                    key = []
                    o_num = int(sect.chars['o_num']) # ifconv_opers_num
                    c_num = int(sect.chars['c_num']) # ifconv_calls_num
                    key.append(o_num)
                    key.append(c_num)
                    if 't_a' in sect.chars:
                        t_a = float(sect.chars['t_a'])
                        t_b = float(sect.chars['t_b'])
                        d_heur = float(sect.chars['d_heur'])
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
        def coord_i(x):
            tmp = x[i]
            if tmp == None:
                return -1
            else:
                return tmp
        value_one_regpar.sort(key = coord_i)
        value_par[parname] = value_one_regpar
    for parname in icv_parnames:
        value_one_icvpar = list(value_icvpar)
        i = par.index_in_icv_seq[parname]
        def coord_i(x):
            tmp = x[i]
            if tmp == None:
                return -1
            else:
                return tmp
        value_one_icvpar.sort(key = coord_i)
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
        nd = dcs_proc[lv].nd_num / dcs_proc[lv].n_num
        # процент мертвых ребер, выявленных на уровне lv оптимизации и не выявленных на предыдущих уровнях оптимизации
        ed = dcs_proc[lv].ed_num / dcs_proc[lv].e_num
        # процент мертвых циклов, выявленных на уровне lv оптимизации и не выявленных на предыдущих уровнях оптимизации
        ld = dcs_proc[lv].ld_num / dcs_proc[lv].l_num
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
        sum_w_task += w_task
        
        tdis = [0] * (gl.MAX_DCS_LEVEL + 1)
        for procname in procs:
            dcs_proc = read.dcs_proc(taskname, procname)
            pdis = get_dcs_proc_dis(dcs_proc,
                                    koef_node_impotance = koef_node_impotance,
                                    koef_edge_impotance = koef_edge_impotance,
                                    koef_loop_impotance = koef_loop_impotance)
            
            w_proc = weight.proc(proc_cnt, procname)
            
            for lv in dcs_levels:
                tdis[lv] += w_proc * pdis[lv]
        
        for lv in dcs_levels:
            dis[lv] += w_task * tdis[lv]
            
    for lv in dcs_levels:
        dis[lv] /= sum_w_task
    
    return dis
