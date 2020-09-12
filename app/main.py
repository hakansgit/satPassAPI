import logging
from flask import Flask, g, jsonify
from flask_cors import CORS, cross_origin
from flask_expects_json import expects_json
import markdown

from schemas import all_TLEs_schema  #, pass_schema
from tle import get_TLEs, update_TLEs


# Create an object named app with CORS
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

logging.basicConfig(filename='example.log',level=logging.DEBUG)

@app.route('/')
def docs():
    with open('README.md') as f:
        return markdown.markdown(f.read(), extensions=['fenced_code'])


@app.route('/api/tles')
@expects_json(all_TLEs_schema)
def allTLEs():
    query = g.data
    if "sat_id" not in query:
        query["sat_id"]=[]
    result = get_TLEs(query["sat_id"])
    return jsonify(result)

@app.route('/api/tles/<int:sat_id>')
def singleTLE(sat_id):
    result = get_TLEs([sat_id])
    return jsonify(result)


if __name__ == '__main__':
    # app.run(port=8000, debug=True)
    app.run(port=9000, debug=True)
