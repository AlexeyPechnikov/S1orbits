#!/bin/sh
set -e

for SATELLITE in S1A S1B
do
    for ORBIT in POEORB RESORB
    do
        for YEAR in $(seq 2014 2024)
        do
            python3 ./dload.py . ${SATELLITE} ${ORBIT} ${YEAR} &
        done
        wait
    done
done
