/**
 * ann_real.c - интерфейс реализации искусственных нейронных сетей
 *
 * Copyright (c) 1992-2019 AO "MCST". All rights reserved.
 */

#include "ann_real.h"

/* Функции инициализации нейронных сетей */
const ann_InitModelFunc_t
ann_InitModel[ANN_MODELS_NUM] =
{
    ann_InitModel1
};

/**
 * Инициализация 1-ой нейронной сети
 */
static ann_Model_ref
ann_InitModel1( ann_Info_t *info) /* инфо */
{
    unsigned int layers_num = 1;
    unsigned int grid_size = 2;
    unsigned int options_num = 1;
    arr_Array_ptr weights     = arr_NewArray( ARR_PROF_UNITS, layers_num, ARR_ZERO_INIT);
    arr_Array_ptr biases      = arr_NewArray( ARR_PROF_UNITS, layers_num, ARR_ZERO_INIT);
    ann_ActivationFunc_t acts = arr_NewArray( ARR_PROF_UNITS, layers_num, ARR_ZERO_INIT);
    list_List_ref options     = arr_NewArray( ARR_PROF_UNITS, options_num, ARR_ZERO_INIT);
    arr_Array_ptr grid        = arr_NewMatrix( ARR_PROF_UNITS, options_num, grid_size);
    ann_Option_ref option;
    list_Unit_ref unit;

    /* 1-ый слой */
    {
        unsigned int m = 2; /* число нейронов на предыдущем слое */
        unsigned int n = 1; /* число нейронов на данном слое */

        /* Создаём атрибуты слоя */
        arr_Array_ptr A = arr_NewMatrix( ARR_PROF_UNITS, m, n);
        arr_Array_ptr b = arr_NewArray( ARR_PROF_UNITS, n, ARR_ZERO_INIT);

        /* Заполняем атрибуты слоя */
        arr_SetMatrixProf( A, 0, 0, fpa_ConvFloatVal( 0x0));
        arr_SetMatrixProf( A, 1, 0, fpa_ConvFloatVal( 0x0));
        arr_SetProf( b, 0, fpa_ConvFloatVal( 0x0));

        /* Запоминаем атрибуты слоя */
        arr_SetProf( weights, 0, A);
        arr_SetProf( biases, 0, b);
        arr_SetProf( acts, 0, ann_Relu);
    }

    /* Запоминаем опции, для которых обучена нейронная сеть, в заданном порядке */
    option = ann_NewOption( "regn_heur1", ANN_OPTION_FLOAT,
                            fpa_ConvFloatVal( scr_GetFloatOption( "regn_heur1")), info);
    arr_SetRef( options, 0, option);

    /* Запоминаем сетку значений опции, связанную с выходом нейронной сети */
    arr_SetMatrixProf( grid, 0, 0, fpa_ConvFloatVal( 0x0));
    arr_SetMatrixProf( grid, 0, 1, fpa_ConvFloatVal( 0x0));

    return (ann_NewModel(layers_num, weights, biases, acts, options, grid, info));
} /* ann_InitModel1 */
