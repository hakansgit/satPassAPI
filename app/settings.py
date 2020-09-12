_DEBUG = True

TLE_SETTINGS = {
    'url': 'http://www.celestrak.com/NORAD/elements/active.txt',
    'updateInterval': 5,
    'localFile': 'TLE.txt',
    'filter': r'^ONEWEB'
}

PASS_SETTINGS = {
    'minElevation': 10,
    'defaultDays': 2
}
