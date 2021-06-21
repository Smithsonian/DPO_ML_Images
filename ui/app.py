#!flask/bin/python
#
# Spatial API. Each route queries the PostGIS database.
#
from flask import Flask, jsonify, request
from flask import Response
from flask import render_template
#from flask import send_file
from flask import redirect, request, current_app
import simplejson as json
import os, logging, sys, locale
#import psycopg2, psycopg2.extras
#from uuid import UUID
#For parallel
#import multiprocessing as mp
#from functools import partial
#from functools import wraps
#import re
#from PIL import Image


app_ver = "0.1"



#logging.basicConfig(stream=sys.stderr)
logging.basicConfig(filename = 'app.log',
                level = logging.DEBUG,
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


#Set locale for number format
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


#Import settings
#import settings

app = Flask(__name__)



#From http://flask.pocoo.org/docs/1.0/patterns/apierrors/
class InvalidUsage(Exception):
    status_code = 400
    def __init__(self, message, status_code = None, payload=None):
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




@app.route('/', methods = ['GET', 'POST'])
def home():
    """Homepage in HTML format"""
    return render_template('home.html')



@app.route('/help', methods = ['GET', 'POST'])
def help():
    """Help page in HTML format"""
    return render_template('help.html')



# @app.route('/data_sources', methods = ['GET', 'POST'])
# def get_sources_html():
#     """Get the details of the data sources in HTML format."""
#     #API Key not needed
#     try:
#         conn = psycopg2.connect(host = settings.host, database = settings.database, user = settings.user, password = settings.password)
#     except psycopg2.Error as e:
#         logging.error(e)
#         raise InvalidUsage('System error', status_code = 500)
#     cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
#     #Check inputs
#     datasource_id = request.values.get('datasource_id')
#     logging.debug(datasource_id)
#     if datasource_id == None:
#         #Build query
#         cur.execute("SELECT *, TO_CHAR(no_features, '999,999,999,999') as no_feat, TO_CHAR(source_date::date, 'dd Mon yyyy') as date_f FROM data_sources WHERE is_online = 't' ORDER BY datasource_id ASC")
#         logging.debug(cur.query)
#         data = cur.fetchall()
#         summary = sum(row['no_features'] for row in data)
#         summary = locale.format("%d", summary, grouping=True)
#     else:
#         cur.execute("SELECT *, TO_CHAR(no_features, '999,999,999,999') as no_feat, TO_CHAR(source_date::date, 'dd Mon yyyy') as date_f FROM data_sources WHERE is_online = 't' AND datasource_id = %(datasource_id)s", {'datasource_id': datasource_id})
#         logging.debug(cur.query)
#         data = cur.fetchall()
#         summary = None
#     cur.close()
#     conn.close()
#     results = {}
#     results = data
j = """[{"mid": "/m/0jbk",
    "name": "Animal",
    "score": 0.6201662421226501,
    "bounding_poly": {
        "normalized_vertices": {
            "x": 0.39320603013038635,
            "y": 0.2360943704843521
        },
        "normalized_vertices": {
          "x": 0.6967532634735107,
          "y": 0.2360943704843521
        },
        "normalized_vertices": {
          "x": 0.6967532634735107,
          "y": 0.3839291036128998
        },
        "normalized_vertices": {
          "x": 0.39320603013038635,
          "y": 0.3839291036128998
        }
    }
    }
]"""

p = json.loads(j)
print(p[0]["bounding_poly"])
#     return render_template('data_sources.html', data = results, summary = summary)




# @app.route('/details', methods = ['GET', 'POST'])
# def get_details_html():
#     """Get the details of the row from a data source in HTML format."""
#     #API Key not needed
#     try:
#         conn = psycopg2.connect(host = settings.host, database = settings.database, user = settings.user, password = settings.password)
#     except psycopg2.Error as e:
#         logging.error(e)
#         raise InvalidUsage('System error', status_code = 500)
#     cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
#     #Check inputs
#     datasource_id = request.values.get('datasource_id')
#     speciessource = request.values.get('speciessource')
#     if datasource_id == None and speciessource == None:
#         raise InvalidUsage('datasource_id and speciessource missing', status_code = 400)
#     uid = request.values.get('id')
#     if uid == None:
#         raise InvalidUsage('id missing', status_code = 400)
#     if datasource_id != None:
#         logging.debug(datasource_id)
#         cur.execute("SELECT * FROM data_sources WHERE datasource_id = %(datasource_id)s", {'datasource_id': datasource_id})
#         logging.debug(cur.query)
#         datasource = cur.fetchone()
#         cur.execute("SELECT %(datasource)s as data_source, * FROM {} WHERE uid = %(uid)s".format(datasource_id), {'uid': uid, 'datasource': "{} ({})".format(datasource['source_title'], datasource['source_url'])})
#         data = cur.fetchone()
#     elif speciessource != None:
#         logging.debug(speciessource)
#         if speciessource == "gbiftaxonomy":
#             cur.execute("SELECT * FROM gbif_vernacularnames WHERE taxonID = %(uid)s", {'uid': uid})
#             logging.debug(cur.query)
#             data = cur.fetchone()
#     logging.info(cur.query)
#     cur.close()
#     conn.close()
#     return render_template('details.html', data = data)





if __name__ == '__main__':
    app.run()
    # app.run(host = '0.0.0.0', debug = False)
    # from optparse import OptionParser
    # oparser = OptionParser()
    # oparser.add_option('-d', '--debug', action='store_true', default=False)
    # opts, args = oparser.parse_args()
    # app.debug = opts.debug
    # app.run(debug = True)
