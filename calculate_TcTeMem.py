#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
import os, random, shutil
from subprocess import Popen, PIPE
from sys import maxsize

# Internal imports
import par, read
import options as gl
import train_data as tr_data
import output

# Вычилсяем папку, из которой запущен процесс
PWD = os.getcwd()

class ExternalScriptError(BaseException):
    pass

def get_cmd_pars(task_name, par_value, procname_list = None):
    """ Формирует опции и аргументы для передачи внешнему скрипту
    """
    cmd = task_name 
    if len(par_value) != 0 or procname_list != None:
        cmd += ' \"'
        for par_name in par_value.keys():
            if par.val_type[par_name] == float:
                cmd += '--letf=' + par_name + ':' + str(par_value[par_name]) + ' '
            elif par.val_type[par_name] == int:
                cmd += '--let=' + par_name + ':' + str(par_value[par_name]) + ' '
            elif par.val_type[par_name] == bool:
                if par_value[par_name]:
                    cmd += '--true=' + par_name + ' '
                else:
                    cmd += '--false=' + par_name + ' '
            else:
                raise BaseException('Unknown type of par')
        if procname_list != None:
            for procname in procname_list:
                cmd += '--debug_proc=' + procname + ' '
        cmd = cmd[:-1] # удаляем последний символ (лишний пробел)
        cmd += '\"'
    return cmd
    
def calculate_abs_values(procs_dic, par_value, separate_procs = False, output = output.runs):
    """ Запускает внешние скипты на задачах из procs_dic со значениями параметров из par_value
        и получает абсолютные значения времени компиляции, времени исполнения и объема потребляемой памяти
    """
    exec_proc = None
    el_pred = None
    result_comp = {}
    result_exec = {}
    result_maxmem = {}
    
    if separate_procs:
        elements = []
        for taskname, procname_list in procs_dic.items():
            if procname_list == None:
                raise BaseException('Warning: there are many runs for run.sh')
            for procname in procname_list:
                elements.append((taskname, procname))
    else:
        elements = list(procs_dic.keys())
        
    
    # Вычисляем абсолютный путь к скриптам SCRIPT_COMP, SCRIPT_EXEC, SCRIPT_COMP_WITH_STAT
    SCRIPT_COMP = os.path.abspath(gl.SCRIPT_COMP)
    SCRIPT_EXEC = os.path.abspath(gl.SCRIPT_EXEC)
    SCRIPT_COMP_WITH_STAT = os.path.abspath(gl.SCRIPT_COMP_WITH_STAT)
        
    tmpdir_name = 'tmp' + '_' + str(random.randrange(10**10))
    os.mkdir(tmpdir_name)
    tmpdir_path = os.path.join(PWD, tmpdir_name)
    os.chdir(tmpdir_path)
    os.system("cp /auto/bokov_g/msu/bin/cmp_spec/*.sh .")
#    shutil.copy( "/auto/bokov_g/msu/bin/cmp_spec/*.sh", ".")
        
    for el in elements:
        if separate_procs:
            taskname = el[0]
            proclist = [el[1]]
        else:
            taskname = el
            proclist = procs_dic[el]
        cmd_pars = get_cmd_pars(taskname, par_value, proclist)
        
        
        # Подсчет времени компиляции для el
        cmd_comp = SCRIPT_COMP + ' ' + cmd_pars
        print(cmd_comp, file=output)
        comp_proc = Popen(cmd_comp, shell=True, stdout=PIPE, stderr=PIPE)
        comp_proc.wait()
        tmp_result = comp_proc.communicate()
        print("comp_time#" + tmp_result[0].decode('utf-8'), end='', file=output)
        if comp_proc.returncode:
            print('comp_error#' + tmp_result[1].decode('utf-8'), file=output)
        try:
            result_comp[el] = float(tmp_result[0])
        except ValueError as error:
            os.chdir(PWD)
            shutil.rmtree(tmpdir_path)
            raise ExternalScriptError(error)
        
        if el != elements[0]:
            # Подсчет времени исполнения для el_pred
            exec_proc.wait()
            tmp_result = exec_proc.communicate()
            print("exec_time#" + tmp_result[0].decode('utf-8'), end='', file=output)
            if exec_proc.returncode:
                print('exec_error#' + tmp_result[1].decode('utf-8'), file=output)
            try:
                result_exec[el_pred] = float(tmp_result[0])
            except ValueError as error:
                os.chdir(PWD)
                shutil.rmtree(tmpdir_path)
                raise ExternalScriptError(error)
            
            if separate_procs:
                taskname_pred = el_pred[0]
                proclist_pred = [el_pred[1]]
            else:
                taskname_pred = el_pred
                proclist_pred = procs_dic[el_pred]
            # Добавление результата запуска в tr_data для el_pred
            tr_data.data.add(taskname_pred, proclist_pred, par_value, result_comp[el_pred], result_exec[el_pred], result_maxmem[el_pred])
        
        # Запуск на исполнение для el
        cmd_exec = SCRIPT_EXEC + ' ' + cmd_pars + ' \"' + tmpdir_path + '\"'
        print(cmd_exec, file=output)
        exec_proc = Popen(cmd_exec, shell=True, stdout=PIPE, stderr=PIPE)
        el_pred = el
        
        # Подсчет объема потребляемой памяти для el
        cmd_comp = SCRIPT_COMP_WITH_STAT + ' ' + cmd_pars
        print(cmd_comp, file=output)
        comp_proc = Popen(cmd_comp, shell=True, stdout=PIPE, stderr=PIPE)
        comp_proc.wait()
        tmp_result = comp_proc.communicate()
        print("max_mem#" + tmp_result[0].decode('utf-8'), end='', file=output)
        if comp_proc.returncode:
            print('comp_with_stat_error#' + tmp_result[1].decode('utf-8'), file=output)
        try:
            result_maxmem[el] = float(tmp_result[0])
        except ValueError as error:
            os.chdir(PWD)
            shutil.rmtree(tmpdir_path)
            raise ExternalScriptError(error)
    
    # Подсчет времени исполнения для последнего элемента в elements
    exec_proc.wait()
    tmp_result = exec_proc.communicate()
    print("exec_time#" + tmp_result[0].decode('utf-8'), end='', file=output)
    if exec_proc.returncode:
        print('exec_error#' + tmp_result[1].decode('utf-8'), file=output)
    try:
        result_exec[el] = float(tmp_result[0])
    except ValueError as error:
            os.chdir(PWD)
            shutil.rmtree(tmpdir_path)
            raise ExternalScriptError(error)
    # Добавление результата запуска в tr_data для последнего элемента в elements
    tr_data.data.add(taskname, proclist, par_value, result_comp[el], result_exec[el], result_maxmem[el])
    
    os.chdir(PWD)
    shutil.rmtree(tmpdir_path)
    
    result = {}
    for el in elements:
        result[el] = (result_comp[el], result_exec[el], result_maxmem[el])
    
    return result
