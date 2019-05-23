#!/usr/bin/python
# -*- coding: utf-8 -*-

# External imports
from math import erf

# Internal imports
import par
import global_vars as gl

def cerf(x):
    '''
    Функция сглаживания для параметров с вещественными значениями
    '''
    return erf(x * gl.ERF_KOEF_FOR_CONTINUOUS_PAR)
def derf(x):
    '''
    Функция сглаживания для параметров со значениями в int
    '''
    return erf(x * gl.ERF_KOEF_FOR_DISCRETE_PAR)

def get_erf(parname):
    '''
    Получить функцию сглаживания для параметра parname
    '''
    if par.val_type[parname] == int:
        return derf
    if par.val_type[parname] == float:
        return cerf
    if par.val_type[parname] == bool:
        raise BaseException('There is not smooth for bool parametors')

class Block:
    '''
    Блок элементов упорядоченного по некоторому признаку массива, равных по этому признаку
    '''
    def __init__(self, val, wsum, num, p_left, p_right):
        self.val = val # значение одинакового признака для всех элементов блока
        self.wsum = wsum # сумма весов всех элементов блока
        self.num = num # порядковый номер блока в упорядоченном массиве
        self.pl = p_left # номер первого элемента блока в упорядоченном массиве
        self.pr = p_right # номер последнего элемента блока в упорядоченном массиве + 1
        
class ItrBlocks:
    '''
    Итератор, который перебирает все блоки по степени их удаленности от некоторого заданного блока 
    '''
    def __iter__(self):
        return self
    
    def __init__(self, bl_center, blocks):
        self.bl_center = bl_center
        self.bl_left = bl_center
        self.bl_right = bl_center
        self.blk = blocks
        
    def see_left(self):
        lnum = self.bl_left.num
        if lnum != 0:
            return self.blk[lnum - 1]
        else:
            return None
    
    def see_right(self):
        rnum = self.bl_right.num
        if rnum != len(self.blk) - 1:
            return self.blk[rnum + 1]
        else:
            return None
        
    def __next__(self):
        cand_left =  self.see_left()
        cand_right = self.see_right()
        if cand_left == None:
            if cand_right == None:
                raise StopIteration
            else:
                self.bl_right = cand_right
                right_dist = abs(cand_right.val - self.bl_center.val)
                return (cand_right,), right_dist
        else:
            if cand_right == None:
                self.bl_left = cand_left
                left_dist = abs(cand_left.val - self.bl_center.val)
                return (cand_left,), left_dist
            else:
                left_dist = abs(cand_left.val - self.bl_center.val)
                right_dist = abs(cand_right.val - self.bl_center.val)
                if left_dist < right_dist:
                    self.bl_left = cand_left
                    return (cand_left,), left_dist
                if left_dist > right_dist:
                    self.bl_right = cand_right
                    return (cand_right,), right_dist
                # если дошли сюда, то left_dist == right_dist, и двигаемся сразу в оба направления
                self.bl_left = cand_left
                self.bl_right = cand_right
                return (cand_left, cand_right), left_dist

def return_weights(pr, sdis, bls, array, w_dis):
    '''
    Процедура уменьшает на процент pr веса элементов блоков bls массива array
    Результирующее распределение весов записывается в sdis
    '''
    for bl in bls:
        for pos in range(bl.pl, bl.pr):
            key = array[pos]
            sdis[key] += pr * w_dis[key]

def give_weight(weight_value, sdis, bls, array):
    '''
    Процедура распределяет вес weight_value на элементы блоков bls массива array
    sdis --- форимируемое распределение весов
    '''
    # считаем число элементов во всех блоках
    w_del = 0.
    for bl in bls:
        w_del += bl.pr - bl.pl
    # распределеляем weight_value равномерно по всем блокам
    for bl in bls:
        for pos in range(bl.pl, bl.pr):
            key = array[pos]
            sdis[key] += weight_value / w_del
        
def get_blocks(array, coord, w_dis):
    '''
    Функция blocks разрезает на блоки массив array, упорядоченный по принципу: a[i] < a[j], если a[i][coord] < a[j][coord].
    '''
    blocks = []
    if len(array) == 0:
        raise BaseException('array is empty')
    el = array[0]
    val_bl = el[coord]
    wsum = w_dis[el]
    bl_cnt = 0
    p_left = 0
    for pos in range(1, len(array)):
        el = array[pos]
        val = el[coord]
        w_el = w_dis[el]
        if val == val_bl:
            wsum += w_el
        else:
            bl = Block(val_bl, wsum, bl_cnt, p_left, pos)
            blocks.append(bl)
            val_bl = val
            wsum = w_el
            bl_cnt += 1
            p_left = pos
    else:
        bl = Block(val_bl, wsum, bl_cnt, p_left, pos + 1)
        blocks.append(bl)
    return blocks

def smooth_dis(array, coord, w_dis, erff):
    '''
    array --- массив векторов одинаковой длины, упорядоченный по координате coord,
    w_dis --- отображение, которое каждому элементу массива array, сопоставляет некоторое число (вес)
    Функция smooth_dis возвращает "сглаживание" w_dis,
    в котором вес каждого элемента массива array частично распределяется на соседние элементы.
    Распределение веса зависит от удаленности элементов массива array по координате coord,
    и определяется функцией erff.
    '''
    sdis = {}
    for key in w_dis.keys():
        sdis[key] = 0.
        
    blocks = get_blocks(array, coord, w_dis)
    for bl_center in blocks:
        w_amount = bl_center.wsum
        # если распределяемый вес маленький, то распределять нечего
        if w_amount < gl.ZERO_LIMIT_FOR_WEIGHT:
            return_weights(1, sdis, (bl_center,), array, w_dis)
            sdis[key] = w_amount
            continue
        itr_blocks = ItrBlocks(bl_center, blocks) # итератор, который перебирает все блоки по удаленности их от bl_center
        bls = (bl_center,)
        er_dist = erff(0)
        for bls_next, dist_next in itr_blocks:
            er_dist_next = erff(dist_next)
            pr = er_dist_next - er_dist # доля веса блока bl_center, которая будет распределена на блоки bls
            
            # распределяем долю веса bl_center на элементы блоков bls
            give_weight(pr * w_amount, sdis, bls, array)
            
            pr_rest = 1 - er_dist_next
            # если доля оставшегося для распределения веса пренебрежимо мала, то прерываем распределение веса
            if pr_rest < gl.ZERO_LIMIT_FOR_ERF:
                # тут тоже надо вернуть вес?
                # return_weights(pr_rest, sdis, (bl_center,), array, w_dis)
                break
            # если абсолютное значение оставшегося для распределения веса мало, то прекращаем распределение веса
            if w_amount * pr_rest < gl.ZERO_LIMIT_FOR_WEIGHT:
                return_weights(pr_rest, sdis, (bl_center,), array, w_dis)
                break
            
            bls = bls_next
            er_dist = er_dist_next
        else:
            pr = 1 - er_dist 
            # распределяем оставшеюся долю веса bl_center на самый удаленный от bl_center блок
            give_weight(pr * w_amount, sdis, bls, array)
            
    return sdis

def get_sm_dis(value_par, reg_parnames, icv_parnames, dis_regpar, dis_icvpar, smooth_stat = gl.SMOOTH_STAT):
    # dis_regpar и dis_icvpar должны быть уже нормированы
    sm_dis = {}
    if not smooth_stat:
        for parname in reg_parnames:
            sm_dis[parname] = dis_regpar
        for parname in icv_parnames:
            sm_dis[parname] = dis_icvpar
    else:
        for parname in reg_parnames:
            erff = get_erf(parname)
            coord = par.index_in_reg_seq[parname]
            if value_par[parname]:
                sm_dis[parname] = smooth_dis(value_par[parname], coord, dis_regpar, erff)
            else:
                sm_dis[parname] = dis_regpar
        for parname in icv_parnames:
            erff = get_erf(parname)
            coord = par.index_in_icv_seq[parname]
            if value_par[parname]:
                sm_dis[parname] = smooth_dis(value_par[parname], coord, dis_icvpar, erff)
            else:
                sm_dis[parname] = dis_icvpar
    return sm_dis
