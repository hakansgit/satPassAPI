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


def getPasses(lat_, lon_, sat_id, min_el=100, st_time='',
              ed_time='', days=0, sun_lit=0):
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

    feedback = []

    if len(sat_id) < 1:
        sat_id = list(satellites_byID.keys())
    else:
        sat_id = [id for id in sat_id if id in satellites_byID]
        if len(sat_id) < 1:
            return []

    lat = str(lat_) + ' N' if lat_ > 0 else str(abs(lat_)) + ' S'
    lon = str(lon_) + ' E' if lon_ > 0 else str(abs(lon_)) + ' W'

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
            if t2 - t1 > PASS_SETTINGS['maxDays']:
                days = PASS_SETTINGS['maxDays']
                feedback.append(f"Maximum observation window is limited to {PASS_SETTINGS['maxDays']} days")
                t2 = ts.utc(t1.utc_datetime() + timedelta(days=days))
    else:
        if days > PASS_SETTINGS['maxDays']:
            days = PASS_SETTINGS['maxDays']
            feedback.append(f"Maximum observation window is limited to {PASS_SETTINGS['maxDays']} days")
        t2 = ts.utc(t1.utc_datetime() + timedelta(days=days))

    if t1.tt > t2.tt:
        return -1

    observer = Topos(lat, lon)

    total_pass_count = 0
    passes = []
    for sid in sat_id:
        satellite = satellites_byID[sid]
        difference = satellite - observer

        t_events, events = satellite.find_events(
            observer, t1, t2, altitude_degrees=min_el)

        if len(events) < 1:
            continue

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

        this_sat_passes = []
        # for t, event in zip(t_events, events):
        for pass_event in pass_events:
            this_pass = []
            for t, event in pass_event:
                event_str = ('rise', 'culminate', 'set',
                             'exit', 'enter')[event]

                topocentric = difference.at(t)
                el, az, distance = topocentric.altaz()
                observation = {
                    'time': str(t.utc_iso()),
                    'event': event_str,
                    'target': {
                        'az': az.degrees,
                        'el': el.degrees,
                        'dist': int(distance.m)
                    },
                    'sun_lit': int(satellite.at(t).is_sunlit(eph))
                }

                this_pass.append(observation)

            pass_sun_lit = int(
                any(observation['sun_lit'] for observation in this_pass))

            if (not sun_lit) or pass_sun_lit:
                this_sat_passes.append({
                    'pass_events': this_pass,
                    'sun_lit': pass_sun_lit
                })

        pass_count = len(this_sat_passes)
        passes.append({
            'name': satellite.name,
            'id': satellite.model.satnum,
            'count': pass_count,
            'passes': this_sat_passes
        })
        total_pass_count += pass_count
        if total_pass_count > PASS_SETTINGS['maxPasses']:
            feedback.append(f"Maximum number of passes is limited to {PASS_SETTINGS['maxPasses']} passes. Limit your observation settings")
            break

    result = {
        'observation': {
            'lat': lat_,
            'lon': lon_,
            'sat_ids': [sat_pass['id'] for sat_pass in passes],
            'min_el': min_el,
            'st_time': str(t1.utc_iso()),
            'ed_time': str(t2.utc_iso()),
            'days': t2.tt - t1.tt,
            'sun_lit': sun_lit
        },
        'total_passes': total_pass_count,
        'satellites': passes
    }
    if len(feedback) > 0:
        result['info'] = feedback
    return result


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

# getPasses(1, 1, [], 5, '2020-09-11T22:42:30Z', '2020-09-12T20:29:29Z')

# getPasses(1, 1, [44058, 44059, 44060], 25, "2020-09-12T22:10:01Z", "2020-09-14T21:30:08Z", sun_lit=0)

# {
#     "lat":1,
#     "lon":1,
#     "sat_id": [44058, 44059, 44060],
#     "min_el": 25,
#     "st_time": "2020-09-12T22:10:01Z",
#     "ed_time": "2020-09-14T21:30:08Z",
#     "sun_lit": 0
# }
