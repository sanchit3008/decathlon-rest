from bson import json_util
from flask import jsonify
import json

def parse_json(data):
    return json.loads(json_util.dumps(data))

def createJsonResponse(parsedJson):
    return jsonify(parse_json(parsedJson))