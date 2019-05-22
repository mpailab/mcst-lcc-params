import sys, os, shutil
from functools import reduce

source_path = sys.argv[1]
dist_path = sys.argv[2]

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

    def w_opers_num (node):
        return node.opers_num * node.counter

    def w_calls_num (node):
        return node.calls_num * node.counter

    def calls_density (node):
        return node.calls_num / node.opers_num

    def w_loads_num (node):
        return node.loads_num * node.counter

    def loads_density (node):
        return node.loads_num / node.opers_num

    def w_stores_num (node):
        return node.stores_num * node.counter

    def stores_density (node):
        return node.stores_num / node.opers_num

class Loop:
    def __init__ (loop, n, ovl, red):
        loop.number = n    # номер цикла
        loop.is_ovl = ovl  # признак накрученного цикла
        loop.is_red = red  # признак сводимиго цикла

class Proc:
    def __init__ (proc, name, t, ns, ls, ds, ps):
        proc.name = name           # имя процедуры
        proc.ticks = t             # число тактов исполнения процедуры
        proc.nodes = ns            # узлы процедуры
        proc.loops = ls            # циклы процедуры
        proc.dom_height  = ds[0]   # высота дерева доминаторов
        proc.dom_weight  = ds[1]   # ширина дерева доминаторов
        proc.dom_branch  = ds[2]   # максимальное ветвление вершины в дереве доминаторов
        proc.pdom_height = ps[0]   # высота дерева постдоминаторов
        proc.pdom_weight = ps[1]   # ширина дерева постдоминаторов
        proc.pdom_branch = ps[2]   # максимальное ветвление вершины в дереве постдоминаторов

    def opers_num (proc):
        return reduce(lambda a, n: a + n.opers_num, proc.nodes, 0)

    def w_opers_num (proc):
        if proc.max_cnt():
            return reduce(lambda a, n: a + n.w_opers_num(), proc.nodes, 0) / proc.max_cnt()
        else:
            return 0

    def max_opers_num (proc):
        return reduce(max, map(lambda n: n.opers_num, proc.nodes), 0)

    def aver_opers_num (proc):
        return proc.opers_num() / proc.nodes_num()

    def w_aver_opers_num (proc):
        return proc.w_opers_num() / proc.nodes_num()

    def calls_num (proc):
        return reduce(lambda a, n: a + n.calls_num, proc.nodes, 0)

    def w_calls_num (proc):
        if proc.max_cnt():
            return reduce(lambda a, n: a + n.w_calls_num(), proc.nodes, 0) / proc.max_cnt()
        else:
            return 0

    def max_calls_num (proc):
        return reduce(max, map(lambda n: n.calls_num, proc.nodes), 0)

    def aver_calls_num (proc):
        return proc.calls_num() / proc.nodes_num()

    def w_aver_calls_num (proc):
        return proc.w_calls_num() / proc.nodes_num()

    def calls_density (proc):
        return reduce(lambda a, n: a + n.calls_density(), proc.nodes, 0)

    def w_calls_density (proc):
        if proc.max_cnt():
            return reduce(lambda a, n: a + n.calls_density(), proc.nodes, 0) / proc.max_cnt()
        else:
            return 0

    def max_calls_density(proc):
        return reduce(max, map(lambda n: n.calls_density(), proc.nodes), 0)

    def aver_calls_density(proc):
        return proc.calls_density() / proc.nodes_num()

    def w_aver_calls_density(proc):
        return proc.w_calls_density() / proc.nodes_num()

    def loads_num (proc):
        return reduce(lambda a, n: a + n.loads_num, proc.nodes, 0)

    def w_loads_num (proc):
        if proc.max_cnt():
            return reduce(lambda a, n: a + n.w_loads_num(), proc.nodes, 0) / proc.max_cnt()
        else:
            return 0

    def max_loads_num (proc):
        return reduce(max, map(lambda n: n.loads_num, proc.nodes), 0)

    def aver_loads_num (proc):
        return proc.loads_num() / proc.nodes_num()

    def w_aver_loads_num (proc):
        return proc.w_loads_num() / proc.nodes_num()

    def loads_density (proc):
        return reduce(lambda a, n: a + n.loads_density(), proc.nodes, 0)

    def w_loads_density (proc):
        if proc.max_cnt():
            return reduce(lambda a, n: a + n.loads_density(), proc.nodes, 0) / proc.max_cnt()
        else:
            return 0

    def max_loads_density(proc):
        return reduce(max, map(lambda n: n.loads_density(), proc.nodes), 0)

    def aver_loads_density(proc):
        return proc.loads_density() / proc.nodes_num()

    def w_aver_loads_density(proc):
        return proc.w_loads_density() / proc.nodes_num()

    def stores_num (proc):
        return reduce(lambda a, n: a + n.stores_num, proc.nodes, 0)

    def w_stores_num (proc):
        if proc.max_cnt():
            return reduce(lambda a, n: a + n.w_stores_num(), proc.nodes, 0) / proc.max_cnt()
        else:
            return 0

    def max_stores_num (proc):
        return reduce(max, map(lambda n: n.stores_num, proc.nodes), 0)

    def aver_stores_num (proc):
        return proc.stores_num() / proc.nodes_num()

    def w_aver_stores_num (proc):
        return proc.w_stores_num() / proc.nodes_num()

    def stores_density (proc):
        return reduce(lambda a, n: a + n.stores_density(), proc.nodes, 0)

    def w_stores_density (proc):
        if proc.max_cnt():
            return reduce(lambda a, n: a + n.stores_density(), proc.nodes, 0) / proc.max_cnt()
        else:
            return 0

    def max_stores_density(proc):
        return reduce(max, map(lambda n: n.stores_density(), proc.nodes), 0)

    def aver_stores_density(proc):
        return proc.stores_density() / proc.nodes_num()

    def w_aver_stores_density(proc):
        return proc.w_stores_density() / proc.nodes_num()

    def nodes_num (proc):
        return len(proc.nodes)

    def w_nodes_num (proc):
        if proc.max_cnt():
            return reduce(lambda a, n: a + n.counter, proc.nodes, 0) / proc.max_cnt()
        else:
            return 0

    def loops_num (proc):
        return len(proc.loops)

    def ovl_loops_num (proc):
        return len([l for l in proc.loops if l.is_ovl])

    def irr_loops_num (proc):
        return len([l for l in proc.loops if not l.is_red])

    def max_cnt (proc):
        return reduce(max, map(lambda n: n.counter, proc.nodes), 0)

    def aver_cnt (proc):
        return reduce(lambda a, n: a + n.counter, proc.nodes, 0) / proc.nodes_num()

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
                h[1],
                list(map(init_node, h[2].split('&'))),
                list(map(init_loop, h[3].split('&'))),
                h[4].split('&'),
                h[5].split('&'))

def init_spec (path, source):
    with open(path + "/" + source) as f:
        return Spec(source.split(".")[0],
                    list(map(init_proc, f.read().splitlines())))

params = [
    (  0, "Число тактов исполнения процедуры", lambda p: p.ticks),
    (  1, "Число операций", Proc.opers_num),
    (  2, "Взвешенное число операций", Proc.w_opers_num),
    (  3, "Максимальное число операций в узле", Proc.max_opers_num),
    (  4, "Среднее число операций в узле", Proc.aver_opers_num),
    (  5, "Взвешенное среднее число операций в узле", Proc.w_aver_opers_num),

    (  6, "Число операций вызова", Proc.calls_num),
    (  7, "Взвешенное число операций вызова", Proc.w_calls_num),
    (  8, "Максимальное число операций вызова в узле", Proc.max_calls_num),
    (  9, "Среднее число операций вызова в узле", Proc.aver_calls_num),
    ( 10, "Взвешенное среднее число операций вызова в узле", Proc.w_aver_calls_num),
    ( 11, "Плотность операций вызова", Proc.calls_density),
    ( 12, "Взвешенная плотность операций вызова", Proc.w_calls_density),
    ( 13, "Максимальная плотность операций вызова в узле", Proc.max_calls_density),
    ( 14, "Средняя плотность операций вызова в узле", Proc.aver_calls_density),
    ( 15, "Взвешенная средняя плотность операций вызова в узле", Proc.w_aver_calls_density),

    ( 16, "Число операций чтения", Proc.loads_num),
    ( 17, "Взвешенное число операций чтения", Proc.w_loads_num),
    ( 18, "Максимальное число операций чтения в узле", Proc.max_loads_num),
    ( 19, "Среднее число операций чтения в узле", Proc.aver_loads_num),
    ( 20, "Взвешенное среднее число операций чтения в узле", Proc.w_aver_loads_num),
    ( 21, "Плотность операций чтений", Proc.loads_density),
    ( 22, "Взвешенная плотность операций вызова", Proc.w_loads_density),
    ( 23, "Максимальная плотность операций вызова в узле", Proc.max_loads_density),
    ( 24, "Средняя плотность операций вызова в узле", Proc.aver_loads_density),
    ( 25, "Взвешенная средняя плотность операций вызова в узле", Proc.w_aver_loads_density),

    ( 26, "Число операций записи", Proc.stores_num),
    ( 27, "Взвешенное число операций записи", Proc.w_stores_num),
    ( 28, "Максимальное число операций записи в узле", Proc.max_stores_num),
    ( 29, "Среднее число операций записи в узле", Proc.aver_stores_num),
    ( 30, "Взвешенное среднее число операций записи в узле", Proc.w_aver_stores_num),
    ( 31, "Плотность операций записи", Proc.stores_density),
    ( 32, "Взвешенная плотность операций вызова", Proc.w_stores_density),
    ( 33, "Максимальная плотность операций вызова в узле", Proc.max_stores_density),
    ( 34, "Средняя плотность операций вызова в узле", Proc.aver_stores_density),
    ( 35, "Взвешенная средняя плотность операций вызова в узле", Proc.w_aver_stores_density),

    ( 36, "Число узлов", Proc.nodes_num),
    ( 37, "Взвешенное число узлов", Proc.w_nodes_num),

    ( 38, "Число циклов", Proc.loops_num),
    ( 39, "Число накрученных циклов", Proc.ovl_loops_num),
    ( 40, "Число несводимых циклов", Proc.irr_loops_num),

    ( 41, "Максимальный счётчик", Proc.max_cnt),
    ( 42, "Средний счётчик", Proc.aver_cnt),

    ( 43, "Высота дерева доминаторов", lambda p: p.dom_height),
    ( 44, "Ширина дерева доминаторов", lambda p: p.dom_weight),
    ( 45, "Максимальное ветвление вершин в дереве доминаторов", lambda p: p.dom_branch),

    ( 46, "Высота дерева постдоминаторов", lambda p: p.pdom_height),
    ( 47, "Ширина дерева постдоминаторов", lambda p: p.pdom_weight),
    ( 48, "Максимальное ветвление вершин в дереве постдоминаторов", lambda p: p.pdom_branch),
]

def desc (param):
    return "{:>3} : {:>1}".format(param[0], param[1])

def calc (param, proc):
    f = param[2]
    return f(proc)

# specs = list(map(lambda x: init_spec(source_path, x), os.listdir(source_path)))

for spec in os.listdir(source_path):
    with open(dist_path + "/params.txt", 'w') as f:
        f.write("\n".join(map(desc, params)))
    dist = open(dist_path + "/" + spec, 'w')
    with open(source_path + "/" + spec) as f:
        for s in f.read().splitlines():
            proc = init_proc(s)
            print(" ".join(map(lambda x: str(calc(x, proc)), params)), file=dist)
    dist.close()
