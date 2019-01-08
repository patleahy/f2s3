import flickrapi
import json


def login(login_file):

    login_data = json.load(open(login_file))

    return flickrapi.FlickrAPI(
        login_data['FLICKR_API_KEY'],
        login_data['FLICKR_API_SECRET'],
        token = flickrapi.auth.FlickrAccessToken(
            login_data['FLICKR_AUTH_KEY'],
            login_data['FLICKR_AUTH_SECRET'],
            'read'))
