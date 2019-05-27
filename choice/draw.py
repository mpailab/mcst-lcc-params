#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
import matplotlib.pyplot as plt
import os, sys
from functools import reduce

# Internal imports
import global_vars as gl
from analyse import resultfile_to_picture
import par, weight
from read import task_list
import smooth_stat as sm
import stat_adaptation as stat


def hist_dict(dic):
    plt.hist(list(dic.keys()), gl.PAR_DIAG_COL_NUM, weights = list(dic.values()))
    plt.show()

def hist(titlename, x_label,
         p_values , p_weights,
         save_pic_flag = gl.SAVE_PIC_FLAG, show_flag = gl.SHOW_FLAG,
         fullstat_flag = gl.USE_ALL_PROCS_IN_STAT, sm_dis_flag = gl.SMOOTH_STAT):
    title = titlename
    p_min = min(p_values)
    p_max = max(p_values)
    p_range = p_max - p_min
    x_split = min(10, gl.PAR_DIAG_COL_NUM)
    x_step = p_range / x_split
    x_marks = [p_min + i * x_step for i in range(x_split)] + [p_max]
    x_marks = [float('%.2f' % x) for x in x_marks]
    
    norm_weights = weight.normolize_to_percents(p_weights)
    
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel('%')
    plt.xticks(x_marks)
    plt.hist(p_values, gl.PAR_DIAG_COL_NUM, weights = norm_weights)
    if gl.DRAW_RUN_RESULTS_ON_GRAPHICS:
        res_path = gl.RUN_LOGS_PATH + '/' + title + '.' + x_label + '.txt'
        if os.path.exists(res_path):
            x_array, y_array = resultfile_to_picture(res_path, title)
            plt.plot(x_array, y_array, 'o')
        res_path = gl.RUN_LOGS_PATH + '/5tasks_some_results/' + x_label + 'all_tasks.txt'
        if os.path.exists(res_path):
            x_array, y_array = resultfile_to_picture(res_path, title)
            plt.plot(x_array, y_array, 'o')
    if save_pic_flag:
        title_print = reduce(lambda x, y: x + y, titlename.split('.'))
        if gl.SAVE_SUBDIR_STRUCTURE_MODE == 2:
            savedir = gl.IMAGES_SAVE_MAIN_DIR + '/' + x_label
            savepath = savedir + '/' + title_print
        elif gl.SAVE_SUBDIR_STRUCTURE_MODE == 1:
            savedir = gl.IMAGES_SAVE_MAIN_DIR + '/' + title_print
            savepath = savedir + '/' + x_label
        else:
            savedir = gl.IMAGES_SAVE_MAIN_DIR
            savepath = savedir + '/' + title_print + ' ' + x_label
        if not os.path.exists(savedir):
            os.makedirs(savedir)
        if fullstat_flag:
            savepath += '_fs'
        if sm_dis_flag:
            savepath += '_smn'
        plt.savefig(savepath)
    if show_flag:
        plt.show()
    else:
        plt.close()
    
def hists_for_pars(reg_parnames, icv_parnames, tasknames = None, hist_for_all_pars = False, smooth_stat = gl.SMOOTH_STAT):
    
    if tasknames == None:
        tasknames = task_list()
    parnames = reg_parnames + icv_parnames
    index_in_own_seq = dict(par.index_in_reg_seq)
    index_in_own_seq.update(par.index_in_icv_seq)
    
    if hist_for_all_pars:
        sum_dis_regpars = {}
        sum_dis_icvpars = {}
    
    print("---------------------------------------------------------------------------")
    if smooth_stat:
        print('Smooth mode: on')
    else:
        print('Smooth mode: off')
    for task in tasknames:
        print("---------------------------------------------------------------------------")
        print("Procedure:", task)
        
        print('Get dis_regpar ...')
        dis_regpar = stat.get_dis_regpar({ task : None })
        if hist_for_all_pars:
            stat.add_dic(sum_dis_regpars, dis_regpar)
        print('ok')
        weight.normolize_dict(dis_regpar)
        
        print('Get dis_icvpar ...')
        dis_icvpar = stat.get_dis_icvpar({ task : None })
        if hist_for_all_pars:
            stat.add_dic(sum_dis_icvpars, dis_icvpar)
        weight.normolize_dict(dis_icvpar)
        print('ok')
        
        
        print('Get value_par ...')
        value_par = stat.get_value_par({ task : None }, reg_parnames, icv_parnames, dis_regpar, dis_icvpar)
        print('ok')
        print('Smoothing stat ...')
        sm_dis = sm.get_sm_dis(value_par, reg_parnames, icv_parnames, dis_regpar, dis_icvpar, smooth_stat = smooth_stat)
        print('ok')
        
        for parname in parnames:
            sys.stdout.write( "Parameter:" + parname + "...")
            coord = index_in_own_seq[parname]
            value_par_proj = [x[coord] for x in value_par[parname]]
            value_par_proj_weights = [sm_dis[parname][x] for x in value_par[parname]]
            hist(task,
                    parname,
                    value_par_proj,
                    value_par_proj_weights,
                    sm_dis_flag = smooth_stat
                    )
            print('ok')
    if not hist_for_all_pars:
        return 0
    
    print("---------------------------------------------------------------------------")
    print("Sum_tasks ...")
    weight.normolize_dict(sum_dis_regpars)
    weight.normolize_dict(sum_dis_icvpars)
    
    proc_dic = { task : None for task in tasknames }
    value_par = stat.get_value_par(proc_dic, reg_parnames, icv_parnames, sum_dis_regpars, sum_dis_icvpars)
    sm_dis = sm.get_sm_dis(value_par, reg_parnames, icv_parnames, sum_dis_regpars, sum_dis_icvpars, smooth_stat = smooth_stat)
    
    for parname in parnames:
            sys.stdout.write( "Parameter:" + parname + "...")
            coord = index_in_own_seq[parname]
            value_par_proj = [x[coord] for x in value_par[parname]]
            value_par_proj_weights = [sm_dis[parname][x] for x in value_par[parname]]
            hist('Sum_Tasks',
                    parname,
                    value_par_proj,
                    value_par_proj_weights,
                    sm_dis_flag = smooth_stat
                    )
            print('ok')


if __name__ == '__main__':
    def filt_func_par(x):
        return True
        #return par.val_type[x] == int
    def filt_func_task(x):
        tnum = int(x[:3])
        if tnum >= 500:
            return True
        else:
            return False
    reg_parnames = list(filter(filt_func_par, par.reg_seq))
    icv_parnames = list(filter(filt_func_par, par.icv_seq))
    tasknames = list(filter(filt_func_task ,task_list()))
    #hists_for_pars(reg_parnames, icv_parnames, tasknames = tasknames, hist_for_all_pars = False, smooth_stat = True)
    hists_for_pars(reg_parnames, icv_parnames, tasknames = tasknames, hist_for_all_pars = False, smooth_stat = False)

