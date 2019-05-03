#!/usr/bin/python
# -*- coding: utf-8 -*-

# External imports
import os
from subprocess import Popen, PIPE

# Internal imports
import global_vars as gl
import par
import read
from stat_adaptation import get_dcs_dis

def eff_all_pars():
    eff = {}
    for parname in par.reg_seq + par.icv_seq:
        eff[parname] = par_eff(parname)
        print
    
    print 't_c-effectiveness for pars'
    table(eff, 0)
    print 't_e-effectiveness for pars'
    table(eff, 1)
    print 'mem-effectiveness for pars'
    table(eff, 2)
    print 'F-effectiveness for pars'
    table(eff, 3)

def table(eff, coord):
    '''
    coord = 0 -> t_c,
    coord = 1 -> t_e,
    coord = 2 -> mem,
    coord = 3 -> F
    '''
    array = eff.items()
    array.sort(lambda x, y: cmp(x[1][coord], y[1][coord]))
    for (parname, it) in array:
        print parname.ljust(26) + ':', it[coord]
    print
    
    
def par_eff(parname):
    '''Функция определяет эффективность параметра'''
    print 'Parname:', parname
    ef_Tc_cnt = 0
    ef_Te_cnt = 0
    ef_M_cnt = 0
    ef_F_cnt = 0
    task_cnt = 0
    print ''.ljust(17) + ' ', 't_c'.rjust(5), 't_e'.rjust(5), 'mem'.rjust(5), 'F'.rjust(5)
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
        if len(tresult) != 0:
            task_cnt += 1
            min_Tc = 0.
            min_Te = 0.
            min_M = 0.
            min_F = 0.
            for it in tresult:
                if it[0] < min_Tc:
                    min_Tc = it[0]
                if it[1] < min_Te:
                    min_Te = it[1]
                if it[2] < min_M:
                    min_M = it[2]
                if it[3] < min_F:
                    min_F = it[3]
            if min_Tc < - gl.DEVIATION_PERCENT_OF_TcTeMemF:
                ef_Tc_cnt += 1
            if min_Te < - gl.DEVIATION_PERCENT_OF_TcTeMemF:
                ef_Te_cnt += 1
            if min_M < - gl.DEVIATION_PERCENT_OF_TcTeMemF:
                ef_M_cnt += 1
            if min_F < - gl.DEVIATION_PERCENT_OF_TcTeMemF:
                ef_F_cnt += 1
            print taskname.ljust(17) + ':', percent_view(min_Tc), percent_view(min_Te), percent_view(min_M), percent_view(min_F)
        #else:
        #    print 'There is not result for ', (taskname, parname)
    #print 'task_num =', task_cnt
    print ('Cnt >=' + percent_view(gl.DEVIATION_PERCENT_OF_TcTeMemF)).ljust(17) + ':',
    print str(ef_Tc_cnt).rjust(5), str(ef_Te_cnt).rjust(5), str(ef_M_cnt).rjust(5), str(ef_F_cnt).rjust(5)
    return ef_Tc_cnt, ef_Te_cnt, ef_M_cnt, ef_F_cnt

def percent_view(x, ndigits = 1):
    tmp_str = str(abs(round(100 * x, ndigits))) + '%'
    return tmp_str.rjust(5)

def TcTeMemF_from_log_for_several_tasks(filepath, taskname):
    cmd = 'grep -C 1 "#" '+ filepath
    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    proc.wait()
    proc_result = proc.communicate()
    if proc.returncode:
        raise BaseException(proc_result[1])
    
    from optimize import F
    
    iterations = proc_result[0].split('--\n')
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
        raise BaseException(proc_result[1])
    
    iterations = proc_result[0].split('--\n')
    
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

def is_logfile_in_newformat(filepath):
    cmd = 'grep exec_time ' + filepath
    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    proc.wait()
    proc_result = proc.communicate()
    if proc.returncode == 2:
        raise BaseException(proc_result[1])
    
    return bool(proc_result[0])
    
def read_logfile_function(filepath, taskname):
    if is_logfile_in_newformat(filepath):
        #return TcTeMemF_newformat(filepath)
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
                print tresult_default
            sum_Tc += tresult_default[0]
            sum_Te += tresult_default[1]
            sum_Mem += tresult_default[2]
            sum_F += tresult_default[3]
    if cnt == 0:
        return None
    else:
        return map(lambda x: round(x, 2), (sum_Tc / cnt, sum_Te / cnt, sum_Mem / cnt))
    
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
        print task
        TcTeMem_default = med_TcTeMemF_default(task)
        #print '  ', TcTeMem_default
        if TcTeMem_default != None:
            print '  ', time_to_human_format(TcTeMem_default[0] + TcTeMem_default[1])
            #print '  ', time_to_human_format(TcTeMem_default[1])
        else:
            print '  ', None
    
#def TcTeMemF_newformat(filepath):
    #'''
    #Разбор логов нового форамата
    #'''
    #cmd = 'grep -A 2 "#" ' + filepath
    #proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    #proc.wait()
    #proc_result = proc.communicate()
    #if proc.returncode:
        #raise BaseException(proc_result[1])
    
    #iterations = proc_result[0].split('--\n')
    
    #result = []
    #for itr in iterations:
        #strs = itr.split('\n')
        
        #parname = strs[2].split('=')[1].split(':')[0]
        #parvalue_str = strs[2].split('\"')[1].split(':')[1]
        #parvalue = par.val_type[parname](parvalue_str)
        
        #t_c = float(strs[0].split('#')[1])
        #t_e = float(strs[4].split('#')[1])
        #mem = float(strs[3].split('#')[1])
        #Fvalue = float(strs[5].split()[2])
        
        #itr_item = [t_c, t_e, mem, Fvalue, parvalue]
        #result.append(itr_item)
    
    #return result

def percent(array):
    if len(array) == 0:
        return []
    item_default = tuple(array[0])
    for item in array:
        for ind in xrange(len(item) - 1):
            item[ind] /= item_default[ind]
            item[ind] -= 1
    return array

def dcs_information_print():
    '''
    Печатает процент мертвых узлов, ребер и циклов в каждом спеке
    '''
    dcs_levels = range(1, gl.MAX_DCS_LEVEL + 1)
    for task in read.task_list():
        print task
        print ' lv:  ', reduce(lambda x, y: x + y, map(lambda x: str(x).rjust(4) + ' ', dcs_levels))
        dis = get_dcs_dis({task: None}, 1, 0, 0)[1:]
        print ' N:   ', reduce(lambda x, y: x + y, map(percent_view, dis))
        dis = get_dcs_dis({task: None}, 0, 1, 0)[1:]
        print ' E:   ', reduce(lambda x, y: x + y, map(percent_view, dis))
        dis = get_dcs_dis({task: None}, 0, 0, 1)[1:]
        print ' L:   ', reduce(lambda x, y: x + y, map(percent_view, dis))
        dis = get_dcs_dis({task: None}, 1, 1, 1)[1:]
        print ' Sum: ', reduce(lambda x, y: x + y, map(percent_view, dis))
        print
    
    print 'All tasks'
    procs_dic = {task: None for task in read.task_list()}
    print ' lv:  ', reduce(lambda x, y: x + y, map(lambda x: str(x).rjust(4) + ' ', dcs_levels))
    dis = get_dcs_dis(procs_dic, 1, 0, 0)[1:]
    print ' N:   ', reduce(lambda x, y: x + y, map(percent_view, dis))
    dis = get_dcs_dis(procs_dic, 0, 1, 0)[1:]
    print ' E:   ', reduce(lambda x, y: x + y, map(percent_view, dis))
    dis = get_dcs_dis(procs_dic, 0, 0, 1)[1:]
    print ' L:   ', reduce(lambda x, y: x + y, map(percent_view, dis))
    dis = get_dcs_dis(procs_dic, 1, 1, 1)[1:]
    print ' Sum: ', reduce(lambda x, y: x + y, map(percent_view, dis))

if __name__ == '__main__':
    #eff_all_pars()
    #dcs_information_print()
    #all_tasks_TcTeMem()
    #filepath = '/home/konoval/Эльбрус/nir_2018-2019/result_from_real_data/5tasks_some_results/ifconv_merge_heurall_tasks.txt'
    #taskname = '544.nab'
    #for el in TcTeMemF_from_log_for_several_tasks(filepath, taskname):
    #    print el
    for parname in par.reg_seq + par.icv_seq:
        print 'default_value_' + parname, '=', par.default_value[parname]
    
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
