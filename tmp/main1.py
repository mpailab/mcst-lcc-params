import sys
from os import listdir

source_path = sys.argv[1]

class Node:
    def __init__(self, data):
        self.data = data

    def number(self):     self.data[0]     # номер узла
    def type(self):       self.data[1]     # тип узла
    def counter(self):    self.data[2]     # счётчик узла
    def opers_num(self):  self.data[3][0]  # число операций в узле
    def calls_num(self):  self.data[3][1]  # число операций вызова в узле
    def loads_num(self):  self.data[3][2]  # число операций чтения в узле
    def stores_num(self): self.data[3][3]  # число операций записи в узле

class Loop:
    def __init__(self, data):
        self.data = data

    def number(self): self.data[0]  # номер цикла
    def is_ovl(self): self.data[1]  # признак накрученного цикла
    def is_red(self): self.data[2]  # признак сводимиго цикла

class Proc:
    def __init__(self, data):
        self.data = data

    def name(self):        self.data[0]     # имя процедуры
    def nodes(self):       self.data[1]     # узлы процедуры
    def loops(self):       self.data[2]     # циклы процедуры
    def dom_height(self):  self.data[3][0]  # высота дерева доминаторов
    def dom_weight(self):  self.data[3][1]  # ширина дерева доминаторов
    def dom_succs(self):   self.data[3][2]  # максимальное ветвление вершины в дереве доминаторов
    def pdom_height(self): self.data[4][0]  # высота дерева постдоминаторов
    def pdom_weight(self): self.data[4][1]  # ширина дерева постдоминаторов
    def pdom_succs(self):  self.data[4][2]  # максимальное ветвление вершины в дереве постдоминаторов

class Spec:
    def __init__(self, data):
        self.data = data

    def name(self):  self.data[0] # имя задачи
    def procs(self): self.data[1] # процедуры задачи

def init_node (str):
    h = str.split('#')
    return Node([int(h[0]), int(h[1]), float(h[2]), list(map(int, h[3].split('|')))])

def init_loop (str):
    h = str.split('#')
    return Loop([int(h[0]), bool(h[1]), bool(h[2])])

def init_proc (str):
    h = str.split(' ')
    return Proc([h[0],
                 list(map(init_node, h[1].split('&'))),
                 list(map(init_loop, h[2].split('&'))),
                 list(map(int, h[3].split('&'))),
                 list(map(int, h[4].split('&')))])

def init_spec (path, source):
    with open(path + "/" + source) as f:
        return Spec([source.split(".")[0],
                     list(map(init_proc, f.read().splitlines()))])

specs = list(map(lambda x: init_spec(source_path, x), listdir(source_path)))

def opers_num(proc):
    return reduce(lambda a, n: a + n.opers_num, proc.nodes.values(), 0)

def calls_num(proc):
    return reduce(lambda a, n: a + n.calls_num, proc.nodes.values(), 0)

def loads_num(proc):
    return reduce(lambda a, n: a + n.loads_num, proc.nodes.values(), 0)

def stores_num(proc):
    return reduce(lambda a, n: a + n.stores_num, proc.nodes.values(), 0)

def nodes_num(proc):
    return len(proc.nodes)

def loops_num(proc):
    return len(proc.loops)

def ovl_loops_num(proc):
    return len(filter(lambda l: l.ovl == 1, proc.loops.values()))

def irred_loops_num(proc):
    return len(filter(lambda l: l.red == 0, proc.loops.values()))

def max_cnt(proc):
    return reduce(lambda a, n: n.counter if a < n.counter else a, proc.nodes.values(), 0)
