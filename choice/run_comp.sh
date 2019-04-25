#!/bin/bash

MACHINE=$1
CPU=$2
SPEC=$3
PARAM=$4
PWD=`pwd`

if [ -z "$PARAM" ]
then
    CMD="./cmp.sh -comp -peak -old -suite 2017r -run $SPEC &> /dev/null"
else
    CMD="./cmp.sh -comp -peak -old -suite 2017r -run $SPEC -old-opt $PARAM &> /dev/null"
fi

if [ $CPU == "NONE" ]
then
    rsh $MACHINE "cd $PWD; $CMD"
else
    rsh $MACHINE "cd $PWD; taskset -c $CPU $CMD"
fi

COMP_TIME=`cat ./work.peak.old/$SPEC.comp_time | 
           awk -F "_" '{ i++; s += $4 } END { if (i>0) print s; else print "error" }'`

echo $COMP_TIME

