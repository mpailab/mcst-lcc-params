#ifndef ANN_IFACE_H
#define ANN_IFACE_H
/**
 * ann_iface.h - интерфейс работы с искусственными нейронными сетями
 *
 * Copyright (c) 1992-2019 AO "MCST". All rights reserved.
 */

// #include "ecomp_iface.h"
// #include "hash_iface.h"
// #include "list_iface.h"
// #include "mem_iface.h"

typedef void* arr_Array_ptr;
typedef void* buff_Buffer_ptr;
typedef void* ire2k_Proc_ref;
typedef void* list_List_ref;
typedef void* cfg_Edge_ref;
typedef void* cfg_Graph_ref;
typedef void* cfg_LoopTree_ref;
typedef void* cfg_Node_ref;
typedef void* ire2k_Oper_ref;
typedef int   ecomp_Bool_t;
typedef float ecomp_Profile_t;
typedef void* hash_Table_ref;
typedef void* pco_ESB_ref;
typedef void* pco_ESBWalk_t;
typedef void* hash_Vector_t;
#define CFO_DCS_DEAD_ELEMS_NUM 3
typedef struct
{
    list_List_ref dead_elems[CFO_DCS_DEAD_ELEMS_NUM];
} cfo_DCSInfo_t;
typedef enum
{
    LIST_LESS    = -1,
    LIST_EQUAL   = 0,
    LIST_GREATER = 1
} list_CmpRes_t;
typedef void* list_Unit_ref;
typedef void* scr_Var_ref;
typedef void* hash_Entry_ref;
typedef void* mem_Pool_ref;
#define ARR_PROF_UNITS 1
#define ARR_ZERO_INIT 0
#define CFG_DOM_TREE 0
#define CFG_PDOM_TREE 1
#define ECOMP_ZERO_PROFILE 0x0
#define CFG_ALL_OPERS(o,n) (;;)
#define HASH_ALL_ENTRIES(o,n) (;;)
#define PCO_ESB_BODY_NODES( n, e, w) (;;)
#define CFG_ALL_MAIN_OPERS(o,n) (;;)
#define MEM_DECLARE_REF(x) void*
#define mem_GetEntry( entry_ref, entry_type) \
( \
  (entry_type *)mem_GetEntrySafe( entry_ref, sizeof(entry_type)) \
)
#define mem_Entry_null 0x0
#define ECOMP_TRUE 1
#define ECOMP_FALSE 0
#define LIST_UNITS( unit, list) (;;)
#define mem_Pool_null 0x0
#define mem_NewPool(a,b) 0x0
#define MEM_AREA_ANN 0
#define ECOMP_ARGS 0
typedef int arr_Index_t;
#define NULL 0x0
#define HASH_INT_KEYS 0
#define HASH_VAL_REF 0
#define S_IRWXU 0
#define S_IRWXG 0
typedef void FILE;
#define CFO_DCS_LEVEL_1 0
#define CFO_DCS_LEVEL_NUM 1
#define CFO_DCS_DEAD_NODES 0
#define CFO_DCS_DEAD_EDGES 1
#define CFO_DCS_DEAD_LOOPS 2

/* Макрос, включающий интерфейсы сбора статистики */
#define ANN_STAT_MODE

/* Локальное переопределение макроса ECOMP_USE_MACROS */
#ifdef ECOMP_USE_MACROS
#define ANN_USE_MACROS
#endif /* ECOMP_USE_MACROS */

/* Локальное переопределение макроса ECOMP_SUPPORT_INTERNAL_CHECK */
#ifdef ECOMP_SUPPORT_INTERNAL_CHECK
#define ANN_CHECK
#endif /* ECOMP_SUPPORT_INTERNAL_CHECK */

/* Локальное переопределение макроса ECOMP_SUPPORT_DEBUG_FEATURES */
#ifdef ECOMP_SUPPORT_DEBUG_FEATURES
#define ANN_DEBUG
#endif /* ECOMP_SUPPORT_DEBUG_FEATURES */

/***************************************************************************************/
/*                                Типы данных интерфейса                               */
/***************************************************************************************/

/**
 * Тип характеристик процедуры
 */
typedef enum
{
#define ANN_FIRST_PROC_CHAR ANN_OPERS_NUM

    ANN_OPERS_NUM = 0, /* Число операций */
    ANN_W_OPERS_NUM, /* Взвешенное число операций */
    ANN_MAX_OPERS_NUM, /* Максимальное число операций в узле */
    ANN_AVER_OPERS_NUM, /* Среднее число операций в узле */
    ANN_W_AVER_OPERS_NUM, /* Взвешенное среднее число операций в узле */

    ANN_CALLS_NUM, /* Число операций вызова */
    ANN_W_CALLS_NUM, /* Взвешенное число операций вызова */
    ANN_MAX_CALLS_NUM, /* Максимальное число операций вызова в узле */
    ANN_AVER_CALLS_NUM, /* Среднее число операций вызова в узле */
    ANN_W_AVER_CALLS_NUM, /* Взвешенное среднее число операций вызова в узле */
    ANN_CALLS_DENSITY, /* Плотность операций вызова */
    ANN_W_CALLS_DENSITY, /* Взвешенная плотность операций вызова */
    ANN_MAX_CALLS_DENSITY, /* Максимальная плотность операций вызова в узле */
    ANN_AVER_CALLS_DENSITY, /* Средняя плотность операций вызова в узле */
    ANN_W_AVER_CALLS_DENSITY, /* Взвешенная средняя плотность операций вызова в узле */

    ANN_LOADS_NUM, /* Число операций чтения */
    ANN_W_LOADS_NUM, /* Взвешенное число операций чтения */
    ANN_MAX_LOADS_NUM, /* Максимальное число операций чтения в узле */
    ANN_AVER_LOADS_NUM, /* Среднее число операций чтения в узле */
    ANN_W_AVER_LOADS_NUM, /* Взвешенное среднее число операций чтения в узле */
    ANN_LOADS_DENSITY, /* Плотность операций чтений */
    ANN_W_LOADS_DENSITY, /* Взвешенная плотность операций вызова */
    ANN_MAX_LOADS_DENSITY, /* Максимальная плотность операций вызова в узле */
    ANN_AVER_LOADS_DENSITY, /* Средняя плотность операций вызова в узле */
    ANN_W_AVER_LOADS_DENSITY, /* Взвешенная средняя плотность операций вызова в узле */

    ANN_STORES_NUM, /* Число операций записи */
    ANN_W_STORES_NUM, /* Взвешенное число операций записи */
    ANN_MAX_STORES_NUM, /* Максимальное число операций записи в узле */
    ANN_AVER_STORES_NUM, /* Среднее число операций записи в узле */
    ANN_W_AVER_STORES_NUM, /* Взвешенное среднее число операций записи в узле */
    ANN_STORES_DENSITY, /* Плотность операций записи */
    ANN_W_STORES_DENSITY, /* Взвешенная плотность операций вызова */
    ANN_MAX_STORES_DENSITY, /* Максимальная плотность операций вызова в узле */
    ANN_AVER_STORES_DENSITY, /* Средняя плотность операций вызова в узле */
    ANN_W_AVER_STORES_DENSITY, /* Взвешенная средняя плотность операций вызова в узле */

    ANN_NODES_NUM, /* Число узлов */
    ANN_W_NODES_NUM, /* Взвешенное число узлов */

    ANN_LOOPS_NUM, /* Число циклов */
    ANN_OVL_LOOPS_NUM, /* Число накрученных циклов */
    ANN_IRR_LOOPS_NUM, /* Число несводимых циклов */

    ANN_MAX_CNT, /* Максимальный счётчик */
    ANN_AVER_CNT, /* Средний счётчик */

    ANN_DOM_HEIGHT, /* Высота дерева доминаторов */
    ANN_DOM_WEIGHT, /* Ширина дерева доминаторов */
    ANN_DOM_BRANCH, /* Максимальное ветвление вершин в дереве доминаторов */

    ANN_PDOM_HEIGHT, /* Высота дерева постдоминаторов */
    ANN_PDOM_WEIGHT, /* Ширина дерева постдоминаторов */
    ANN_PDOM_BRANCH, /* Максимальное ветвление вершин в дереве постдоминаторов */
#define ANN_LAST_PROC_CHAR ANN_PDOM_BRANCH
    ANN_NONE_CHAR
#define ANN_PROC_CHARS_NUM (int)ANN_NONE_CHAR

} ann_ProcChar_t;

/* Цикл по всех характеристикам процедуры */
#define ANN_ALL_PROC_CHARS( proc_char) \
( \
    proc_char = (unsigned int) ANN_FIRST_PROC_CHAR; \
    proc_char <= (unsigned int) ANN_LAST_PROC_CHAR; \
    proc_char++ \
)

/* Тип функции активации */
typedef void (* ann_ActivationFunc_t) (arr_Array_ptr);

/**
 * Тип поддерживаемых опций компилятора
 */
typedef enum
{
    ANN_OPTION_BOOL = 0,
    ANN_OPTION_INT,
    ANN_OPTION_FLOAT

} ann_OptionType_t;

typedef struct
{
    char           * name;
    ann_OptionType_t type;
    ecomp_Profile_t  value;

} ann_Option_t;

/* Тип ссылки на опцию компилятора */
typedef MEM_DECLARE_REF( ann_Option_t) ann_Option_ref;

/* Получение указателя на опцию компилятора */
#define ANN_GET_OPTION_PTR(ref) mem_GetEntry( ref, ann_Option_t)

/**
 * Тип модели нейронной сети
 * 
 * Нейронная сеть состоит из слоёв, каждый из которых представляет собой набор нейронов.
 * Связи нейронов i-ого слоя с нейронами (i-1)-слоя определяются матрицей weights[i].
 * При этом 0-ым слоем считается вход нейронной сети. Смещение нейронов i-ого слоя
 * определяется вектором biases[i], а их функция активации - это acts[i].
 * 
 * Если 
 *   x_i - вектор значений нейронов (i-1)-ого слоя,
 *   y_i - вектор значений нейронов i-ого слоя,
 *   A_i = weights[i] - матрица связей нейронов i-ого слоя,
 *   b_i = biases[i]  - вектор смещений нейронов i-ого слоя,
 *   f_i = acts[i]    - функция активации нейронов i-ого слоя,
 * то
 *   y_i = f_i (A_i * x_i + b_i),
 * 
 * причём функция f_i применяется к вектору A_i * x_i + b_i покомпонентно.
 * 
 * Входом нейронной сети является вектор значений характеристик процедуры. Длина входного
 * вектора равна ANN_PROC_CHARS_NUM, его элементы определены в ann_ProcChar_t.
 * 
 * Если в нейронной сети n слоёв, то y_n - это значение выхода нейронной сети, которое
 * задает вектор вероятностей значений опций компилятора согласно заданной сетке.
 */
typedef struct
{
    unsigned int layers_num;   /* число слоёв нейронной сети */
    unsigned int outputs_num;  /* число выходов нейронной сети */
    arr_Array_ptr weights;     /* веса связей между нейронами соседних слоёв */
    arr_Array_ptr biases;      /* смещения нейронов на каждой слое */
    ann_ActivationFunc_t acts; /* функции активации нейронов на каждом слое */
    arr_Array_ptr options;     /* опции компилятора, для которых обучена нейронная сеть */
    arr_Array_ptr grid;        /* сетка значений опции компилятора, ассоциированная с
                                  выходом нейронной сети */
} ann_Model_t;

/* Тип ссылки на модель нейронной сети */
typedef MEM_DECLARE_REF( ann_Model_t) ann_Model_ref;

/* Получение указателя на модель нейронной сети */
#define ANN_GET_MODEL_PTR(ref) mem_GetEntry( ref, ann_Model_t)

/**
 * Информационная структура для работы с нейронными сетями
 */
typedef struct
{
    list_List_ref models;  /* список обученных нейронных сетей */

    mem_Pool_ref models_pool;  /* пул нейронных сетей */
    mem_Pool_ref options_pool; /* пул опций компилятора */

} ann_Info_t;

/* Тип функции инициализации нейронной сети */
typedef ann_Model_ref (* ann_InitModelFunc_t) (ann_Info_t *);

#ifdef ANN_STAT_MODE

/**
 * Тип характеристик узлов на фазе regions
 */
typedef enum
{
#define ANN_FIRST_RGN_NODE_CHAR ANN_RGN_NODE_N_CNT

    ANN_RGN_NODE_N_CNT = 0,     /* счётчик узла в процедуре */
    ANN_RGN_NODE_V_CNT,         /* счётчик узла в относительно головы региона */
    ANN_RGN_NODE_S_ENTER,       /* признак наличия бокового (не из региона) входа у узла */
    ANN_RGN_NODE_P_OPERS_NUM,   /* число операций в процедуре после обработки узла */
    ANN_RGN_NODE_R_OPERS_NUM,   /* число операций в регионе после обработки узла */
    ANN_RGN_NODE_UNBAL,         /* признак несбалансированного схождения */
    ANN_RGN_NODE_UNBAL_VALUE,   /* величина несбалансированного схождения */
    ANN_RGN_NODE_UNBAL_SH_ALT,  /* вероятность короткой пльтернативы в несбал. схождении */

#define ANN_LAST_RGN_NODE_CHAR ANN_RGN_NODE_UNBAL_SH_ALT
    ANN_RGN_NODE_NONE_CHAR
#define ANN_RGN_NODE_CHARS_NUM (int)ANN_RGN_NODE_NONE_CHAR

} ann_RgnNodeChar_t;

/**
 * Информационная структура для сбора статистики на фазе regions
 */
typedef struct
{
    ire2k_Proc_ref  proc;      /* процедура */
    ecomp_Profile_t max_cnt;   /* максимальный счётчик процедуры до применения regions */
    unsigned int    opers_num; /* число операций до применения regions */
    list_List_ref   regions;   /* список регионов
                                  Каждый регион - это список массивов характеристик узлов,
                                  голове которого приписано две характеристики региона:
                                  - ссылка на голову региона
                                  - число операций в набранном регионе */
} ann_RegionsInfo_t;

/**
 * Тип характеристик скалярных участков на фазе if_conv
 */
typedef enum
{
#define ANN_FIRST_IFC_ESB_CHAR ANN_IFC_ESB_CNT

    ANN_IFC_ESB_CNT = 0,     /* счётчик головы скалярного участка */
    ANN_IFC_ESB_OPERS_NUM,   /* число операций в скалярном участе */
    ANN_IFC_ESB_CALLS_NUM,   /* число операций вызова в скалярном участе */
    ANN_IFC_ESB_MERGE,       /* признак слитого скалярного участка */
    ANN_IFC_ESB_BEFORE_TIME, /* оценочное время планирования скалярного участка */
    ANN_IFC_ESB_AFTER_TIME,  /* время планирования скалярного участка после слияния */
    ANN_IFC_ESB_MERGE_HEUR,  /* коэффициент полезности слияния */

#define ANN_LAST_IFC_ESB_CHAR ANN_IFC_ESB_MERGE_HEUR
    ANN_IFC_ESB_NONE_CHAR
#define ANN_IFC_ESB_CHARS_NUM (int)ANN_IFC_ESB_NONE_CHAR

} ann_IfConvESBChar_t;

/**
 * Информационная структура для сбора статистики на фазе if_conv
 */
typedef struct
{
    ire2k_Proc_ref  proc;      /* процедура */
    list_List_ref   regions;   /* список регионов
                                  Каждый регион - это список массивов характеристик
                                  сливаемых скалярных участков */
} ann_IfConvInfo_t;

#endif /* ANN_STAT_MODE */

/***************************************************************************************/
/*                        Прототипы функций доступа к данным                           */
/***************************************************************************************/

#ifdef ANN_USE_MACROS

/* Получить число слоёв нейронной сети */
#define ann_GetLayersNum( model) (ANN_GET_MODEL_PTR( model)->layers_num)

/* Получить число выходов нейронной сети */
#define ann_GetOutputsNum( model) (ANN_GET_MODEL_PTR( model)->outputs_num)

/* Получить веса связей слоёв нейронной сети */
#define ann_GetWeights( model) (ANN_GET_MODEL_PTR( model)->weights)

/* Получить смещения слоёв нейронной сети */
#define ann_GetBiases( model) (ANN_GET_MODEL_PTR( model)->biases)

/* Получить функции активации слоёв нейронной сети */
#define ann_GetActs( model) (ANN_GET_MODEL_PTR( model)->acts)

/* Получить опции компилятора, для которых обучена нейронная сеть */
#define ann_GetOptions( model) (ANN_GET_MODEL_PTR( model)->options)

/* Получить сетку значений опции компилятора, связанную с выходом нейронной сети */
#define ann_GetGrid( model) (ANN_GET_MODEL_PTR( model)->grid)

/* Получить имя опции */
#define ann_GetOptionName( option) (ANN_GET_OPTION_PTR( model)->name)

/* Получить тип опции */
#define ann_GetOptionType( option) (ANN_GET_OPTION_PTR( model)->type)

/* Получить значение опции */
#define ann_GetOptionValue( option) (ANN_GET_OPTION_PTR( model)->value)

#else /* !ANN_USE_MACROS */

extern unsigned int ann_GetLayersNum( ann_Model_ref model);
extern unsigned int ann_GetOutputsNum( ann_Model_ref model);
extern arr_Array_ptr ann_GetWeights( ann_Model_ref model);
extern arr_Array_ptr ann_GetBiases( ann_Model_ref model);
extern ann_ActivationFunc_t ann_GetActs( ann_Model_ref model);
extern arr_Array_ptr ann_GetOptions( ann_Model_ref model);
extern arr_Array_ptr ann_GetGrid( ann_Model_ref model);
extern char * ann_GetOptionName( ann_Option_ref option);
extern ann_OptionType_t ann_GetOptionType( ann_Option_ref option);
extern ecomp_Profile_t ann_GetOptionValue( ann_Option_ref option);

#endif /* !ANN_USE_MACROS */

/***************************************************************************************/
/*                      Прототипы локальных функций интерфейса                         */
/***************************************************************************************/

extern void ann_Relu( arr_Array_ptr input);
extern void ann_SoftMax( arr_Array_ptr input);

/***************************************************************************************/
/*                       Прототипы внешних функций интерфейса                          */
/***************************************************************************************/

/* Скорректировать значения опций компилятора для процедуры proc */
extern void ann_CorrectProcOptions( ire2k_Proc_ref proc);

#ifdef ANN_STAT_MODE

extern void ann_PrintProcChars( ire2k_Proc_ref proc);
extern void ann_InitRegionsStat( ire2k_Proc_ref proc);
extern void ann_AddRegionsStat( cfg_Node_ref head);
extern void ann_AddRegionsOpersNum( cfg_Node_ref head, unsigned int opers_num);
extern void ann_AddRegionsNodeStat( cfg_Node_ref head,
                                    ecomp_Profile_t n_cnt,
                                    ecomp_Profile_t v_cnt,
                                    ecomp_Bool_t s_enter,
                                    unsigned int proc_opers,
                                    unsigned int region_opers);
extern void ann_AddRegionsNodeUnbalStat( cfg_Node_ref head,
                                         unsigned int max_dep,
                                         unsigned int min_dep,
                                         ecomp_Profile_t sh_alt);
extern void ann_PrintRegionsStat( );
extern void ann_InitIfConvStat( ire2k_Proc_ref proc);
extern void ann_AddIfConvStat( cfg_Node_ref head);
extern void ann_AddIfConvESBStatBefore( pco_ESB_ref esb);
extern void ann_AddIfConvESBStatAfter( pco_ESB_ref esb,
                                       ecomp_Profile_t time_before,
                                       ecomp_Profile_t time_after,
                                       ecomp_Profile_t merge_heur);
extern void ann_PrintIfConvStat( );
extern void ann_PrintDCSStat( ire2k_Proc_ref proc);

#else /* !ANN_STAT_MODE */

#define ann_PrintProcChars( proc)
#define ann_InitRegionsStat( proc)
#define ann_AddRegionsStat( head)
#define ann_AddRegionsOpersNum( head, opers_num)
#define ann_AddRegionsNodeStat( head, n_cnt, v_cnt, s_enter, proc_opers, region_opers)
#define ann_AddRegionsNodeUnbalStat( head, max_dep, min_dep, sh_alt)
#define ann_PrintRegionsStat( )
#define ann_InitIfConvStat( proc)
#define ann_AddIfConvStat( head)
#define ann_AddIfConvESBStatBefore( esb)
#define ann_AddIfConvESBStatAfter( esb, time_before, time_after, merge_heur)
#define ann_PrintIfConvStat( )
#define ann_PrintDCSStat( proc)

#endif /* ANN_STAT_MODE */

#endif /* ! ANN_IFACE_H */