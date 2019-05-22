import sys
import os
import re
import shutil
from functools import reduce

source_path = sys.argv[1]
dist_path = sys.argv[2]

if os.path.exists(dist_path):
    shutil.rmtree(dist_path)
os.makedirs(dist_path)

class Node:
    def __init__(self, n, t):
        self.number     = n   # номер узла
        self.type       = t   # тип узла
        self.counter    = 0   # счётчик узла
        self.opers_num  = 0   # число операций в узле
        self.calls_num  = 0   # число операций вызова в узле
        self.loads_num  = 0   # число операций чтения в узле
        self.stores_num = 0   # число операций записи в узле

class Loop:
    def __init__(self, n, ovl, red):
        self.number     = n     # номер цикла
        self.overlapped = ovl   # признак накрученного цикла
        self.reduced    = red   # признак сводимиго цикла

class Proc:
    def __init__(self, name):
        self.name = name       # имя процедуры
        self.nodes = {}        # узлы процедуры
        self.loops = {}        # циклы процедуры
        self.dom_height  = 0   # высота дерева доминаторов
        self.dom_weight  = 0   # ширина дерева доминаторов
        self.dom_succs   = 0   # максимальное ветвление вершины в дереве доминаторов
        self.pdom_height = 0   # высота дерева постдоминаторов
        self.pdom_weight = 0   # ширина дерева постдоминаторов
        self.pdom_succs  = 0   # максимальное ветвление вершины в дереве постдоминаторов

node_type = {
    "Simple" : 0,
    "If"     : 1,
    "Return" : 2,
    "Start"  : 3,
    "Stop"   : 4,
    "Switch" : 5,
    "Hyper"  : 6,
    "Jump"   : 7,
    "Tmp"    : 8
    }

source_path = sys.argv[1]
dist_path = sys.argv[2]

for spec_name in os.listdir(source_path):
    dist = open(dist_path + '/' + spec_name + '.txt', 'w')
    for proc_name in os.listdir(source_path + "/" + spec_name):
        proc = Proc(proc_name.split(".")[0])
        file = open(source_path + "/" + spec_name + "/" + proc_name)
        for line in file:
            line = line[:-1]
            if line[0] == 'N':
                n = int(line.split()[0].split(":")[1])
                p = line.split()[1].split(":")[0]
                v = line.split()[1].split(":")[1]
                if p == "type":    proc.nodes[n] = Node(n,node_type[v])
                elif p == "cnt":   proc.nodes[n].counter = float(v)
                elif p == "o_num": proc.nodes[n].opers_num = int(v)
                elif p == "c_num": proc.nodes[n].calls_num = int(v)
                elif p == "l_num": proc.nodes[n].loads_num = int(v)
                elif p == "s_num": proc.nodes[n].stores_num = int(v)
                elif p == "L":
                    ovl = line.split()[2].split(":")[1]
                    red = line.split()[3].split(":")[1]
                    proc.loops[int(v)] = Loop(int(v),ovl,red)
            else:
                p = line.split(":")[0]
                v = int(line.split(":")[1])
                if p == "dom_height":    proc.dom_height = v
                elif p == "dom_weight":  proc.dom_weight = v
                elif p == "dom_succs":   proc.dom_succs = v
                elif p == "pdom_height": proc.pdom_height = v
                elif p == "pdom_weight": proc.pdom_weight = v
                elif p == "pdom_succs":  proc.pdom_succs = v
        file.close()
        dist.write(proc.name + " ")
        dist.write('&'.join(map(lambda n:
            str(n.number) + "#" +
            str(n.type) + "#" +
            str(n.counter) + "#" +
            str(n.opers_num) + "|" + str(n.calls_num) + "|" + str(n.loads_num) + "|" + str(n.stores_num),
            proc.nodes.values())) + " ")
        dist.write('&'.join(map(lambda l:
            str(l.number) + "#" +
            str(l.overlapped) + "#" +
            str(l.reduced),
            proc.loops.values())) + " ")
        dist.write(str(proc.dom_height) + "&" + str(proc.dom_weight) + "&" + str(proc.dom_succs) + " ")
        dist.write(str(proc.pdom_height) + "&" + str(proc.pdom_weight) + "&" + str(proc.pdom_succs) + "\n")
    dist.close()
