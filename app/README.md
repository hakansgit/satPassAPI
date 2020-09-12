# satPassAPI

API to query satellite passes over a location and obtain satellite TLE

## Endpoints

### `Get All TLEs`

*Get TLE data for all avaialable satellites*

URL : `/api/all_tles/`

Method : `GET`

#### **Success Response**

Code : `200 OK`

example:
```json
{
    "tles": [
        ...,
        {
            "sat_id": 25544,
            "sat_name": "ISS (ZARYA)",
            "line1": "1 25544U 98067A   20255.60890557  .00025955  00000-0  47833-3 0  9998",
            "line2": "2 25544  51.6443 280.7958 0000764 115.7723  29.7792 15.48963765245413" 
        },
        ...
    ]
}
```


### `Get Multiple TLEs`

*Get TLE data for all avaialable satellites or selected satellites*

URL : `/api/tles/`

Method : `GET`

**Data**: (required) Limits API Response to IDs listed in the data
```json
{
    "sat_id": [...]
}
```


#### **Success Response**

Code : `200 OK`

example:
```json
{
    "tles": [
        ...,
        {
            "sat_id": 25544,
            "sat_name": "ISS (ZARYA)",
            "line1": "1 25544U 98067A   20255.60890557  .00025955  00000-0  47833-3 0  9998",
            "line2": "2 25544  51.6443 280.7958 0000764 115.7723  29.7792 15.48963765245413" 
        },
        ...
    ]
}
```

### `Get TLE by ID`

*Get TLE data for a single satellite using satellite NORAD ID number*

**URL** : `/api/tles/:id/`

**URL Parameters** : `id=[integer]` where `id` is the NORAD ID of the satellite.

**Method** : `GET`

#### **Success Response**

Code : `200 OK`

example:
```json
{
    "tles": [
        {
            "id": 25544,
            "name": "ISS (ZARYA)",
            "line1": "1 25544U 98067A   20255.60890557  .00025955  00000-0  47833-3 0  9998",
            "line2": "2 25544  51.6443 280.7958 0000764 115.7723  29.7792 15.48963765245413" 
        }
    ]
}
```

#### Notes
Result is returned in a single element array

### `Get passes for multiple satellites`

*Get pass informaiton for all avaialable satellites or selected satellites*

URL : `/api/passes/`

Method : `GET`

**Data**: Omit sat_id to return passes for all satellites
```json
{
    "sat_id": [...],        // optional: list of satellites to observe
    "lat": 38.9072,         // required: observer's latitude 
    "lon": -77.0369,        // required: observer's longitude
}
```

#### **Success Response**

Code : `200 OK`

example:
```json
{
    "passes": [
        {
            "sat_id": 25544,
            "sat_name": "ISS (ZARYA)",
            "visible": false,
            "rise": {
                "alt": "10.00",
                "az": "317.05",
                "az_octant": "NW",
                "utc_datetime": "2020-06-02 05:22:20.959562+00:00",
                "utc_timestamp": 1591075340,
                "is_sunlit": false,
                "visible": false
            },
            "culmination": {
                "alt": "79.94",
                "az": "44.48",
                "az_octant": "NE",
                "utc_datetime": "2020-06-02 05:25:44.705872+00:00",
                "utc_timestamp": 1591075544,
                "is_sunlit": false,
                "visible": false
            },
            "set": {
                "alt": "10.00",
                "az": "130.38",
                "az_octant": "SE",
                "utc_datetime": "2020-06-02 05:29:10.634226+00:00",
                "utc_timestamp": 1591075750,
                "is_sunlit": false,
                "visible": false
            },
        }
    ]
}
```