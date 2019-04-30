#!/usr/bin/python
# -*- coding: utf-8 -*-

# External imports
import os, random, shutil
from subprocess import Popen, PIPE
from sys import maxsize

# Internal imports
import par, read

# Вычилсяем папку, из которой запущен процесс
PWD = os.getcwd()

class ExternalScriptError(BaseException):
    pass

def get_cmd_pars(task_name, par_value, procname_list = None, output = None):
    cmd = task_name 
    if len(par_value) != 0 or procname_list != None:
        cmd += ' \"'
        for par_name in par_value.iterkeys():
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
    
def calculate_abs_values(procs_dic, par_value, separate_procs = False, output = None):
    exec_proc = None
    el_pred = None
    result_comp = {}
    result_exec = {}
    result_maxmem = {}
    
    if separate_procs:
        elements = []
        for taskname, procname_list in procs_dic.iteritems():
            if procname_list == None:
                raise BaseException('Warning: there are many runs for run.sh')
            for procname in procname_list:
                elements.append((taskname, procname))
    else:
        elements = procs_dic.keys()
        
    
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
            cmd_pars = get_cmd_pars(el[0], par_value, [el[1]], output)
        else:
            cmd_pars = get_cmd_pars(el, par_value, procs_dic[el], output)
            
        cmd_comp = SCRIPT_COMP + ' ' + cmd_pars
        print >> output, cmd_comp
        comp_proc = Popen(cmd_comp, shell=True, stdout=PIPE, stderr=PIPE)
        comp_proc.wait()
        tmp_result = comp_proc.communicate()
        print >> output, "comp_time#" + tmp_result[0],
        if comp_proc.returncode:
            print >> output, 'comp_error#' + tmp_result[1],
        try:
            result_comp[el] = float(tmp_result[0])
        except ValueError as error:
            os.chdir(PWD)
            shutil.rmtree(tmpdir_path)
            raise ExternalScriptError(error)
        
        if el != elements[0]:
            exec_proc.wait()
            tmp_result = exec_proc.communicate()
            print >> output, "exec_time#" + tmp_result[0],
            if exec_proc.returncode:
                print >> output, 'exec_error#' + tmp_result[1]
            try:
                result_exec[el_pred] = float(tmp_result[0])
            except ValueError as error:
                os.chdir(PWD)
                shutil.rmtree(tmpdir_path)
                raise ExternalScriptError(error)
        
        cmd_exec = SCRIPT_EXEC + ' ' + cmd_pars + ' \"' + tmpdir_path + '\"'
        print >> output, cmd_exec
        exec_proc = Popen(cmd_exec, shell=True, stdout=PIPE, stderr=PIPE)
        el_pred = el
        
        cmd_comp = SCRIPT_COMP_WITH_STAT + ' ' + cmd_pars
        print >> output, cmd_comp
        comp_proc = Popen(cmd_comp, shell=True, stdout=PIPE, stderr=PIPE)
        comp_proc.wait()
        tmp_result = comp_proc.communicate()
        print >> output, "max_mem#" + tmp_result[0],
        if comp_proc.returncode:
            print >> output, 'comp_with_stat_error#' + tmp_result[1]
        try:
            result_maxmem[el] = float(tmp_result[0])
        except ValueError as error:
            os.chdir(PWD)
            shutil.rmtree(tmpdir_path)
            raise ExternalScriptError(error)
        
    exec_proc.wait()
    tmp_result = exec_proc.communicate()
    print >> output, "exec_time#" + tmp_result[0],
    if exec_proc.returncode:
        print >> output, 'exec_error#' + tmp_result[1]
    try:
        result_exec[el_pred] = float(tmp_result[0])
    except ValueError as error:
            os.chdir(PWD)
            shutil.rmtree(tmpdir_path)
            raise ExternalScriptError(error)
    
    os.chdir(PWD)
    shutil.rmtree(tmpdir_path)
    
    result = {}
    for el in elements:
        result[el] = (result_comp[el], result_exec[el], result_maxmem[el])
        
    return result
