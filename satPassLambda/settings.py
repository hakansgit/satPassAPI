_DEBUG = False


TLE_SETTINGS = {
    'url': 'http://www.celestrak.com/NORAD/elements/active.txt',
    'updateInterval': 21600,
    'localFile': 'TLE.txt',
    'filter': r'^ONEWEB'
}

PASS_SETTINGS = {
    'minElevation': 10,
    'defaultDays': 2,
    'maxDays': 5,
    'maxPasses': 10
}
