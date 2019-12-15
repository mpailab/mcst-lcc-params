#!/usr/bin/python
# -*- coding: utf-8 -*-

# External imports
import os, sys
from ast import literal_eval
from itertools import count, product

# Internal imports
import options as gl

# Запись заголовочного файла
def write_h( models_num, file):

    file.write("""#ifndef ANN_REAL_H
#define ANN_REAL_H
/**
 * ann_real.h - интерфейс реализации искусственных нейронных сетей
 *
 * Copyright (c) 1992-2019 AO "MCST". All rights reserved.
 */

#include "ann_iface.h"

/* Число обученных нейронных сетей */
#define ANN_MODELS_NUM """ + str(models_num) + """

/* Функции инициализации нейронных сетей */
extern const ann_InitModelFunc_t ann_InitModel[ANN_MODELS_NUM];

/***************************************************************************************/
/*                  Прототипы функций инициализации нейронных сетей                    */
/***************************************************************************************/
    """)

    for i in range(1, models_num + 1):

        file.write("""
extern ann_Model_ref ann_InitModel""" + str(i) + """( ann_Info_t *info);""")


    file.write("""

#endif /* ! ANN_IFACE_H */""")

# Запись модели в интерфейсный файл
def write_model_с( options, grid, model, file):

    layers = [layer for layer in model.layers if type(layer).__name__ not in ['Dropout', 'Flatten']]
    assert (any (type(layer).__name__ not in ['Dense'] for layer in model.layers))
    
    layers_num = len(layers)
    grid_size = len(grid)
    options_num = len(options)

    file.write("""
    unsigned int layers_num = """ + str(layers_num) + """;
    unsigned int grid_size = """ + str(grid_size) + """;
    unsigned int options_num = """ + str(options_num) + """;
    arr_Array_ptr weights     = arr_NewArray( ARR_PROF_UNITS, layers_num, ARR_ZERO_INIT);
    arr_Array_ptr biases      = arr_NewArray( ARR_PROF_UNITS, layers_num, ARR_ZERO_INIT);
    ann_ActivationFunc_t acts = arr_NewArray( ARR_PROF_UNITS, layers_num, ARR_ZERO_INIT);
    list_List_ref options     = arr_NewArray( ARR_PROF_UNITS, options_num, ARR_ZERO_INIT);
    arr_Array_ptr grid        = arr_NewMatrix( ARR_PROF_UNITS, options_num, grid_size);
    ann_Option_ref option;
    list_Unit_ref unit;
    """)

    for l in range(layers_num):
        
        layer = layers[l]

        weights = layer.get_weights()[0]
        (m,n) = weights.shape

        biases = layer.get_weights()[1]
        (k,)  = biases.shape

        activation = layer.get_config()['activation']

        assert (n == k and activation in ['relu', 'softmax'])

        f = 'ann_Relu' if activation == 'relu' else 'ann_SoftMax'

        file.write("""
    /* """ + str(l+1) + """-ый слой */
    {
        unsigned int m = """ + str(m) + """; /* число нейронов на предыдущем слое */
        unsigned int n = """ + str(n) + """; /* число нейронов на данном слое */

        /* Создаём атрибуты слоя */
        arr_Array_ptr A = arr_NewMatrix( ARR_PROF_UNITS, m, n);
        arr_Array_ptr b = arr_NewArray( ARR_PROF_UNITS, n, ARR_ZERO_INIT);

        /* Заполняем атрибуты слоя */""")

        for i, j in product(range(m), range(n)):

            w = weights.item((i, j))
            assert (isinstance(w, float))

            file.write("""
        arr_SetMatrixProf( A, """ + str(i) + ", " + str(j) + ", fpa_ConvFloatVal( " + str(w) + "));")

        for i in range(n):

            w = biases.item(i)
            assert (isinstance(w, float))

            file.write("""
        arr_SetProf( b, """ + str(i) + ", fpa_ConvFloatVal( " + str(w) + "));")

        file.write("""

        /* Запоминаем атрибуты слоя */
        arr_SetProf( weights, """ + str(l) + """, A);
        arr_SetProf( biases, """ + str(l) + """, b);
        arr_SetProf( acts, """ + str(l) + ", " + f +  ");")

        file.write("""
    }
        """)

    file.write("""
    /* Запоминаем опции, для которых обучена нейронная сеть, в заданном порядке */""")

    for i in range(options_num):

        option = options[i]

        if gl.PARAMS[option][0] == float:
            file.write("""
    option = ann_NewOption( \"""" + option + """\", ANN_OPTION_FLOAT,
                            fpa_ConvFloatVal( scr_GetFloatOption( \"""" + option + """\")), 
                            info);""")

        elif gl.PARAMS[option][0] == int:
            file.write("""
    option = ann_NewOption( \"""" + option + """\", ANN_OPTION_FLOAT,
                            fpa_ConvIntVal( scr_GetIntOption( \"""" + option + """\")), 
                            info);""")

        else:
            assert(gl.PARAMS[option][0] == bool)
            file.write("""
    option = ann_NewOption( \"""" + option + """\", ANN_OPTION_FLOAT,
                            scr_GetBoolOptionWithDefault( \"""" + option + """\",
                                                          ECOMP_FALSE)
                            ? ECOMP_ONE_PROFILE : ECOMP_ZERO_PROFILE,
                            info);""")

        file.write("""
    arr_SetRef( options, """ + str(i) + ", option);")

    file.write("""

    /* Запоминаем сетку значений опции, связанную с выходом нейронной сети */""")
    for i, j in product(range(grid_size), range(options_num)):

        w = grid[i][j]

        if isinstance(w, float):
            file.write("""
    arr_SetMatrixProf( grid, """ + str(j) + ", " + str(i) + ", fpa_ConvFloatVal( " + str(w) + "));")

        elif isinstance(w, int):
            file.write("""
    arr_SetMatrixProf( grid, """ + str(j) + ", " + str(i) + ", fpa_ConvIntVal( " + str(w) + "));")

        else:
            assert(isinstance(w, bool))
            file.write("""
    arr_SetMatrixProf( grid, """ + str(j) + ", " + str(i) + ", " + ("ECOMP_ONE_PROFILE" if w else "ECOMP_ZERO_PROFILE") + ");")

    file.write("""

    return (ann_NewModel(layers_num, weights, biases, acts, options, grid, info));""")

# Запись интерфейсного файла
def write_с( models, file):

    file.write("""/**
 * ann_real.c - интерфейс реализации искусственных нейронных сетей
 *
 * Copyright (c) 1992-2019 AO "MCST". All rights reserved.
 */

#include "ann_real.h"

/* Функции инициализации нейронных сетей */
const ann_InitModelFunc_t
ann_InitModel[ANN_MODELS_NUM] =
{""")

    for i in range(1, len(models) + 1):

        file.write("""
    ann_InitModel""" + str(i) + ",")

    file.write("""
};
    """)

    for i in range(1, len(models) + 1):

        model = models[i-1]

        file.write("""
/**
 * Инициализация """ + str(i) + """-ой нейронной сети
 */
static ann_Model_ref
ann_InitModel""" + str(i) + """( ann_Info_t *info) /* инфо */
{""")

        write_model_с( model[0], model[1], model[2], file)

        file.write("""
} /* ann_InitModel""" + str(i) + """ */
        """)

# Options numbering file name
def options_nums_file_name ():
    return os.path.join(gl.TRAIN_MODEL_DIR, 'options_to_model.txt')

# Trained neural networks file name
def model_file_name (i):
    return os.path.join(gl.TRAIN_MODEL_DIR, 'model' + str(i) + '.h5')

# Read trained neural networks
# Returns: 
#   hash table { options -> model }, 
# where options - tuple of options names,
#       model   - trained neural network for given options.
def read ():

    # Read options numbering
    with open(options_nums_file_name(), 'r') as file:
        options_to_number = literal_eval(file.read())

    # Take load tool from tensorflow
    from tensorflow import keras
    load = lambda i: keras.models.load_model(model_file_name(i))

    # Read trained neural networks with respect to given options numbering
    options_to_model = dict([ (gr, load(i)) for gr, i in options_to_number.items() ])

    return options_to_model

# Write trained neural networks
# Args: list of tuples (options, grid, model),
# where options - tuple of options names,
#       grid    - grid of options values
#       model   - trained neural network for given options and grid.
def write( models):

    if gl.С_MODEL_DIR:

        with open(gl.С_MODEL_DIR + '/ann_real.h', 'w', encoding="koi8-r") as file:
            write_h( len(models), file)

        with open(gl.С_MODEL_DIR + '/ann_real.c', 'w', encoding="koi8-r") as file:
            write_с( models, file)

    if gl.TRAIN_MODEL_DIR:

        # Create options numbering
        options_to_number = dict(zip([options for options, _, _ in models], count()))

        # Write options numbering
        with open(options_nums_file_name(), 'w') as file:
            file.write(str(options_to_number))

        # Write trained neural networks with respect to given options numbering
        for options, _, model in models:
            model.save(model_file_name(options_to_number[options]))
