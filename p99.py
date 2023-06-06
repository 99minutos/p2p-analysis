from time import sleep

import mapbox
import geojson
import requests
from bson import ObjectId

from process import mongo

# Set your Mapbox access token
access_token = 'YOUR_MAPBOX_ACCESS_TOKEN'
db = mongo['p2p']['p99_network_v2']
shipments_db = mongo['p2p']['analysis']

# Initialize Mapbox client
service = mapbox.Directions(access_token=access_token)


def save_p99_to_mongo(p99_data):
    # Insert the p99 data into the MongoDB collection
    db.insert_one(p99_data)


def generate_isochrone(lat, lng, time=10, resolution=100, profile='driving'):
    # Set your Mapbox access token
    access_token = 'pk.eyJ1IjoiOTltaW51dG9zIiwiYSI6ImNsaWttbmk4YTA4cXUzZHFzbnEycmltZTkifQ.voo7RbrWJUg691lAHb-SGw'

    # Set the profile for the isochrone request
    profile = 'mapbox/{}'.format(profile)  # Example: driving

    # Set the coordinates for the center point
    coordinates = '{},{}'.format(lng, lat)  # Example: longitude,latitude

    # Set the parameter for isochrone contour (minutes or meters)
    contours_param = 'contours_minutes'  # Example: contours_minutes or contours_meters

    # Set the value for the isochrone contour parameter
    contours_value = time  # Example: 10 minutes or 1000 meters

    # Construct the API URL
    url = f'https://api.mapbox.com/isochrone/v1/{profile}/{coordinates}?{contours_param}={contours_value}&access_token={access_token}&polygons=true'

    # Send a GET request to the API endpoint
    response = requests.get(url)
    sleep(0.1)
    # Check the response status code
    if response.status_code == 200:
        # Print the API response data
        data = response.json()
        return data
    else:
        raise Exception('not geojson')


def crawl_p99_network():
    import requests

    # Set the initial URL for the API endpoint
    initial_url = "https://royal-antwerp-ud4taa7gptqe.vapor-farm-e1.com/api/v1/99minutes/apiV3/points99?filter[is_active]=1&pageSize=50&page=1"
    # Initialize an empty list to store the results
    results = []

    # Start the pagination loop
    while initial_url:
        # Send a GET request to the current URL
        response = requests.get(initial_url)
        print('crawl_p99_network: {}'.format(initial_url))
        # Parse the response as JSON
        data = response.json()

        # Extract the results from the current page and add them to the list
        p99_list = data['data']

        for p99 in p99_list:
            if p99['description'] is None:
                continue
            print('p99: {}'.format(p99['description']))
            p99['isochrone_walk'] = generate_isochrone(
                p99['latitude'], p99['longitude'], time=7, resolution=100, profile='walking')

            save_p99_to_mongo(p99)

        # Check if there is a next page
        if 'next' in data:
            # Set the next URL for the next iteration
            initial_url = data['next']
            # initial_url = None
        else:
            # If there is no next URL, end the pagination loop
            initial_url = None

    # Process the final results
    for result in results:
        # Do something with each result
        print(result)

    print('Pagination complete.')


def belongs_to_p99(shipment):
    query = {
        'isochrone_walk.features.geometry': {
            '$geoIntersects': {
                '$geometry': {
                    'type': 'Point',
                    'coordinates': [shipment['lng'], shipment['lat']]
                }
            }
        }
    }

    has_p99 = db.find(query, {'locationId': 1})
    p99_list = list(has_p99)

    if len(p99_list) == 0:
        return None

    result = shipments_db.update_one({
        '_id': ObjectId(shipment['_id'])
    }, {
        '$set': {
            'p99': p99_list,
            'elected_p99': p99_list[0]['locationId']
        }
    })

    return result


if __name__ == '__main__':
    crawl_p99_network()
