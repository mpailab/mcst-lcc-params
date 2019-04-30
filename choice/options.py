# External imports
import sys, getopt

# Possible somesing like this https://docs.python.org/3.3/library/argparse.html is better

class Options:
    def __init__(self):
        self.outputdir = 'NONE'
        self.pars = [
            'regn_max_proc_op_sem_size',
            'regn_opers_limit',
            'regn_heur1',
            'regn_heur2',
            'regn_heur3',
            'regn_heur4',
            'regn_disb_heur',
            'regn_heur_bal1',
            'regn_heur_bal2',
            'regn_prob_heur',
            'ifconv_opers_num',
            'ifconv_calls_num',
            'ifconv_merge_heur'
            ]
        self.specs = [
            '500.perlbench',
            '502.gcc',
            '503.bwaves',
            '505.mcf',
            '508.namd',
            '510.parest',
            '511.povray',
            '519.lbm',
            '521.wrf',
            '523.xalancbmk',
            '525.x264',
            '526.blender',
            '527.cam4',
            '531.deepsjeng',
            '538.imagick',
            '541.leela',
            '544.nab',
            '548.exchange2',
            '549.fotonik3d',
            '554.roms',
            '557.xz'
            ]
        self.is_every_proc = False
        self.is_smooth = False
        self.is_group = False
        self.is_dcs = False
        self.is_seq = False
        self.comp_machine = 'pear'
        self.comp_cpu_num = 'NONE'
        self.exec_machine = 'cordelia'
        self.exec_cpu_num = 'NONE'

def usage():
    return ('main.py [-o <outputdir>]'
                   ' [--every]'
                   ' [--smooth]'
                   ' [--group]'
                   ' [--dcs]'
                   ' [--pars=<params_list>]'
                   ' [--specs=<specs_list>]'
                   ' [--comp_machine=<x86_machine_name>]'
                   ' [--comp_cpu=<x86_machine_cpu>]'
                   ' [--exec_machine=<x86_machine_name>]'
                   ' [--exec_cpu=<x86_machine_cpu>]'
                   ' [-h]')

def read(argv):

    options = Options()

    try:
        opts, args = getopt.getopt(argv,"ho:",["odir=",
                                                   "comp_machine=", "comp_cpu=",
                                                   "exec_machine=", "exec_cpu=",
                                                   "every", "smooth", "group", "dcs",
                                                   "pars=", "specs="])
    except getopt.GetoptError:
        print usage()
        sys.exit(2)
    
    

    #if args != '':
        #print usage()
        #sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print usage()
            sys.exit()

        elif opt in ("-o", "--odir"):
            options.outputdir = arg

        elif opt == "--comp_machine":
            options.comp_machine = arg

        elif opt == "--comp_cpu":
            options.comp_cpu_num = arg

        elif opt == "--exec_machine":
            options.exec_machine = arg

        elif opt == "--exec_cpu":
            options.exec_cpu_num = arg

        elif opt == "--every":
            options.is_every_proc = True

        elif opt == "--smooth":
            options.is_smooth = True

        elif opt == "--seq":
            options.is_seq = True

        elif opt == "--dcs":
            options.is_seq = True

        elif opt == "--pars":
            options.pars = arg.split(',')

        elif opt == "--specs":
            options.specs = arg.split(',')
    
    return options
