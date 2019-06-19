#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
import sys, os
from functools import reduce

# Internal imports
import options as gl
import specs
import strategy as strat
import stat_adaptation as adt
import calculate_TcTeMem as clc
import optimize as opt
import par
import check_stat
import train

# Запуск ИС в подрежиме "метод имитации отжига"
def run():

    # Подгружаем базу данных для обучения
    train.DB.load()

    # Получаем стратегию в рабочем формате, параллельно проверяя ее на корректность
    strategy = strat.get(gl.OPTIMIZATION_STRATEGY)
    spec_procs = specs.get(gl.SPECS)
    
    if gl.INHERIT_STAT:
        check_stat.check()

    if gl.SEQ_OPTIMIZATION_WITH_STRATEGY and gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
        print('Synchronous optimization of specs :')  # all
        specs.fprint(spec_procs)
        print('Successive optimization with the strategy :') # seq
        strat.fprint(strategy)
        
        try:
            opt.seq_optimize(spec_procs, strategy)
        except clc.ExternalScriptError:
            print('fail')
            print('An error by giving (t_c, t_e, m) from external script')
        else:
            print("ok")
    elif gl.SEQ_OPTIMIZATION_WITH_STRATEGY and not gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
        print('Independent optimization for every spec in') # every_spec
        specs.fprint(spec_procs)
        print('Successive optimization with the strategy :') # seq
        strat.fprint(strategy)
        
        for specname, proclist in spec_procs.items():
            print("---------------------------------------------------------------------------")
            print("Spec:", specname)
            
            try:
                opt.seq_optimize({specname: proclist}, strategy)
            except clc.ExternalScriptError:
                print('fail')
                print('An error by giving (t_c, t_e, m) from external script')
            else:
                print("ok")

    elif not gl.SEQ_OPTIMIZATION_WITH_STRATEGY and gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
        print('Synchronous optimization of specs :')  # all
        specs.fprint(spec_procs)
        print('Independent optimization on every parametors group in the strategy :') # not seq
        strat.fprint(strategy)
        
        dis_regpar = adt.get_dis_regpar(spec_procs)
        dis_icvpar = adt.get_dis_icvpar(spec_procs)
        
        for parnames in strategy:
            print("---------------------------------------------------------------------------")
            print("Group:", parnames)
            
            is_dcs_pargroup = reduce(lambda x, y: x and y, [p in par.dcs or p == 'dcs' for p in parnames])
            is_nesting_pargroup = len(parnames) == 1 and parnames[0] in par.nesting
            
            try:
                if is_dcs_pargroup:
                    opt.dcs_optimize(spec_procs)
                elif is_nesting_pargroup:
                    opt.optimize_bool_par(spec_procs, parnames[0])
                else:
                    opt.optimize(spec_procs, parnames, dis_regpar = dis_regpar, dis_icvpar = dis_icvpar)
            except clc.ExternalScriptError:
                print('fail')
                print('An error by giving (t_c, t_e, m) from external script')
            else:
                print("ok")
    elif not gl.SEQ_OPTIMIZATION_WITH_STRATEGY and not gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
        print('Independent optimization for every spec in') # every_spec
        specs.fprint(spec_procs)
        print('Independent optimization on every parametors group in the strategy :') # not seq
        strat.fprint(strategy)
        
        for specname, proclist in spec_procs.items():
            print("---------------------------------------------------------------------------")
            print("---------------------------------------------------------------------------")
            print("Spec:", specname)
            
            dis_regpar = adt.get_dis_regpar({specname : proclist})
            dis_icvpar = adt.get_dis_icvpar({specname : proclist})
            
            for parnames in strategy:
                print("---------------------------------------------------------------------------")
                print("Group:", parnames)
                
                is_dcs_pargroup = reduce(lambda x, y: x and y, [p in par.dcs or p == 'dcs' for p in parnames])
                is_nesting_pargroup = len(parnames) == 1 and parnames[0] in par.nesting
                try:
                    if is_dcs_pargroup:
                        opt.dcs_optimize({specname : proclist})
                    elif is_nesting_pargroup:
                        opt.optimize_bool_par({specname : proclist}, parnames[0])
                    else:
                        opt.optimize({specname : proclist}, parnames, dis_regpar = dis_regpar, dis_icvpar = dis_icvpar)
                except clc.ExternalScriptError:
                    print('fail')
                    print('An error by giving (t_c, t_e, m) from external script')
                else:
                    print("ok")
