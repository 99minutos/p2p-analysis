import requests
import urllib.parse


def geocode2(address, zipcode, locality):
    print('GOOGLE: {}'.format(address))
    url = "https://geocoding-private-qndxoltwga-uc.a.run.app/geocode"
    params = {
        "address": "{} {} {}".format(address, zipcode, locality),
        "country": "MEX",
    }
    response = requests.post(url, json=params)
    data = response.json()
    return {
        **data['location'],
        **data
    }


def geocode(address, zipcode, locality):
    try:
        # Set up the Geocoding url
        url = "https://api.deyde.com/deyde-ws/deydePlusJson"
        params = {
            "user": "MINUI6RB",
            "password": "JONAQV60",
            "productList": "mx,dom,cod,xy,xyg",
            "toNormalize": "{} {} {}".format(address, zipcode, locality)
        }

        print('DEYDE: {}'.format(params['toNormalize']))
        # Encode the parameters
        encoded_params = urllib.parse.urlencode(params)

        # Combine the URL and encoded parameters
        new_url = url + "?" + encoded_params

        response = requests.get(new_url)

        data = response.json()
        loc = data['deydePlusResult']

        location = {
            'lat': float(loc['coordYG']),
            'lng': float(loc['coordXG']),
            **loc
        }
        return location
    except Exception as e:
        return geocode2(address, zipcode, locality)
