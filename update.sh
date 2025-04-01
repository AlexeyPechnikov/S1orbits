#!/bin/bash
#set -e

# determine OS and execute the respective date commands
if [[ "$OSTYPE" == "darwin"* ]]
then
    MONTHS="$(date '+%Y-%m') $(date -v-1m '+%Y-%m')"
else
    MONTHS="$(date '+%Y-%m') $(date '+%Y-%m' --date='1 month ago')"
fi

for SATELLITE in S1A S1B S1C
do
    for ORBIT in POEORB RESORB
    do
        for MONTH in $MONTHS
        do
            #python3 ./dload.py . ${SATELLITE} ${ORBIT} ${MONTH} &
            python3 ./dload.py . ${SATELLITE} ${ORBIT} ${MONTH} || echo "ERR: ${SATELLITE} ${ORBIT} ${MONTH}" &
        done
        wait
    done
done
