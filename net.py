#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from functools import reduce

import options as gl
import func as clc
import par
import train

class VectIter:
    """
        Итератор перебирает все возможные n-ки значений для параметров,
        если задан спектр возможных значений для каждого параметра
    """
    def __init__(self, values):
        """ 
            Формат задания возможных значений параметров:
            values = {p_1 : [v^1_1, ..., v^1_k1], ..., p_n : [v^n_1, ..., v^n_kn]}
        """
        self.values = values
        self.axes = list(values.keys())
        for ax in self.axes:
            if not values[ax]:
                raise Exception('The empty possible values for parametor : ' + ax)
        self.state = {ax : iter(values[ax]) for ax in self.axes}
        self.val = {ax: next(self.state[ax]) for ax in self.axes}

    def __iter__(self):
        return self
    
    def __next__(self):
        
        # формируем результат текущего запуска next
        if self.val == None:
            raise StopIteration
        res = dict(self.val)
        
        # формируем результат следующего запуска next
        for ax in self.axes:
            try:
                # пытаемся перейти к следующему значению по текущей оси
                self.val[ax] = next(self.state[ax])
            except StopIteration:
                # заново инициализируемо ось, по которой достигнуто максимальное значение
                self.state[ax] = iter(self.values[ax])
                self.val[ax] = next(self.state[ax])
                # и переходим к следующей оси
                continue
            # если перход к следущему значению на оси было выполнено успешно, то останавливаемся
            break
        else:
            # если по всем осям было достигнуто максимальное значение, то мы все перебрали
            # и при следующем запуске next будет остановка
            self.val = None
        return res


def run():
    
    pgroups = par.strategy(restricte_groups_for_anneal_method = False)
    print('Net creating on every parametor group:') # not seq
    par.print_strategy(pgroups)
    
    spec_procs = par.specs()
    if gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
        print('Synchronous net creating for specs :')  # all
    else:
        print('Net creating for every spec :')  # every_spec
    par.print_specs(spec_procs)
    
    # запуск при значениях параметра по-умолчанию
    clc.calculate_abs_values(spec_procs, {})
    
    for group in pgroups:
        print("---------------------------------------------------------------------------")
        print("Group:", group)
        if gl.SYNCHRONOUS_OPTIMIZATION_FOR_SPECS:
            create_net(spec_procs, group)
        else:
            for specname, proclist in spec_procs.items():
                print("---------------------------------------------------------------------------")
                print("Spec:", specname)
                create_net({specname: proclist}, group)

    
def create_net(procs_dic, pgroup, points_num = gl.points_num):
    """
        Построение многомерной сетки для группы параметров pgroup
    """
        
    # получаем список возможных значений для каждого параметра
    values = {}
    for parname in pgroup:
        # получаем минимальное и максимальное значения для parname
        if parname == 'dcs':
            parname = 'dcs_level'
        vtype = par.val_type[parname]
        min_value_par, max_value_par = par.ranges[parname]
        # получаем список возможных значений для parname
        if vtype == bool:
            values[parname] = [False, True]
        else:
            if points_num == 1:
                val = (max_value_par + min_value_par) / 2
                if vtype == int:
                    val = round(val)
                values[parname] = [val]
            else:
                segments_num = points_num - 1
                vals = []
                for i in range(points_num):
                    val = min_value_par + i * (max_value_par - min_value_par) / segments_num
                    if vtype == int:
                        val = round(val)
                    if not val in vals:
                        vals.append(val)
                values[parname] = vals
                    
    # строим узлы сетки
    nodes = iter(VectIter(values))
    
    # вычисляем узел значений по-умолчанию
    par_value_default = {}
    for parname in pgroup:
        if parname == 'dcs':
            par_value_default['dcs_kill'] = par.default_value['dcs_kill']
            par_value_default['dcs_level'] = par.default_value['dcs_level']
        else:
            par_value_default[parname] = par.default_value[parname]
                        
    # добавляем в базу результат запуска при значении параметров по-умолчанию
    for specname, proclist in procs_dic.items():
            t_c, t_e, v_mem = train.DB[specname].default
            train.DB[specname].add(proclist, par_value_default, t_c, t_e, v_mem)
    
    # производим вычисления в узлах сетки
    for node in nodes:
        if 'dcs_level' in node:
            if node['dcs_level'] == 0:
                node['dcs_kill'] = False
            else:
                node['dcs_kill'] = True
        if node == par_value_default:
            continue
        print(node)
        clc.calculate_abs_values(procs_dic, node)
    
