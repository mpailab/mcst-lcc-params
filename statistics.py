#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
import os, sys
from sys import maxsize
from math import erf

# Internal imports
import options as gl
import par, verbose

#########################################################################################
# Чтение статистики компилируемых процедур

# Выбор каталога, из которого будет считываться статистика
if gl.INHERIT_STAT:
    STAT_PATH_FOR_READ = gl.STAT_PATH
else:
    STAT_PATH_FOR_READ = gl.DINUMIC_STAT_PATH

class Node:
    """характеристики узла"""
    def __init__(self):
        # отображение: имя характеристики узла -> значение этой характеристики
        self.chars = {}

class Proc:
    """характеристики процедуры на этапе regions"""
    def __init__(self):
        # отображение: имя характеристики процедуры -> значение этой характеристики
        self.chars = {}

        # неассоциативный массив узлов (типа Node) процедуры; ключами выступают номера узлов в процедуре
        self.nodes = {}

        # неассоциативный массив циклов процедуры; ключами выступают номера циклов в процедуре
        self.loops = {}

        # отображение: номер головы региона -> регион (типа Region)
        self.regions = {}

class Region:
    """характеристики региона на этапе regions"""
    def __init__(self):

        # отображение: имя характеристики региона -> значение этой характеристики
        self.chars = {}

        # неассоциативный массив узлов, которые пытались добавить в регион; ключами выступают номера узлов в процедуре
        self.nodes = {}

class Icv_Proc:
    """характеристики процедуры на этапе if_conv"""
    def __init__(self):
        # отображение: имя характеристики процедуры -> значение этой характеристики
        self.chars = {}

        self.regions = {}

class Icv_Region:
    """характеристики региона на этапе if_conv"""
    def __init__(self):
        # отображение: имя характеристики региона -> значение этой характеристики
        self.chars = {}
        # отображение: номер головы участка региона -> участок региона
        self.sects = {}
        
class Dcs_level:
    """характеристики процедуры на этапе dcs"""
    def __init__(self, procname, opt_level, n_num, e_num, l_num, nd_num, ed_num, ld_num, N, E, L):
        self.procname = procname # имя процедуры, к которой применяется оптимизация
        self.opt_level = opt_level # применяемый уровень оптизации фазы dcs
        self.n_num = n_num # общее количество узлов в процедуре
        self.e_num = e_num # общее количество ребер в процедуре
        self.l_num = l_num # общее количество циклов в процедуре
        self.nd_num = nd_num # количество найденных мертвых узлов в процедуре
        self.ed_num = ed_num # количество найденных мертвых ребер в процедуре
        self.ld_num = ld_num # количество найденных мертвых циклов в процедуре
        self.N = N # множество номеров всех найденных мертвых узлов
        self.E = E # множество номеров всех найденных мертвых ребер
        self.L = L # множество номеров всех найденных мертвых циклов

# Считывает статистику компиляции процедуры procname задачи taskname на фазе regions
def get_proc(taskname, procname, stat_dir = None):
    proc = Proc()
    if stat_dir is None:
        stat_dir = os.path.join(STAT_PATH_FOR_READ, taskname)
    with open(os.path.join(stat_dir, procname, 'regions.txt')) as file:
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
                        if nodenum not in proc.regions[hnum].nodes:
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
                if name == "L":
                    proc.loops[value] = {'ovl' : strr.split()[2].split(":")[1], 
                                        'red' : strr.split()[3].split(":")[1]}
                else:
                    if name == 'type':
                        #В этом случае узел с номером nodenum раньше не встречался
                        proc.nodes[num] = Node()
                    proc.nodes[num].chars[name] = value
            else:
                #В этом случае в strr содержится информация о характеристике процедуры
                name = strr.split(':')[0]
                value = strr.split(':')[1]
                proc.chars[name] = value
    return proc

# Считывает статистику компиляции процедуры procname задачи taskname на фазе if_conv
def get_icv_proc(taskname, procname):
    proc = Icv_Proc()
    procpath = os.path.join(STAT_PATH_FOR_READ, taskname, procname)
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
                if enum not in proc.regions[hnum].sects:
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

# Считывает статистику компиляции фазы dcs процедуры procname задачи taskname (для всех уровней dcs-оптимизации)
def get_dcs_proc(taskname, procname, difference_from_levels = True):
    procpath = os.path.join(STAT_PATH_FOR_READ, taskname, procname)
    proc = [None] # proc[0] = None -> нет нулевого уровня оптимизации
    dcs_levels = range(1, gl.MAX_DCS_LEVEL + 1)
    for lv in dcs_levels:
        proc.append(dcs_level(procpath, lv)) # proc[lv] -- результат оптимизации на уровне lv
    if difference_from_levels == True:
        for lv in dcs_levels[1:].__reversed__(): # перебираем все пары (уровень, предыдущий уровень), начиная с последнего уровня
            lv_pr = lv - 1
            proc[lv].nd_num -= proc[lv_pr].nd_num
            proc[lv].ed_num -= proc[lv_pr].ed_num
            proc[lv].ld_num -= proc[lv_pr].ld_num
            proc[lv].N -= proc[lv_pr].N
            proc[lv].E -= proc[lv_pr].E
            proc[lv].L -= proc[lv_pr].L
            
            # Вычислим процент метвых узлов, дуг, циклов находимых на каждом уровне
            proc[lv].nd = proc[lv].nd_num / proc[lv].n_num if proc[lv].n_num else 0
            proc[lv].ed = proc[lv].ed_num / proc[lv].e_num if proc[lv].e_num else 0
            proc[lv].ld = proc[lv].ld_num / proc[lv].l_num if proc[lv].l_num else 0
    return proc

# Считывает статистику компиляции фазы dcs процедуры procname задачи taskname (для уровня lv dcs-оптимизации)
def dcs_level(procpath, lv):
    lvpath = procpath + '/dcs_' + str(lv) + '.txt'
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
def get_dis_par(procs_dic, get_dis_par_for_proc, normolize_mode = True):
    dis_par = {}
    for taskname, proc_list in procs_dic.items():
        procs, proc_cnt, w_task = get_procs_and_weights(taskname, proc_list)
        for procname in procs:
            w_proc = proc_weight(proc_cnt, procname)
            dis_par_proc = get_dis_par_for_proc(taskname, procname)
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
    
def get_unnorm_dis_regpar_for_proc(taskname, procname):
    """
        Формирует распределение параметров фазы regions по статистике компиляции процедуры procname задачи taskname
        Полученное распределение не нормируется
    """
    dis_par = {}
    proc = get_proc(taskname, procname)
    proc_max_cnt = float(proc.chars['max_cnt'])
    if not gl.DINUMIC_PROC_OPERS_NUM:
        proc_opers_num = int(proc.chars['opers_num']) # regn_max_proc_op_sem_size
    if proc_max_cnt == 0:
        return {}
    sum_reg_cnt = sum([float(regn.chars['cnt']) for regn in proc.regions.values()], 0)
    for regn in proc.regions.values():
        reg_cnt = float(regn.chars['cnt'])
        if not gl.DINUMIC_REGN_OPERS_NUM:
            reg_opers_num = int(regn.chars['opers_num']) # regn_opers_limit
        rel_reg_cnt = reg_cnt / sum_reg_cnt
        w_regn = regn_weight(reg_cnt, rel_reg_cnt)
        for num, node in regn.nodes.items():
            #FIXME убрать все проверки in node.chars в случае отсутствия warning-сообщений при тестировании
            #В итоговой версии можно завернуть тело этого цикла в блок try: ... except ValueError: continue
            if 'n_cnt' in node.chars:
                n_cnt = float(node.chars['n_cnt'])
            else:
                verbose.warning('There is not "n_cnt" : %s %s N:%s' % (taskname, procname, num))
                continue
            if 's_enter' in node.chars:
                s_enter = int(node.chars['s_enter'])
            else:
                verbose.warning('There is not "s_enter" : %s %s N:%s' % (taskname, procname, num))
                s_enter = 0
            if 'v_cnt' in node.chars:
                v_cnt = float(node.chars['v_cnt'])
            else:
                verbose.warning('There is not "v_cnt" : %s %s N:%s' % (taskname, procname, num))
                continue
            w = node_weight(n_cnt, v_cnt, proc_max_cnt) * w_regn
            key = []
            if gl.DINUMIC_PROC_OPERS_NUM:
                if not 'proc_opers_num' in node.chars:
                    verbose.warning('There is not "proc_opers_num" : %s %s N:%s' % (taskname, procname, num))
                    continue
                proc_opers_num = int(node.chars['proc_opers_num']) # regn_max_proc_op_sem_size
            key.append(proc_opers_num)
            if gl.DINUMIC_REGN_OPERS_NUM:
                if not 'regn_opers_num' in node.chars:
                    verbose.warning('There is not "regn_opers_num" : %s %s N:%s' % (taskname, procname, num))
                    continue
                reg_opers_num = int(node.chars['regn_opers_num']) # regn_opers_limit
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
            
            if 'unb' in node.chars and node.chars['unb'] == 1:
                if not 'unb_max_dep' in node.chars:
                    verbose.warning('There is not "unb_max_dep" : %s %s N:%s' % (taskname, procname, num))
                    continue
                if not 'unb_min_dep' in node.chars:
                    verbose.warning('There is not "unb_min_dep" : %s %s N:%s' % (taskname, procname, num))
                    continue
                p = int(node.chars['unb_max_dep']) - int(node.chars['unb_min_dep']) # regn_disb_heur
                key.append(p)
                p = reg_cnt / proc_max_cnt                                          # regn_heur_bal1
                key.append(p)
                p = n_cnt / proc_max_cnt                                            # regn_heur_bal2
                key.append(p)
                if not 'unb_sh_alt_prob' in node.chars:
                    verbose.warning('There is not "unb_sh_alt_prob" : %s %s N:%s' % (taskname, procname, num))
                    continue
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
            icv_proc = get_icv_proc(taskname, procname)
            sum_reg_cnt = 0
            for regn in icv_proc.regions.values():
                sum_reg_cnt += float(regn.chars['cnt'])
            if sum_reg_cnt == 0:
                return {}
            for _, regn in icv_proc.regions.items():
                reg_cnt = float(regn.chars['cnt'])
                rel_reg_cnt = reg_cnt / sum_reg_cnt
                w_regn = icv_regn_weight(reg_cnt, rel_reg_cnt)
                for sect in regn.sects.values():
                    sect_cnt = float(sect.chars['cnt'])
                    w = icv_sect_weight(sect_cnt) * w_regn
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
            dcs_proc = get_dcs_proc(taskname, procname)
            pdis = get_dcs_proc_dis(dcs_proc,
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

def check(specs = gl.SPECS, train = False):
    
    if gl.INHERIT_STAT or train:

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
