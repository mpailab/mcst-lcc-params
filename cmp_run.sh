#!/bin/bash

# Внутренние переменные
CURDIR=`pwd`

# Переменные, соответствующие аргументам, подаваемым скрипту
IS_COMP=0
IS_EXEC=0
IS_STAT=0
SUITE=""
SPEC=""
IS_BASE=0
IS_PEAK=0
OPTS=""
DIR=""
SERVER=""
PROF_DIR=""
MODE=""

# Нештатный выход из скрипта
die()
{
    echo -e "$@" >& 2
    exit 1
}

# Обрабатываем аргументы, поданные скрипту
until [ -z "$1" ]
do
  case "$1" in
    "-comp") IS_COMP=1 ; IS_EXEC=0 ; IS_STAT=0 ;;
    "-exec") IS_COMP=0 ; IS_EXEC=1 ; IS_STAT=0 ;;
    "-stat") IS_COMP=0 ; IS_EXEC=0 ; IS_STAT=1 ;;

    "-suite")
      shift
      SUITE="$1"
      
      ;;

    "-spec")
      shift
      SPEC="$1"
      ;;

    "-base") IS_BASE=1 ; IS_PEAK=0 ;;
    "-peak") IS_BASE=0 ; IS_PEAK=1 ;;

    "-opt")
      shift
      OPTS="$1"
      ;;

    "-dir")
      shift
      DIR="$1"
      ;;

    "-server")
      shift
      SERVER="$1"
      ;;

    "-prof")
      shift
      PROF_DIR="$1"
      ;;
      
    *) die "invalid argument '$1'" ;;
  esac

  shift
done

# Проверяем корректность аргументов, поданных скрипту
[ $IS_COMP == 1 ] || [ $IS_EXEC == 1 ] || [ $IS_STAT == 1 ] || die "no <-comp|-exec|-stat> option"
[ "$SUITE" != "" ] || die "no parameter for -suite option"
[ "$SPEC" != "" ] || die "no parameter for -spec option"
[ $IS_BASE == 1 ] || [ $IS_PEAK == 1 ] || die "no <-base|-peak> option"
[ $IS_STAT == 0 ] || [ "$DIR" != "" ] || die "no parameter for -dir option in -stat mode"
[ "$SERVER" != "" ] || die "no parameter for -server option"
[ $IS_EXEC == 0 ] || [ "$PROF_DIR" != "" ] || die "no parameter for -prof option in -exec mode"

# Формируем аргументы для срипта
ARGS=""

if [ $IS_COMP == 1 ] || [ $IS_STAT == 1 ]
then
    ARGS=" -comp"
else
    ARGS=" -exec"
fi

if [ "$SUITE" != "" ]
then
    ARGS="$ARGS -suite $SUITE"
fi

if [ "$SPEC" != "" ]
then
    ARGS="$ARGS -run $SPEC"
fi

if [ $IS_BASE == 1 ]
then
    ARGS="$ARGS -base"
    MODE="base"
fi

if [ $IS_PEAK == 1 ]
then
    ARGS="$ARGS -peak"
    MODE="peak"
fi

if [ $IS_STAT == 1 ]
then
    OPTS="$OPTS --true=msu_print --lets=msu_test_name:$SPEC --lets=msu_dir_name:$DIR"
    ARGS="$ARGS -new -new-opt \"$OPTS\" -force -max-mem"
else
    if [ "$OPTS" == "" ]
    then 
        ARGS="$ARGS -old -force"
    else
        ARGS="$ARGS -old -old-opt \"$OPTS\" -force"
    fi
fi

# Запускаем срипт на специфической машине
DATA=`date +%Y%m%d%H%M%S`
CMP_STDOUT="cmp_stdout_$DATA"
CMP_RES=$(rsh $SERVER "cd $CURDIR; ./cmp.sh $ARGS &> $CMP_STDOUT; echo \$?")

if [ $CMP_RES == 1 ]
then
    echo "in $CURDIR/cmp.sh:" >& 2
    ERROR=`cat $CMP_STDOUT`
    REGEX=".* error[ :]\s*(.*)"
    if [[ $ERROR =~ $REGEX ]]
    then
        echo ${BASH_REMATCH[1]} >& 2
    else
        echo $ERROR >& 2
    fi
    exit 1
fi

# Обрабатываем результаты срипта
RES=""

if [ $IS_COMP == 1 ]
then
    RES=`cat ./work.$MODE.old/$SPEC.comp_time | 
         awk -F "_" '{ i++; s += $4 } END { if (i>0) print s; else print "error" }'`
fi

if [ $IS_EXEC == 1 ]
then
    RES=`cat ./work.$MODE.old/$SPEC.exec_time_ref | 
         awk -F "_" '{ i++; s += $4 } END { if (i>0) print s; else print "error" }'`

    # Получаем профили исполняемых процедур
    cd "work.$MODE.old"
    $CURDIR/make_prof.sh $SPEC &> $CMP_STDOUT
    if [ $? -ne 0 ]
    then
        echo "in $CURDIR/make_prof.sh:" >& 2
        cat $CMP_STDOUT >& 2
        pwd >& 2
        exit 1
    fi

    # Суммируем профили исполняемых процедур
    declare -A TIME
    declare -A NUM
    for prof in `ls exec.$SPEC/prof*.txt`
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
        echo "$proc $time" >> $PROF_DIR/$SPEC.txt
    done

    cd $CURDIR
fi

if [ $IS_STAT == 1 ]
then
    RES=`cat ./work.$MODE.new/$SPEC.mem | grep "max memory usage" |
         awk '{ if( s < $4 ) s = $4; } END { print s }'`
fi

# Печатаем результат
echo $RES

