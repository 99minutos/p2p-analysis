import requests
import urllib.parse


def geocode(address, zipcode, locality):
    # Set up the Geocoding url
    url = "https://api.deyde.com/deyde-ws/deydePlusJson"
    params = {
        "user": "MINUI6RB",
        "password": "JONAQV60",
        "productList": "mx,dom,cod,xy,xyg",
        "toNormalize": "{} {} {}".format(address, zipcode, locality)
    }

    print('Geocoding: {}'.format(params['toNormalize']))
    # Encode the parameters
    encoded_params = urllib.parse.urlencode(params)

    # Combine the URL and encoded parameters
    new_url = url + "?" + encoded_params

    # Print the new URL
    print(new_url)

    response = requests.get(new_url)

    data = response.json()
    loc = data['deydePlusResult']

    location = {
        'lat': float(loc['coordYG']),
        'lng': float(loc['coordXG']),
        **loc
    }

    return location
