#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from functools import reduce

import options as gl
import func as clc
import par
import train

def run():
    
    parnames = list(set(reduce(lambda x, y: x + y, par.strategy())))
    spec_procs = par.specs()
    
    if gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
        print('Synchronous net creating for specs :')  # all
    else:
        print('Net creating for every specs :')  # every_spec
    par.print_specs(spec_procs)
    
    print('Net creating on every parametor :') # not seq
    for parname in parnames:
        print('    ' + parname)
    
    
    # запуск при значениях параметра по-умолчанию
    clc.calculate_abs_values(spec_procs, {})
    for parname in parnames:
        print("---------------------------------------------------------------------------")
        print("Par:", parname)
    
        if gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
            create_net(spec_procs, parname)
        else:
            for specname, proclist in spec_procs.items():
                print("---------------------------------------------------------------------------")
                print("Spec:", specname)
                create_net({specname: proclist}, parname)

    
def create_net(procs_dic, parname, points_num = gl.points_num):
    
    # получаем минимальное и максимальное значения для параметра
    min_value_par, max_value_par = par.ranges[parname]
    
    # строим узлы сетки
    vtype = par.val_type[parname]
    if vtype == bool:
        values = [False, True]
    else:
        if points_num == 1:
            val = (max_value_par + min_value_par) / 2
            if vtype == int:
                val = round(val)
            values = [val]
        else:
            segments_num = points_num - 1
            segment_len = (max_value_par - min_value_par) / segments_num
            values = []
            for i in range(points_num):
                val = min_value_par + i * segment_len
                if vtype == int:
                    val = round(val)
                values.append(val)
    
    if parname == 'dcs':
        par_value_default = {'dcs_kill': par.default_value['dcs_kill'] , 'dcs_level' : par.default_value['dcs_level']}
        # добавляем в базу запуск при значении параметра по-умолчанию
        for specname, proclist in procs_dic.items():
            t_c, t_e, v_mem = train.DB[specname].default
            train.DB[specname].add(proclist, par_value_default, t_c, t_e, v_mem)
        for val in values:
            if val == 0:
                dcs_kill_val = False
            else:
                dcs_kill_val = True
            par_value = {'dcs_kill': dcs_kill_val, 'dcs_level' : val}
            if par_value != par_value_default:
                clc.calculate_abs_values(procs_dic, par_value)
    else:
        default_val = par.default_value[parname]
        # добавляем в базу запуск при значении параметра по-умолчанию
        for specname, proclist in procs_dic.items():
            t_c, t_e, v_mem = train.DB[specname].default
            train.DB[specname].add(proclist, {parname: default_val}, t_c, t_e, v_mem)
        
        # исключаем из узлов сетки значения параметров по-умолчанию
        if default_val in values:
            values.remove(default_val)
        # вычисляем в узлах сетки
        for val in values:
            clc.calculate_abs_values(procs_dic, {parname : val})
    
    
