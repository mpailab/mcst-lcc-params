#!/usr/bin/python3
# -*- coding: utf-8 -*-

def check():
    if not os.path.exists(gl.STAT_PATH):
        print('Error!')
        sys.exit()
    for specname, proclist in spec_procs.items():
        specpath = os.path.join(gl.STAT_PATH, specname)
        if not os.path.exists(specpath):
            print('Error! There is not statictic for task :', specname)
            sys.exit()
        if proclist == None:
            proclist = os.listdir(specpath)
        for procname in proclist:
            path = os.path.join(specpath, procname)
            if not os.path.exists(path):
                print('Error! There is not statictic for proc', procname, 'of task', specname)
                sys.exit()
                
            path_reg = os.path.join(path, 'regions.txt')
            if not os.path.exists(path_reg):
                print('Error! Incorrect statictic for proc', procname, 'of task', specname)
                print('       There is not file :',  path_reg)
                sys.exit()
                
            path_icv = os.path.join(path, 'if_conv.txt')
            if not os.path.exists(path_icv):
                print('Error! Incorrect statictic for proc', procname, 'of task', specname)
                print('       There is not file :',  path_icv)
                sys.exit()
                
            dcs_levels = range(1, gl.MAX_DCS_LEVEL + 1)
            for lv in dcs_levels:
                lv_file = 'dcs_' + str(lv) + '.txt'
                path_lv = os.path.join(path, lv_file)
                if not os.path.exists(path_lv):
                    print('Error! Incorrect statictic for proc', procname, 'of task', specname)
                    print('       There is not file :',  path_lv)
                    sys.exit()
