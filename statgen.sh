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
# Списки бенчмарков
##########################################################################################

SPEC_F1995_LIST="101.tomcatv 102.swim 103.su2cor 104.hydro2d 107.mgrid 110.applu 125.turb3d 141.apsi 145.fpppp 146.wave5"
SPEC_I1995_LIST="099.go 124.m88ksim 126.gcc 129.compress 130.li 132.ijpeg 134.perl 147.vortex"
SPEC_1995_LIST="$SPEC_F1995_LIST $SPEC_I1995_LIST"

SPEC_F2000_LIST="178.galgel 187.facerec 189.lucas 191.fma3d 168.wupwise 171.swim 172.mgrid 173.applu 177.mesa 179.art 183.equake 188.ammp 200.sixtrack 301.apsi"
SPEC_I2000_LIST="164.gzip 175.vpr 176.gcc 181.mcf 186.crafty 197.parser 252.eon 253.perlbmk 254.gap 255.vortex 256.bzip2 300.twolf"
SPEC_2000_LIST="$SPEC_F2000_LIST $SPEC_I2000_LIST"

SPEC_F2006_LIST="470.lbm 482.sphinx3 410.bwaves 433.milc 434.zeusmp 450.soplex 459.GemsFDTD 444.namd 453.povray 435.gromacs 437.leslie3d 447.dealII 465.tonto 436.cactusADM 454.calculix 481.wrf 416.gamess"
SPEC_I2006_LIST="429.mcf 462.libquantum 473.astar 401.bzip2 458.sjeng 456.hmmer 400.perlbench 445.gobmk 464.h264ref 471.omnetpp 403.gcc 483.xalancbmk"
SPEC_2006_LIST="$SPEC_F2006_LIST $SPEC_I2006_LIST"

SPEC_F2017_LIST="503.bwaves 507.cactuBSSN 508.namd 510.parest 511.povray 519.lbm 521.wrf 526.blender 527.cam4 538.imagick 544.nab 549.fotonik3d 554.roms 603.bwaves 607.cactuBSSN 619.lbm 621.wrf 627.cam4 628.pop2 638.imagick 644.nab 649.fotonik3d 654.roms"
SPEC_I2017_LIST="500.perlbench 502.gcc 505.mcf 520.omnetpp 523.xalancbmk 525.x264 531.deepsjeng 541.leela 548.exchange2 557.xz 600.perlbench 602.gcc 605.mcf 620.omnetpp 623.xalancbmk 625.x264 631.deepsjeng 641.leela 648.exchange2 657.xz"
SPEC_2017_LIST="$SPEC_F2017_LIST $SPEC_I2017_LIST"

SPEC_ALL_LIST="$SPEC_1995_LIST $SPEC_2000_LIST $SPEC_2006_LIST $SPEC_2017_LIST"

SPEC_TABLE=(
    ["all"]="$SPEC_ALL_LIST"
    ["1995"]="$SPEC_1995_LIST"
    ["f1995"]="$SPEC_F1995_LIST"
    ["i1995"]="$SPEC_I1995_LIST"
    ["2000"]="$SPEC_2000_LIST"
    ["f2000"]="$SPEC_F2000_LIST"
    ["i2000"]="$SPEC_I2000_LIST"
    ["2006"]="$SPEC_2006_LIST"
    ["f2006"]="$SPEC_F2006_LIST"
    ["i2006"]="$SPEC_I2006_LIST"
    ["2017r"]="$SPEC_2017_LIST"
    ["f2017r"]="$SPEC_F2017_LIST"
    ["i2017r"]="$SPEC_I2017_LIST"
)

##########################################################################################
# Внутренние переменные срипта
##########################################################################################

HOST_NAME=`hostname`
SCRIPT_NAME=`basename $0`
SHORT_SCRIPT_NAME=`basename $0 .sh`
SCRIPT_NAME_BLANK=`printf ' %.0s' {1..${#SCRIPT_NAME}}`
CUR_DIR=`pwd`
DATA=`date +%Y%m%d%H%M%S`

OPTS_STR=""
MODE=""
IS_WHOLE=0
IS_PROF=0
IS_MATH=0
SUITE="all"
TEST_NAME=""
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
    echo -e "error: $@"
    exit 1
} # die

# Нештатный выход из скрипта
warning ()
{
    echo -e "warning: $@"
} # die

# Печать опций скрипта
print_usage()
{
    echo "usage: $SCRIPT_NAME <-opts STR> <mode> [-fwhole] [-prof] [-math]"
    echo "       $SCRIPT_NAME_BLANK [-suite STR] [-run STR] [-comp STR] [-exec STR]"
    echo "       $SCRIPT_NAME_BLANK [-grid NUM] [-s DIR] [-o DIR]"
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
    echo "-run STR   - run only specified benchmarks STR"
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

# Проверка того, что $1 - имя существующего пакета бенчмарков
check_suite ()
{
    local -n suite=$1
    [[ "${!SPEC_TABLE[@]}" == *"$suite"* ]] || die "invalid parameter for -suite option"
} # check_suite

# Проверка того, $1 - список бенчмарков из пакета $2
check_specs ()
{
    local -n specs=$1
    local -n suite=$2
    for spec in "${specs[@]}"
    do
        [[ "${SPEC_TABLE[$suite]}" == *"$spec"* ]] || die "benchmark '$spec' is not in the suite '$suite'"
    done
} # check_specs

# Проверка того, что список $1 является списком допустимых машин
check_machines ()
{
    local -n machine_list=$1
    for i in "${!machine_list[@]}"
    do
        timelimit -s15 -t1 rsh ${machine_list[$i]} echo "ok" > /dev/null 2>&1
        case "$?" in
            0)
                ;;

            143)
                warning "machine '${machine_list[$i]}' is not available and will be skipped"
                unset -v 'machine_list[$i]'
                ;;

            *) die "invalid machine name '${machine_list[$i]}'" ;;
        esac
    done
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

# Считываем аргументы скрипта
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

        "-fwhole") IS_WHOLE=1 ;;
        "-prof")   IS_PROF=1  ;;
        "-math")   IS_MATH=1  ;;

        "-suite")
            shift
            SUITE="$1"
            [ "$SUITE" != "" ] || die "no parameter for -suite option"
            ;;

        "-run")
            shift
            TEST_NAME="$1"
            [ "$TEST_NAME" != "" ] || die "no parameter for -run option"
            ;;

        "-comp")
            shift
            COMP_MACHINE="$1"
            [ "$COMP_MACHINE" != "" ] || die "no parameter for -comp option"
            ;;

        "-exec")
            shift
            EXEC_MACHINE="$1"
            [ "$EXEC_MACHINE" != "" ] || die "no parameter for -exec option"
            ;;

        "-grid")
            shift
            GRID="$1"
            [ "$GRID" != "" ] || die "no parameter for -grid option"
            ;;

        "-s")
            shift
            SOURCE_DIR="$1"
            [ "$SOURCE_DIR" != "" ] || die "invalid parameter for -s option"
            ;;

        "-o")
            shift
            OUTPUT_DIR="$1"
            [ "$OUTPUT_DIR" != "" ] || die "invalid parameter for -o option"
            ;;

        "-h"|"-help"|"--help")
            print_usage 
            ;;

        *) die "invalid argument '$1'" ;;
    esac

    shift
done

#-----------------------------------------------------------------------------------------
# Проверяем корректность аргументов

[ "$OPTS_STR" != "" ] || die "no parameter for -opts option"
if [ "$OPTS_STR" == "list" ]
then
    print_supported_options
    exit 0
fi
IFS=' ' read -r -a OPTS_LIST <<< "$OPTS_STR"
check_options $OPTS_LIST

[ "$MODE" != "" ] || die "<mode> is not specified"

check_suite SUITE

if [ "$TEST_NAME" == "" ]
then
    $TEST_NAME="${SPEC_TABLE[$SUITE]}"
fi
IFS=' ' read -r -a TEST_NAME_LIST <<< "$TEST_NAME"
check_specs TEST_NAME_LIST

IFS=' ' read -r -a COMP_MACHINE_LIST <<< "$COMP_MACHINE"
check_machines COMP_MACHINE_LIST
[ ! -z "$COMP_MACHINE_LIST" ] || die "there are no available comp-machines"

IFS=' ' read -r -a EXEC_MACHINE_LIST <<< "$EXEC_MACHINE"
check_machines EXEC_MACHINE_LIST
[ ! -z "$EXEC_MACHINE_LIST" ] || die "there are no available exec-machines"

is_number "$GRID" || die "invalid parameter for -grid option"

[ -d "$SOURCE_DIR" ] || die "there is no a directory '$SOURCE_DIR'"
SOURCE_DIR=`realpath $SOURCE_DIR`
[ -f "$SOURCE_DIR/cmp.sh" ] || die "there is no a script '$SOURCE_DIR/cmp.sh'"

[ -d "$OUTPUT_DIR" ] || mkdir $OUTPUT_DIR || die "can't create a directory '$OUTPUT_DIR'"
OUTPUT_DIR=`realpath $OUTPUT_DIR`

##########################################################################################
# Инициализация внутренних переменных
##########################################################################################

PROCS_CHARS_FILE="$OUTPUT_DIR/procs_chars.txt"
PROCS_COMP_TIME_FILE="$OUTPUT_DIR/procs_comp_time.txt"
PROCS_EXEC_TIME_FILE="$OUTPUT_DIR/procs_exec_time.txt"
PROCS_EMUL_EXE_FILE="$OUTPUT_DIR/procs_emul_exe.txt"

BASE_ARGS="$MODE -suite $SUITE -old -force"
BASE_INNER_ARGS=""
if [ $IS_WHOLE == 1 ]
then
    BASE_ARGS="$BASE_ARGS -fwhole"
fi
if [ $IS_PROF == 1 ]
then
    BASE_ARGS="$BASE_ARGS -prof"
fi
if [ $IS_MATH == 1 ]
then
    BASE_INNER_ARGS="$BASE_INNER_ARGS -ffast-math"
fi

##########################################################################################
# Основной блок скрипта
##########################################################################################

# Переходим в рабочую директорию
WORK_DIR="$CUR_DIR/$SHORT_SCRIPT_NAME_$DATA"
mkdir $WORK_DIR || die "can't create a directory '$WORK_DIR'"
cd $WORK_DIR

# Копируем исходники
cp $SOURCE_DIR/*.sh .

# Собираем характеристики процедур 
INNER_ARGS="$BASE_INNER_ARGS --lets=ann_procs_chars_file:$PROCS_CHARS_FILE"
ARGS="-comp $BASE_ARGS -run \"${TEST_NAME_LIST[@]}\" -old-opt \"$INNER_ARGS\""
if [ "${#COMP_MACHINE_LIST[@]}" > 1 ]
then
    rsh "${COMP_MACHINE_LIST[1]}" "cd $WORK_DIR; ./cmp.sh $ARGS" &
    PROCS_CHARS_PID=$!
else
    rsh "${COMP_MACHINE_LIST[0]}" "cd $WORK_DIR; ./cmp.sh $ARGS"
fi

# Собираем начальные значения времени компиляции и emul_exe процедур 
INNER_ARGS="$BASE_INNER_ARGS --lets=procs_comp_time_file:$PROCS_COMP_TIME_FILE"
INNER_ARGS="$INNER_ARGS --lets=procs_emul_exe_file:$PROCS_EMUL_EXE_FILE"
ARGS="-comp $BASE_ARGS -run \"${TEST_NAME_LIST[@]}\" -old-opt \"$INNER_ARGS\""
rsh "${COMP_MACHINE_LIST[0]}" "cd $WORK_DIR; ./cmp.sh $ARGS"

"--true=print_proc_ire2k_time --true=emul_exe"

# Дожидаемся завершения сбора характеристик процедур
wait $PROCS_CHARS_PID

OPT_START_NUM=0
COMP_STEP_NUM=`echo "scale=0; ${#OPTS_LIST[@]}/${#COMP_MACHINE_LIST[@]}" | bc`
for (( comp_step=0; comp_step <= $COMP_STEP_NUM; comp_step++ ))
do
    if [ (($OPT_START_NUM + ${#COMP_MACHINE_LIST[@]})) <= ${#OPTS_LIST[@]} ]
    then
        OPT_END_NUM=$(($OPT_DELTA + ${#COMP_MACHINE_LIST[@]}))
    else
        OPT_END_NUM=${#COMP_MACHINE_LIST[@]}
    fi

    comp_i=0
    for (( opt_num=$OPT_START_NUM; opt_num < $OPT_END_NUM; opt_num++ ))
    do
        OPT_NAME=${OPTS_LIST[$opt_num]}
        IFS=' ' read -r -a OPT_ATTR <<< "${OPT[$OPT_NAME]}}"
        OPT_TYPE=${ATTR[0]}
        OPT_VALUE=${ATTR[1]}
        OPT_STEP=${ATTR[2]}
        OPT_MAX_VALUE=${ATTR[3]}
        if ( $OPT_MAX_VALUE > $GRID )
        then
            OPT_STEP=`echo "scale=5; $OPT_STEP * ($OPT_MAX_VALUE / $GRID)" | bc`
        fi

        while [ $OPT_VALUE < $OPT_MAX_VALUE ]
        do
            OPT_STAT_DIR="$OUTPUT_DIR/$OPT_NAME_$OPT_VALUE"
            PROCS_COMP_TIME_FILE="$OPT_STAT_DIR/procs_comp_time.txt"
            PROCS_EXEC_TIME_FILE="$OPT_STAT_DIR/procs_exec_time.txt"
            PROCS_EMUL_EXE_FILE="$OPT_STAT_DIR/procs_emul_exe.txt"
            
            OPT_VALUE=`echo "scale=5; $OPT_VALUE + $OPT_STEP" | bc`
            
            INNER_ARGS="$BASE_INNER_ARGS --lets=procs_comp_time_file:$PROCS_COMP_TIME_FILE"
            INNER_ARGS="$INNER_ARGS --lets=procs_emul_exe_file:$PROCS_EMUL_EXE_FILE"
            ARGS="-comp $BASE_ARGS -run \"${TEST_NAME_LIST[@]}\" -old-opt \"$INNER_ARGS\""
            rsh "${COMP_MACHINE_LIST[$comp_i]}" "cd $WORK_DIR; ./cmp.sh $ARGS"
        done

        comp_i=$((comp_i + 1))
    done

    OPT_START_NUM=$OPT_END_NUM
done
