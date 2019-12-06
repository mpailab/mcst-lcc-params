/**
 * ann.c - интерфейс работы с искусственными нейронными сетями
 *
 * Copyright (c) 1992-2019 AO "MCST". All rights reserved.
 */

#include "ann_iface.h"
#include "ann_real.h"
                                 
/***************************************************************************************/
/*                              Функции доступа к данным                               */
/***************************************************************************************/

#ifndef ANN_USE_MACROS

/**
 * Получить число слоёв нейронной сети 
 */
unsigned int 
ann_GetLayersNum( ann_Model_ref model) /* нейронная сеть */
{
    ann_Model_t * model_p;
    model_p = ANN_GET_MODEL_PTR( model);
    return (model_p->layers_num);
} /* ann_GetLayersNum */

/**
 * Получить число выходов нейронной сети 
 */
unsigned int 
ann_GetOutputsNum( ann_Model_ref model) /* нейронная сеть */
{
    ann_Model_t * model_p;
    model_p = ANN_GET_MODEL_PTR( model);
    return (model_p->outputs_num);
} /* ann_GetOutputsNum */

/**
 * Получить веса связей слоёв нейронной сети
 */
arr_Array_ptr 
ann_GetWeights( ann_Model_ref model) /* нейронная сеть */
{
    ann_Model_t * model_p;
    model_p = ANN_GET_MODEL_PTR( model);
    return (model_p->weights);
} /* ann_GetWeights */

/**
 * Получить смещения слоёв нейронной сети
 */
arr_Array_ptr 
ann_GetBiases( ann_Model_ref model) /* нейронная сеть */
{
    ann_Model_t * model_p;
    model_p = ANN_GET_MODEL_PTR( model);
    return (model_p->biases);
} /* ann_GetBiases */

/**
 * Получить функции активации слоёв нейронной сети
 */
ann_ActivationFunc_t 
ann_GetActs( ann_Model_ref model) /* нейронная сеть */
{
    ann_Model_t * model_p;
    model_p = ANN_GET_MODEL_PTR( model);
    return (model_p->acts);
} /* ann_GetActs */

/**
 * Получить опции компилятора, для которых обучена нейронная сеть
 */
arr_Array_ptr 
ann_GetOptions( ann_Model_ref model) /* нейронная сеть */
{
    ann_Model_t * model_p;
    model_p = ANN_GET_MODEL_PTR( model);
    return (model_p->options);
} /* ann_GetOptions */

/**
 * Получить сетку значений опции компилятора, связанную с выходом нейронной сети
 */
arr_Array_ptr 
ann_GetGrid( ann_Model_ref model) /* нейронная сеть */
{
    ann_Model_t * model_p;
    model_p = ANN_GET_MODEL_PTR( model);
    return (model_p->grid);
} /* ann_GetGrid */

/**
 * Получить имя опции
 */
char * 
ann_GetOptionName( ann_Option_ref option) /* нейронная сеть */
{
    ann_Option_t * option_p;
    option_p = ANN_GET_OPTION_PTR( option);
    return (option_p->name);
} /* ann_GetOptionName */

/**
 * Получить тип опции
 */
ann_OptionType_t 
ann_GetOptionType( ann_Option_ref option) /* нейронная сеть */
{
    ann_Option_t * option_p;
    option_p = ANN_GET_OPTION_PTR( option);
    return (option_p->type);
} /* ann_GetOptionType */

/**
 * Получить значение опции
 */
ecomp_Profile_t 
ann_GetOptionValue( ann_Option_ref option) /* нейронная сеть */
{
    ann_Option_t * option_p;
    option_p = ANN_GET_OPTION_PTR( option);
    return (option_p->value);
} /* ann_GetOptionValue */

#endif /* !ANN_USE_MACROS */
                                 
/***************************************************************************************/
/*                              Вспомогательные функции                                */
/***************************************************************************************/

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
        if ( fpa_IsLes( arr_GetProf( input, i), ECOMP_ZERO_PROFILE) )
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

/**
 * Вычисление расстояния между векторами
 */
static ecomp_Profile_t
ann_Distance( arr_Array_ptr x, arr_Array_ptr y)
{
    unsigned int i, n = arr_GetLength( x);
    ecomp_Profile_t res = ECOMP_ZERO_PROFILE;

    ECOMP_ASSERT( n == arr_GetLength( y) );

    for (i = 0; i < n; i++ )
    {
        ecomp_Profile_t z = fpa_Sub( arr_GetProf( x, i), arr_GetProf( y, i));
        res = fpa_Add( res, fpa_Mul( z, z));
    }
    
    return (fpa_Sqrt( res));
} /* ann_Distance */

/**
 * Создание нейронной сети
 */
static ann_Model_ref
ann_NewModel( unsigned int layers_num,   /* число слоёв */
              arr_Array_ptr weights,     /* веса связей */
              arr_Array_ptr biases,      /* смещения */
              ann_ActivationFunc_t acts, /* функции активации */
              list_List_ref options,     /* опции компилятора */
              arr_Array_ptr grid,        /* сетка значений опции компилятора */
              ann_Info_t  * info)        /* инфо */
{
    ann_Model_ref model;
    ann_Model_t * model_p;

    model = mem_NewEntry( info->models_pool);
    model_p = ANN_GET_MODEL_PTR( model);
    model_p->layers_num = layers_num;
    model_p->weights = weights;
    model_p->biases = biases;
    model_p->acts = acts;
    model_p->options = options;
    model_p->grid = grid;

    return (model);
} /* ann_NewModel */

/**
 * Создание опции компилятора
 */
static ann_Option_ref
ann_NewOption( char           * name, /* число слоёв */
               ann_OptionType_t type, /* веса связей */
               ecomp_Profile_t value, /* смещения */
               ann_Info_t    * info)  /* инфо */
{
    ann_Option_ref option;
    ann_Option_t * option_p;

    option = mem_NewEntry( info->options_pool);
    option_p = ANN_GET_OPTION_PTR( option);
    option_p->name = name;
    option_p->type = type;
    option_p->value = value;

    return (option);
} /* ann_NewOption */

/**
 * Записать значение опции компилятора
 */
static void
ann_WriteOption( ann_Option_ref option) /* опция */
{
    char *name = ann_GetOptionName( option);
    ecomp_Profile_t value = ann_GetOptionValue( option);
    
    switch ( ann_GetOptionType( option) )
    {
      case ANN_OPTION_FLOAT:
        scr_SetFloatOption( name, fpa_ConvToFloatVal( value));
        break;
        
      case ANN_OPTION_INT:
        scr_SetIntOption( name, fpa_ConvToIntVal( value));
        break;

      case ANN_OPTION_BOOL:
        scr_SetBoolOption( name, fpa_ConvToIntVal( value) != 0);
        break;
    
      default:
        ecomp_InternalError( ECOMP_ARGS, "ann internal error");
    }

    return;
} /* ann_WriteOption */

/***************************************************************************************/
/*                             Основной блок интерфейса                                */
/***************************************************************************************/

/**
 * Минимальное допустимое значение вероятности принятия новых значений опций
 * в данной сетке нейронной сети
 */
#define ANN_MIN_ADMISSIBLE_PROB fpa_ConvFloatVal( 0.75)

/**
 * Минимальное допустимое значение отношения вероятности новых значений опций
 * к вероятности текущих значений опций в данной сетке нейронной сети
 */
#define ANN_MIN_ADMISSIBLE_RATIO fpa_ConvFloatVal( 2.0)

/**
 * Вычисление вектора характеристик процедуры
 */
static arr_Array_ptr
ann_CalcProcChars( ire2k_Proc_ref proc) /* процедура */
{
    cfg_Edge_ref edge;
    cfg_Graph_ref cfg = cfg_GetProcGraph( proc);
    cfg_LoopTree_ref loop_tree = cfg_GetGraphLoopTree( cfg);
    cfg_Node_ref node;
    ire2k_Oper_ref oper;
    ecomp_Profile_t node_cnt;
    ecomp_Profile_t node_opers_num, node_calls_num, node_loads_num, node_stores_num;
    ecomp_Profile_t node_calls_density, node_loads_density, node_stores_density;
    unsigned int n, o_num, c_num, l_num, s_num;
    ecomp_Bool_t is_dom = cfg_IsTreeBuilt( cfg, CFG_DOM_TREE);
    ecomp_Bool_t is_pdom = cfg_IsTreeBuilt( cfg, CFG_PDOM_TREE);
    arr_Array_ptr proc_chars = arr_NewArray( ARR_PROF_UNITS, 
                                             ANN_PROC_CHARS_NUM, 
                                             ARR_ZERO_INIT);
    
    /* Группа переменных, соответствующих характеристикам процедуры */
    ecomp_Profile_t opers_num = fpa_ConvIntVal( cfo_GetProcNumNodes( proc));
    ecomp_Profile_t w_opers_num = ECOMP_ZERO_PROFILE;
    unsigned int max_opers_num = 0;
    ecomp_Profile_t aver_opers_num;
    ecomp_Profile_t w_aver_opers_num;
    unsigned int calls_num = 0;
    ecomp_Profile_t w_calls_num = ECOMP_ZERO_PROFILE;
    unsigned int max_calls_num = 0;
    ecomp_Profile_t aver_calls_num;
    ecomp_Profile_t w_aver_calls_num;
    ecomp_Profile_t calls_density = ECOMP_ZERO_PROFILE;
    ecomp_Profile_t w_calls_density = ECOMP_ZERO_PROFILE;
    ecomp_Profile_t max_calls_density = ECOMP_ZERO_PROFILE;
    ecomp_Profile_t aver_calls_density;
    ecomp_Profile_t w_aver_calls_density;
    unsigned int loads_num = 0;
    ecomp_Profile_t w_loads_num = ECOMP_ZERO_PROFILE;
    unsigned int max_loads_num = 0;
    ecomp_Profile_t aver_loads_num;
    ecomp_Profile_t w_aver_loads_num;
    ecomp_Profile_t loads_density = ECOMP_ZERO_PROFILE;
    ecomp_Profile_t w_loads_density = ECOMP_ZERO_PROFILE;
    ecomp_Profile_t max_loads_density = ECOMP_ZERO_PROFILE;
    ecomp_Profile_t aver_loads_density;
    ecomp_Profile_t w_aver_loads_density;
    unsigned int stores_num = 0;
    ecomp_Profile_t w_stores_num = ECOMP_ZERO_PROFILE;
    unsigned int max_stores_num = 0;
    ecomp_Profile_t aver_stores_num;
    ecomp_Profile_t w_aver_stores_num;
    ecomp_Profile_t stores_density = ECOMP_ZERO_PROFILE;
    ecomp_Profile_t w_stores_density = ECOMP_ZERO_PROFILE;
    ecomp_Profile_t max_stores_density = ECOMP_ZERO_PROFILE;
    ecomp_Profile_t aver_stores_density;
    ecomp_Profile_t w_aver_stores_density;
    ecomp_Profile_t nodes_num = fpa_ConvIntVal( graph_GetGraphNodeNumber( cfg));
    ecomp_Profile_t w_nodes_num;
    unsigned int loops_num = graph_GetGraphNodeNumber( loop_tree);
    unsigned int ovl_loops_num = 0;
    unsigned int irr_loops_num = 0;
    ecomp_Profile_t max_cnt = cfo_FindProcMaxCounter( proc);
    ecomp_Profile_t aver_cnt = ECOMP_ZERO_PROFILE;
    unsigned int dom_height;
    unsigned int dom_weight;
    unsigned int dom_branch;
    unsigned int pdom_height;
    unsigned int pdom_weight;
    unsigned int pdom_branch;

    /* При необходимости сторим дерево доминаторов и постдоминаторов */    
    if ( !is_dom )
    {
        cfa_DominFast( cfg);
    }
    if ( !is_pdom )
    {
        cfa_PDominFast( cfg);
    }

    /* Извлекаем свойства дерева доминаторов */
    node = cfg_GetTreeRootNode( cfg, CFG_DOM_TREE);
    dom_height = cfo_GetTreeNodeHeightRec( node, CFG_DOM_TREE);
    dom_weight = cfo_GetTreeNodeWeightRec( node, CFG_DOM_TREE);
    dom_branch = 0;

    /* Извлекаем свойства дерева постдоминаторов */
    node = cfg_GetTreeRootNode( cfg, CFG_PDOM_TREE);
    pdom_height = cfo_GetTreeNodeHeightRec( node, CFG_PDOM_TREE);
    pdom_weight = cfo_GetTreeNodeWeightRec( node, CFG_PDOM_TREE);
    pdom_branch = 0;

    /* Обработка узлов упр. графа */
    for ( node = graph_GetGraphFirstNode( cfg);
          mem_IsNotRefNull( node);
          node = graph_GetGraphNextNode( node) )
    {
        /* Находим число операций разного типа */
        o_num = 0;
        c_num = 0;
        l_num = 0;
        s_num = 0;
        for CFG_ALL_OPERS( oper, node)
        {
            o_num++;
            if ( ire2k_IsOperCall( oper) ) c_num++;
            if ( ire2k_IsOperLoad( oper) ) l_num++;
            if ( ire2k_IsOperStore( oper) ) s_num++;
        }

        /**
         * Корректируем характеристики процедуры
         */

        node_cnt = cfg_GetNodeCounter( node);
        aver_cnt = fpa_Add( aver_cnt, node_cnt);

        /*-------------------------------------------------------------------------------*/

        node_opers_num = fpa_ConvIntVal( o_num);
        w_opers_num = fpa_Add( w_opers_num, fpa_Mul( node_opers_num, node_cnt));
        if ( o_num > max_opers_num )
        {
            max_opers_num = o_num;
        }

        /*-------------------------------------------------------------------------------*/

        calls_num += c_num;
        node_calls_num = fpa_ConvIntVal( c_num);
        if ( c_num > max_calls_num )
        {
            max_calls_num = c_num;
        }
        w_calls_num = fpa_Add( w_calls_num, fpa_Mul( node_calls_num, node_cnt));
        node_calls_density = fpa_Div( node_calls_num, node_opers_num);
        calls_density = fpa_Add( calls_density, node_calls_density);
        w_calls_density = fpa_Add( w_calls_density, fpa_Mul( node_calls_density, node_cnt));
        if ( fpa_IsGrt( node_calls_density, max_calls_density) )
        {
            max_calls_density = node_calls_density;
        }

        /*-------------------------------------------------------------------------------*/

        loads_num += l_num;
        node_loads_num = fpa_ConvIntVal( l_num);
        if ( l_num > max_loads_num )
        {
            max_loads_num = l_num;
        }
        w_loads_num = fpa_Add( w_loads_num, fpa_Mul( node_loads_num, node_cnt));
        node_loads_density = fpa_Div( node_loads_num, node_opers_num);
        loads_density = fpa_Add( loads_density, node_loads_density);
        w_loads_density = fpa_Add( w_loads_density, fpa_Mul( node_loads_density, node_cnt));
        if ( fpa_IsGrt( node_loads_density, max_loads_density) )
        {
            max_loads_density = node_loads_density;
        }

        /*-------------------------------------------------------------------------------*/

        stores_num += s_num;
        node_stores_num = fpa_ConvIntVal( s_num);
        if ( s_num > max_stores_num )
        {
            max_stores_num = s_num;
        }
        w_stores_num = fpa_Add( w_stores_num, fpa_Mul( node_stores_num, node_cnt));
        node_calls_density = fpa_Div( node_calls_num, node_opers_num);
        stores_density = fpa_Add( stores_density, node_stores_density);
        w_stores_density = fpa_Add( w_stores_density, fpa_Mul( node_stores_density, node_cnt));
        if ( fpa_IsGrt( node_stores_density, max_stores_density) )
        {
            max_stores_density = node_stores_density;
        }

        /*-------------------------------------------------------------------------------*/

        if ( cfg_IsNodeLoopHead( node) )
        { 
            if ( cfg_IsLoopMarkedForOverlap( cfg_GetNodeLoop( node)) ) 
            {
                ovl_loops_num += 1;
            }
            if ( !cfg_IsLoopReducible( cfg_GetNodeLoop( node)) ) 
            {
                irr_loops_num += 1;
            }
        }

        /*-------------------------------------------------------------------------------*/

        n = 0;
        for ( edge = cfg_GetFirstTreeSucc( node, CFG_DOM_TREE);
              mem_IsNotRefNull( edge);
              edge = cfg_GetNextTreeSucc( edge) )
        {
            n++;
        }
        if ( n > dom_branch )
        {
            dom_branch = n;
        }

        /*-------------------------------------------------------------------------------*/

        n = 0;
        for ( edge = cfg_GetFirstTreeSucc( node, CFG_PDOM_TREE);
              mem_IsNotRefNull( edge);
              edge = cfg_GetNextTreeSucc( edge) )
        {
            n++;
        }
        if ( n > pdom_branch )
        {
            pdom_branch = n;
        }
    }

    /* Подчищаем за собой */
    if ( !is_dom )
    {
        cfg_ClearTree( cfg, CFG_DOM_TREE);
    }
    if ( !is_pdom )
    {
        cfg_ClearTree( cfg, CFG_PDOM_TREE);
    }

    /* Завершающая коррекция характеристик процедуры */
    w_opers_num = ( fpa_IsZero( max_cnt)
                    ? ECOMP_ZERO_PROFILE
                    : fpa_Div( w_opers_num, max_cnt));
    aver_opers_num = fpa_Div( fpa_ConvIntVal( opers_num), nodes_num);
    w_aver_opers_num = fpa_Div( w_opers_num, nodes_num);
    w_calls_num = ( fpa_IsZero( max_cnt)
                    ? ECOMP_ZERO_PROFILE
                    : fpa_Div( w_calls_num, max_cnt));
    aver_calls_num = fpa_Div( fpa_ConvIntVal( calls_num), nodes_num);
    w_aver_calls_num = fpa_Div( w_calls_num, nodes_num);
    aver_calls_density = fpa_Div( calls_density, nodes_num);
    w_calls_density = ( fpa_IsZero( max_cnt)
                        ? ECOMP_ZERO_PROFILE
                        : fpa_Div( w_calls_density, max_cnt));
    w_aver_calls_density = fpa_Div( w_calls_density, nodes_num);
    w_loads_num = ( fpa_IsZero( max_cnt)
                    ? ECOMP_ZERO_PROFILE
                    : fpa_Div( w_loads_num, max_cnt));
    aver_loads_num = fpa_Div( fpa_ConvIntVal( loads_num), nodes_num);
    w_aver_loads_num = fpa_Div( w_loads_num, nodes_num);
    aver_loads_density = fpa_Div( loads_density, nodes_num);
    w_loads_density = ( fpa_IsZero( max_cnt)
                        ? ECOMP_ZERO_PROFILE
                        : fpa_Div( w_loads_density, max_cnt));
    w_aver_loads_density = fpa_Div( w_loads_density, nodes_num);
    w_stores_num = ( fpa_IsZero( max_cnt)
                    ? ECOMP_ZERO_PROFILE
                    : fpa_Div( w_stores_num, max_cnt));
    aver_stores_num = fpa_Div( fpa_ConvIntVal( stores_num), nodes_num);
    w_aver_stores_num = fpa_Div( w_stores_num, nodes_num);
    aver_stores_density = fpa_Div( stores_density, nodes_num);
    w_stores_density = ( fpa_IsZero( max_cnt)
                        ? ECOMP_ZERO_PROFILE
                        : fpa_Div( w_stores_density, max_cnt));
    w_aver_stores_density = fpa_Div( w_stores_density, nodes_num);
    w_nodes_num = ( fpa_IsZero( max_cnt)
                    ? ECOMP_ZERO_PROFILE
                    : fpa_Div( aver_cnt, max_cnt));
    aver_cnt = fpa_Div( aver_cnt, nodes_num);
    
    /* Запоминаем значения характеристик процедуры */
    arr_SetProf( proc_chars, ANN_OPERS_NUM, opers_num);
    arr_SetProf( proc_chars, ANN_W_OPERS_NUM, w_opers_num);
    arr_SetProf( proc_chars, ANN_MAX_OPERS_NUM, fpa_ConvIntVal( max_opers_num));
    arr_SetProf( proc_chars, ANN_AVER_OPERS_NUM, aver_opers_num);
    arr_SetProf( proc_chars, ANN_W_AVER_OPERS_NUM, w_aver_opers_num);
    arr_SetProf( proc_chars, ANN_CALLS_NUM, fpa_ConvIntVal( calls_num));
    arr_SetProf( proc_chars, ANN_W_CALLS_NUM, w_calls_num);
    arr_SetProf( proc_chars, ANN_MAX_CALLS_NUM, fpa_ConvIntVal( max_calls_num));
    arr_SetProf( proc_chars, ANN_AVER_CALLS_NUM, aver_calls_num);
    arr_SetProf( proc_chars, ANN_W_AVER_CALLS_NUM, w_aver_calls_num);
    arr_SetProf( proc_chars, ANN_CALLS_DENSITY, calls_density);
    arr_SetProf( proc_chars, ANN_W_CALLS_DENSITY, w_calls_density);
    arr_SetProf( proc_chars, ANN_MAX_CALLS_DENSITY, max_calls_density);
    arr_SetProf( proc_chars, ANN_AVER_CALLS_DENSITY, aver_calls_density);
    arr_SetProf( proc_chars, ANN_W_AVER_CALLS_DENSITY, w_aver_calls_density);
    arr_SetProf( proc_chars, ANN_LOADS_NUM, fpa_ConvIntVal( loads_num));
    arr_SetProf( proc_chars, ANN_W_LOADS_NUM, w_loads_num);
    arr_SetProf( proc_chars, ANN_MAX_LOADS_NUM, fpa_ConvIntVal( max_loads_num));
    arr_SetProf( proc_chars, ANN_AVER_LOADS_NUM, aver_loads_num);
    arr_SetProf( proc_chars, ANN_W_AVER_LOADS_NUM, w_aver_loads_num);
    arr_SetProf( proc_chars, ANN_LOADS_DENSITY, loads_density);
    arr_SetProf( proc_chars, ANN_W_LOADS_DENSITY, w_loads_density);
    arr_SetProf( proc_chars, ANN_MAX_LOADS_DENSITY, max_loads_density);
    arr_SetProf( proc_chars, ANN_AVER_LOADS_DENSITY, aver_loads_density);
    arr_SetProf( proc_chars, ANN_W_AVER_LOADS_DENSITY, w_aver_loads_density);
    arr_SetProf( proc_chars, ANN_STORES_NUM, fpa_ConvIntVal( stores_num));
    arr_SetProf( proc_chars, ANN_W_STORES_NUM, w_stores_num);
    arr_SetProf( proc_chars, ANN_MAX_STORES_NUM, fpa_ConvIntVal( max_stores_num));
    arr_SetProf( proc_chars, ANN_AVER_STORES_NUM, aver_stores_num);
    arr_SetProf( proc_chars, ANN_W_AVER_STORES_NUM, w_aver_stores_num);
    arr_SetProf( proc_chars, ANN_STORES_DENSITY, stores_density);
    arr_SetProf( proc_chars, ANN_W_STORES_DENSITY, w_stores_density);
    arr_SetProf( proc_chars, ANN_MAX_STORES_DENSITY, max_stores_density);
    arr_SetProf( proc_chars, ANN_AVER_STORES_DENSITY, aver_stores_density);
    arr_SetProf( proc_chars, ANN_W_AVER_STORES_DENSITY, w_aver_stores_density);
    arr_SetProf( proc_chars, ANN_NODES_NUM, nodes_num);
    arr_SetProf( proc_chars, ANN_W_NODES_NUM, w_nodes_num);
    arr_SetProf( proc_chars, ANN_LOOPS_NUM, fpa_ConvIntVal( loops_num));
    arr_SetProf( proc_chars, ANN_OVL_LOOPS_NUM, fpa_ConvIntVal( ovl_loops_num));
    arr_SetProf( proc_chars, ANN_IRR_LOOPS_NUM, fpa_ConvIntVal( irr_loops_num));
    arr_SetProf( proc_chars, ANN_MAX_CNT, max_cnt);
    arr_SetProf( proc_chars, ANN_AVER_CNT, aver_cnt);
    arr_SetProf( proc_chars, ANN_DOM_HEIGHT, fpa_ConvIntVal( dom_height));
    arr_SetProf( proc_chars, ANN_DOM_WEIGHT, fpa_ConvIntVal( dom_weight));
    arr_SetProf( proc_chars, ANN_DOM_BRANCH, fpa_ConvIntVal( dom_branch));
    arr_SetProf( proc_chars, ANN_PDOM_HEIGHT, fpa_ConvIntVal( pdom_height));
    arr_SetProf( proc_chars, ANN_PDOM_WEIGHT, fpa_ConvIntVal( pdom_weight));
    arr_SetProf( proc_chars, ANN_PDOM_BRANCH, fpa_ConvIntVal( pdom_branch));

    return (proc_chars);
} /* ann_CalcProcChars */

/**
 * Вычисление значения нейронной сети на входном векторе
 */
static arr_Array_ptr
ann_CalcOutput( ann_Model_ref model, /* нейронная сеть */
                arr_Array_ptr input) /* входной вектор */
{
    arr_Array_ptr output;
    arr_Array_ptr weights = ann_GetWeights(model);
    arr_Array_ptr biases = ann_GetBiases(model);
    arr_Array_ptr acts = ann_GetActs(model);
    unsigned int layers_num = ann_GetLayersNum(model);
    unsigned int i, j, l, m, n;

    /* Обходим слои и вычисляем значения их нейронов */
    input = arr_CopyArray( input);
    for ( l = 0; l < layers_num; l++, input = output, arr_DeleteArray( input) )
    {
        arr_Array_ptr A = (arr_Array_ptr)arr_GetPtr( weights, l);
        arr_Array_ptr b = (arr_Array_ptr)arr_GetPtr( biases, l);
        ann_ActivationFunc_t f = (ann_ActivationFunc_t)arr_GetPtr( acts, l);

        /* Проверяем соответствие размера матрицы весов и входного вектора */
        n = arr_GetMatrixDimension( A);
        m = arr_GetLength( input);
        ECOMP_ASSERT( arr_GetLength( A) == n * m );

        /* Вычисляем значение входного вектора */
        output = arr_NewArray( ARR_PROF_UNITS, n, ARR_ZERO_INIT);
        for ( i = 0; i < n; i++ )
        {
            /* Производим умножение матрицы A на вектор input */
            ecomp_Profile_t x = arr_GetProf( b, i);
            for ( j = 0; j < m; j++ )
            {
                x = fpa_Add( x, fpa_Mul( arr_GetMatrixProf( A, j, i), arr_GetProf( input, j)));
            }
            arr_SetProf( output, i, x);
        }
        f(output); /* Применяем функцию активации */
    }

    return (output);
} /* ann_CalcOutput */

/**
 * Поиск точки на сетке, наименее удалённой от точки, соответствующей 
 * текущим значениям опций компилятора
 */
static unsigned int
ann_FindOptionsIndexInGrid( arr_Array_ptr options, /* опции компилятора */
                            arr_Array_ptr grid)    /* сетка значений опции компилятора */
{
    arr_Array_ptr x, y;
    ecomp_Profile_t z, u;
    unsigned int i, j;
    unsigned int m = arr_GetLength( options);
    unsigned int n = arr_GetMatrixDimension( grid);
    unsigned int res;

    ECOMP_ASSERT( arr_GetLength( grid) == n * m && n > 1 );

    x = arr_NewArray( ARR_PROF_UNITS, m, ARR_ZERO_INIT);
    for ( j = 0; j < m; j++ )
    {
        arr_SetProf( x, j, ann_GetOptionValue( arr_GetProf( options, j)));
    }

    y = arr_NewArray( ARR_PROF_UNITS, m, ARR_ZERO_INIT);
    for ( j = 0; j < m; j++ )
    {
        arr_SetProf( y, j, arr_GetMatrixProf( grid, j, 0));
    }
    u = ann_Distance( x, y);
    arr_DeleteArray( y);
    res = 0;

    for ( i = 1; i < n; i++ )
    {
        y = arr_NewArray( ARR_PROF_UNITS, m, ARR_ZERO_INIT);
        for ( j = 0; j < m; j++ )
        {
            arr_SetProf( y, j, arr_GetMatrixProf( grid, j, i));
        }

        z = ann_Distance( x, y);
        if ( fpa_IsLes( z, u) )
        {
            u = z;
            res = i;
        }

        arr_DeleteArray( y);
    }
    
    arr_DeleteArray( x);

    return (res);
} /* ann_FindOptionsIndexInGrid */

/**
 * Инициализация пакета работы с нейронными сетями
 */
void
ann_Init( ann_Info_t *info_p) /* инфо */
{
    ann_Model_ref model;
    unsigned int n, models_num;

    /* Инициализируем информационную структуру */
    mem_InitStructPtr( info_p);

    info_p->models_pool = mem_NewPool( ann_Model_t, MEM_AREA_ANN);
    info_p->options_pool = mem_NewPool( ann_Option_t, MEM_AREA_ANN);
    info_p->lists_pool = list_NewPool( 0);

    info_p->models = list_New( info_p->lists_pool);

    for ( n = 0; n < ANN_MODELS_NUM; n++ )
    {
        model = ann_InitModel[n]( info_p);
        list_InsRef( info_p->models, model);
    }

    return;
} /* ann_Init */

/**
 * Закрытие пакета работы с нейронными сетями
 */
void
ann_Close( ann_Info_t *info_p) /* инфо */
{
    ann_Model_ref model;
    arr_Array_ptr weights, biases;
    unsigned int i;
    list_Unit_ref unit;

    for LIST_UNITS( unit, info_p->models)
    {
        model = list_GetRef( unit);
        weights = ann_GetWeights( model);
        biases  = ann_GetBiases( model);

        for ( i = 0; i < ann_GetLayersNum( model); i++ )
        {
            arr_DeleteArray( arr_GetProf( weights, i));
            arr_DeleteArray( arr_GetProf( biases, i));
        }

        arr_DeleteArray( weights);
        arr_DeleteArray( biases);
        arr_DeleteArray( ann_GetActs( model));
        arr_DeleteArray( ann_GetOptions( model));
        arr_DeleteArray( ann_GetGrid( model));
    }
    
    mem_DeletePool( info_p->models_pool);
    mem_DeletePool( info_p->options_pool);
    list_DeletePool( info_p->lists_pool);

    return;
} /* ann_Init */

/**
 * Скорректировать значения опций компилятора для процедуры proc 
 * в соответствии с предобученной нейронной сетью
 */
void 
ann_CorrectProcOptions( ire2k_Proc_ref proc) /* процедура */
{
    ann_Model_ref model;
    ann_Info_t info, *info_p = &info;
    arr_Array_ptr grid, options, best_options, output;
    arr_Array_ptr proc_chars = ann_CalcProcChars( proc);
    ecomp_Profile_t accur, prob, max_prob;
    list_Unit_ref unit;
    unsigned int i, n, new_point, old_point;

    /* Инициализируем пакет */
    ann_Init( info_p);

    /**
     * Находим значения опций, определеных обученными нейронными сетями,
     * и проверяем эффективность этих значений. Также определяем наилучшую
     * комбинацию значений опций среди всех нейронных сетей.
     */
    accur = ECOMP_ZERO_PROFILE;
    best_options = mem_Entry_null;
    for LIST_UNITS( unit, info_p->models)
    {
        model = list_GetRef( unit);
        options = ann_GetOptions( model);
        grid = ann_GetGrid( model);
        n = arr_GetMatrixDimension( grid);

        /* Вычисляем значение нейронной сети на наборе характеристик процедуры */
        output = ann_CalcOutput( model, proc_chars);
        ECOMP_ASSERT( arr_GetLength( output) == n );

        /**
         * Находим точку на сетке, которая по мнению нейронной сети 
         * соответствует более оптимальным значениям опций компилятора
         */
        new_point = 0;
        max_prob = arr_GetProf( output, 0);
        for ( i = 1; i < n; i++ )
        {
            prob = arr_GetProf( output, i);
            if ( fpa_IsGrt( prob, max_prob) )
            {
                new_point = i;
                max_prob = prob;
            }
        }

        if ( fpa_IsGeq( max_prob, ANN_MIN_ADMISSIBLE_PROB) )
        {
            /* Находим точку на сетке, соответствующую текущим значениям опций */
            old_point = ann_FindOptionsIndexInGrid( options, grid);
            prob = arr_GetProf( output, old_point);

            if ( fpa_IsGeq( max_prob, fpa_Mul( ANN_MIN_ADMISSIBLE_RATIO, prob)) )
            {
                if ( fpa_IsGrt( max_prob, accur) )
                {
                    accur = max_prob;
                    for ( i = 0; i < arr_GetLength( options); i++ )
                    {
                        arr_SetProf( options, arr_GetMatrixProf( grid, i, new_point));
                    }
                    best_options = options;
                }
            }
        }

        /* Подчищаем за собой */
        arr_DeleteArray( output);
    }
    
    /* Если были найдены более оптимальные значения опций, устанавливаем их */
    if ( mem_IsNotRefNull( best_options) )
    {
        for ( i = 0; i < arr_GetLength( best_options); i++ )
        {
            ann_WriteOption( arr_GetRef( best_options, i));
        }
    }

    /* Подчищаем за собой */
    ann_Close( info_p);

    return;
} /* ann_CorrectProcOptions */
