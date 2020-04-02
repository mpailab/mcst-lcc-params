#!/bin/bash

# Скрипт запускает процесс сбора статистики работы компилятора при варьировании значений
# выделенных опций компилятора lcc

##########################################################################################
# Опции компилятора lcc
##########################################################################################

# Хэш-таблица настраиваемых опций компилятора lcc
# option_name -> (type, initial value, step, steps number)
declare -A OPTS

OPTS["regn_max_proc_op_sem_size"]="int 0 1 50000"
OPTS["regn_heur1"]="float 0.0 0.001 1000"
OPTS["regn_heur2"]="float 0.0 0.001 1000"
OPTS["regn_heur3"]="float 0.0 0.001 1000"
OPTS["regn_heur4"]="float 0.0 0.001 1000"
OPTS["regn_heur_bal1"]="float 0.0 0.001 1000"
OPTS["regn_heur_bal2"]="float 0.0 0.001 1000"
OPTS["regn_opers_limit"]="int 0 1 5000"
OPTS["regn_prob_heur"]="float 0.0 0.001 1000"
OPTS["regn_disb_heur"]="int 0 1 15"
OPTS["ifconv_merge_heur"]="float 0.0 0.001 1000"
OPTS["ifconv_opers_num"]="int 0 1 500"
OPTS["ifconv_calls_num"]="int 0 1 10"
OPTS["dcs_level"]="int 0 1 4"

# Печать допустимых для настройки опций компилятора lcc
print_supported_options ()
{
    for x in ${!OPTS[@]}
    do
        echo "$x"
    done
} # print_supported_options

# Проверка того, что список $1 является списком опций компилятора
check_options ()
{
    for x in $1
    do
        [ ${OPTS[$x]+_} ] || die "invalid option name '$x', should be one of ${!OPTS[@]}"
    done
} # check_options

##########################################################################################
# Внутренние переменные срипта
##########################################################################################

HOST_NAME=`hostname`
SCRIPT_NAME=`basename $0`
SHORT_SCRIPT_NAME=`basename $0 .sh`
CUR_DIR=`pwd`
DATA=`date +%Y%m%d%H%M%S`

OPTS_STR=""
MODE=""
IS_WHOLE=0
IS_PROF=0
IS_MATH=0
SUITE="all"
COMP_MACHINE="$HOST_NAME"
EXEC_MACHINE="cordelia"
GRID=100
SOURCE_DIR="$CUR_DIR"
OUTPUT_DIR="$CUR_DIR"

##########################################################################################
# Внутренние функции срипта
##########################################################################################

# Нештатный выход из скрипта
die ()
{
    echo -e "$SCRIPT_NAME: error: $@"
    exit 1
} # die

# Печать опций скрипта
print_usage()
{
    echo "usage: $SCRIPT_NAME <-opts STR> <mode> [-fwhole] [-prof] [-math] [-suite STR]"
    echo "              [-comp STR] [-exec STR] [-grid NUM] [-s DIR] [-o DIR]"
    echo
    echo "POSITIONAL OPTIONS:"
    echo "-opts STR  - generate statistics only for specified compiler options STR;"
    echo "             specify 'list' to show all available options"
    echo "mode       - use specified mode (-O1, -O2, -O3, -O4, -base, -peak)"
    echo
    echo "COMMON OPTIONS:"
    echo "-fwhole    - compile benchmarks in whole program mode"
    echo "-prof      - use -fprofile-use"
    echo "-math      - use -ffast-math"
    echo "-suite STR - run only specified suite of benchmarks: all, [fi]1995, [fi]2000,"
    echo "             [fi]2006, [fi]2017r (by default: $SUITE)"
    echo "-comp STR  - run compilation on specified machines (by default: $COMP_MACHINE)"
    echo "-exec STR  - run execution on specified machines (by default: $EXEC_MACHINE)"
    echo "-grid NUM  - use grid with N points (by default: $GRID)"
    echo
    echo "OTHER OPTIONS:"
    echo "-s DIR     - use specified directory DIR with script cmp.sh"
    echo "             (by default: $SOURCE_DIR)"
    echo "-o DIR     - use specified directory DIR for saving of statistics"
    echo "             (by default: $OUTPUT_DIR)"
    echo "-h         - print this help"
    exit 0
} # print_usage

# Является ли поданный аргумент пакетом задач
is_suite ()
{
    SUITES="all 1995 f1995 i1995 2000 f2000 i2000 2006 f2006 i2006 2017r f2017r i2017r"
    if [[ "$SUITES" != *"$1"* ]]
    then
        return 1
    fi
} # is_suite

# Проверка того, что список $1 является списком допустимых машин
check_machines ()
{
    return 1
} # check_machines

# Является ли поданный аргумент числом
is_number ()
{
    if [ "$1" = "" ] || \
       [ `expr "$1" : '[ ]*[0-9.]\+[ ]*'` != `expr length "$1"` ] || \
       [ `expr "$1" : '[ ]*[0.]\+[ ]*'`   == `expr length "$1"` ]
    then
        return 1
    fi
} # is_number

##########################################################################################
# Обработка аргументов, поданных скрипту
##########################################################################################

until [ -z "$1" ]
    do
    case "$1" in

        "-opts")
            shift
            OPTS_STR="$1"
            ;;

        "-O1"|"-O2"|"-O3"|"-O4"|"-base"|"-peak")
            [ "$MODE" == "" ] || die "mode '$MODE' is already specified"
            MODE="$1" 
            ;;

        "-fwhole")
            IS_WHOLE=1 
            ;;

        "-prof")
            IS_PROF=1 
            ;;

        "-math")
            IS_MATH=1 
            ;;

        "-suite")
            shift
            SUITE="$1"
            [ "$SUITE" != "" ] || die "no parameter for -suite option"
            is_suite "$SUITE" || die "invalid parameter for -suite option"
            ;;

        "-comp")
            shift
            COMP_MACHINE="$1"
            [ "$COMP_MACHINE" != "" ] || die "no parameter for -comp option"
            IFS=' ' read -r -a COMP_MACHINE_LIST <<< "$COMP_MACHINE"
            check_machines $COMP_MACHINE_LIST
            ;;

        "-exec")
            shift
            EXEC_MACHINE="$1"
            [ "$EXEC_MACHINE" != "" ] || die "no parameter for -exec option"
            IFS=' ' read -r -a EXEC_MACHINE_LIST <<< "$EXEC_MACHINE"
            check_machines $EXEC_MACHINE_LIST
            ;;

        "-grid")
            shift
            GRID="$1"
            is_number "$GRID" || die "invalid parameter for -grid option"
            ;;

        "-s")
            shift
            SOURCE_DIR="$1"
            [ -d "$SOURCE_DIR" ] || die "invalid parameter for -s option"
            ;;

        "-o")
            shift
            OUTPUT_DIR="$1"
            [ -d "$OUTPUT_DIR" ] || die "invalid parameter for -o option"
            ;;

        "-h"|"-help"|"--help")
            print_usage 
            ;;

        *) die "invalid argument '$1'" ;;
    esac

    shift
done

[ "$OPTS_STR" != "" ] || die "no parameter for -opts option"
if [ "$OPTS_STR" == "list" ]
then
    print_supported_options
    exit 0
fi
IFS=' ' read -r -a OPTS_LIST <<< "$OPTS_STR"
check_options $OPTS_LIST

[ "$MODE" != "" ] || die "<mode> is not specified"

##########################################################################################
# Основной блок скрипта
##########################################################################################
