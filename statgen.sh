#!/bin/bash

# Скрипт запускает процесс сбора статистики работы компилятора при варьировании значений
# выделенных опций компилятора lcc

##########################################################################################
# Опции компилятора lcc
##########################################################################################

# Хэш-таблица настраиваемых опций компилятора lcc
# option_name -> (TYPE, initial value, step, steps number)
declare -A OPTS_INFO

OPTS_INFO["regn_max_proc_op_sem_size"]="int 0 1 50000"
OPTS_INFO["regn_heur1"]="float 0.0 0.001 1.0"
OPTS_INFO["regn_heur2"]="float 0.0 0.001 1.0"
OPTS_INFO["regn_heur3"]="float 0.0 0.001 1.0"
OPTS_INFO["regn_heur4"]="float 0.0 0.001 1.0"
OPTS_INFO["regn_heur_bal1"]="float 0.0 0.001 1.0"
OPTS_INFO["regn_heur_bal2"]="float 0.0 0.001 1.0"
OPTS_INFO["regn_opers_limit"]="int 0 1 5000"
OPTS_INFO["regn_prob_heur"]="float 0.0 0.001 1.0"
OPTS_INFO["regn_disb_heur"]="int 0 1 15"
OPTS_INFO["ifconv_merge_heur"]="float 0.0 0.001 1.0"
OPTS_INFO["ifconv_opers_num"]="int 0 1 500"
OPTS_INFO["ifconv_calls_num"]="int 0 1 10"
OPTS_INFO["dcs_level"]="int 0 1 4"

##
# Печать допустимых для настройки опций компилятора lcc
##
print_supported_options ()
{
    echo "Supported options:"
    for x in ${!OPTS_INFO[@]}
    do
        echo "  $x"
    done
} # print_supported_options

##
# Проверка того, что список $1 является списком опций компилятора
##
check_options ()
{
    for x in $1
    do
        [ ${OPTS_INFO[$x]+_} ] || die "invalid option name '$x'.\nUse '-opts list' to show all available options"
    done
} # check_options

##
# Получить точность вычислений значений параметра в зависимости от его типа
#
# Аргументы:
#  $1 - тип параметра (int или float)
##
get_scale()
{
    case "$1" in

        "int")   echo 0 ;;
        "float") echo 5 ;;
        *) die "invalid option type '$1'" ;;
    esac
}

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

declare -A SPEC_TABLE
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

##
# Проверка того, что $1 - имя существующего пакета бенчмарков
##
check_suite ()
{
    local -n suite=$1
    [[ "${!SPEC_TABLE[@]}" == *"$suite"* ]] || die "invalid parameter for -suite option"
} # check_suite

##
# Проверка того, $1 - список бенчмарков из пакета $2
##
check_specs ()
{
    local -n specs=$1
    local -n suite=$2
    for spec in "${specs[@]}"
    do
        [[ "${SPEC_TABLE[$suite]}" == *"$spec"* ]] || die "benchmark '$spec' is not in the suite '$suite'.\nUse '-run list' to show all available benchmarks."
    done
} # check_specs

##
# Печать доступных бенчмарков
##
print_supported_benchmarks ()
{
    local -n suite=$1
    local -a benchmarks
    IFS=' ' read -r -a benchmarks <<< "${SPEC_TABLE[$suite]}"
    echo "Supported benchmarks of suite '$suite':"
    for x in ${benchmarks[@]}
    do
        echo "  $x"
    done
} # print_supported_options

##########################################################################################
# Внутренние переменные срипта
##########################################################################################

HOST_NAME=`hostname`
SCRIPT_NAME=`basename $0`
SHORT_SCRIPT_NAME=`basename $0 .sh`
SCRIPT_NAME_BLANK=`head -c ${#SCRIPT_NAME} < /dev/zero | tr '\0' ' '`
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

##
# Нештатный выход из скрипта
##
die ()
{
    echo -e "error: $@"
    exit 1
} # die

##
# Выдача предупреждения
##
warning ()
{
    echo -e "warning: $@"
} # die

##
# Печать опций скрипта
##
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
    echo "-run STR   - run only specified benchmarks STR;"
    echo "             specify 'list' to show all available benchmarks"
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

##
# Проверка того, что список $1 является списком допустимых машин
##
check_machines ()
{
    local -n machine_list=$1
    for i in "${!machine_list[@]}"
    do
        timelimit -s15 -t2 rsh ${machine_list[$i]} echo "ok" > /dev/null 2>&1
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

##
# Является ли поданный аргумент числом
##
is_number ()
{
    if [ "$1" = "" ] || \
       [ `expr "$1" : '[ ]*[0-9.]\+[ ]*'` != `expr length "$1"` ] || \
       [ `expr "$1" : '[ ]*[0.]\+[ ]*'`   == `expr length "$1"` ]
    then
        return 1
    fi
} # is_number

##
# Запустить компиляцию заданного теста на заданной машине при заданного значении опции
# 
# Аргументы:
#  $1 - имя машины компиляции
#  $2 - имя машины исполнения
#  $3 - имя теста
#  $4 - значение опции
#  $5 - директория для сброса статистики
##
compile()
{
    local machine="$1"
    local exec_machine="$2"
    local test="$3"
    local value="$4"
    local stat_dir="$5"

    echo "  compile $test on $machine for $value"

    if [ -z "$machine" ] || [ -z "$exec_machine" ] || [ -z "$test" ] || [ -z "$value" ] || [ -z "$stat_dir" ]
    then
        return 1
    fi

    local args="$BASE_INNER_ARGS"
    args="$args --lets=procs_comp_time_file:$stat_dir/procs_comp_time.txt"
    args="$args --lets=procs_emul_exe_file:$stat_dir/procs_emul_exe.txt"
    if [ "$value" != "none" ]
    then
        # Запускаем компиляцию в каталоге, привязанном к текущей машине исполнения
        if [ "$TYPE" == "int" ]
        then
            args="$args --let=$OPTION:$value}"
        else
            args="$args --letf=$OPTION:$value}"
        fi
        args="-comp $BASE_ARGS -run $test -old-opt \"$args\""
        rsh "$machine" "cd $WORK_DIR/$exec_machine; ./cmp.sh $args" &> /dev/null
    else
        # При выполнении предварительной задачи из стека компиляция 
        # запускает единожды в корневой рабочей директории
        args="-comp $BASE_ARGS -run $test -old-opt \"$args\""
        rsh "$machine" "cd $WORK_DIR; ./cmp.sh $args" &> /dev/null
    fi

} # compile

##
# Получить статистику исполнения теста на заданной машине исполнения 
# 
# Аргументы:
#  $1 - имя машины исполнения
#  $2 - имя теста
#  $3 - директория для сброса статистики
##
get_exec_stat()
{
    local machine="$1"
    local test="$2"
    local stat_dir="$3"
    local lpwd=`pwd`

    if [ -z "$machine" ] || [ -z "$test" ] || [ -z "$stat_dir" ]
    then
        return 1
    fi

    # Получаем профили исполняемых процедур
    cd "$WORK_DIR/$machine/$CMP_RES_DIR"
    $WORK_DIR/make_prof.sh $test &> /dev/null
    if [ $? -ne 0 ]
    then
        warning "make_prof.sh is failed for '$test'"

    else
        # Суммируем профили исполняемых процедур
        local -A TIME
        local -A NUM
        for prof in `ls exec.$test/prof*.txt`
        do
            declare -a rows
            readarray -t rows < <(cat $prof | grep "% " | grep -v "(*)")
            for i in ${!rows[@]}
            do
                row="${rows[$i]}"
                proc=`echo $row | awk '{print $6}'`
                time=`echo $row | awk '{print $5}'`
                num=1
                if [ ${TIME[$proc]+abc} ]
                then
                    time=`echo "${TIME[$proc]}+$time" | bc`
                    num=$((${NUM[$proc]} + 1))
                fi
                TIME[$proc]=$time
                NUM[$proc]=$num
            done
        done

        # Сохраняем профили исполняемых процедур
        for proc in ${!TIME[@]}
        do 
            time=`echo "${TIME[$proc]}/${NUM[$proc]}" | bc`
            echo "$proc $time" >> $stat_dir/procs_exec_time.txt
        done
    fi

    # Возвращаемся в текущий каталог
    cd $lpwd

} # get_exec_stat

##
# Запустить исполнение заданного теста на заданной машине исполнения
# при заданного значении опции
# 
# Аргументы:
#  $1 - имя машины исполнения
#  $2 - имя теста
#  $3 - значение опции
#  $4 - директория для сброса статистики
#  $5 - pid последнего процесса на host-машине, запустившего исполнение на машине $1
##
execute()
{
    local machine="$1"
    local test="$2"
    local value="$3"
    local stat_dir="$4"
    local pid="$5"

    echo "  execute $test on $machine for $value"

    if [ -z "$machine" ] || [ -z "$test" ] || [ -z "$value" ] || [ -z "$stat_dir" ]
    then
        return 1
    fi

    # Ждём завершения последнего процесса на host-машине, 
    # запустившего исполнение на данной машине исполнения
    while [ -n "$pid" ] && [ -e /proc/$pid ]
    do
        sleep 1
    done

    # При необходимости ждём завершения ночного тестирования
    local available=`rsh $machine "[ -f /tmp/flags/machine_locked ] || echo yes" 2> /dev/null`
    while [ -z "$available" ]
    do
        sleep 1000
        available=`rsh $machine "[ -f /tmp/flags/machine_locked ] || echo yes" 2> /dev/null`
    done

    # Для чистоты статистики ждём освобождения машины исполнения
    local uptime=`rsh $machine uptime 2> /dev/null | awk '{print $(NF-2) $(NF-1) $NF}'`
    IFS=',' read -r -a load <<< "$uptime"
    local cpu_num=`rsh $machine nproc 2> /dev/null`
    local n=`echo "scale=0; $cpu_num / 4" | bc`
    while (( $(echo "${load[0]} > $n || ${load[1]} > $n || ${load[2]} > $n" | bc -l) ))
    do
        sleep 1
        uptime=`rsh $machine uptime 2> /dev/null | awk '{print $(NF-2) $(NF-1) $NF}'`
        IFS=',' read -r -a load <<< "$uptime"
    done
    
    # Машина свободна запускаем исполнения теста
    local args="-exec $BASE_ARGS -run $test"
    [ -z "$BASE_INNER_ARGS" ] || args="$args -old-opt \"$BASE_INNER_ARGS\""
    rsh "$machine" "cd $WORK_DIR/$machine; ./cmp.sh $args" &> /dev/null

    # Собираем статистику исполнения
    get_exec_stat "$machine" "$test" "$stat_dir"

    while (( ${LOCK["$machine"]} ))
    do
        sleep 1
    done

    # Определяем следующее значение опции
    if [ "$value" == "none" ]
    then
        # Выставляем начальное значение опции для текущей машины исполнения
        value="${VALUES["$machine"]}"

    else
        # Выставляем следующее значение опции для текущей машины исполнения
        value=`echo "scale=$SCALE; $value + ${STEPS["$machine"]}" | bc`
    fi

    # Добавляем в конец стека задачу компиляции и исполнения данного теста
    # со следующим значением опции (т.к. дочерние процессы не могут менять значения
    # переменных родительского процесса, то реализуем этот механизм посредством
    # записи и чтения из специальных файлов)
    local msg="STOP > $machine"
    if (( $(echo "$value < $MAX_VALUE" | bc -l) ))
    then
        msg="$test $machine $value"
    fi
    local data=`date +%Y%m%d%H%M%S`
    local file="/dev/shm/${SHORT_SCRIPT_NAME}_task_${data}_${test}_${machine}_${value}"
    echo "$msg" > $file

} # execute

##
# Выполнить текущую задачу из стека
# 
# Аргументы:
#  $1 - список характеристик задачи (p1 p2 p3 p4), где
#       p1 - признак предворительной задачи
#       p2 - имя теста
#       p3 - имя машины исполнения
#       p4 - значение параметра
##
perform()
{
    local -n task=$1
    local test="${task[0]}"
    local exec_machine="${task[1]}"
    local value="${task[2]}"

    echo "task: ${task[@]}"

    # Создаём директорию для сбора статистики
    local stat_dir="$OUTPUT_DIR/$OPTION.$value.$test.$exec_machine"
    mkdir $stat_dir || die "can't create a directory '$stat_dir'"

    if [ "$value" == "none" ]
    then
        # Для предварительных задач компиляцию запускаем лишь единожды
        if [ "$exec_machine" == "${EXEC_MACHINES[0]}" ]
        then
            compile "$COMP_MACHINE" "$exec_machine" "$test" "$value" "$stat_dir"
        fi

        # Копируем результаты компиляции в каталог, привязанный к текущей машине исполнения
        cp -r $WORK_DIR/$CMP_RES_DIR/$test* $WORK_DIR/$exec_machine/$CMP_RES_DIR

    else
        # Запускаем компиляцию для текущего значения параметра
        compile "$COMP_MACHINE" "$exec_machine" "$test" "$value" "$stat_dir"
    fi

    # Запускаем процесс исполнения для текущего значения параметра
    execute "$exec_machine" "$test" "$value" "$stat_dir" "${PIDS["$exec_machine"]}" &
    local pid=$!
    PIDS["$exec_machine"]=$pid
    if [ "$value" == "none" ]
    then
        PIDS_INFO["$pid"]+="$test $exec_machine $value ${VALUES["$exec_machine"]}"
    else
        PIDS_INFO["$pid"]+="$test $exec_machine $value ${STEPS["$exec_machine"]}"
    fi

} # perform

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
IFS=' ' read -r -a OPTS <<< "$OPTS_STR"
check_options $OPTS

[ "$MODE" != "" ] || die "<mode> is not specified"

check_suite SUITE

if [ "$TEST_NAME" == "" ]
then
    TEST_NAME="${SPEC_TABLE[$SUITE]}"

elif [ "$TEST_NAME" == "list" ]
then
    print_supported_benchmarks SUITE
    exit 0
fi
IFS=' ' read -r -a TEST_NAMES <<< "$TEST_NAME"
check_specs TEST_NAMES SUITE

IFS=' ' read -r -a COMP_MACHINES <<< "$COMP_MACHINE"
check_machines COMP_MACHINES
[ ! -z "$COMP_MACHINES" ] || die "there are no available comp-machines"
[ "${#COMP_MACHINES[@]}" == 1 ] || warning "currently, multiple comp-machines are not supported. Only '${COMP_MACHINES[0]}' will be used."
COMP_MACHINE=${COMP_MACHINES[0]}

IFS=' ' read -r -a EXEC_MACHINES <<< "$EXEC_MACHINE"
check_machines EXEC_MACHINES
[ ! -z "$EXEC_MACHINES" ] || die "there are no available exec-machines"

is_number "$GRID" || die "invalid parameter for -grid option"

[ -d "$SOURCE_DIR" ] || die "there is no a directory '$SOURCE_DIR'"
SOURCE_DIR=`realpath $SOURCE_DIR`
[ -f "$SOURCE_DIR/cmp.sh" ] || die "there is no a script '$SOURCE_DIR/cmp.sh'"

[ -d "$OUTPUT_DIR" ] || mkdir $OUTPUT_DIR || die "can't create a directory '$OUTPUT_DIR'"
OUTPUT_DIR=`realpath $OUTPUT_DIR`

##########################################################################################
# Инициализация внутренних переменных
##########################################################################################

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

CMP_RES_DIR="${MODE#"-"}"
if [ $IS_WHOLE == 1 ]
then
    CMP_RES_DIR="$CMP_RES_DIR.wh"
fi
if [ $IS_PROF == 1 ]
then
    CMP_RES_DIR="$CMP_RES_DIR.prof"
fi
CMP_RES_DIR="work.$CMP_RES_DIR.old"

##########################################################################################
# Основной блок скрипта
##########################################################################################

# Переходим в рабочую директорию
WORK_DIR="$CUR_DIR/${SHORT_SCRIPT_NAME}_$DATA"
mkdir $WORK_DIR || die "can't create a directory '$WORK_DIR'"
cd $WORK_DIR

# Копируем исходники в рабочий каталог
cp $SOURCE_DIR/*.sh .

# Создаём рабочии поддиректории для каждой машины исполнения по отдельности
# и копируем в них исходники скрипта cmp.sh
for exec_machine in "${EXEC_MACHINES[@]}"
do
    EXEC_WORK_DIR="$WORK_DIR/$exec_machine"
    mkdir $EXEC_WORK_DIR || die "can't create a directory '$EXEC_WORK_DIR'"   
    cp $SOURCE_DIR/*.sh $EXEC_WORK_DIR
    mkdir "$EXEC_WORK_DIR/$CMP_RES_DIR" || die "can't create a directory '$EXEC_WORK_DIR/$CMP_RES_DIR'"
done

# Собираем характеристики процедур 
INNER_ARGS="$BASE_INNER_ARGS --lets=ann_procs_chars_file:$OUTPUT_DIR/procs_chars.txt"
ARGS="-comp $BASE_ARGS -run \"${TEST_NAMES[@]}\" -old-opt \"$INNER_ARGS\""
if [ "$COMP_MACHINE" == "$HOST_NAME" ]
then
    rsh "$COMP_MACHINE" "cd $WORK_DIR; ./cmp.sh $ARGS" &> /dev/null
else
    # Машина компиляции отлична от host-машины, для экономии времени 
    # характеристики процедур соберём на host-машине
    rsh "$HOST_NAME" "cd $WORK_DIR; ./cmp.sh $ARGS" &> /dev/null &
fi

# Обходим опции и собираем статистику для каждой из них по отдельности
IS_NEXT=0
for OPTION in ${OPTS[@]}
do
    [ "$IS_NEXT" ] || echo
    echo "option: $OPTION"

    # Получаем характеристики опции
    IFS=' ' read -r -a ATTR <<< "${OPTS_INFO[$OPTION]}"
    TYPE=${ATTR[0]}
    VALUE=${ATTR[1]}
    STEP=${ATTR[2]}
    MAX_VALUE=${ATTR[3]}

    # Устанавливаем точность вычисления значений опции
    SCALE=$(get_scale $TYPE)

    # Корретируем шаг увеличения изменений опции
    if (( $(echo "($MAX_VALUE / $STEP) > $GRID" | bc -l) ))
    then
        STEP=`echo "scale=$SCALE; $MAX_VALUE / $GRID" | bc`
    fi

    # Инициализируем глобальные таблицы параметров машин исполнения
    declare -A VALUES # таблица начальных значений опции:
                      # (<машина исполнения> => <значение опции>)
    declare -A STEPS
    declare -A PIDS   # pid последненого процесса на host-машине, 
                      # запустившего процесс на машине исполнения:
                      # (<машина исполнения> => <pid>)
    for exec_machine in "${EXEC_MACHINES[@]}"
    do
        VALUES["$exec_machine"]="$VALUE"
        STEPS["$exec_machine"]=`echo "scale=$SCALE; $STEP * ${#EXEC_MACHINES[@]}" | bc`
        PIDS["$exec_machine"]=""
        VALUE=`echo "scale=$SCALE; $VALUE + $STEP" | bc`
    done

    # Создаём стек задач и заполняем его предварительными задачами
    declare -a STACK=()
    for test in "${TEST_NAMES[@]}"
    do
        for exec_machine in "${EXEC_MACHINES[@]}"
        do
            STACK+=("$test $exec_machine none")
        done
    done

    declare -A LOCK
    declare -A PIDS_INFO=()

    # Ждём освобождения стека и выполнения всех запущенных задач
    IS_WAIT=1
    while (( $IS_WAIT ))
    do
        if ls /dev/shm/${SHORT_SCRIPT_NAME}_task_* 1> /dev/null 2>&1
        then
            for file in `ls /dev/shm/${SHORT_SCRIPT_NAME}_task_*`
            do
                TASK=$(head -n 1 $file)
                if [[ "$TASK" == "STOP > "* ]]
                then
                    IFS=' ' read -r -a TASK_ATTR <<< "$TASK"
                    exec_machine=${TASK_ATTR[2]}
                    for machine in "${!PIDS[@]}"
                    do
                        LOCK["$machine"]=1
                        
                        PID="${PIDS["$machine"]}"
                        if [ -n "$(ps -p $PID -o pid=)" ]
                        then
                            IFS=' ' read -r -a PID_ATTR <<< "${PIDS_INFO[$PID]}"
                            TEST="${PID_ATTR[0]}"
                            VALUE=`echo "scale=$SCALE; ${PID_ATTR[2]} + ${PID_ATTR[3]} + ${STEPS["$machine"]}" | bc`
                            if [ -n "$(ps -p $PID -o pid=)" ]
                            then
                                if (( $(echo "$VALUE < $MAX_VALUE" | bc -l) ))
                                then
                                    STEPS["$machine"]=`echo "scale=$SCALE; 2 * ${STEPS["$machine"]}" | bc`
                                    STEPS["$exec_machine"]="${STEPS["$machine"]}"
                                    STACK+=("$TEST $exec_machine $VALUE")
                                    
                                    LOCK["$machine"]=0
                                    break
                                fi
                            fi
                        fi
                        LOCK["$machine"]=0
                    done
                else
                    STACK+=("$TASK")
                fi
                rm $file
            done
        fi

        if (( ${#STACK[@]} ))
        then
            # Стек непуст, выполняем первую его задачу
            IFS=' ' read -r -a TASK <<< "${STACK[0]}"
            STACK=("${STACK[@]:1}")
            perform TASK

        else
            # Стек пуст, проверяем завершение запущенных задач
            IS_WAIT=0
            if (( ${#EXEC_MACHINES[@]} > 1 ))
            then
                for exec_machine in "${EXEC_MACHINES[@]}"
                do
                    if [ -n "$(ps -p ${PIDS["$exec_machine"]} -o pid=)" ]
                    then
                        # Есть незавершённая задача, ждём ...
                        while ! ls /dev/shm/${SHORT_SCRIPT_NAME}_task_* 1> /dev/null 2>&1
                        do
                            sleep 1
                        done
                        IS_WAIT=1
                        break
                    fi
                done
            else
                exec_machine=${EXEC_MACHINES[0]}
                if [ -n "$(ps -p ${PIDS["$exec_machine"]} -o pid=)" ]
                then
                    wait "${PIDS["$exec_machine"]}"
                    IS_WAIT=1
                fi
            fi
        fi
    done

    # Ждём завершения всех фоновых процессов
    wait

    IS_NEXT=1
done
