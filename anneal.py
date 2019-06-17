#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
from functools import reduce

# Internal imports
import globals as gl
import specs
import strategy as strat
import stat_adaptation as adt
import calculate_TcTeMem as clc
import optimize as opt
import par
import train_data as tr_data

def close_annealing():
    tr_data.data.write_to_files()
    # tr_data.data.write_to_screen()
    exit()

# Запуск ИС в подрежиме "метод имитации отжига"
def run():

    if not gl.GAIN_STAT_ON_EVERY_OPTIMIZATION_STEP:
        # FIXME: если мы сами не собираем статистику, то
        # следует убедиться, что в папке gl.STAT_PATH она присутствует для всех спеков и их процедур из gl.SPECS
        # если ее там нет в должном виде, то надо
        #       1 вариант -> выдать ошибку
        #       2 вариант -> собрать статистику в gl.STAT_PATH
        pass

    # Получаем стратегию в рабочем формате, параллельно проверяя ее на корректность
    strategy = strat.get(gl.OPTIMIZATION_STRATEGY)
    spec_procs = specs.get(gl.SPECS)
    # !надо проверить, что спеки и процедуры в spec_procs взяты не с потолка

    #if not os.path.isdir(gl.OUTPUTDIR):
        #print('Warning! There is not directory: ', gl.OUTPUTDIR)
        #print('         The output directory is not given')
        #print('         The output is on the screen')
        

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
        except KeyboardInterrupt:
            print()
            close_annealing()
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
            except KeyboardInterrupt:
                print()
                close_annealing()
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
            except KeyboardInterrupt:
                print()
                close_annealing()
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
                except KeyboardInterrupt:
                    print()
                    close_annealing()
                else:
                    print("ok")
    close_annealing()
