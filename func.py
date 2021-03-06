﻿#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
import os, random, shutil
from subprocess import Popen, PIPE
import sys
from sys import maxsize
import time

# Internal imports
import par
import options as gl
import train
import verbose

# Вычилсяем папку, из которой запущен процесс
PWD = os.getcwd()
SCRIPT_CMP_RUN = os.path.abspath(gl.SCRIPT_CMP_RUN)
SCRIPT_CMP_INIT = os.path.abspath(gl.SCRIPT_CMP_INIT)

class ExternalScriptError(gl.IntsysError):
    def __init__(self, error, script = SCRIPT_CMP_RUN):
        self.script = script
        self.error = error.strip()
    
    def __str__(self):
        return 'in external script %s:\n%s' % (self.script, self.error)

class ExternalScriptOutput(ExternalScriptError):
    def __init__(self, error, script = SCRIPT_CMP_RUN):
        self.script = script
        self.error = 'external script %s returns %r, could not convert it to float' % (script, error.strip())

# Инициализация внешнего скрипта
def init_ext_script():
    cmd = SCRIPT_CMP_INIT + ' .'
    # print(cmd, file=output)
    prog = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    prog.wait()
    _, error = prog.communicate()
    if prog.returncode or error:
        raise ExternalScriptError(error.decode('utf-8'), SCRIPT_CMP_INIT)

# Запуск внешнего срипта
def run_ext_script(mode, spec, opts, processes):
    assert(mode in gl.CMP_MODES)
    wait = ' '.join(map(lambda p: 'tail --pid=' + str(p.pid) + ' -f /dev/null;', processes)) if processes else ''
    cmd = ( SCRIPT_CMP_RUN 
            + ' -' + mode 
            + ' -suite ' + gl.CMP_SUITE 
            + ' -spec ' + spec
            + ' -' + gl.COMP_MODE
            + (' -opt ' + opts if opts else '')
            + ' -dir ' + gl.DINUMIC_STAT_PATH
            + ' -server ' + (gl.EXEC_SERVER if mode == 'exec' else gl.COMP_SERVER)
            + ' -prof ' + gl.PROC_WEIGHT_PATH ) 
    return Popen(wait + ' ' + cmd, shell=True, stdout=PIPE, stderr=PIPE)

# Опции для передачи внешнему скрипту
def ext_script_opts(task_name, par_value, procname_list = None): 
    cmd = ""
    if len(par_value) != 0 or procname_list != None:
        cmd += '\"'
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
                raise Exception('Unknown type of par')
        if procname_list != None:
            for procname in procname_list:
                cmd += '--debug_proc=' + procname + ' '
        cmd = cmd[:-1] # удаляем последний символ (лишний пробел)
        cmd += '\"'
    return cmd

# Запускает внешние скрипты на задачах из specs со значениями параметров из par_value
# и получает абсолютные значения времени компиляции, времени исполнения и объема потребляемой памяти
def calculate_abs_values(specs, par_value):

    # Настраиваем печать сообщений
    output = verbose.trace

    print('\nCalculate compile time, execution time and maximal memory usage for ' + ('' if par_value else 'default ') + 'parameters', file=output)
    for par, value in par_value.items():
        print(' ', par, '=', str(value), file=output)
    
    # Создаем временный каталог
    tmpdir_name = 'tmp' + '_' + str(random.randrange(10**10))
    os.mkdir(tmpdir_name)

    # Запоминаем каталог для последующего удаления
    tmpdir_path = os.path.join(PWD, tmpdir_name)

    # Стек запущенных процессов
    stack = []
    heap = []

    # Таблица результатов: {spec_name -> (comp_time, exec_time, max_mem)}
    res = {}

    # Список проблемных spec-ов
    failed_specs = []

    try:

        # Переходим в новый каталог
        os.chdir(tmpdir_path)

        # Инициализируем внешний скрипт
        init_ext_script()

        # Запускаем внешний скрипт для каждого спека по отдельности
        print('Run jobs:', file=verbose.debug)
        for spec, procs in specs.items():

            # Готовим входные аргументы для внешнего срипта
            opts = ext_script_opts(spec, par_value, procs)

            # Запускаем внешний скрипт на компиляцию
            comp_proc = run_ext_script( 'comp', spec, opts, 
                                        ([stack[-1][3]] if stack else []))
            verbose.print_job(comp_proc.pid, comp_proc.args)

            # Запускаем внешний скрипт на исполнение
            exec_proc = run_ext_script( 'exec', spec, opts, 
                                        ([comp_proc, stack[-1][2]] if stack else [comp_proc]))
            verbose.print_job(exec_proc.pid, exec_proc.args)

            # Запускаем внешний скрипт на компиляцию с получением статистики
            stat_proc = run_ext_script('stat', spec, opts, [comp_proc])
            verbose.print_job(stat_proc.pid, stat_proc.args)

            # Запоминаем запущенные процессы
            stack.append((spec, comp_proc, exec_proc, stat_proc))
            heap.append(comp_proc)
            heap.append(exec_proc)
            heap.append(stat_proc)

        # Ожидаем завершение процессов
        print('Waiting for terminating of jobs:', file=verbose.debug)
        def is_run(p):
            if p.poll() is None:
                return True
            verbose.print_job(p.pid, "done")
            return False
        while heap: 
            heap = [ p for p in heap if is_run(p) ]
            time.sleep(1)

        # Обрабатываем результаты
        for spec, comp_proc, exec_proc, stat_proc in stack:

            print('  ' + spec + ' ... ', end='', file=output, flush=True)

            try:

                # Получаем время компиляции
                comp_output, comp_error = comp_proc.communicate()
                if comp_proc.returncode or comp_error:
                    raise ExternalScriptError(comp_error.decode('utf-8'))
                try:
                    comp_time = float(comp_output)
                except ValueError as error:
                    raise ExternalScriptOutput(comp_output.decode('utf-8'))

                # Получаем время исполнения
                exec_output, exec_error = exec_proc.communicate()
                if exec_proc.returncode or exec_error:
                    raise ExternalScriptError(exec_error.decode('utf-8'))
                try:
                    exec_time = float(exec_output)
                except ValueError as error:
                    raise ExternalScriptOutput(exec_output.decode('utf-8'))

                # Получаем максимальный объем потребления памяти
                stat_output, stat_error = stat_proc.communicate()
                if stat_proc.returncode or stat_error:
                    raise ExternalScriptError(stat_error.decode('utf-8'))
                try:
                    max_mem = float(stat_output)
                except ValueError as error:
                    raise ExternalScriptOutput(stat_output.decode('utf-8'))

                # Добавляем полученные результаты в базу данных
                train.DB.add(spec, specs[spec], par_value, comp_time, exec_time, max_mem)

                # Заполняем таблицу результатов
                res[spec] = (comp_time, exec_time, max_mem)

                print('ok', file=output)
                print('    comp_time = ' + str(comp_time), file=output)
                print('    exec_time = ' + str(exec_time), file=output)
                print('    max_mem = ' + str(max_mem), file=output)

            except ExternalScriptError as error:

                # Не удалось получить данные для данного spec-а. В этом случае исключаем проблемный spec из рассмотрения.
                print('fail', file=output)
                verbose.warning('in calculating (t_c, t_e, m) for spec %s:\n%s' % (spec, error), verbose.debug)
                print('Failed spec %s will be excluded.' %spec, file=verbose.trace)
                failed_specs.append(spec)

            except KeyboardInterrupt as error:

                raise KeyboardInterrupt(error)

    except ExternalScriptError as error:

        raise gl.IntsysError(error)

    except KeyboardInterrupt as error:

        raise KeyboardInterrupt(error)

    finally:

        # Удаляем запущенные процессы
        [ p.kill() for p in heap if p.poll() is None ]

        # Возвращаемся в исходный каталог и удаляем временные файлы
        os.chdir(PWD)
        shutil.rmtree(tmpdir_path)

        # Востанавливаем стандартный ввод/вывод после удалённых запусков
        os.system('stty sane')


    # Удаляем проблемные спеки
    for spec in failed_specs:
        del specs[spec]
    
    print(file=output)
        
    return res
