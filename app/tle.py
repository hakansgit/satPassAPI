import logging
import urllib.request
import os
import time
from itertools import islice
import re
import json

import settings
from utils import setInterval, chunker

TLEs = []

@setInterval(10)
def update_TLEs():
    global TLEs

    url = settings.TLE_URL
    logging.info(f"Retrieving TLE information from {url}")
    req = urllib.request.Request(url, method='GET')
    retrieved_lines = []
    with urllib.request.urlopen(req) as f:
        if f.status == 200:
            retrieved_lines = [line.decode().replace('\r\n', '').strip()
                               for line in list(f.readlines())]
        else:
            logging.error(f'Cannot retrieve TLE file: {f.status}: {f.reason}')

    # if you get an error page from ISP with a stupid 200 code
    if len(retrieved_lines) < 3 or retrieved_lines[0].startswith('<!'):
        logging.error(f'Cannot retrieve TLE file: {retrieved_lines[0]}')

        # if no TLEs in memory fall back to last local temp file
        if len(TLEs) < 3:
            with open(settings.TLE_local_file) as local:
                TLEs = json.load(local)
        return

    # filter retrieved lines to TLEs array and write to local temp file
    pattern = re.compile(settings.TLE_filter)

    new_TLEs = []
    for group in chunker(retrieved_lines, 3):
        if len(group) == 3 and pattern.match(group[0]):
            sat = {
                'name': group[0],
                'id': int(group[2].split()[1]),
                'line1': group[1],
                'line2': group[2]
            }
            new_TLEs.append(sat)
    TLEs = new_TLEs

    # write to local file
    with open(settings.TLE_local_file, 'w') as local:
        json.dump(TLEs, local, ensure_ascii=False, indent=4)
    logging.info(
        f'Retrieved {len(retrieved_lines)//3} TLEs from {url}, filtered {len(TLEs)} TLEs')


def get_TLEs(sat_id):
    """ Returns TLEs for satellites identified with id:<int> in sat_id array
    Returns all TLEs if sat_id is empty """
    if len(sat_id) > 0:
        return [tle for tle in TLEs if tle['id'] in sat_id]
    else:
        return TLEs



# update TLE data
# stop = update_TLEs()