#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from functools import reduce

import options as gl
import specs
import strategy as strat
import stat_adaptation as adt # требуется для нахождения минимального и максимального значений параметров
import calculate_TcTeMem as clc
import par
import train

def close():
    print()
    train.close()
    sys.exit()

def run():
    
    parnames = list(set(reduce(lambda x, y: x + y, strat.get())))
    spec_procs = specs.get(gl.SPECS)
    
    if gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
        print('Synchronous net creating for specs :')  # all
    else:
        print('Net creating for every specs :')  # every_spec
    specs.fprint(spec_procs)
    
    print('Net creating on every parametor :') # not seq
    for parname in parnames:
        print('    ' + parname)
    
    
    # запуск при значениях параметра по-умолчанию
    result_default = clc.calculate_abs_values(spec_procs, {})
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

    
def create_net(procs_dic, parname, points_num = 5):
    
    # получаем минимальное и максимальное значения для параметра
    if parname == 'dcs_level' or parname == 'dcs':
        max_value_par = gl.MAX_DCS_LEVEL
        min_value_par = 0
    elif parname in par.reg_seq:
        dis_regpar = adt.get_dis_regpar(procs_dic)
        value_par = adt.get_value_par(procs_dic, [parname], [], dis_regpar, None)
        ind = par.index_in_reg_seq[parname]
        max_value_par = value_par[parname][-1][ind] + 1
        min_value_par = max(value_par[parname][0][ind] - 1, 0)
    elif parname in par.icv_seq:
        dis_icvpar = adt.get_dis_icvpar(procs_dic)
        value_par = adt.get_value_par(procs_dic, [], [parname], None, dis_icvpar)
        ind = par.index_in_icv_seq[parname]
        max_value_par = value_par[parname][-1][ind] + 1
        min_value_par = max(value_par[parname][0][ind] - 1, 0)
    
    # строим узлы сетки
    if parname == 'dcs':
        vtype = int
    else:
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
    
    
