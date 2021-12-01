import requests
from pprint import pprint

'''
    HELPERS
'''
def get_api_name(landing_page):
    try:
        api_response = requests.get(url = landing_page, params = {'f':'json'})
        json_api_response = api_response.json()
    except requests.ConnectionError as exception:
        return False

    return json_api_response["title"]

def get_routes(landing_page):
    routes = []
    url = landing_page+'/routes'

    try:
        api_response = requests.get(url = url)
        json_api_response = api_response.json()
    except requests.ConnectionError as exception:
        return False
        
    for route in json_api_response["links"]:
        if route["rel"] == "item":
            link = route["href"].split('/')
            routeId = link[-1]
            element = dict(href=route["href"], title=route["title"], id=routeId)
            routes.append(element)

    return routes
