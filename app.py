import json
import requests
import os
from pprint import pp, pprint
from helpers import get_routes, get_api_name, create_dir_if_not_exists, store_local_copy_of_routes

from flask import Flask, render_template, request, url_for
app = Flask(__name__)

API_BASE_URL = "https://routingsprint.skymantics.com"
API_NAME = get_api_name(API_BASE_URL)
DEFAULT_ZOOM = "10"
DEFAULT_CENTER = "[-118.246648,34.054343]"
TILESERVER_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
LOCAL_ROUTE_STORAGE = "./routes/"

@app.route('/')
def index():
    ROUTES = get_routes(API_BASE_URL, LOCAL_ROUTE_STORAGE)
    if not request.root_url:
        # this assumes that the 'index' view function handles the path '/'
        request.root_url = url_for('index', _external=True)
    return render_template(
        'index.html', 
        tileserver=TILESERVER_URL,
        routes=ROUTES,
        name=API_NAME,
        zoom=DEFAULT_ZOOM,
        center=DEFAULT_CENTER
    )

@app.route('/route')
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
    params = {
        'name': route_name,
        'waypoints':{ 'value': { 'type': 'Multipoint', 'coordinates':json.loads(waypoints)} }
    }

    # Optional params 
    if (request.args.get('max_height') != '' and request.args.get('max_height') != None):
        max_height_from_request = request.args.get('max_height')
        params['height'] =  max_height_from_request

    if (request.args.get('max_weight') != '' and request.args.get('max_weight') != None):
        max_weight_from_request = request.args.get('max_weight')
        params['weight'] =  max_weight_from_request

    if (request.args.get('preference') != '' or request.args.get('preference') != None):
        preference_from_request = request.args.get('preference')
        params['preference'] =  preference_from_request

    obstacles_from_request = json.loads(request.args.get('obstacles'))
    if len(obstacles_from_request['coordinates']) == 1 and len(obstacles_from_request['coordinates'][0][0]) > 2:
        params['obstacles'] =  { 'value': obstacles_from_request }

    route_def = { 'inputs': {} }
    route_def['inputs'] = params

    print(params)

    api_response = requests.post(url = URL, headers = {'Accept': 'application/geo+json', 'content-type': 'application/json'}, json = route_def)
    # extracting data in json format
    json_api_response = api_response.json()
    # Get features 
    json_fearures_list = json_api_response["features"]
    # Parsing to string
    features_list = json.dumps(json_fearures_list)

    # Save a local copy of the route
    if "links" in json_api_response:
        create_dir_if_not_exists(LOCAL_ROUTE_STORAGE)
        store_local_copy_of_routes(json_api_response, LOCAL_ROUTE_STORAGE)
    
    # Returning string
    return features_list

@app.route('/all')
def all_routes():
    json_routes_list = get_routes(API_BASE_URL, LOCAL_ROUTE_STORAGE)
    # Parsing to string
    routes_list = json.dumps(json_routes_list)
    # Returning string
    return routes_list

@app.route('/route/named')
def named_route():
    route_id = request.args.get('route_link')
    target_url = API_BASE_URL+'/routes/' + route_id
    
    try:
        # sending get request and saving the response as response object
        api_response = requests.get(url = target_url, headers = {'Accept': 'application/geo+json'})
        # extracting data in json format
        json_api_response = api_response.json()

        # Save a local copy of the route
        f = open(LOCAL_ROUTE_STORAGE + route_id + '.json', 'w+', encoding='utf8')
        json.dump(json_api_response, f, indent=4)
        f.close()

    except:
        # if network problem, try to load a local copy
        try:
            f = open(LOCAL_ROUTE_STORAGE + route_id + '.json', "r+")
            json_api_response = json.load(f)
            f.close()
        except requests.ConnectionError as exception:
            return ""

    # Get features 
    json_fearures_list = json_api_response["features"]
    # Parsing to string
    features_list = json.dumps(json_fearures_list)
    # Returning string
    return features_list
    
@app.route('/route/delete')
def delete_route():
    try:
        route_id = request.args.get('route_link')
        target_url = API_BASE_URL+'/routes/'+route_id
        # sending get request and saving the response as response object
        api_response = requests.delete(url = target_url)
        # extracting data in json format
        json_api_response = api_response.json()
        # try to delete a local copy, if exists
        try:
            os.remove(LOCAL_ROUTE_STORAGE + route_id + '.json')
        except:
            print("No local copy of ", route_id)
        # TODO: Improve the returned data
        return dict(result = 'OK')
    except requests.ConnectionError as exception:
        return dict(result = 'No Internet connection')

