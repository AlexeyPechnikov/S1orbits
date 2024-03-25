#!/bin/bash
set -e

TODAY=$(date '+%Y')

for SATELLITE in S1A S1B
do
    for ORBIT in POEORB RESORB
    do
        for YEAR in $(seq 2014 "$TODAY")
        do
            python3 ./dload.py . ${SATELLITE} ${ORBIT} ${YEAR} &
        done
        wait
    done
done
