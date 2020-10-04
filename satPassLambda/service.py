# -*- coding: utf-8 -*-

from jsonschema.exceptions import ValidationError
from schemas import passes_for_multi_sat_schema
import json
import utils
from passes import getPasses

def passes(query):
    try:
        # jsonValidate(instance=query, schema=passes_for_multi_sat_schema)
        utils.DefaultValidatingDraft7Validator(passes_for_multi_sat_schema).validate(query)
    except ValidationError as e:
        return errorResponse(400, e.message)

    result = getPasses(query['lat'], query['lon'], query['sat_id'],
                       query['min_el'], query['st_time'], query['ed_time'],
                       query['days'], query['sun_lit'])
    if result == -1:
        return errorResponse(400, "Error in observation parameters")
    elif result == 0:
        return errorResponse(404, "No passes found")
    else:
        return json.dumps(result)

paths = {
    "/api/passes" : {
        "POST": passes
    }
}

def handler(event, context):
    path = event.get('path')
    method = event.get('httpMethod')
    body = json.loads(event.get('body'))

    result = paths[path][method](body)
   
    return result
        
def errorResponse(statusCode, message):
    return {
        "statusCode" : statusCode,
        "body": json.dumps({ "error" : message }),
        "headers": {
            "Content-Type": "application/json",
        }
    }
