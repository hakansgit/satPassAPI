# -*- coding: utf-8 -*-

from json.decoder import JSONDecodeError
from jsonschema.exceptions import ValidationError
from schemas import passes_for_multi_sat_schema
import json
import utils
from passes import getPasses

def passesPost(query):
    # validate the query against schema
    try:
        utils.DefaultValidatingDraft7Validator(passes_for_multi_sat_schema).validate(query)
    except ValidationError as e:
        return errorResponse(400, e.message)

    # calculate passes
    result = getPasses(query['lat'], query['lon'], query['sat_id'],
                       query['min_el'], query['st_time'], query['ed_time'],
                       query['days'], query['sun_lit'])
    if result == -1:
        return errorResponse(400, "Error in observation parameters")
    elif result == 0:
        return errorResponse(404, "No passes found")
    else:
        return response(200, result)

def passesGet(query):
    return response(200, passes_for_multi_sat_schema)

def errorResponse(statusCode, message):
    return response(statusCode, { "error" : message })

def response(statusCode, body):
    return {
        "statusCode" : statusCode,
        "body": json.dumps(body),
        "headers": {
            "Content-Type": "application/json",
        }
    }

paths = {
    "/api/passes" : {
        "POST": passesPost,
        "GET": passesGet,
    }
}

def lambda_handler(event, context):
    path = event.get('path')
    method = event.get('httpMethod')

    # parse request body as json
    try:
        body = json.loads(event.get('body'))
    except JSONDecodeError as e:
        return errorResponse(400, "Error decoding JSON request - " + e.msg)

    # check if path exists
    if path in paths.keys():
        #check if method is valid for this path
        if method in paths[path].keys():
            result = paths[path][method](body)
        else:
            result = errorResponse(400, f"Method \"{method}\" not supported on path \"{path}\"")
    else:
        result = errorResponse(404, f"Path \"{path}\" not found")

    return result
