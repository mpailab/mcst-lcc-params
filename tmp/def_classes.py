#!/usr/bin/python

class Node:
    def __init__(self):
        # отображение: имя характеристики узла -> значение этой характеристики
        self.chars = {}

class Proc:
    def __init__(self):
        # отображение: имя характеристики процедуры -> значение этой характеристики
        self.chars = {}

        # неассоциативный массив узлов (типа Node) процедуры; ключами выступают номера узлов в процедуре
        self.nodes = {}

        # отображение: номер головы региона -> регион (типа Region)
        self.regions = {}

        # отображение: имя характеристики процедуры на этапе -> значение этой характеристики
        #self.icv_chars = {}

class Region:
    def __init__(self):

        # отображение: имя характеристики региона -> значение этой характеристики
        self.chars = {}

        # неассоциативный массив узлов, которые пытались добавить в регион; ключами выступают номера узлов в процедуре
        self.nodes = {}

class Task:
    def __init__(self):
        self.name = ''
        # map: procname -> importance
        self.proc_cnt = {}
        # map: procname -> proc
        self.procs = {}
        # map: procname -> proc на этапе if_conv
        self.icv_procs = {}

class Icv_Proc:
    '''процедура на этапе if_conv'''
    def __init__(self):
        # отображение: имя характеристики процедуры -> значение этой характеристики
        self.chars = {}

        self.regions = {}

class Icv_Region:
    '''регион на этапе if_conv'''
    def __init__(self):
        # отображение: имя характеристики региона -> значение этой характеристики
        self.chars = {}
        # отображение: номер головы участка региона -> участок региона
        self.sects = {}

class Dcs_level:
    '''результаты применения оптимизации фазы dcs к процедуре'''
    def __init__(self, procname, opt_level, n_num, e_num, l_num, nd_num, ed_num, ld_num, N, E, L):
        self.procname = procname # имя процедуры, к которой применяется оптимизация
        self.opt_level = opt_level # применяемый уровень оптизации фазы dcs
        self.n_num = n_num # общее количество узлов в процедуре
        self.e_num = e_num # общее количество ребер в процедуре
        self.l_num = l_num # общее количество циклов в процедуре
        self.nd_num = nd_num # количество найденных мертвых узлов в процедуре
        self.ed_num = ed_num # количество найденных мертвых ребер в процедуре
        self.ld_num = ld_num # количество найденных мертвых циклов в процедуре
        self.N = N # множество номеров всех найденных мертвых узлов
        self.E = E # множество номеров всех найденных мертвых ребер
        self.L = L # множество номеров всех найденных мертвых циклов
