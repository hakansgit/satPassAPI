from skyfield.api import Topos, load
from numpy import arange, insert, append
from datetime import datetime, timedelta
import dateutil.parser

import json

from utils import get_cardinal
from tle import satellites_byID
from settings import PASS_SETTINGS

ts = load.timescale()
eph = load('de421.bsp')


def getPasses(lat, lon, sat_id, min_el=100, st_time='',
              ed_time='', days=-1, sun_lit=0):
    """Returns satellite passes as events 
        0:rise, 1: culminate, 2:set, 
        -1:enter (enter into observation window), 
        3:exit (exit observation window)

    ``lat`` — latitude in decimal 
    ``lon`` — longitude in decimal
    ``sat_id`` — list of ids for the satellites to observe
    ``min_el`` — minimum elevation angle to detect pass events
    ``st_time`` — observation window start time in UTC iso string
    ``ed_time`` — observation window end time in UTC iso string
    ``sun_lit`` — (default=0) return passes where satellite is sun_lit
    """

    sat_id = [id for id in sat_id if id in satellites_byID]
    if len(sat_id) < 1:
        return []

    lat = str(lat) + ' N' if lat > 0 else str(abs(lat)) + ' S'
    lon = str(lon) + ' E' if lon > 0 else str(abs(lon)) + ' E'

    if min_el >= 90:
        min_el = PASS_SETTINGS['minElevation']

    if not st_time:
        t1 = ts.now()
    else:
        t1 = ts.from_datetime(dateutil.parser.isoparse(st_time))

    if not days:
        if not ed_time:
            days = PASS_SETTINGS['defaultDays']
            t2 = ts.utc(t1.utc_datetime() + timedelta(days=days))
        else:
            t2 = ts.from_datetime(dateutil.parser.isoparse(ed_time))
    else:
        t2 = ts.utc(t1.utc_datetime() + timedelta(days=days))

    if t1.tt > t2.tt:
        return -1

    observer = Topos(lat, lon)
    satellite = satellites_byID[sat_id[0]]
    difference = satellite - observer

    t_events, events = satellite.find_events(
        observer, t1, t2, altitude_degrees=min_el)

    if len(events) < 1:
        return[]

    # group events into complete passes
    pass_events = []

    # if first event not rise, add enter event
    # if last not event not set add exit event
    if events[0] > 0:
        events = insert(events, 0, -1)
        t_events = insert(t_events, 0, t1)
    if events[-1] < 2:
        events = append(events, 3)
        t_events = append(t_events, t2)

    prev_event = -1
    idx = 0
    while idx < len(events):
        pass_event = []
        while idx < len(events) and events[idx] >= prev_event:
            pass_event.append((t_events[idx], events[idx]))
            prev_event = events[idx]
            idx += 1
        pass_events.append(pass_event)
        prev_event = -1

    passes = []
    # for t, event in zip(t_events, events):
    for pass_event in pass_events:
        this_pass = []
        for t, event in pass_event:
            event_str = ('rise', 'culminate', 'set', 'exit', 'enter')[event]

            topocentric = difference.at(t)
            el, az, distance = topocentric.altaz()
            observation = {
                'time': str(t.utc_iso()),
                'event': event_str,
                'satellite': {
                    'name': satellite.name,
                    'id': satellite.model.satnum
                },
                'target': {
                    'az': az.degrees,
                    'el': el.degrees,
                    'dist': int(distance.m)
                },
                'sun_lit': int(satellite.at(t).is_sunlit(eph))
            }

            this_pass.append(observation)

        pass_sun_lit = int(any(observation['sun_lit'] for observation in this_pass))

        if (not sun_lit) or pass_sun_lit:
            passes.append({
                'pass': this_pass,
                'sun_lit': pass_sun_lit
            })

    return passes


def getSatelliteLatLong(sat_id, t0=None):
    if t0 is None:
        t = ts.now()
    else:
        t = ts.from_datetime(dateutil.parser.isoparse(t0))

    result = []
    for id in sat_id:
        sat = satellites_byID[id]
        subpoint = sat.at(t).subpoint()
        result.append({
            'name': sat.name,
            'id': sat.model.satnum,
            'lat': subpoint.latitude.degrees,
            'lon': subpoint.longitude.degrees,
            'alt': int(subpoint.elevation.m)
        })
    return result

# getPasses(1, 1, [44057], 5, '2020-09-11T22:42:30Z', '2020-09-12T20:29:29Z')
