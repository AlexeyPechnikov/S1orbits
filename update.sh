#!/bin/sh
set -e

for SATELLITE in S1A S1B
do
    for ORBIT in POEORB RESORB
    do
        for DATE in $(date "+%Y-%m") $(date -v-1m "+%Y-%m")
        do
            python3 ./dload.py . ${SATELLITE} ${ORBIT} ${DATE} &
        done
        wait
    done
done
