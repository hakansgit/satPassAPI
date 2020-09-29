import logging
from flask import Flask, g, jsonify, abort
from flask_cors import CORS, cross_origin
from flask_expects_json import expects_json
import markdown

from schemas import multiple_TLEs_schema, passes_for_multi_sat_schema, passes_for_single_sat_schema
from tle import get_TLEs, checkTLEs
from passes import getPasses

# Create an object named app with CORS
app = Flask(__name__)
cors = CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_HEADERS'] = ['Content-Type', 'Authorization']
app.config['CORS_AUTOMATIC_OPTIONS'] = True

logging.basicConfig(filename='example.log', level=logging.DEBUG)

@app.before_request
def checkTLEage():
    checkTLEs()

@app.route('/')
def docs():
    with open('app/README.md') as f:
        return markdown.markdown(f.read(), extensions=['fenced_code'])


@app.route('/api/all_tles')
def allTLEs():
    result = get_TLEs([])
    return jsonify(result)


@app.route('/api/tles', methods=['GET', 'POST'])
@expects_json(multiple_TLEs_schema)
def multiple_TLEs():
    query = g.data
    if 'sat_id' not in query or len(query['sat_id']) < 1:
        abort(400)
    result = get_TLEs(query['sat_id'])
    if len(result) < 1:
        abort(404)
    return jsonify(result)


@app.route('/api/tles/<int:sat_id>')
def singleTLE(sat_id):
    result = get_TLEs([sat_id])
    if len(result) < 1:
        abort(404)
    return jsonify(result)


@app.route('/api/all_passes', methods=['GET', 'POST'])
@expects_json(passes_for_single_sat_schema, fill_defaults=True)
def allSatPass():
    query = g.data
    # print(query)
    result = getPasses(query['lat'], query['lon'], [],
                       query['min_el'], query['st_time'], query['ed_time'],
                       query['days'], query['sun_lit'])
    if result == -1:
        abort(400)
    if len(result) < 1:
        # print('yok canim')
        abort(404)
    return jsonify(result)
 

@app.route('/api/passes', methods=['GET', 'POST'])
@expects_json(passes_for_multi_sat_schema, fill_defaults=True)
def multiSatPass():
    query = g.data
    if len(query['sat_id']) < 1:
        abort(400, 'No satellite ID was specified')
    result = getPasses(query['lat'], query['lon'], query['sat_id'],
                       query['min_el'], query['st_time'], query['ed_time'],
                       query['days'], query['sun_lit'])
    if result == -1:
        abort(400)
    if len(result) < 1:
        abort(404)
    return jsonify(result)

@app.route('/api/passes/<int:sat_id>', methods=['GET', 'POST'])
@expects_json(passes_for_single_sat_schema, fill_defaults=True)
def singleSatPass(sat_id):
    query = g.data
    result = getPasses(query['lat'], query['lon'], [sat_id],
                       query['min_el'], query['st_time'], query['ed_time'],
                       query['days'], query['sun_lit'])
    if result == -1:
        abort(400)
    if len(result) < 1:
        abort(404)
    return jsonify(result)


if __name__ == '__main__':
    # app.run(port=8000, debug=True)
    app.run('0.0.0.0', port=80, debug=True)
    # app.run(port=9000, debug=True)
