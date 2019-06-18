#!/usr/bin/python3
# -*- coding: utf-8 -*-

from functools import reduce
import os


import options as gl
import specs
import par

use_pickle = False
if use_pickle:
    import pickle

class TrData:
    def __init__(self):
        spec_list = specs.get(gl.SPECS).keys()
        # data: spec -> (prname_1, ..., prname_n) -> [(prval_1, ..., prval_n, rel_t_c, rel_t_e, rel_v_mem), ...]
        self.data = {specname : {} for specname in spec_list}
        # default : spec -> (t_c_default, t_e_default, mem_default)
        self.default = {specname : None for specname in spec_list}
        
    def read(self):
        if use_pickle:
            for specname in self.data.keys():
                path = os.path.join(gl.TRAIN_DATA_DIR, specname + '.bat')
                if not os.path.exists(path):
                    continue
                rfile = open(path, 'rb')
                self.data[specname] = pickle.load(rfile)
                rfile.close()
        else:
            for specname in self.data.keys():
                path = os.path.join(gl.TRAIN_DATA_DIR, specname + '.txt')
                if not os.path.exists(path):
                    continue
                rfile = open(path)
                for line in rfile:
                    strs = line.split()
                    parnames = tuple(strs[0].split(':'))
                    self.data[specname][parnames] = []
                    for res in strs[1:]:
                        res = res.split(':')
                        for i in range(len(parnames)):
                            res[i] = par.val_type[parnames[i]](res[i])
                        for i in [-3, -2, -1]:
                            res[i] = float(res[i])
                        res = tuple(res)
                        self.data[specname][parnames].append(res)
                rfile.close()
                
    
    def add(self, specname, proclist, par_value, t_c, t_e, v_mem):
        """
            par_value имеет вид {pname_1 : pvalue_1, ..., pname_n : pvalue_n}
        """
        
        # инициализируем значения тройки (t_c, t_e, v_mem) при значении параметров по-умолчанию,
        # если дан результат запуска specname на пустом словаре par_value
        if not par_value:
            self.default[specname] = (t_c, t_e, v_mem)
            return
        
        parnames = list(par_value.keys())
        parnames.sort()
        parnames = tuple(parnames)
        
        values = tuple(map(lambda parname: par_value[parname], parnames))
        
        if self.default[specname] == None:
            raise Exception('There is not default values for t_e, t_c, mem in TrData')
        
        results = (t_c / self.default[specname][0], t_e / self.default[specname][1], v_mem / self.default[specname][2])
        
        if parnames in self.data[specname]:
            self.data[specname][parnames].append(values + results)
        else:
            self.data[specname][parnames] = [values + results]
    
    def write(self, specname, output = None):
        def my_str(x):
            if type(x) == bool:
                return str(int(x))
            else:
                return str(x)
        
        for parnames, res_list in self.data[specname].items():
            parnames = reduce(lambda x, y: x + ':' + y, parnames) # "par_1:par_2:...:par_n"
            print(parnames, file = output, end = '')
            for res in res_list:
                res = reduce(lambda x, y: my_str(x) + ':' + my_str(y), res) # "val_1:...:val_n:rt_c:rt_e:rv_m"
                print(' ' + res, file = output, end = '')
            print(file = output)
    
    def write_to_files(self):
        if not use_pickle:
            for specname in self.data.keys():
                path = os.path.join(gl.TRAIN_DATA_DIR, specname + '.txt')
                ofile = open(path, 'w')
                self.write(specname, output = ofile)
                ofile.close()
        else:
            for specname in self.data.keys():
                path = os.path.join(gl.TRAIN_DATA_DIR, specname + '.bat')
                ofile = open(path, 'wb')
                pickle.dump(self.data[specname], ofile, 2)
                ofile.close()
            
    def write_to_screen(self):
        for specname in self.data.keys():
            print('Specname: ', specname)
            self.write(specname)

data = TrData()
# при первом подключении модуля (подключении модуля в main) инициализируем имеющиеся данные о запусках
# FIXME подрежим "нейронная сеть" будет использовать этот модуль? Если да, то возможно здесь потребуется корректировка кода.
data.read()
