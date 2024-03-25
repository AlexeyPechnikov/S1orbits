#!/usr/bin/env python3
# python3.11 ./dload.py . S1B RESORB 2024

import sys
import numpy as np
import requests
import pandas as pd
import re
import os
import glob
from datetime import datetime, timedelta
import zipfile
from io import BytesIO
import xmltodict

http_timeout = 30
# use simplified check, on client it could be more strict if needed
offset_start = timedelta(hours=1)
offset_end   = timedelta(hours=1)
# common parameters
base_url = 'https://step.esa.int/auxdata/orbits/Sentinel-1/{product}/{satellite}/{year}/{month:02}'

# Check if the number of command line arguments (excluding the script name) is exactly two
if len(sys.argv) != 5:
    print(f'Error: Expected 4 arguments, but received {len(sys.argv) - 1}.')
    print(f'Usage: python {sys.argv[0]} basedir satellite=S1A|S1B|... product=RESORB|POEORB date=Y|Y-m|Y-m-d')
    sys.exit(1)

basedir   = sys.argv[1]
satellite = sys.argv[2]
product   = sys.argv[3]
date      = sys.argv[4]

# # debug
# print(f"basedir: {basedir}")
# print(f"satellite: {satellite}")
# print(f"product: {product}")
# print(f"date: {date}")

def download_orbit(basedir, properties, base_url):
    #print (properties)
    # S1A_OPER_AUX_POEORB_OPOD_20240222T070809_V20240201T225942_20240203T005942.EOF.zip
    scene_parts = properties.orbit[:-8].split('_')
    time = scene_parts[5]
    start_time = scene_parts[6][1:]
    stop_time = scene_parts[7]
    #print ('time, start_time, stop_time', time, start_time, stop_time)
    start_time_dt = datetime.strptime(start_time, '%Y%m%dT%H%M%S')
    stop_time_dt = datetime.strptime(stop_time, '%Y%m%dT%H%M%S')
    interval = (stop_time_dt - start_time_dt)
    #print ('start_time_dt', start_time_dt, 'stop_time_dt', stop_time_dt, 'interval', interval)
    # 'RESORB' | 'POEORB'
    product = scene_parts[3]
    if product == 'POEORB':
        assert interval.days == 1
        # covers one day completely
        date_dts = [start_time_dt  + timedelta(days=1)]
    elif product == 'RESORB':
        assert interval.days in [0]
        # covers one or two days partially
        date_dts = [start_time_dt  + offset_start , stop_time_dt   - offset_end]
    dates = list(set([date_dt.strftime('%Y-%m-%d') for date_dt in date_dts]))
    
    #print ('dates', dates)
    assert len(dates) in [1, 2]

    for date in dates:
        dirname = os.path.join(satellite, date[:4], date[5:7], date[8:])
        orbitname = os.path.join(basedir, dirname, properties.orbit)
        #print ('dirname', dirname, 'orbitname', orbitname)

        # create the directory if needed
        os.makedirs(os.path.dirname(orbitname), exist_ok=True)

        # use the orbit files extension (.EOF or .zip) to check previous ones
        ext = os.path.splitext(orbitname)[1]

        # do not download RESORB orbits when POEORB orbit(s) available
        if product == 'RESORB':
            poeorbs = glob.glob('*POEORB*' + ext, root_dir=os.path.dirname(orbitname))
            #print ('poeorbs', poeorbs)
            if len(poeorbs) > 0:
                continue

        # do nothing when the file already exists
        if os.path.exists(orbitname) and os.path.getsize(orbitname) > 0:
            continue

        # download new orbit file into temporal file and rename after size check
        url = base_url.format(product=product, satellite=satellite,
                              year=start_time[:4], month=start_time[4:6]) +\
              '/' + properties.orbit
        print ('\t', url, '=>', dirname)
#         with requests.get(url, timeout=http_timeout) as response:
#             response.raise_for_status()
#             # truncate previously inclompletely downloaded or not processed file if needed
#             with open(orbitname + '.tmp', 'wb') as f:
#                 f.write(response.content)

        with requests.get(url, timeout=http_timeout) as response:
            response.raise_for_status()
            if zipfile.is_zipfile(BytesIO(response.content)):
                # open zip file from response content and extract only the specified 'properties.orbit'
                # sometimes, the archive inlcudes also directories structure with the same orbit file inside
                with zipfile.ZipFile(BytesIO(response.content), 'r') as zip_in:
                    # extract the filename without the zip extension
                    filename = os.path.splitext(properties.orbit)[0]
                    zip_files = zip_in.namelist()
                    if len(zip_files) == 0:
                        raise Exception('ERROR: Downloaded file is empty zip archive.')
                    if len(zip_files) > 1:
                        print ('NOTE: Downloaded zip archive includes multiple files.')
                    if filename in zip_files:
                        # extract specific file content
                        orbit_content = zip_in.read(filename)
                        #print('orbit_content', len(orbit_content))
                        # check XML validity
                        doc = xmltodict.parse(orbit_content)
                        # write the extracted content back to a new zip file
                        with zipfile.ZipFile(orbitname + '.tmp', 'w', zipfile.ZIP_DEFLATED) as zip_out:
                            zip_out.writestr(filename, orbit_content)
            else:
                raise Exception('ERROR: Downloaded file is not a valid zip archive.')
        # move the processed and validated file to the permanent place
        #if os.path.getsize(orbitname + '.tmp') == properties.size:
        if os.path.exists(orbitname + '.tmp'):
            os.rename(orbitname + '.tmp', orbitname)
        #else:
        #    raise Exception('ERROR: Downloaded orbits size differ from expected:',
        #                    os.path.getsize(orbitname + '.tmp'), properties.size)
        
        # cleanup - RESORB orbits should be removed when POEORB orbit(s) added
        if product == 'POEORB':
            resorbs = glob.glob('*RESORB*' + ext, root_dir=os.path.dirname(orbitname))
            #print ('resorbs', resorbs)
            for resorb in resorbs:
                fullname = os.path.join(os.path.dirname(orbitname), resorb)
                os.remove(fullname)

        # TODO: generate directory listing in README.md
        orbs = glob.glob('*ORB*' + ext, root_dir=os.path.dirname(orbitname))
        indexname = os.path.join(basedir, dirname, 'index.csv')
#         indexlines = []
#         for orb in orbs:
#             orbitpath = os.path.join(os.path.dirname(orbitname), orb)
#             size = os.path.getsize(orbitpath)
#             indexlines.append(f'{orb}\t{size}')
        with open(indexname + '.tmp', 'w') as f:
            f.write('\n'.join(sorted(orbs)))
        os.rename(indexname + '.tmp', indexname)

if len(date) == 4:
    year = date
    months = list(range(1, 12 + 1))
elif len(date) in [7, 10]:
    year = date[:4]
    months = [int(date[5:7])]
else:
    raise Exception(f'ERROR: date {date} should be an year, month, or day like "2014", "2014-01", "2014-01-01"')
print ('year', year, 'months', months)

# obtain monthly orbit lists
for month in months:
    url = base_url.format(product=product, satellite=satellite, year=year, month=month)
    print (url)
    try:
        # some orbit lists can be missed, for example, for S1B satellite in 2024
        with requests.get(url, timeout=http_timeout) as response:
            response.raise_for_status()
            lines = response.text.splitlines()
            #[print (line) for line in lines]
            pattern_orbit  = r'<a href="(S1\w_OPER_AUX_(POE|RES)ORB_OPOD_\d{8}T\d{6}_V\d{8}T\d{6}_\d{8}T\d{6}.EOF.zip)">.*</a> (\d{2}.+\d{2})\W+(\d+)'
            orbits = [(match.group(1), match.group(3), int(match.group(4))) for line in lines if (match := re.search(pattern_orbit, line))]
            orbits = pd.DataFrame(orbits, columns=['orbit','date','size']).dropna()
            for orbit in orbits.itertuples():
                try:
                    download_orbit(basedir, orbit, base_url)
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)
