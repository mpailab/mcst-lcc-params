# External imports
import sys, getopt

# Possible somesing like this https://docs.python.org/3.3/library/argparse.html is better

class Options:
    def __init__(self, pars, specs):
        self.dataset = './DataSet'
        self.pars = pars
        self.specs = specs
        self.interp = 1

def usage():
    return ('usage: main.py [--dataset=<data_set>] [--pars=<params>] [--specs=<specs>] [--interp=<interp_order>] [-h]\n'
            '\n'
            'OPTIONS:\n'
            ' --dataset  - set a dataset directory (default: ./DataSet)\n'
            ' --pars     - specify a comma-separated list of compiler options (default: all options)\n'
            ' --specs    - specify a comma-separated list of compiled specs (default: all specs)\n'
            ' --interp   - specify an order of spline interpolation (values: linear, quadratic, cubic; default: linear)\n'
            ' -h         - print this help')

def read(argv, pars, specs):

    options = Options(pars, specs)

    try:
        opts, args = getopt.getopt(argv, "h:", ["dataset=", "pars=", "specs=", "interp="])
    except getopt.GetoptError:
        print(usage())
        sys.exit(2)

    if args != []:
        print(usage())
        sys.exit(2)
    
    for opt, arg in opts:

        if opt == '-h':
            print(usage())
            sys.exit()

        elif opt == '--dataset':
            options.dataset = arg

        elif opt == '--pars':
            options.pars = arg.split(',')

        elif opt == '--specs':
            options.specs = arg.split(',')

        elif opt == '--interp':
            if arg in ['linear', 'quadratic', 'cubic']:
                options.interp = arg
            else:
                print(usage())
                sys.exit()
    
    return options
