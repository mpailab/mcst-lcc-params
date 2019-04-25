#!/usr/bin/python
# -*- coding: utf-8 -*-

# External imports
import sys

# Internal imports
import calculate_TcTeMem as calc
import options, weight
import smooth_stat as sm
from optimize import optimize, seq_optimize, dcs_optimize
from stat_adaptation import get_dis_regpar, get_dis_icvpar, add_dic

# Read script options
options = options.read(sys.argv[1:])

# Init globals
calc.COMP_MACHINE = options.comp_machine
calc.COMP_CPU_NUM = options.comp_cpu_num
calc.EXEC_MACHINE = options.exec_machine
calc.EXEC_CPU_NUM = options.exec_cpu_num
sm.SMOOTH_STAT    = options.is_smooth

if options.is_seq:

    print 'Group optimization'

    for spec in options.specs:

        if options.outputdir == 'NONE':
            print "---------------------------------------------------------------------------"
            print "Spec:", spec
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
            print 'fail'
            print 'calc.ExternalScriptError:', error
        else:
            print "ok" 

elif options.is_dcs:

    print 'Dcs optimization'

    for spec in options.specs:

        if options.outputdir == 'NONE':
            print "---------------------------------------------------------------------------"
            print "Spec:", spec
            ffile = None
        else:
            sys.stdout.write( "Spec " + spec + " ...")
            ffile = open('./' + options.outputdir + '/' + spec + '.dcs.txt', 'w', 0)

        try:
            dcs_optimize( { spec : None },
                          dcs_zero_limit = 0.001,
                          output = ffile,
                          nesting_off_attempt = True)

        except calc.ExternalScriptError as error:
            print 'fail'
            print 'calc.ExternalScriptError:', error
        else:
            print "ok" 

elif options.is_every_proc:

    for spec in options.specs:
        print "---------------------------------------------------------------------------"
        print "Spec:", spec
        
        dis_regpars = get_dis_regpar({ spec : None })
        weight.normolize_dict(dis_regpars)
        
        dis_icvpars = get_dis_icvpar({ spec : None })
        weight.normolize_dict(dis_icvpars)
        
        for par in options.pars:

            if options.outputdir == 'NONE':
                print "Parameter:", spec
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
                print 'fail'
                print 'calc.ExternalScriptError:', error
            else:
                print "ok"   
else:
    print "---------------------------------------------------------------------------"
    print "All tasks ..."

    sum_dis_regpars = {}
    sum_dis_icvpars = {}
    for spec in options.specs:
        add_dic(sum_dis_regpars, get_dis_regpar({ spec : None }))
        add_dic(sum_dis_icvpars, get_dis_icvpar({ spec : None }))
    weight.normolize_dict(sum_dis_regpars)
    weight.normolize_dict(sum_dis_icvpars)

    for par in options.pars:

        if options.outputdir == 'NONE':
            print "Parameter:", spec
            ffile = None
        else:
            sys.stdout.write( "Parameter " + par + " ...")
            ffile = open('./' + options.outputdir + '/' + spec + '.all.txt', 'w', 0)

        try:
            optimize( { options.specs[i] : None for i in xrange(0, len(options.specs)) },
                        [ par ],
                        every_proc_is_individual_task = False, 
                        output = ffile,
                        dis_regpar = sum_dis_regpars,
                        dis_icvpar = sum_dis_icvpars)

        except calc.ExternalScriptError as error:
            print 'fail'
            print 'calc.ExternalScriptError:', error
        else:
            print "ok"
