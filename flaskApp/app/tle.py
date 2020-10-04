import time
import logging
import urllib.request
# import time
import re
import json
from pathlib import Path
from skyfield.api import EarthSatellite

from settings import TLE_SETTINGS, _DEBUG
# from utils import setInterval
from utils import chunker

TLEs = []
TLEs_byID = {}

satellites = []
satellites_byID = {}

def prep_data():
    global TLEs
    global TLEs_byID
    global satellites
    global satellites_byID

    # print('prepping data')
    # print(len(TLEs))

    for tle in TLEs:
        satellite = EarthSatellite(tle['line1'], tle['line2'], tle['name'])
        satellites.append(satellite)
        tle['epoch'] = str(satellite.epoch.utc_iso())
    
    TLEs_byID = {sat['id']: sat for sat in TLEs}
    satellites_byID = {sat.model.satnum: sat for sat in satellites}

def update_TLEs(localOnly = False):
    global TLEs

    # print('updating TLEs')

    if localOnly and Path(TLE_SETTINGS['localFile']).is_file():
        with open(TLE_SETTINGS['localFile']) as local:
            TLEs = json.load(local)
            prep_data()
            return
        
    url = TLE_SETTINGS['url']
    logging.info(f"Retrieving TLE information from {url}")
    # print('downloading TLEs')

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
            with open(TLE_SETTINGS['localFile']) as local:
                TLEs = json.load(local)
                prep_data()
        return

    # filter retrieved lines to TLEs array and write to local temp file
    pattern = re.compile(TLE_SETTINGS['filter'])

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
    prep_data()

    # write to local file
    with open(TLE_SETTINGS['localFile'], 'w') as local:
        json.dump(TLEs, local, ensure_ascii=False, indent=4)
    logging.info(
        f'Retrieved {len(retrieved_lines)//3} TLEs from {url}, filtered {len(TLEs)} TLEs')


def get_TLEs(sat_id):
    """ Returns TLEs for satellites identified with id:<int> in sat_id array
    Returns all TLEs if sat_id is empty """
    if len(sat_id) > 0:
        return [TLEs_byID[int(id)] for id in sat_id if id in TLEs_byID]
    else:
        return TLEs

TLElastChecked = time.time()
def checkTLEs():
    global TLElastChecked
    now = time.time()
    if now - TLElastChecked > TLE_SETTINGS['updateInterval']:
        update_TLEs(localOnly = _DEBUG)
        TLElastChecked = time.time()

update_TLEs(localOnly = _DEBUG)

# @setInterval(TLE_SETTINGS['updateInterval'])
# def periodically_update_TLEs():
#     update_TLEs()

# # update TLE data
# if _DEBUG:
#     update_TLEs(localOnly = True)
# else:
#     stop = periodically_update_TLEs()