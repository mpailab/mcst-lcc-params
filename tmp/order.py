import sys, os, shutil
from functools import reduce

source_path = sys.argv[1]
order_path = sys.argv[2]
dist_path = sys.argv[3]

if os.path.exists(dist_path):
    shutil.rmtree(dist_path)
os.makedirs(dist_path)

class Node:
    def __init__ (node, n, t, c, os):
        node.number     = n       # номер узла
        node.type       = t       # тип узла
        node.counter    = c       # счётчик узла
        node.opers_num  = os[0]   # число операций в узле
        node.calls_num  = os[1]   # число операций вызова в узле
        node.loads_num  = os[2]   # число операций чтения в узле
        node.stores_num = os[3]   # число операций записи в узле

class Loop:
    def __init__ (loop, n, ovl, red):
        loop.number = n    # номер цикла
        loop.is_ovl = ovl  # признак накрученного цикла
        loop.is_red = red  # признак сводимиго цикла

class Proc:
    def __init__ (proc, name, ns, ls, ds, ps):
        proc.name = name           # имя процедуры
        proc.order = 0             # число тактов исполнения процедуры
        proc.nodes = ns            # узлы процедуры
        proc.loops = ls            # циклы процедуры
        proc.dom_height  = ds[0]   # высота дерева доминаторов
        proc.dom_weight  = ds[1]   # ширина дерева доминаторов
        proc.dom_branch  = ds[2]   # максимальное ветвление вершины в дереве доминаторов
        proc.pdom_height = ps[0]   # высота дерева постдоминаторов
        proc.pdom_weight = ps[1]   # ширина дерева постдоминаторов
        proc.pdom_branch = ps[2]   # максимальное ветвление вершины в дереве постдоминаторов

class Spec:
    def __init__(self, name, ps):
        self.name  = name      # имя задачи
        self.procs = ps        # процедуры задачи

def init_node (str):
    h = str.split('#')
    return Node(int(h[0]), int(h[1]), float(h[2]), list(map(int, h[3].split('|'))))

def init_loop (str):
    h = str.split('#')
    return Loop(int(h[0]), bool(h[1]), bool(h[2]))

def init_proc (str):
    h = str.split(' ')
    return Proc(h[0],
                list(map(init_node, h[1].split('&'))),
                list(map(init_loop, h[2].split('&'))),
                h[3].split('&'),
                h[4].split('&'))

def init_spec (path, source):
    with open(path + "/" + source) as f:
        return Spec(source.split(".")[0],
                    list(map(init_proc, f.read().splitlines())))

def print_proc (proc, file):
    file.write(proc.name + " ")
    file.write(str(proc.order) + " ")
    file.write('&'.join(map(lambda n:
        str(n.number) + "#" +
        str(n.type) + "#" +
        str(n.counter) + "#" +
        str(n.opers_num) + "|" + str(n.calls_num) + "|" + str(n.loads_num) + "|" + str(n.stores_num),
        proc.nodes)) + " ")
    file.write('&'.join(map(lambda l:
        str(l.number) + "#" +
        str(l.is_ovl) + "#" +
        str(l.is_red),
        proc.loops)) + " ")
    file.write(str(proc.dom_height) + "&" + str(proc.dom_weight) + "&" + str(proc.dom_branch) + " ")
    file.write(str(proc.pdom_height) + "&" + str(proc.pdom_weight) + "&" + str(proc.pdom_branch) + "\n")

# specs = list(map(lambda x: init_spec(source_path, x), os.listdir(source_path)))

for spec in os.listdir(source_path):
    procs = {}
    with open(source_path + "/" + spec) as f:
        for s in f.read().splitlines():
            proc = init_proc(s)
            procs[proc.name] = proc
    if os.path.exists(order_path + "/" + spec):
        with open(order_path + "/" + spec) as f:
            for s in f.read().splitlines():
                h = s.split()
                if h[0] in procs: procs[h[0]].order = int(h[1])
    dist = open(dist_path + "/" + spec, 'w')
    for proc in procs.values():
        print_proc(proc, dist)
    dist.close()
