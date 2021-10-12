import json
import requests
from pprint import pp, pprint

from flask import Flask, render_template, request, url_for
app = Flask(__name__)

API_BASE_URL = 'https://dp21.skymantics.com'

DEFAULT_LIMIT = 20
TILESERVER_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'

@app.route('/')
def index():
    if not request.root_url:
        # this assumes that the 'index' view function handles the path '/'
        request.root_url = url_for('index', _external=True)
    return render_template(
        'index.html', 
        tileserver=TILESERVER_URL,

    )

@app.route('/route', defaults={

})
def get_route():
    if (request.args.get('waypoints') != '' or request.args.get('waypoints') != None):
        waypoints_from_request = request.args.get('waypoints')
    # Get the waypoints from the request
    waypoints = waypoints_from_request
    # Set the API resource url
    URL = API_BASE_URL+"/routes"
    PARAMS = {
        'waypoints':json.loads(waypoints),
    }
    # sending get request and saving the response as response object
    api_response = requests.post(url = URL, json = PARAMS)
    # extracting data in json format
    json_api_response = api_response.json()
    # Get features 
    json_fearures_list = json_api_response["features"]
    # Parsing to string
    features_list = json.dumps(json_fearures_list)
    # Returning string
    return features_list