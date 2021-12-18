import os
import requests
import json
from pprint import pprint

'''
    HELPERS
'''
def get_api_name(landing_page):
    try:
        api_response = requests.get(url = landing_page, headers = {'Accept': 'application/geo+json'}, params = {'f':'json'})
        json_api_response = api_response.json()
    except requests.ConnectionError as exception:
        return ""

    if "title" in json_api_response: return json_api_response["title"]
    else: return "No title"

def get_routes(landing_page, local_route_storage):

    routes = []
    url = landing_page+'/routes'

    # GET /routes is not compulsary to implement
    try:
        api_response = requests.get(url = url, headers = {'Accept': 'application/geo+json'})
    except requests.ConnectionError as exception:
        return get_local_routes(local_route_storage)
    if api_response.status_code > 229:
        return get_local_routes(local_route_storage)
    try:
        json_api_response = api_response.json()
    except ValueError as e:
        return get_local_routes(local_route_storage)

    loaded_ids = []
    if "links" in json_api_response:
        for route in json_api_response["links"]:
            if route["rel"] == "item":
                link = route["href"].split('/')
                routeId = link[-1]
                element = dict(href=route["href"], title=route["title"], id=routeId)
                routes.append(element)
                loaded_ids.append(routeId)

    return routes

def get_local_routes(local_route_storage):

    routes = []
    # Add routes stored locally that were not provided by the server (possibly down)
    for item in os.listdir(local_route_storage):
        if os.path.isfile(os.path.join(local_route_storage, item)) and item.endswith('.json'):
            route_id = item.replace('.json', '')
            f = open(local_route_storage + item, "r+")
            route_content = json.load(f)
            f.close()
            element = dict(href=route_id, title=route_content["name"], id=route_id)
            routes.append(element)

    return routes
    
def create_dir_if_not_exists(path):
    if os.path.exists(path) == False:
        os.makedirs(path)

def store_local_copy_of_routes(validJsonResponse, path):
    for route in validJsonResponse["links"]:
        if route["rel"] == "self":
            link = route["href"].split('/')
            routeId = link[-1]
            f = open(path + routeId + '.json', 'w+', encoding='utf8')
            json.dump(validJsonResponse, f, indent=4)
            f.close()
