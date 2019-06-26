#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
import os, random, shutil
from subprocess import Popen, PIPE
import sys
from sys import maxsize

# Internal imports
import par
import options as gl
import train
import verbose

# Вычилсяем папку, из которой запущен процесс
PWD = os.getcwd()
SCRIPT_CMP_RUN = os.path.abspath(gl.SCRIPT_CMP_RUN)
SCRIPT_CMP_INIT = os.path.abspath(gl.SCRIPT_CMP_INIT)

class ExternalScriptError(BaseException):
    def __init__(self, value):
        self.parameter = value
    
    def __str__(self):
        return 'An error in external sript %r. %s' % (gl.SCRIPT_CMP_RUN, self.parameter)

# Инициализация внешнего скрипта
def init_ext_script(dir, output = verbose.runs):
    cmd = SCRIPT_CMP_INIT + ' ' + dir
    print(cmd, file=output)
    prog = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    prog.wait()

# Запуск внешнего срипта
def run_ext_script(mode, spec, opts, output = verbose.runs):
    assert(mode in gl.CMP_MODES)
    cmd = ( SCRIPT_CMP_RUN 
            + ' -' + mode 
            + ' -suite ' + gl.CMP_SUITE 
            + ' -spec ' + spec
            + ' -' + gl.COMP_MODE
            + ' -opt ' + opts
            + ' -dir ' + gl.DINUMIC_STAT_PATH
            + ' -server ' + (gl.EXEC_SERVER if mode == 'exec' else gl.COMP_SERVER))
    print(cmd, file=output)
    return Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)

# Опции для передачи внешнему скрипту
def ext_script_opts(task_name, par_value, procname_list = None):
    cmd = task_name 
    if len(par_value) != 0 or procname_list != None:
        cmd += ' \"'
        for par_name in par_value.keys():
            if par.types[par_name] == float:
                cmd += '--letf=' + par_name + ':' + str(par_value[par_name]) + ' '
            elif par.types[par_name] == int:
                cmd += '--let=' + par_name + ':' + str(par_value[par_name]) + ' '
            elif par.types[par_name] == bool:
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
    
# Запускает внешние скипты на задачах из procs_dic со значениями параметров из par_value
# и получает абсолютные значения времени компиляции, времени исполнения и объема потребляемой памяти
def calculate_abs_values(procs_dic, par_value, separate_procs = False, output = verbose.runs):

    exec_proc = None
    result_comp = {}
    result_exec = {}
    result_maxmem = {}

    elements = []
    for taskname, procname_list in procs_dic.items():
        if separate_procs:
            for procname in procname_list:
                elements.append((taskname, [procname]))
        else:
            elements.append((taskname, procname_list))
        
    tmpdir_name = 'tmp' + '_' + str(random.randrange(10**10))
    os.mkdir(tmpdir_name)
    tmpdir_path = os.path.join(PWD, tmpdir_name)
    os.chdir(tmpdir_path)

    init_ext_script(tmpdir_name, output)
        
    for el in elements:

        taskname = el[0]
        proclist = el[1]
        cmd_pars = ext_script_opts(taskname, par_value, proclist)

        # Запуск на компиляцию для el
        comp_proc = run_ext_script('comp', taskname, cmd_pars, output)
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
            
            taskname_pred = el_pred[0]
            proclist_pred = el_pred[1]

            # Добавление результата запуска в tr_data для el_pred
            train.DB.add(taskname_pred, proclist_pred, par_value, result_comp[el_pred], result_exec[el_pred], result_maxmem[el_pred])
        
        # Запуск на исполнение для el
        exec_proc = run_ext_script('exec', taskname, cmd_pars, output)
        el_pred = el
        
        # Подсчет объема потребляемой памяти для el
        comp_proc = run_ext_script('comp', taskname, cmd_pars, output)
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
    train.DB.add(taskname, proclist, par_value, result_comp[el], result_exec[el], result_maxmem[el])
    
    os.chdir(PWD)
    shutil.rmtree(tmpdir_path)
    
    result = {}
    for el in elements:
        result[el] = (result_comp[el], result_exec[el], result_maxmem[el])
    
    return result
