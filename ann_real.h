#ifndef ANN_REAL_H
#define ANN_REAL_H
/**
 * ann_real.h - интерфейс реализации искусственных нейронных сетей
 *
 * Copyright (c) 1992-2020 AO "MCST". All rights reserved.
 */

#include "ann_iface.h"

/* Число обученных нейронных сетей */
#define ANN_MODELS_NUM 7

/* Функции инициализации нейронных сетей */
extern const ann_InitModelFunc_t ann_InitModel[ANN_MODELS_NUM];

#endif /* ! ANN_IFACE_H */