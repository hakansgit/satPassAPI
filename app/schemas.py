
multiple_TLEs_schema = {
    "type": "object",
    "properties": {
        "sat_id": {
            "type": "array",
            "items": {
                "type": "number"
            }
        },
    },
    "required": ["sat_id"]
}

passes_for_multi_sat_schema = {
    "type": "object",
    "properties": {
        "sat_id": {
            "type": "array",
            "items": {
                "type": "number"
            }
        },
        "lat": {
            "type": "number"
        },
        "lon": {
            "type": "number"
        },
        "min_el": {
            "type": "number",
            "default": 100
        },
        "st_time": {
            "type": "string",
            "default": ""
        },
        "ed_time": {
            "type": "string",
            "default": ""
        },
        "days": {
            "type": "number",
            "default": 0
        },
        "sun_lit": {
            "type": "number",
            "default": 0
        },
    },
    "required": ["sat_id", "lat", "lon"]
}

passes_for_single_sat_schema = {
    "type": "object",
    "properties": {
        "lat": {
            "type": "number"
        },
        "lon": {
            "type": "number"
        },
        "min_el": {
            "type": "number",
            "default": 100
        },
        "st_time": {
            "type": "string",
            "default": ""
        },
        "ed_time": {
            "type": "string",
            "default": ""
        },
        "days": {
            "type": "number",
            "default": 0
        },
        "sun_lit": {
            "type": "number",
            "default": 0
        },
    },
    "required": ["lat", "lon"]
}
