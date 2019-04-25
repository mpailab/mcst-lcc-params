#!/bin/bash

MACHINE=$1
CPU=$2
SPEC=$3
PARAM="--true=msu_print --lets=msu_test_name:$SPEC --lets=msu_dir_name:/auto/bokov_g/msu/spec/stat/tmp_comp $4"
CMD="./cmp.sh -comp -peak -new -suite 2017r -run $SPEC -new-opt \"$PARAM\" -max-mem -force &> /dev/null"
PWD=`pwd`

if [ $CPU == "NONE" ]
then
    rsh $MACHINE "cd $PWD; $CMD"
else
    rsh $MACHINE "cd $PWD; taskset -c $CPU $CMD"
fi

MAX_MEM=`cat ./work.peak.new/$SPEC.mem | 
         awk '{ if( s < $4 ) s = $4; } END { print s }'`

echo $MAX_MEM

