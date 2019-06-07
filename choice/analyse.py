#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
import os
from subprocess import Popen, PIPE
from functools import reduce
from scipy import interpolate
import numpy as np
import matplotlib.pyplot as plt

# Internal imports
import global_vars as gl
import par
import read
from stat_adaptation import get_dcs_dis
from optimize import F


def eff_all_pars():
    eff = {}
    for parname in par.reg_seq + par.icv_seq:
        eff[parname] = par_eff(parname)
        print()
    
    print('t_c-effectiveness for pars')
    table(eff, 0)
    print('t_e-effectiveness for pars')
    table(eff, 1)
    print('mem-effectiveness for pars')
    table(eff, 2)
    print('F-effectiveness for pars')
    table(eff, 3)

def table(eff, coord):
    '''
    coord = 0 -> t_c,
    coord = 1 -> t_e,
    coord = 2 -> mem,
    coord = 3 -> F
    '''
    array = list(eff.items())
    array.sort(key = lambda x: x[1][coord])
    for (parname, it) in array:
        print(parname.ljust(26) + ':', it[coord])
    print()
    
    
def par_eff(parname, mode = 0):
    '''Функция определяет эффективность параметра'''
    print('Parname:', parname)
    ef_Tc_cnt = 0
    ef_Te_cnt = 0
    ef_M_cnt = 0
    ef_F_cnt = 0
    task_cnt = 0
    
    print(''.ljust(17) + ' ', 't_c'.rjust(5), 't_e'.rjust(5), 'mem'.rjust(5), 'F'.rjust(5), 'parvalue'.rjust(10))

    for taskname in read.task_list():
        tresult = []
        filepath = gl.RUN_LOGS_PATH + '/' + taskname + '.' + parname + '.txt'
        if os.path.exists(filepath):
            tresult += percent(read_logfile_function(filepath, taskname))
        filepath = gl.RUN_LOGS_PATH + '/5tasks_some_results/' + parname + 'all_tasks.txt'
        if os.path.exists(filepath):
            tresult += percent(read_logfile_function(filepath, taskname))
        #else:
            #filepath = gl.RUN_LOGS_PATH + '/results_v5/' + taskname + '.' + parname + '.txt'
            #if os.path.exists(filepath):
                #exist_resultfile = True
        tresult = list(filter(lambda it: it[3] < 1. / 7, tresult))
        if tresult:
            task_cnt += 1
            min_Tc = tresult[0]
            min_Te = tresult[0]
            min_M = tresult[0]
            min_F = tresult[0]
            for it in tresult:
                if it[0] < min_Tc[0]:
                    min_Tc = it
                if it[1] < min_Te[1]:
                    min_Te = it
                if it[2] < min_M[2]:
                    min_M = it
                if it[3] < min_F[3]:
                    min_F = it
            if min_Tc[0] < - gl.DEVIATION_PERCENT_OF_TcTeMemF:
                ef_Tc_cnt += 1
            if min_Te[1] < - gl.DEVIATION_PERCENT_OF_TcTeMemF:
                ef_Te_cnt += 1
            if min_M[2] < - gl.DEVIATION_PERCENT_OF_TcTeMemF:
                ef_M_cnt += 1
            if min_F[3] < - gl.DEVIATION_PERCENT_OF_TcTeMemF:
                ef_F_cnt += 1
            
            print (taskname.ljust(17) + ':', end = ' ')
            if mode == -1:
                 print (percent_view(min_Tc[0]), percent_view(min_Te[1]), percent_view(min_M[2]), percent_view(min_F[3]),'  ', min_F[4])
            elif mode == 0:
                print (percent_view(min_Tc[0]), percent_view(min_Tc[1]), percent_view(min_Tc[2]), percent_view(min_Tc[3]),'  ', min_Tc[4])
            elif mode == 1:
                print (percent_view(min_Te[0]), percent_view(min_Te[1]), percent_view(min_Te[2]), percent_view(min_Te[3]),'  ', min_Te[4])
            elif mode == 2:
                print (percent_view(min_M[0]), percent_view(min_M[1]), percent_view(min_M[2]), percent_view(min_M[3]),'  ', min_M[4])
            elif mode == 3:
                print (percent_view(min_F[0]), percent_view(min_F[1]), percent_view(min_F[2]), percent_view(min_F[3]),'  ', min_F[4])
        #else:
        #    print( 'There is not result for ', (taskname, parname))
    #print( 'task_num =', task_cnt)
    #print(('Cnt >=' + percent_view(gl.DEVIATION_PERCENT_OF_TcTeMemF)).ljust(17) + ':', end=' ')
    #print(str(ef_Tc_cnt).rjust(5), str(ef_Te_cnt).rjust(5), str(ef_M_cnt).rjust(5), str(ef_F_cnt).rjust(5))
                
    
    return ef_Tc_cnt, ef_Te_cnt, ef_M_cnt, ef_F_cnt

def percent(array, num = 4):
    if len(array) == 0:
        return []
    item_default = tuple(array[0])
    for item in array:
        for ind in range(num):
            item[ind] /= item_default[ind]
            item[ind] -= 1
    return array

def percent_view(x, ndigits = 1):
    tmp = round(100 * x, ndigits)
    if tmp != 0:
        tmp = -tmp
    tmp_str = str(tmp) + '%'
    
    return tmp_str.rjust(5)

def read_TcTeMemF_database(rel_mode = True, bad_points = True, off_F_limit = False, allow_empty = False):
    """
        result = [(taskname, parname, tp_result), ...]
    """
    result = []
    for parname in par.reg_seq + par.icv_seq:
        for taskname in read.task_list():
            tp_result = []
            filepath = gl.RUN_LOGS_PATH + '/' + taskname + '.' + parname + '.txt'
            if os.path.exists(filepath):
                tp_result += read_logfile_function(filepath, taskname)
            filepath = gl.RUN_LOGS_PATH + '/5tasks_some_results/' + parname + 'all_tasks.txt'
            if os.path.exists(filepath):
                tp_result += read_logfile_function(filepath, taskname)
            if not tp_result:
                if allow_empty:
                    result.append((taskname, parname, tp_result))
                continue
            if not bad_points:
                Tc_0, Te_0, Mem_0 = tp_result[0][0], tp_result[0][1], tp_result[0][2]
                def not_bad_point(x):
                    return (
                        x[0] / Tc_0 <= 1 + gl.COMP_TIME_INCREASE_ALLOWABLE_PERCENT and
                        x[1] / Te_0 <= 1 + gl.EXEC_TIME_INCREASE_ALLOWABLE_PERCENT and
                        x[2] / Mem_0 <= 1 + gl.MEMORY_INCREASE_ALLOWABLE_PERCENT
                        )
                tp_result = list(filter(not_bad_point, tp_result))
            if bad_points and off_F_limit:
                trio_default = tp_result[0][:3]
                for it in tp_result:
                    ci = gl.TIME_COMP_IMPOTANCE
                    ei = gl.TIME_EXEC_IMPOTANCE
                    mi = gl.MEMORY_IMPOTANCE
                    it[3] = ci * it[0] / trio_default[0] + ei * it[1] / trio_default[1] + mi * it[2] / trio_default[2]
            if rel_mode:
                tp_result = percent(tp_result)
            result.append((taskname, parname, tp_result))
    return result
            
def print_TcTeMemF_database(data_TcTeMemF):
    for item in data_TcTeMemF:
        space = '    '
        print (item[0], item[1])
        for x in item[2]:
            print (space, x)

def TcTeMemF_from_log_for_several_tasks(filepath, taskname):
    cmd = 'grep -C 1 "#" '+ filepath
    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    proc.wait()
    proc_result = proc.communicate()
    if proc.returncode:
        raise BaseException(proc_result[1].decode('utf-8'))
    
    iterations = proc_result[0].decode('utf-8').split('--\n')
    result = []
    for itr in iterations:
        strs = itr.split('\n')
        parname = strs[0].split('=')[1].split(':')[0]
        parvalue_str = strs[0].split('\"')[1].split(':')[1]
        parvalue = par.val_type[parname](parvalue_str)
        
        # Поиск значений t_c, t_e, mem для запуска задачи taskname на итерации itr
        strs_iter = iter(strs)
        for st in strs_iter:
            if taskname in st:
                break
        else:
            continue # если задача не найдена, то переходим к следующей итерации
            # break # может быть лучше даже так
        for st in strs_iter:
            if 'comp_time#' in st:
                t_c = float(st.split('#')[1])
                break
        else:
            continue
        for st in strs_iter:
            if 'max_mem#' in st:
                mem = float(st.split('#')[1])
                break
        else:
            continue
        for st in strs_iter:
            if 'exec_time#' in st:
                t_e = float(st.split('#')[1])
                break
        else:
            continue
        trio = (t_c, t_e, mem)
        
        itr_item = [t_c, t_e, mem, None, parvalue]
        result.append(itr_item)
        
    if len(result) == 0:
        return result
    else:
        trio_default = result[0][:3]
        for itr_item in result:
            trio = itr_item[:3]
            rel_trio = (trio[0] / trio_default[0], trio[1] / trio_default[1], trio[2] / trio_default[2])
            Fvalue = F([rel_trio])
            itr_item[3] = Fvalue
    
    return result
        

def TcTeMemF(filepath):
    '''Производит разбор лога работы функции нахождения оптимального значения параметра '''
    #cmd = 'grep -A 2 bin ' + filepath + ' | grep -v "#"'
    cmd = 'grep -A 2 bin ' + filepath
    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    proc.wait()
    proc_result = proc.communicate()
    if proc.returncode:
        raise BaseException(proc_result[1].decode('utf-8'))
    
    iterations = proc_result[0].decode('utf-8').split('--\n')
    
    result = []
    for itr in iterations:
        strs = itr.split('\n')
        
        parname = strs[0].split('=')[1].split(':')[0]
        parvalue_str = strs[0].split('\"')[1].split(':')[1]
        parvalue = par.val_type[parname](parvalue_str)
        
        trio = strs[1][1:].split()
        t_c, t_e, mem = map(float, trio)
        
        Fvalue = float(strs[2].split()[2])
        
        itr_item = [t_c, t_e, mem, Fvalue, parvalue]
        result.append(itr_item)
    
    return result

def is_logfile_in_newdata_TcTeMemFformat(filepath):
    cmd = 'grep exec_time ' + filepath
    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    proc.wait()
    proc_result = proc.communicate()
    if proc.returncode == 2:
        raise BaseException(proc_result[1].decode('utf-8'))
    
    return bool(proc_result[0].decode('utf-8'))
    
def read_logfile_function(filepath, taskname):
    if is_logfile_in_newdata_TcTeMemFformat(filepath):
        #return TcTeMemF_newdata_TcTeMemFformat(filepath)
        return TcTeMemF_from_log_for_several_tasks(filepath, taskname)
    else:
        return TcTeMemF(filepath)

def med_TcTeMemF_default(taskname, print_more = False):
    cnt = 0
    sum_Tc = 0.
    sum_Te = 0.
    sum_Mem = 0.
    sum_F = 0.
    for parname in par.reg_seq + par.icv_seq:
        filepath = gl.RUN_LOGS_PATH + '/' + taskname + '.' + parname + '.txt'
        exist_resultfile = False
        if os.path.exists(filepath):
            exist_resultfile = True
        else:
            filepath = gl.RUN_LOGS_PATH + '/results_v5/' + taskname + '.' + parname + '.txt'
            if os.path.exists(filepath):
                exist_resultfile = True
        if exist_resultfile:
            cnt += 1
            tresult_default = read_logfile_function(filepath, taskname)[0]
            if print_more:
                print(tresult_default)
            sum_Tc += tresult_default[0]
            sum_Te += tresult_default[1]
            sum_Mem += tresult_default[2]
            sum_F += tresult_default[3]
    if cnt == 0:
        return None
    else:
        return [round(x, 2) for x in (sum_Tc / cnt, sum_Te / cnt, sum_Mem / cnt)]
    
def time_to_human_format(time):
    '''
    Convert time in seconds to format (h, m, s)
    '''
    time = int(round(time))
    htime = time // 3600
    mtime = time % 3600 // 60
    stime = time % 3600 % 60
    
    time_str = ''
    if htime != 0:
        time_str += str(htime) + 'h'
    if mtime != 0:
        time_str += str(mtime) + 'm'
    if stime != 0:
        time_str += str(stime) + 's'
    
    return time_str

def all_tasks_TcTeMem(human_format = False):
    for task in read.task_list():
        print(task)
        TcTeMem_default = med_TcTeMemF_default(task)
        #print '  ', TcTeMem_default
        if TcTeMem_default != None:
            print('  ', time_to_human_format(TcTeMem_default[0] + TcTeMem_default[1]))
            #print '  ', time_to_human_format(TcTeMem_default[1])
        else:
            print('  ', None)


def dcs_information_print():
    '''
    Печатает процент мертвых узлов, ребер и циклов в каждом спеке
    '''
    dcs_levels = range(1, gl.MAX_DCS_LEVEL + 1)
    for task in read.task_list():
        print(task)
        print(' lv:  ', reduce(lambda x, y: x + y, [str(x).rjust(4) + ' ' for x in dcs_levels]))
        dis = get_dcs_dis({task: None}, 1, 0, 0)[1:]
        print(' N:   ', reduce(lambda x, y: x + y, map(percent_view, dis)))
        dis = get_dcs_dis({task: None}, 0, 1, 0)[1:]
        print(' E:   ', reduce(lambda x, y: x + y, map(percent_view, dis)))
        dis = get_dcs_dis({task: None}, 0, 0, 1)[1:]
        print(' L:   ', reduce(lambda x, y: x + y, map(percent_view, dis)))
        dis = get_dcs_dis({task: None}, 1, 1, 1)[1:]
        print(' Sum: ', reduce(lambda x, y: x + y, map(percent_view, dis)))
        print()
    
    print('All tasks')
    procs_dic = {task: None for task in read.task_list()}
    print(' lv:  ', reduce(lambda x, y: x + y, [str(x).rjust(4) + ' ' for x in dcs_levels]))
    dis = get_dcs_dis(procs_dic, 1, 0, 0)[1:]
    print(' N:   ', reduce(lambda x, y: x + y, map(percent_view, dis)))
    dis = get_dcs_dis(procs_dic, 0, 1, 0)[1:]
    print(' E:   ', reduce(lambda x, y: x + y, map(percent_view, dis)))
    dis = get_dcs_dis(procs_dic, 0, 0, 1)[1:]
    print(' L:   ', reduce(lambda x, y: x + y, map(percent_view, dis)))
    dis = get_dcs_dis(procs_dic, 1, 1, 1)[1:]
    print(' Sum: ', reduce(lambda x, y: x + y, map(percent_view, dis)))

def modename(mode):
    if mode == 0:
        return 't_c'
    elif mode == 1:
        return 't_e'
    elif mode == 2:
        return 'mem'
    elif mode == 3:
        return 'F'

def best_points(data_TcTeMemF, mode = 3, limit = 0.01, keyform = 't'):
    """
        keyform -> 't', 'p', 'tp'
    """
    newdata_TcTeMemF = []
    for tp_it in data_TcTeMemF:
        for rs in tp_it[2]:
            newdata_TcTeMemF.append(rs + [tp_it[0], tp_it[1]])
    newdata_TcTeMemF.sort(key = lambda x: x[mode], reverse = False)
    
    filt = []
    base = set()
    for it in newdata_TcTeMemF:
        if keyform == 'tp':
            key = (it[-2], it[-1])
        elif keyform == 't':
            key = it[-2]
        elif keyform == 'p':
            key = it[-1]
        if not key in base and it[mode] <= -limit:
            base.add(key)
            filt.append(it)
    
    wtask = max(map(lambda x: len(x[-2]), filt))
    wpar = max(map(lambda x: len(x[-1]), filt))
    wval = max(map(lambda x: len(str(x[-3])), filt))
    print ('Taskname'.ljust(wtask), 'Parname'.ljust(wpar), ' ', 'parvalue'.ljust(wval), modename(mode).center(5))
    filt.reverse()
    for it in filt:
        for i in range(4):
            it[i] = percent_view(it[i])
        print (it[-2].ljust(wtask), it[-1].ljust(wpar), ' ', str(it[-3]).ljust(wval), it[mode])

def get_sp(data_TcTeMemF, kind = 'slinear', mode = 3):
    """
        [[taskname, parname, f, x_min, x_max, y_default]]
        kind -> 'linear', 'quadratic', 'cubic'
    """
    result = []
    for item in data_TcTeMemF:
        #item[2].sort(key = lambda it: it[4])
        x = list(map(lambda it: it[4], item[2]))
        y = list(map(lambda it: it[mode], item[2]))
        f = interpolate.interp1d(x, y, kind=kind, fill_value="extrapolate")
        y_default = item[2][0][mode]
        x_min = min(x)
        x_max = max(x)
        result.append([item[0], item[1], f, x_min, x_max, y_default])
    return result

def get_intervals(sp, step_f = 0.01, step_i = 50, draw = False):
    for parname in par.reg_seq + par.icv_seq:
        print ('Parname', ':', parname)
        space = '    '
        psp = list(filter(lambda it: it[1] == parname, sp))
        p_min = min(map(lambda it: it[3], psp))
        p_max = max(map(lambda it: it[4], psp))
        #tf = map(lambda it: it[2], psp)
        def good_point_max(pnt):
            for it in psp:
                f = it[2]
                y_default = it[-1]
                if f(pnt) < y_default:
                    continue
                else:
                    return False
            return True
        def good_point_av(pnt):
            tmp = 1.
            y_default = psp[0][-1]
            for it in psp:
                f = it[2]
                tmp *= f(pnt)
            if tmp ** (1 / len(psp)) < y_default:
                return True
            else:
                return False
        def good_point_mean(pnt):
            tmp = 0
            y_default = psp[0][-1]
            for it in psp:
                f = it[2]
                tmp += f(pnt)
            if tmp  / len(psp) < y_default:
                return True
            else:
                return False
        if par.val_type[parname] == int:
            x = np.arange(p_min, p_max + 1, step = step_i, dtype = np.int32)
            #continue
        else:
            x = np.arange(p_min, p_max + step_f, step = step_f)
        if draw:
            for it in psp:
                f = it[2]
                plt.plot(x, f(x), label = it[0])
            plt.ylabel(modename(mode))
            plt.title(parname)
            # plt.legend()
            plt.show()
        print(np.array(list(filter(good_point_max, x))))


if __name__ == '__main__':
    #eff_all_pars()
    #dcs_information_print()
    #all_tasks_TcTeMem()
    #filepath = '/home/konoval/Эльбрус/nir_2018-2019/result_from_real_data/5tasks_some_results/ifconv_merge_heurall_tasks.txt'
    #taskname = '544.nab'
    #for el in TcTeMemF_from_log_for_several_tasks(filepath, taskname):
    #    print el
    #for parname in par.reg_seq + par.icv_seq:
    #    print('default_value_' + parname, '=', par.default_value[parname])
    data_TcTeMemF = read_TcTeMemF_database(rel_mode = True, bad_points = True, off_F_limit = True)
    mode = 2
    print('Mode:', modename(mode))
    sp = get_sp(data_TcTeMemF, mode = mode)
    get_intervals(sp, draw = True)
    
def resultfile_to_picture(filepath, taskname):
    iterations = read_logfile_function(filepath, taskname)
    
    x_array = []
    y_array = []
    for itr in iterations:
        Fvalue = itr[3]
        parvalue = itr[4]
        x_array.append(parvalue)
        
        Fvalue_default = gl.TIME_COMP_IMPOTANCE + gl.TIME_EXEC_IMPOTANCE + gl.MEMORY_IMPOTANCE
        y_value = (Fvalue - Fvalue_default) * 100
        if y_value > 100:
            y_value = 100
        y_array.append(y_value)
        
    return x_array, y_array
