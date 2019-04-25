#!/bin/bash

MACHINE=$1
CPU=$2
SPEC=$3
PARAM=$4
DIR=$5

if [ -z "$DIR" ]
then
    DIR="$PARAM"
fi

if [ $CPU == "NONE" ]
then
    rsh $MACHINE "cd $DIR; ./cmp.sh -exec -peak -old -suite 2017r -run $SPEC &> /dev/null"
else
    rsh $MACHINE "cd $DIR; taskset -c $CPU ./cmp.sh -exec -peak -old -suite 2017r -run $SPEC &> /dev/null"
fi

EXEC_TIME=`cat ./work.peak.old/$SPEC.exec_time_ref | 
           awk -F "_" '{ i++; s += $4 } END { if (i>0) print s; else print "error" }'`

echo $EXEC_TIME

