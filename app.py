import json
import requests
from pprint import pp, pprint
from helpers import get_routes

from flask import Flask, render_template, request, url_for
app = Flask(__name__)

API_BASE_URL = 'https://dp21.skymantics.com'
ROUTES = get_routes(API_BASE_URL)
DEFAULT_LIMIT = 20
TILESERVER_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
pprint(ROUTES)
@app.route('/')
def index():
    if not request.root_url:
        # this assumes that the 'index' view function handles the path '/'
        request.root_url = url_for('index', _external=True)
    return render_template(
        'index.html', 
        tileserver=TILESERVER_URL,
        routes=ROUTES
    )

@app.route('/route', defaults={

})
def get_route():
    if (request.args.get('waypoints') != '' or request.args.get('waypoints') != None):
        waypoints_from_request = request.args.get('waypoints')
    else:
        waypoints_from_request = None
    if (request.args.get('route_name') != '' or request.args.get('route_name') != None):
        route_name_from_request = request.args.get('route_name')
    else:
        route_name_from_request = None
    # Get the waypoints from the request
    waypoints = waypoints_from_request
    # Get the route name from the request
    route_name = route_name_from_request
    # Set the API resource url
    URL = API_BASE_URL+"/routes"
    PARAMS = {
        'waypoints':json.loads(waypoints),
        'name': route_name
    }
    # sending get request and saving the response as response object
    api_response = requests.post(url = URL, json = PARAMS)
    # extracting data in json format
    json_api_response = api_response.json()
    # Get features 
    pprint(json_api_response)
    json_fearures_list = json_api_response["features"]
    # Parsing to string
    features_list = json.dumps(json_fearures_list)
    # Returning string
    return features_list

@app.route('/named_route')
def get_routes():
    json_routes_list = get_routes(API_BASE_URL)
    # Parsing to string
    routes_list = json.dumps(json_routes_list)
    # Returning string
    return routes_list

@app.route('/route/named')
def named_route():
    route_id = request.args.get('route_link')
    target_url = API_BASE_URL+'/rimac/routes/'+route_id
    # sending get request and saving the response as response object
    api_response = requests.get(url = target_url)
    # extracting data in json format
    json_api_response = api_response.json()
    # Get features 
    pprint(json_api_response)
    json_fearures_list = json_api_response["features"]
    # Parsing to string
    features_list = json.dumps(json_fearures_list)
    # Returning string
    return features_list
    
