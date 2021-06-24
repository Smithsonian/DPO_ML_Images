#!flask/bin/python
#
# Flask test app
#
from flask import Flask, jsonify, request
from flask import Response
from flask import render_template
import simplejson as json
import os, logging, sys, locale

app_ver = "0.1"

# logging.basicConfig(stream=sys.stderr)
logging.basicConfig(filename='app.log',
                    level=logging.DEBUG,
                    filemode='a',
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%y-%m-%d %H:%M:%S'
                    )
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

# Set locale for number format
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

# Import settings
# import settings

app = Flask(__name__)


# From http://flask.pocoo.org/docs/1.0/patterns/apierrors/
class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(404)
def page_not_found(e):
    logging.error(e)
    data = json.dumps({'error': "route not found"})
    return Response(data, mimetype='application/json'), 404


@app.errorhandler(500)
def page_not_found(e):
    logging.error(e)
    data = json.dumps({'error': "system error"})
    return Response(data, mimetype='application/json'), 500


@app.route('/', methods=['GET', 'POST'])
def home():
    """Homepage in HTML format"""
    return render_template('home.html')


@app.route('/results', methods=['GET', 'POST'])
def get_results():
    j = """[{"mid": "/m/0jbk",
    "name": "Animal",
    "score": 0.6201662421226501,
    "bounding_poly": [
        {"normalized_vertices": {
            "x": 0.39320603013038635,
            "y": 0.2360943704843521
        }},
        {"normalized_vertices": {
          "x": 0.6967532634735107,
          "y": 0.2360943704843521
        }},
        {"normalized_vertices": {
          "x": 0.6967532634735107,
          "y": 0.3839291036128998
        }},
        {"normalized_vertices": {
          "x": 0.39320603013038635,
          "y": 0.3839291036128998
        }}
        ]
    }
    ]"""
    p = json.loads(j)
    ## Instead of hard coding the json data, read from file using these lines:
    # with open('data/a19900709000cp03.json') as json_file:
    #     data = json.load(json_file)
    # p = json.loads(json_file)
    x = p[0]["bounding_poly"][1]["normalized_vertices"]["x"]
    y = p[0]["bounding_poly"][1]["normalized_vertices"]["y"]
    return render_template('results.html', x_value=x, y_value=y)


@app.route('/results_file', methods=['GET', 'POST'])
def get_resultsfile():
    # Instead of hard coding the json data, read from file
    import glob
    path = "data/*.jpg"
    from pathlib import Path
    for file in glob.glob(path):
        file_stem = Path(file).stem
        json_file = "{}/{}.json".format("data", file_stem)
        # print(file_stem)
        print(json_file)
        with open(json_file) as jsonfile:
            p = json.load(jsonfile)
            print(p)
        x = p["localized_object_annotations"][0]["bounding_poly"]["normalized_vertices"][0]["x"]
        y = p["localized_object_annotations"][0]["bounding_poly"]["normalized_vertices"][0]["y"]
        x_1 = p["localized_object_annotations"][0]["bounding_poly"]["normalized_vertices"][1]["x"]
        y_1 = p["localized_object_annotations"][0]["bounding_poly"]["normalized_vertices"][1]["y"]
        x_2 = p["localized_object_annotations"][0]["bounding_poly"]["normalized_vertices"][2]["x"]
        y_2 = p["localized_object_annotations"][0]["bounding_poly"]["normalized_vertices"][2]["y"]
        x_3 = p["localized_object_annotations"][0]["bounding_poly"]["normalized_vertices"][3]["x"]
        y_3 = p["localized_object_annotations"][0]["bounding_poly"]["normalized_vertices"][3]["y"]
        name = p["localized_object_annotations"][0]["name"]
        score = p["localized_object_annotations"][0]["score"]

    return render_template('results.html',name = name, score = score, x = x, y = y,x_1 = x_1, y_1 = y_1,
                           x_2 = x_2, y_2 = y_2, x_3 = x_3, y_3 = y_3, file = file )


if __name__ == '__main__':
    app.run()
