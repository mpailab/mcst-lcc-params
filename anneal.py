﻿#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
from copy import deepcopy
from functools import reduce
import math, random, sys, os
from sys import maxsize

# Internal imports
import options as gl
import statistics as stat
import func as clc
import par, train, verbose

if gl.TEMPERATURE_LAW_TYPE == 1:
    def temperature_law(i):
        """ 1 / n """
        return 1. / i
elif gl.TEMPERATURE_LAW_TYPE == 2:
    def temperature_law(i):
        """ alpha ^ n """
        return gl.ALPHA_IN_TEPMERATURE_LAW ** i
else:
    def temperature_law(i):
        """ 1 / ln(n + 1) """
        return 1. / math.log(i + 1)

def temperature(i):
    '''Функция вычисляет значение температуры на итерации i
       i = 1, 2, ...
    '''
    koef = gl.START_TEMPERATURE / temperature_law(1)
    return koef * temperature_law(i)

# Вероятностное распределение, определяющее выбор следующего состояния системы в зависимости от ее текущих состояния и температуры
if gl.DISTRIBUTION_LAW_TYPE == 1:
    def distribution(T):
        """ распределение для сверхбыстрого отжига """
        return random.choice([-1, 1]) * T * ((1 + 1./T) ** abs(2 * random.uniform(-0.5, 0.5)) - 1)
elif gl.DISTRIBUTION_LAW_TYPE == 2:
    def distribution(T):
        """ распределение Коши """
        return T * math.tan(math.pi * random.uniform(-0.5, 0.5))
elif gl.DISTRIBUTION_LAW_TYPE == 3:
    def distribution(T):
        """ равномерное распределение """
        return math.sqrt(T * 3) * random.uniform(-1, 1)
else:
    def distribution(T):
        """ нормальное распределение """
        return random.gauss(0, T)
            
def F(list_trio):
    """
    Минимизируемый функционал
    """
    len_list_trio = len(list_trio)
    if len_list_trio == 0:
        raise BaseException('list_trio is empty')
    
    mul_delta_T_comp = 1
    mul_delta_T_exec = 1
    mul_delta_V = 1
    for trio in list_trio:
        delta_T_comp = trio[0]
        if delta_T_comp > 1. + gl.COMP_TIME_INCREASE_ALLOWABLE_PERCENT:
            return maxsize
        mul_delta_T_comp *= delta_T_comp
        
        delta_T_exec = trio[1]
        if delta_T_exec > 1. + gl.EXEC_TIME_INCREASE_ALLOWABLE_PERCENT:
            return maxsize
        mul_delta_T_exec *= delta_T_exec
        
        delta_V = trio[2]
        if delta_V > 1. + gl.MEMORY_INCREASE_ALLOWABLE_PERCENT:
            return maxsize
        mul_delta_V *= delta_V
    
    mul_delta_T_exec = mul_delta_T_exec ** (1. / len_list_trio)
    mul_delta_T_comp = mul_delta_T_comp ** (1. / len_list_trio)
    mul_delta_V = mul_delta_V ** (1. / len_list_trio)
    
    result = gl.TIME_EXEC_IMPOTANCE * mul_delta_T_exec
    result += gl.TIME_COMP_IMPOTANCE * mul_delta_T_comp
    result += gl.MEMORY_IMPOTANCE * mul_delta_V
    
    return result

def calculate_F(values, values_default):
    list_rel_trio = []
    for key in values.keys():
        trio = values[key]
        trio_default = values_default[key]
        rel_trio = (trio[0] / trio_default[0], trio[1] / trio_default[1], trio[2] / trio_default[2])
        list_rel_trio.append(rel_trio)
    return F(list_rel_trio)

def condition(x_list, coord, old_pv_list, new_pv_list, index_0_flag, index_1_flag):
    if index_0_flag:
        parname = par.reg_seq[0]
        x = x_list[0]
        if not (par.cond[parname](x, old_pv_list[0]) and par.cond[parname](x, new_pv_list[0])):
            return False
    if index_1_flag:
        parname = par.reg_seq[1]
        x = x_list[1]
        if not (par.cond[parname](x, old_pv_list[1]) and par.cond[parname](x, new_pv_list[1])):
            return False
    for i in range(2, coord):
        parname = par.reg_seq[i]
        x = x_list[i]
        if not (par.cond[parname](x, old_pv_list[i]) and par.cond[parname](x, new_pv_list[i])):
            return False
    return True

def icv_condition(x_list, coord, old_pv_list, new_pv_list):
    for i in range(coord):
        parname = par.icv_seq[i]
        x = x_list[i]
        if not (par.cond[parname](x, old_pv_list[i]) and par.cond[parname](x, new_pv_list[i])):
            return False
    return True
    

def shift(par_list, max_sum, dis_par, cond):
    '''Функция выдает максимальное число последовательно идущих от начала элементов списка par_list,
    сумма весов которых не превосходит max_sum.
    Отображение dis_par сопоставляет каждому элементу списка par_list его вес '''
    current_sum = 0
    position_shift = 0
    while (current_sum <= max_sum) and (position_shift != len(par_list)):
        par_value = par_list[position_shift]
        if gl.UNRELATED_PARAMS or cond(par_value):
            current_sum += dis_par[par_value]
        position_shift += 1
    #if not (current_sum <= max_sum): # ошибка
    #    position_shift -= 1
    return position_shift

def corr_shift(par_list, position_shift, coord):
    '''Корректировка position_shift в случае, когда par_list[position_shift:] и par_list[:position_shift]
    содержат узлы, одинаковые по координате coord.'''
    if position_shift == 0 or position_shift == len(par_list):
        return position_shift
    val_left = par_list[position_shift - 1][coord]
    val_right = par_list[position_shift][coord]
    while val_left == val_right:
        position_shift -= 1 # сдвигаеся влево
        if position_shift == 0:
            return position_shift
        val_right = val_left
        val_left = par_list[position_shift - 1][coord]
    return position_shift

def find_position(value, array, coord):
    # Элементы array наборы чисел одинаковой длины
    # Элементы array должны быть упорядоченны по coord-ий координате
    len_array = len(array)
    if len_array == 0:
        raise BaseException('searching position of the value in empty array')
    if value < array[0][coord]:
        left = 'left_limit'
        right = 0
        return (left, right)
    for i in range(len_array - 1):
        a_i = array[i][coord]
        a_si = array[i+1][coord]
        if value == a_i:
            left = i
            right = i
            return (left, right)
        if value < a_si:
            left = i
            right = i + 1
            return (left, right)
    left = len_array - 1
    if value == array[len_array - 1][coord]:
        right = left
    else:
        right = 'right_limit'
    return (left, right)

def get_reg_parnames(parname_list):
    parnames = []
    for parname in par.reg_seq:
        if parname in parname_list:
            parnames.append(parname)
    return parnames

def get_icv_parnames(parname_list):
    parnames = []
    for parname in par.icv_seq:
        if parname in parname_list:
            parnames.append(parname)
    return parnames

def pv_list_from_dic(pv_dic, parnames):
    tmp_list = []
    for parname in parnames:
        if parname in pv_dic:
            tmp_list.append(pv_dic[parname])
        else:
            tmp_list.append(par.defaults[parname])
    return tuple(tmp_list)

def get_value(parname, value_par, inf_value_par, sup_value_par, position, min_position, max_position, coord):
    if (par.cond[parname] == par.gr) or (par.cond[parname] == par.less_eq):
        if position != min_position:
            return value_par[parname][position - 1][coord]
        else:
            return inf_value_par[parname]
    elif (par.cond[parname] == par.gr_eq) or (par.cond[parname] == par.less):
        if position != max_position:
            return value_par[parname][position][coord]
        else:
            return sup_value_par[parname]
        
def optimize(procs_dic, par_names,
             dis_regpar,
             dis_icvpar,
             par_start_value,
             val_F_start,
             result_start,
             result_default,
             new_stat_for_every_step = not gl.INHERIT_STAT,
             output = verbose.debug
            ):
    '''
    procs_dic: taskname -> list_of_some_procnames_of_taskname (for some taskname)
    if procs_dic[taskname] is equal to None, then procs_dic[taskname] := all procnames of taskname
    '''
    
    # объеденим отображения index_in_reg_seq и index_in_icv_seq в index_in_own_seq
    index_in_own_seq = dict(par.index_in_reg_seq)
    index_in_own_seq.update(par.index_in_icv_seq)
    
    # выделяем из списка заданных параметров в отдельные упорядоченные списки параметры фазы regions и if_conv
    all_reg_parnames = get_reg_parnames(par_names)
    all_icv_parnames = get_icv_parnames(par_names)
    
    # установка значения по умолчанию для параметров
    par_default_value = {}
    for parname in all_reg_parnames + all_icv_parnames:
        par_default_value[parname] = par.defaults[parname]
    
    j_for_exec_run = 0
    
    # вычисление значения функционала при значении параметров по умолчанию
    val_F_default = calculate_F(result_default, result_default)
    
    # установка начальных значений для параметров
    # вычисление значения функционала при начальном значении параметров
    # в par_start_value могут быть заданы значения для тех параметров, которых нет в par_names,
    # и наоборот, не всем параметрам из par_names отображение par_start_value может сопоставлять значения.
    # Дополним par_start_value значениями по умолчанию для тех параметров из par_names,
    # которым par_start_value не сопоставлет никакого значения
    tmp_dict = dict(par_default_value)
    tmp_dict.update(par_start_value)
    par_start_value = tmp_dict
    # делаем так, чтобы par_start_value и par_default_value были определены на одном и томже списке параметров
    par_default_value = {parname : par.defaults[parname] for parname in par_start_value.keys()}
    
    # инициализация текущего значения функционала
    val_F_current = val_F_start
    par_current_value = dict(par_start_value)
    print('F_start = ', val_F_current, file=verbose.F)
    print(file=verbose.runs)
    
    # установка начальных значений для лучшего значения функционала F, лучшего значения параметра
    # и шага алгоритма, на котором они достигаются
    i_for_best_value = 0
    if val_F_current < val_F_default:
        par_best_value = dict(par_current_value)
        result_best = dict(result_start)
        val_F_best = val_F_current
    else:
        par_best_value = dict(par_default_value)
        result_best = dict(result_default)
        val_F_best = val_F_default
    
    # вычисление распределений параметров 
    value_par = stat.get_value_par(procs_dic, all_reg_parnames, all_icv_parnames, dis_regpar, dis_icvpar)
    
    # если value_par[parname] == [], то выкинуть parname из all_reg_parnames (all_icv_parnames)
    # т.е., если нет возможных значений для parname, то оптимизировать по нему не надо
    reg_parnames = [par for par in all_reg_parnames if value_par[par]]
    icv_parnames = [par for par in all_icv_parnames if value_par[par]]
    
    # если списки reg_parnames и icv_parnames оба пусты
    if not reg_parnames and not icv_parnames:
        print('Scale of posible values for parametors is empty', file=verbose.err)
        print('For solve this problem increase a number of optimizated procedures', file=verbose.err)
        print('Interrupt optimization', file=verbose.err)
        print(file=output)
        par_value_print('The best values for parametors :', par_best_value, file=verbose.optval)
        print('The best values were found for', i_for_best_value, 'iterations of algorithm', file=output)
        print('The run-scripts was started for', j_for_exec_run * len(procs_dic), 'times', file=output)
        print('The best (t_c, t_e, m) is', result_best, file=output)
        print('The best value for F is', val_F_best, file=output)
        return (par_best_value, val_F_best, result_best)
    
    # вычисление распределений параметров
    sm_dis = stat.get_sm_dis(value_par, reg_parnames, icv_parnames, dis_regpar, dis_icvpar)
    
    # инициализация базы данных для хранения всех найденных значений функционала F и распределений параметров
    F_run_result = ([], [], [], [])
    
    # добавление в базу соответсвующих значений при значении параметров по умолчанию
    F_run_result[0].append(par_default_value)
    F_run_result[1].append(val_F_default)
    F_run_result[2].append(None)
    F_run_result[3].append(None)
    
    # добавление в базу соответсвующих значений при начальном значении параметров
    F_run_result[0].append(dict(par_current_value))
    F_run_result[1].append(val_F_current)
    if gl.MEM_RESTRICTION:
        F_run_result[2].append(None)
        F_run_result[3].append(None)
    else:
        F_run_result[2].append(deepcopy(value_par))
        F_run_result[3].append(deepcopy(sm_dis))
    
    j_for_temperature = 1 # задание начального уровня темпрературы
    iterr = 0 # инициализация счетчика внешних итераций алгоритма
    
    # current_to_new_candidate = False
    current_to_candidate = False # инициализация флага перехода алгоритма к новому набору параметров
    
    # основной цикл
    ind = 0
    while (iterr < gl.MAX_NUMBER_ITERATIONS or (iterr < 3 * gl.MAX_NUMBER_ITERATIONS and (iterr <= i_for_best_value + 1))):
        iterr += 1
        print('Iteration ' + str(iterr) + ':', file=output)
        
        if new_stat_for_every_step and current_to_candidate:

            # Формируем распределения value_par и sm_dis возможных значений параметров 
            if F_run_result[2][ind] == None:

                # Нет информации о распределении параметров

                # Пересчитываем распределения всех параметров на основе новой статистики
                if len(all_reg_parnames) != 0:
                    dis_regpar = stat.get_dis_regpar(procs_dic)
                if len(all_icv_parnames) != 0:
                    dis_icvpar = stat.get_dis_icvpar(procs_dic)
                
                # Формируем распределения возможных значений для заданной группы параметров
                value_par = stat.get_value_par(procs_dic, all_reg_parnames, all_icv_parnames, dis_regpar, dis_icvpar)
                
                # Выкидываем те параметры, для которых не удалось найти возможные значения
                reg_parnames = [par for par in all_reg_parnames if value_par[par]]
                icv_parnames = [par for par in all_icv_parnames if value_par[par]]
                
                # Если пригодных значений нет, то завершаем оптимизацию
                if not reg_parnames and not icv_parnames:
                    print('Scale of posible values for parametors is empty', file=verbose.err)
                    print('For solve this problem increase a number of optimizated procedures', file=verbose.err)
                    print('Interrupt optimization', file=verbose.err)
                    print(file=output)
                    break
                
                # Вычисляем новую шкалу возможных значений для оставшихся параметров
                sm_dis = stat.get_sm_dis(value_par, reg_parnames, icv_parnames, dis_regpar, dis_icvpar)

                # Если нет ограничения по памяти, то сохраняем распределения в таблице
                if not gl.MEM_RESTRICTION:
                    F_run_result[2][ind] = value_par
                    F_run_result[3][ind] = sm_dis

            else:
                # Информация о распределении параметров уже найдена
                value_par = F_run_result[2][ind]
                sm_dis = F_run_result[3][ind]
            
        
        if (new_stat_for_every_step and current_to_candidate) or iterr == 1:
            sup_value_par = {}
            inf_value_par = {}
            for parname in reg_parnames + icv_parnames:
                i = index_in_own_seq[parname]
                sup_value_par[parname] = value_par[parname][-1][i] + 1 # число заведомо большее всех элементов value_par_list
                inf_value_par[parname] = max(value_par[parname][0][i] - 1, 0) # число заведомо меньшее всех элементов value_par_list или 0, если такого не бывает
            
            #поиск места текущих значений par_current_value в value_par
            min_position = {}
            max_position = {}
            position = {}
            for parname in reg_parnames + icv_parnames:
                min_position[parname] = 0
                max_position[parname] = len(value_par[parname])
                i = index_in_own_seq[parname]
                left, right = find_position(par_current_value[parname], value_par[parname], i)
                if right == 'right_limit':
                    right = max_position[parname]
                if (left == right) and ((par.cond[parname] == par.gr) or (par.cond[parname] == par.less_eq)):
                    position[parname] = right + 1
                else:
                    position[parname] = right
        
        current_reg_pv_list = pv_list_from_dic(par_current_value, par.reg_seq)
        current_icv_pv_list = pv_list_from_dic(par_current_value, par.icv_seq)
        
        max_step = temperature(j_for_temperature)
        print('Temperature:', str(max_step * 100) + '%', file=output)
        for attempt in range(gl.MAX_NUMBER_OF_ATTEMPTS_FOR_ITERATION + 1):
            # сдвигаемся в случайную точку, отстоящую не больше чем на max_step
            if attempt != gl.MAX_NUMBER_OF_ATTEMPTS_FOR_ITERATION:
                #step_iterr_sum = abs(random.gauss(0, max_step))
                step_iterr_sum = abs(distribution(max_step))
            else:
                step_iterr_sum = max_step
            print('Max sum of steps for all parametors:', str(step_iterr_sum * 100) + '%', file=output)
                
            step_iterr = {}
            for parnames in [reg_parnames, icv_parnames]:
                 # формируем случайные числа step_iterr[p_1], ..., step_iterr[p_n] такие,
                 # что step_iterr[p_1] + ... + step_iterr[p_n] = step_iterr_sum,
                 # где [p_1, ..., p_n] = parnames.
                if len(parnames) == 0:
                    continue
                sum_tmp = 0
                for parname in parnames:
                    tmp = random.uniform(0, 1)
                    step_iterr[parname] = tmp
                    sum_tmp += tmp
                koef_tmp = step_iterr_sum / sum_tmp
                for parname in parnames:
                    step_iterr[parname] *= koef_tmp
            print('Steps for parametors:', file=output)
            print(' ', step_iterr, file=output)
            
            print('Directions for parametors:', file=output)
            attempt_is_bad = True
            new_reg_pv_list = []
            par_candidate_value = {}
            position_candidate = {}
            for parname in reg_parnames:
                coord = par.index_in_reg_seq[parname]
                for i in range(len(new_reg_pv_list), coord):
                    tmp_parname = par.reg_seq[i]
                    if tmp_parname in par_start_value:
                        new_reg_pv_list.append(par_start_value[tmp_parname])
                    else:
                        new_reg_pv_list.append(par.defaults[tmp_parname])
                if parname in par.doub_kind: # если parname связан с дублированием узлов,
                    index_0_flag = True # то proc_opers_num может его блокировать
                else:
                    index_0_flag = False
                if parname in par.reg_extend_regn_list: # если parname связан с увеличением числа узлов в регионе,
                    index_1_flag = True # то regn_opers_num может его блокировать
                else:
                    index_1_flag = False
                cond = lambda x_list: condition(x_list, coord, current_reg_pv_list, new_reg_pv_list, index_0_flag, index_1_flag)
                coin = random.choice([True, False])
                if coin:
                    right_list = value_par[parname][position[parname]:]
                    position_shift = shift(right_list, step_iterr[parname], sm_dis[parname], cond)
                    position_shift = corr_shift(right_list, position_shift, coord)
                    print(' ', parname, ': ->', file=output)
                else:
                    left_list = value_par[parname][:position[parname]]
                    left_list.reverse()
                    position_shift = shift(left_list, step_iterr[parname], sm_dis[parname], cond)
                    position_shift = - corr_shift(left_list, position_shift, coord)
                    print(' ', parname, ': <-', file=output)
                if position_shift != 0:
                    attempt_is_bad = False
                    
                position_candidate[parname] = position[parname] + position_shift
                par_candidate_value[parname] = \
                    get_value(parname, value_par, inf_value_par, sup_value_par,\
                              position_candidate[parname], min_position[parname], max_position[parname], coord)
                
                new_reg_pv_list.append(par_candidate_value[parname])
            
            new_icv_pv_list = []
            for parname in icv_parnames:
                coord = par.index_in_icv_seq[parname]
                for i in range(len(new_icv_pv_list), coord):
                    tmp_parname = par.icv_seq[i]
                    if tmp_parname in par_start_value:
                        new_icv_pv_list.append(par_start_value[tmp_parname])
                    else:
                        new_icv_pv_list.append(par.defaults[tmp_parname])
                cond = lambda x_list: icv_condition(x_list, coord, current_icv_pv_list, new_icv_pv_list)
                coin = random.choice([True, False])
                if coin:
                    right_list = value_par[parname][position[parname]:]
                    position_shift = shift(right_list, step_iterr[parname], sm_dis[parname], cond)
                    position_shift = corr_shift(right_list, position_shift, coord)
                    print(' ', parname, ': ->', file=output)
                else:
                    left_list = value_par[parname][:position[parname]]
                    left_list.reverse()
                    position_shift = shift(left_list, step_iterr[parname], sm_dis[parname], cond)
                    position_shift = - corr_shift(left_list, position_shift, coord)
                    print(' ', parname, ': <-', file=output)
                if position_shift != 0:
                    attempt_is_bad = False
                position_candidate[parname] = position[parname] + position_shift
                par_candidate_value[parname] = \
                    get_value(parname, value_par, inf_value_par, sup_value_par,\
                              position_candidate[parname], min_position[parname], max_position[parname], coord)
                new_icv_pv_list.append(par_candidate_value[parname])
                
            if attempt_is_bad:
                continue
            else:
                break
        else:
            print('There is not variants for candidate values in step', iterr, 'of the algorithm', file=output)
            print(file=output)
            #if gl.DECREASE_TEMPERATURE_BEFORE_UNFORTUNATE_ITERATIONS:
            #        j_for_temperature += 1
            continue
        
        tmp_dict = dict(par_start_value)
        tmp_dict.update(par_candidate_value)
        par_candidate_value = tmp_dict
        
        candidate_is_new = False
        if par_candidate_value in F_run_result[0]:
            print('There is F(result of run.sh on par_dict = ' + str(par_candidate_value) + ') in our database', file=output)
            ind = F_run_result[0].index(par_candidate_value)
            val_F_candidate = F_run_result[1][ind]
            print('F(...) = ', val_F_candidate, file=output)
        else:
            candidate_is_new = True
            result_candidate = clc.calculate_abs_values(procs_dic, par_candidate_value)
            j_for_exec_run += 1
            val_F_candidate = calculate_F(result_candidate, result_default)
            F_run_result[0].append(dict(par_candidate_value))
            F_run_result[1].append(val_F_candidate)
            F_run_result[2].append(None)
            F_run_result[3].append(None)
            ind = -1
            print('F(...) = ', val_F_candidate, file=verbose.F)
        
        if val_F_candidate < val_F_best:
            par_best_value = dict(par_candidate_value)
            if candidate_is_new:
                result_best = dict(result_candidate)
            else:
                raise BaseException('There is imposible. Not new list of pars is the best')
            val_F_best = val_F_candidate
            i_for_best_value = iterr
        
        current_to_candidate = False
        if val_F_candidate < val_F_current:
            current_to_candidate = True
            par_current_value = par_candidate_value
            val_F_current = val_F_candidate
            j_for_temperature += 1
            if not new_stat_for_every_step:
                    position = position_candidate
            print('Moving to the better value', file=output)
        else:
            delta_val_F = val_F_candidate - val_F_current
            chance_move = math.exp(- delta_val_F / temperature(j_for_temperature))
            if chance_move > random.random():
                current_to_candidate = True
                par_current_value = par_candidate_value
                val_F_current = val_F_candidate
                j_for_temperature += 1
                if not new_stat_for_every_step:
                    position = position_candidate
                print('Moving to the not better value with chance_move =', chance_move, file=output)
            else:
                if gl.TEMP_MODE == 0:
                    j_for_temperature += 1
                print('Not moving to the candidate value with chance_move =', chance_move, file=output)
        
        # current_to_new_candidate = current_to_candidate and candidate_is_new
        print(file=verbose.runs)
    
    par_value_print('The best values for parametors :', par_best_value, file=verbose.optval)
    print('The best values were found for', i_for_best_value, 'iterations of algorithm', file=output)
    print('The run-scripts was started for', j_for_exec_run * len(procs_dic), 'times', file=output)
    print('The best (t_c, t_e, m) is', result_best, file=output)
    print('The best value for F is', val_F_best, file=output)
    
    return (par_best_value, val_F_best, result_best)

def dcs_optimize(procs_dic,
                 par_start_value,
                 val_F_start,
                 result_start,
                 result_default,
                 check_zero_level = True,
                 dcs_zero_limit = gl.DSC_IMPOTANCE_LIMIT,
                 output = verbose.debug
                 ):
    
    j_for_exec_run = 0
    val_F_default = calculate_F(result_default, result_default)
    
    par_default_value = {parname : par.defaults[parname] for parname in par.dcs}
    
    # установка начальных значений для параметров
    # вычисление значения функционала при начальном значении параметров
    # в par_start_value могут быть заданы значения для тех параметров, которых нет в par.dcs,
    # и наоборот, не всем параметрам из par.dcs отображение par_start_value может сопоставлять значения.
    # Дополним par_start_value значениями по умолчанию для тех параметров из par.dcs,
    # которым par_start_value не сопоставлет никакого значения
    tmp_dict = dict(par_default_value)
    tmp_dict.update(par_start_value)
    par_start_value = tmp_dict
    # делаем так, чтобы par_start_value и par_default_value были определены на одном и томже списке параметров
    par_default_value = {parname : par.defaults[parname] for parname in par_start_value.keys()}
    
    par_value = dict(par_start_value)
    print('F_start = ', val_F_start, file=verbose.F)
    
    # установка начальных значений для лучшего значения функционала F и лучшего значения параметра
    if val_F_start < val_F_default:
        par_best_value = dict(par_start_value)
        result_best = dict(result_start)
        val_F_best = val_F_start
    else:
        par_best_value = dict(par_default_value)
        result_best = dict(result_default)
        val_F_best = val_F_default
    
    dis = stat.get_dcs_dis(procs_dic)
    dcs_levels = range(0, gl.MAX_DCS_LEVEL + 1)
    for lv in dcs_levels:
        print(file=output)
        print('dcs_level:', lv, file=output)
        if lv == 0 or dis[lv] > dcs_zero_limit:
            if lv == 0:
                if not check_zero_level:
                    continue
                par_value.update({'dcs_kill': False, 'dcs_level': lv})
            else:
                par_value.update({'dcs_kill': True, 'dcs_level': lv})
            if par_value == par_start_value:
                print('Result of dcs optimization in the level', lv, 'is already known', file=output)
                continue
            result_candidate = clc.calculate_abs_values(procs_dic, par_value)
            j_for_exec_run += 1
            val_F_candidate = calculate_F(result_candidate, result_default)
            print('F(...) = ', val_F_candidate, file=verbose.F)
            if val_F_candidate < val_F_best:
                par_best_value = dict(par_value)
                result_best = dict(result_candidate)
                val_F_best = val_F_candidate
        else:
            print('Dcs optimization in the level', lv, 'will not be effective', file=output)
    
    print(file=output)
    par_value_print('The best values for parametors :', par_best_value, file=verbose.optval)
    print('The run-scripts was started for', j_for_exec_run * len(procs_dic), 'times', file=output)
    print('The best (t_c, t_e, m) is', result_best, file=output)
    print('The best value for F is', val_F_best, file=output)
    
    return (par_best_value, val_F_best, result_best)
    
def optimize_bool_par(procs_dic, parname,
                      par_start_value,
                      val_F_start,
                      result_start,
                      result_default,
                      output = verbose.default
                      ):
    
    j_for_exec_run = 0
    val_F_default = calculate_F(result_default, result_default)
    
    par_default_value = {parname : par.defaults[parname]}
    
    # установка начальных значений для параметров
    # вычисление значения функционала при начальном значении параметров
    tmp_dict = dict(par_default_value)
    tmp_dict.update(par_start_value)
    par_start_value = tmp_dict
    # делаем так, чтобы par_start_value и par_default_value были определены на одном и томже списке параметров
    par_default_value = {parname : par.defaults[parname] for parname in par_start_value.keys()}
            
    print('F_start = ', val_F_start, file=verbose.F)
    print(file=verbose.runs)
    
    # установка начальных значений для лучшего значения функционала F и лучшего значения параметра
    if val_F_start < val_F_default:
        par_best_value = dict(par_start_value)
        result_best = dict(result_start)
        val_F_best = val_F_start
    else:
        par_best_value = dict(par_default_value)
        result_best = dict(result_default)
        val_F_best = val_F_default
    
    par_value = dict(par_start_value)
    # пробуем другое значение для булевой переменной, по которой хотим произвести оптимизацию
    par_value[parname] = not par_value[parname]
    print('Switch parametor', parname, 'to value : ', par_value[parname], file=output)
    
    result_candidate = clc.calculate_abs_values(procs_dic, par_value)
    j_for_exec_run += 1
    val_F_candidate = calculate_F(result_candidate, result_default)
    print('F(...) = ', val_F_candidate, file=verbose.F)
    print(file=verbose.runs)
    
    if val_F_candidate < val_F_best:
        par_best_value = dict(par_value)
        result_best = dict(result_candidate)
        val_F_best = val_F_candidate
    
    par_value_print('The best values for parametors :', par_best_value, file=verbose.optval)
    print('The run-scripts was started for', j_for_exec_run * len(procs_dic), 'times', file=output)
    print('The best (t_c, t_e, m) is', result_best, file=output)
    print('The best value for F is', val_F_best, file=output)
    
    return (par_best_value, val_F_best, result_best)

def par_value_print(head, par_value, file=verbose.optval, space = '    ' if gl.VERBOSE else '', sep = ':'):
    print(head, file=verbose.screen)
    for par in par_value:
        print(space, par, sep, par_value[par], file=file)


# Запуск ИС в подрежиме "метод имитации отжига"
def run():

    # проверка корректности стратегии
    par.check_strategy()
    
    # Подгружаем базу данных
    train.DB.load()

    # Получаем стратегию, спеки, и начальную точку значений параметров
    strategy = par.strategy()
    specs = par.specs()
    par_start = gl.PAR_START
    is_seq = gl.SEQ_OPTIMIZATION_WITH_STRATEGY
    
    output = verbose.screen
    space = '  '

    print('Run annealing for specs', file = output)
    for spec, procs in specs.items():
        print(space, spec, ':', (', '.join(procs) if procs else 'all procedures'), file = output)

    print('with respect to the ' + ('sequential' if is_seq else 'independent') + ' strategy', file = output)
    for group in strategy:
        print(space, ', '.join(group), file = output)
    
    # Перед вызовом внешних скриптов надо удостовериться, что заданы каталоги для сбора статистики и весов исполняемых процедур
    if not gl.INHERIT_STAT and gl.DINUMIC_STAT_PATH is None:
        verbose.undef(gl.DINUMIC_STAT_PATH.param)
    if gl.PROC_WEIGHT_PATH == None:
        verbose.undef(gl.PROC_WEIGHT_PATH.param)
        
    # Вычисляем значение времени компиляции, времени исполнения и объема потребляемой памяти для значений параметров по умолчанию
    try:
        defaults = clc.calculate_abs_values(specs, {})
    except gl.IntsysError as error:
        verbose.error('in calculating default (t_c, t_e, m):\n%s' % error)
    
    # Вычисляем значение времени компиляции, времени исполнения и объема потребляемой памяти для начальной точки значений
    try:
        if par.is_default(par_start):
            print('with start point: default values', file = output)
            starts = defaults
        else:
            par_value_print('with start point:', par_start, file = output, space = space)
            starts = clc.calculate_abs_values(specs, par_start)
    except gl.IntsysError as error:
        verbose.error('in calculating start (t_c, t_e, m):\n%s' % error)
        
    # проверка корректности статистики
    stat.check()
    
    # Получаем распределения параметров
    print('Calculate parameters distribution ... ', end='', flush=True, file = verbose.trace)
    try:
        dis_regpar = stat.get_dis_regpar(specs)
        dis_icvpar = stat.get_dis_icvpar(specs)
    except gl.IntsysError as error:
        verbose.error(str(error))
    print('ok', file = verbose.trace)
    
    pv, fv, rv = par_start, calculate_F(starts, defaults), starts
    
    for group in strategy:
        print(file = verbose.screen)
        print('---------------------------------------------------------------------------', file = verbose.groupname)
        print('Group of parametors: %s\n' % str(group), file = verbose.screen)
        
        try:
            if any (p in par.dcs for p in group):
                next_pv, next_fv, next_rv = dcs_optimize(specs, pv, fv, rv, defaults)

            elif any (p in par.nesting for p in group):
                next_pv, next_fv, next_rv = optimize_bool_par(specs, group[0], pv, fv, rv, defaults)

            else:
                next_pv, next_fv, next_rv = optimize(specs, group, dis_regpar, dis_icvpar, pv, fv, rv, defaults)

            if is_seq:
                pv, fv, rv = next_pv, next_fv, next_rv
    
        except gl.IntsysError as error:
            print(error)
    
    if is_seq:
        print('\n---------------------------------------------------------------------------\n', file = verbose.groupname)
        par_value_print('The final values :', pv, file=verbose.silent)
        print('The final (t_c, t_e, m) is', fv, file=verbose.debug)
        print('The final value for F is', rv, file=verbose.debug)

