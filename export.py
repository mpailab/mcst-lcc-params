#!/usr/bin/python
# -*- coding: utf-8 -*-

# External imports
import os, sys

def export_model(model, path):

    with open(path + '/ann_iface.h', 'w') as f:
        f.write("""
#ifndef ANN_IFACE_H
#define ANN_IFACE_H
/**
 * ann_iface.h - интерфейс работы с искусственными нейронными сетями
 *
 * Copyright (c) 1992-2019 AO "MCST". All rights reserved.
 */

 export void ann_Main( arr_Array_ptr input);

 #endif /* ! ANN_IFACE_H */
        """)

    with open(path + '/ann.c', 'w') as f:
        f.write("""
/**
 * ann.c - интерфейс работы с искусственными нейронными сетями
 *
 * Copyright (c) 1992-2019 AO "MCST". All rights reserved.
 */

#include "nn_iface.h"

/**
 * Вычисление функции Relu на массиве вещественных чисел
 * 
 * Warnings: Результат зависывается в тот же массив
 */
static void
ann_Relu( arr_Array_ptr input) /* массив вещественных чисел */
{
    unsigned int i, n = arr_GetLength( input);

    /* Имеет смысл применяться только к непустому массиву */
    if ( n == 0 )
    {
        return;
    }

    /* Собственно вычисление функции Relu для элементов массива */
    for ( i = 0; i < n; i++ )
    {
        elem = arr_GetProf( input, i);
        if ( fpa_IsLes( elem, ECOMP_ZERO_PROFILE) )
        {
            arr_SetProf( input, i, ECOMP_ZERO_PROFILE);
        }
    }

    return;
} /* ann_Relu */

/**
 * Вычисление функции SoftMax на массиве вещественных чисел
 * 
 * Warnings: Результат зависывается в тот же массив
 */
static void
ann_SoftMax( arr_Array_ptr input) /* массив вещественных чисел */
{
    ecomp_Profile_t elem, max, sum, offset;
    unsigned int i, n = arr_GetLength( input);

    /* Имеет смысл применяться только к непустому массиву */
    if ( n == 0 )
    {
        return;
    }

    /* Находим максимальное значение в массиве */
    max = arr_GetProf( input, 0);
    for ( i = 1; i < n; i++ )
    {
        elem = arr_GetProf( input, i);
        if ( fpa_IsGrt( elem, max) )
        {
            max = elem;
        }
    }

    /* Находим нормализованную сумму элементов массива */
    sum = ECOMP_ZERO_PROFILE;
    for ( i = 0; i < n; i++ )
    {
        elem = arr_GetProf( input, i);
        sum = fpa_Add( sum, fpa_Exp( fpa_Sub( elem, max)));
    }

    /* Собственно вычисление функции SoftMax для элементов массива */
    offset = fpa_Add( max, fpa_Log( sum));
    for ( i = 0; i < n; i++ )
    {
        elem = arr_GetProf( input, i);
        arr_SetProf( input, i, fpa_Exp( fpa_Sub( elem, offset)));
    }

    return;
} /* ann_SoftMax */

/* Тип функции активации */
typedef void (* ann_ActivationFunc_t) (arr_Array_ptr);

void
ann_Main( arr_Array_ptr input) /* массив вещественных чисел */
{
    unsigned int i;
        """)

        layers = [layer for layer in model.layers if type(layer).__name__ not in ['Dropout', 'Flatten']]
        assert (any (type(layer).__name__ not in ['Dense'] for layer in model.layers))

        f.write("""
    arr_Array_ptr weights[""" + len(layers) + """];
    arr_Array_ptr biases[""" + len(layers) + """];
    ann_ActivationFunc_t activation[""" + len(layers) + """];

        """)

        l = 0
        for layer in layers:

            weights = layer.get_weights()[0]
            (n,m) = weights.shape()

            biases = layer.get_weights()[1]
            (k,)  = biases.shape()

            activation = layer.get_config()['activation']

            assert (n == k and activation in ['relu', 'softmax'])

            g = 'ann_Relu' if activation == 'relu' else 'ann_SoftMax'

            f.write("""
    weights[""" + str(l) + """] = arr_NewMatrix( ARR_PROF_UNITS, """ + str(n) + """, """ + str(m) + """);
            """)

            for i, j in zip(range(n), range(m)):

                w = weights.item((i, j))
                assert (isinstance(w, float))

                f.write("""
    arr_SetMatrixProf( weights[""" + str(l) + """], """ + str(i) + """, """ + str(j) + """, fpa_ConvFloatVal( """ + str(w) + """));
                """)

            f.write("""

    biases[""" + str(l) + """]  = arr_NewArray( ARR_PROF_UNITS, """ + str(n) + """, ARR_ZERO_INIT);
            """)

            for i in range(n):

                w = biases.item(i)
                assert (isinstance(w, float))

                f.write("""
    arr_SetProf( biases[""" + str(l) + """], """ + str(i) + """, fpa_ConvFloatVal( """ + str(w) + """));
                """)

            f.write("""

    activation[""" + str(l) + """] = """ + g + """;

            """)

            l += 1

        f.write("""
    for ( l = 0; l < """ + str(l) + """; l++ )
    {
        n = arr_GetLength( weights[l]);
        m = arr_GetMatrixDimension( weights[l]);
        ECOMP_ASSERT( arr_GetLength( input) == m );

        next_input = arr_NewArray( ARR_PROF_UNITS, n, ARR_ZERO_INIT);
        for ( i = 0; i < n; i++ )
        {
            x = arr_GetProf( biases[l], i);
            for ( j = 0; j < m; j++ )
            {
                x = fpa_Add( x, fpa_Mul( arr_GetMatrixProf( weights[l], i, j), arr_GetProf( input, j)));
            }
            arr_SetProf( next_input, i, x)
        }

        input = next_input;
    }

    return;
} /* ann_Main */
        """)
