import urllib.request
from skyfield.api import EarthSatellite

from settings import TLE_SETTINGS
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

    for tle in TLEs:
        satellite = EarthSatellite(tle['line1'], tle['line2'], tle['name'])
        satellites.append(satellite)
        tle['epoch'] = str(satellite.epoch.utc_iso())
    
    TLEs_byID = {sat['id']: sat for sat in TLEs}
    satellites_byID = {sat.model.satnum: sat for sat in satellites}

def update_TLEs():
    global TLEs

    url = TLE_SETTINGS['url']

    req = urllib.request.Request(url, method='GET')
    retrieved_lines = []
    with urllib.request.urlopen(req) as f:
        if f.status == 200:
            retrieved_lines = [line.decode().replace('\r\n', '').strip()
                               for line in list(f.readlines())]
        else:
            raise Exception("Error downloading TLE file")

    new_TLEs = []
    for group in chunker(retrieved_lines, 3):
        sat = {
            'name': group[0],
            'id': int(group[2].split()[1]),
            'line1': group[1],
            'line2': group[2]
        }
        new_TLEs.append(sat)
    TLEs = new_TLEs
    prep_data()

update_TLEs()