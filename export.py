#!/usr/bin/python
# -*- coding: utf-8 -*-

# External imports
import os, sys
from ast import literal_eval
from itertools import count, product
from textwrap import wrap

# Internal imports
import options as gl
import par

# Запись заголовочного файла
def write_h( models_num, file):

    file.write("""#ifndef ANN_REAL_H
#define ANN_REAL_H
/**
 * ann_real.h - интерфейс реализации искусственных нейронных сетей
 *
 * Copyright (c) 1992-2020 AO "MCST". All rights reserved.
 */

#include "ann_iface.h"

/* Число обученных нейронных сетей */
#define ANN_MODELS_NUM """ + str(models_num) + """

/* Функции инициализации нейронных сетей */
extern const ann_InitModelFunc_t ann_InitModel[ANN_MODELS_NUM];

#endif /* ! ANN_IFACE_H */""")

# Convert numpy array to float
def to_float(data):

    from numpy import vectorize

    def boolstr_to_floatstr(v):
        if v == 'True':
            return '1'
        elif v == 'False':
            return '0'
        else:
            return v

    return vectorize(boolstr_to_floatstr)(data).astype(float)

def float_str (x):
    assert (isinstance(x, float))
    return str(x)

# Запись модели в интерфейсный файл
def write_model_с( model_num, options, grid, model, file):

    grid = to_float(grid)
    layers = [layer for layer in model.layers if type(layer).__name__ not in ['Dropout', 'Flatten']]
    assert (any (type(layer).__name__ not in ['Dense'] for layer in model.layers))
    
    layers_num = len(layers)
    grid_size = len(grid)
    options_num = len(options)

    for l in range(layers_num):
        
        layer = layers[l]

        weights = layer.get_weights()[0]
        (m,n) = weights.shape

        biases = layer.get_weights()[1]
        (k,)  = biases.shape

        activation = layer.get_config()['activation']

        assert (n == k and activation in ['relu', 'softmax'])

        file.write("""
/* Матрица весов слоя """ + str(l+1) + """ в модели """ + str(model_num) + """ */
static const double ann_Matrix_""" + str(model_num) + """_""" + str(l+1) + """[""" + str(m) + """][""" + str(n) + """] = 
{""")
        for i in range(m):
            file.write("""
    {
        """ + '\n        '.join(wrap(', '.join(float_str(weights.item((i, j))) for j in range(n)), 81)) + """
    },""")
        file.write("""
};

/* Вектор смещений слоя """ + str(l+1) + """ в модели """ + str(model_num) + """ */
static const double ann_Bias_""" + str(model_num) + """_""" + str(l+1) + """[""" + str(n) + """] = 
{
    """ + '\n    '.join(wrap(', '.join(float_str(biases.item(j)) for j in range(n)), 81)) + """
};""")

    file.write("""
/* Сетка значений опций компилятора в модели """ + str(model_num) + """ */
static const double ann_Grid_""" + str(model_num) + """[""" + str(options_num) + """][""" + str(grid_size) + """] = 
{""")
    for i in range(options_num):
        file.write("""
    {
        """ + '\n        '.join(wrap(', '.join(float_str(grid[j][i]) for j in range(grid_size)), 81)) + """
    },""")
    file.write("""
};

/**
 * Инициализация """ + str(model_num) + """-ой нейронной сети
 */
static ann_Model_ref
ann_InitModel""" + str(model_num) + """( ann_Info_t *info) /* инфо */
{
    unsigned int layers_num = """ + str(layers_num) + """;
    unsigned int grid_size = """ + str(grid_size) + """;
    unsigned int options_num = """ + str(options_num) + """;
    arr_Array_ptr weights = arr_NewArray( ARR_PTR_UNITS, layers_num, ARR_ZERO_INIT);
    arr_Array_ptr biases  = arr_NewArray( ARR_PTR_UNITS, layers_num, ARR_ZERO_INIT);
    arr_Array_ptr acts    = arr_NewArray( ARR_PTR_UNITS, layers_num, ARR_ZERO_INIT);
    arr_Array_ptr options = arr_NewArray( ARR_REF_UNITS, options_num, ARR_ZERO_INIT);
    arr_Array_ptr grid    = arr_NewMatrix( ARR_PROF_UNITS, options_num, grid_size);
    ann_Option_ref option;
    ecomp_Profile_t value;
    unsigned int i, j;
    """)

    for l in range(layers_num):
        
        layer = layers[l]
        weights = layer.get_weights()[0]
        biases = layer.get_weights()[1]
        f = 'ann_Relu' if layer.get_config()['activation'] == 'relu' else 'ann_SoftMax'
        (m,n) = weights.shape

        file.write("""
    /* """ + str(l+1) + """-ый слой */
    {
        const unsigned int m = """ + str(m) + """; /* число нейронов на предыдущем слое */
        const unsigned int n = """ + str(n) + """; /* число нейронов на данном слое */

        /* Создаём атрибуты слоя */
        arr_Array_ptr matrix = arr_NewMatrix( ARR_PROF_UNITS, m, n);
        arr_Array_ptr bias   = arr_NewArray( ARR_PROF_UNITS, n, ARR_ZERO_INIT);

        /* Заполняем атрибуты слоя */
        for ( i = 0; i < n; i++ )
        {
            for ( j = 0; j < m; j++ )
            {
                arr_SetMatrixProf( matrix, j, i, 
                                   fpa_ConvFloatVal( ann_Matrix_""" + str(model_num) + """_""" + str(l+1) + """[j][i]));
                arr_SetProf( bias, i, 
                             fpa_ConvFloatVal( ann_Bias_""" + str(model_num) + """_""" + str(l+1) + """[i]));
            }
        }

        /* Запоминаем атрибуты слоя */
        arr_SetPtr( weights, """ + str(l) + """, (arr_Ptr_t)matrix);
        arr_SetPtr( biases, """ + str(l) + """, (arr_Ptr_t)bias);
        arr_SetPtr( acts, """ + str(l) + ", (arr_Ptr_t)" + f +  ");")

        file.write("""
    }
""")

    file.write("""
    /* Запоминаем опции, для которых обучена нейронная сеть, в заданном порядке */""")

    for i in range(options_num):

        option = options[i]

        if gl.PARAMS[option][0] == float:
            file.write("""
    value = fpa_ConvIntVal( scr_GetFloatOptionWithDefault( \"""" + option + """\", """ + par.defaults[option] + """));
    option = ann_NewOption( \"""" + option + """\", ANN_OPTION_FLOAT, value, info);""")

        elif gl.PARAMS[option][0] == int:
            file.write("""
    value = fpa_ConvIntVal( scr_GetIntOptionWithDefault( \"""" + option + """\", """ + par.defaults[option] + """));
    option = ann_NewOption( \"""" + option + """\", ANN_OPTION_INT, value, info);""")

        else:
            assert(gl.PARAMS[option][0] == bool)
            file.write("""
    value = scr_GetBoolOptionWithDefault( \"""" + option + """\", ECOMP_FALSE) ? ECOMP_ONE_PROFILE : ECOMP_ZERO_PROFILE;
    option = ann_NewOption( \"""" + option + """\", ANN_OPTION_BOOL, value, info);""")

        file.write("""
    arr_SetRef( options, """ + str(i) + ", option);")

    file.write("""

    /* Запоминаем сетку значений опции, связанную с выходом нейронной сети */
    {
        const unsigned int m = """ + str(options_num) + """; /* число опций компилятора */
        const unsigned int n = """ + str(grid_size) + """; /* число шагов в сетке */

        /* Заполняем стетку значений опций компилятора */
        for ( i = 0; i < m; i++ )
        {
            for ( j = 0; j < n; j++ )
            {
                arr_SetMatrixProf( grid, i, j, 
                                   fpa_ConvFloatVal( ann_Grid_""" + str(model_num) + """[i][j]));
            }
        }
    }

    return (ann_NewModel(layers_num, weights, biases, acts, options, grid, info));

} /* ann_InitModel""" + str(model_num) + """ */
""")

# Запись интерфейсного файла
def write_с( models, file):

    file.write("""/**
 * ann_real.c - интерфейс реализации искусственных нейронных сетей
 *
 * Copyright (c) 1992-2020 AO "MCST". All rights reserved.
 */

#include "fpa_iface.h"
#include "scr_iface.h"

#include "ann_real.h"
""")

    for i in range(1, len(models) + 1):

        model = models[i-1]
        write_model_с( i, model[0], model[1], model[2], file)

    file.write("""
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
