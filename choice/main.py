#!/usr/bin/python3
# -*- coding: utf-8 -*-

# External imports
import sys

# Read script options
import options
options = options.read(sys.argv[1:])

# Init globals
import global_vars as gl
gl.COMP_MACHINE = options.comp_machine
gl.COMP_CPU_NUM = options.comp_cpu_num
gl.EXEC_MACHINE = options.exec_machine
gl.EXEC_CPU_NUM = options.exec_cpu_num
gl.SMOOTH_STAT    = options.is_smooth

# Internal imports
import calculate_TcTeMem as calc
import weight
from stat_adaptation import get_dis_regpar, get_dis_icvpar, add_dic
from optimize import optimize, seq_optimize, dcs_optimize


if options.is_seq:

    print('Group optimization')

    for spec in options.specs:

        if options.outputdir == 'NONE':
            print("---------------------------------------------------------------------------")
            print("Spec:", spec)
            ffile = None
        else:
            sys.stdout.write( "Spec " + spec + " ...")
            ffile = open('./' + options.outputdir + '/' + spec + '.group.txt', 'w', 0)

        pargroup_seq = [
            ['regn_max_proc_op_sem_size'],
            ['regn_opers_limit'],
            ['regn_heur1', 'regn_heur2', 'regn_heur3', 'regn_heur4'],
            ['regn_disb_heur'],
            ['regn_heur_bal1', 'regn_heur_bal2'],
            ['regn_prob_heur'],
            ['ifconv_opers_num', 'ifconv_calls_num', 'ifconv_merge_heur']
        ]

        try:
            seq_optimize( { spec : None }, pargroup_seq, 
                          every_proc_is_individual_task = False, 
                          output = ffile)

        except calc.ExternalScriptError as error:
            print('fail')
            print('calc.ExternalScriptError:', error)
        else:
            print("ok") 

elif options.is_dcs:

    print('Dcs optimization')

    for spec in options.specs:

        if options.outputdir == 'NONE':
            print("---------------------------------------------------------------------------")
            print("Spec:", spec)
            ffile = None
        else:
            sys.stdout.write( "Spec " + spec + " ...")
            ffile = open('./' + options.outputdir + '/' + spec + '.dcs.txt', 'w', 0)

        try:
            dcs_optimize( { spec : None },
                          dcs_zero_limit = 0.001,
                          output = ffile)

        except calc.ExternalScriptError as error:
            print('fail')
            print('calc.ExternalScriptError:', error)
        else:
            print("ok") 

elif options.is_every_proc:

    for spec in options.specs:
        print("---------------------------------------------------------------------------")
        print("Spec:", spec)
        
        dis_regpars = get_dis_regpar({ spec : None })
        weight.normolize_dict(dis_regpars)
        
        dis_icvpars = get_dis_icvpar({ spec : None })
        weight.normolize_dict(dis_icvpars)
        
        for par in options.pars:

            if options.outputdir == 'NONE':
                print("Parameter:", spec)
                ffile = None
            else:
                sys.stdout.write( "Parameter " + par + " ...")
                ffile = open('./' + options.outputdir + '/' + spec + '.' + par + '.txt', 'w', 0)

            try:
                optimize( { spec : None }, [ par ], 
                        every_proc_is_individual_task = False, 
                        output = ffile,
                        dis_regpar = dis_regpars,
                        dis_icvpar = dis_icvpars)

            except calc.ExternalScriptError as error:
                print('fail')
                print('calc.ExternalScriptError:', error)
            else:
                print("ok")   
else:
    print("---------------------------------------------------------------------------")
    print("All tasks ...")

    sum_dis_regpars = {}
    sum_dis_icvpars = {}
    for spec in options.specs:
        add_dic(sum_dis_regpars, get_dis_regpar({ spec : None }))
        add_dic(sum_dis_icvpars, get_dis_icvpar({ spec : None }))
    weight.normolize_dict(sum_dis_regpars)
    weight.normolize_dict(sum_dis_icvpars)

    for par in options.pars:

        if options.outputdir == 'NONE':
            print("Parameter:", spec)
            ffile = None
        else:
            sys.stdout.write( "Parameter " + par + " ...")
            ffile = open('./' + options.outputdir + '/' + spec + '.all.txt', 'w', 0)

        try:
            optimize( { options.specs[i] : None for i in range(0, len(options.specs)) },
                        [ par ],
                        every_proc_is_individual_task = False, 
                        output = ffile,
                        dis_regpar = sum_dis_regpars,
                        dis_icvpar = sum_dis_icvpars)

        except calc.ExternalScriptError as error:
            print('fail')
            print('calc.ExternalScriptError:', error)
        else:
            print("ok")
