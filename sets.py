import flickrapi
from plflickr import login
import json
from sys import argv
import pandas as pd
import os


def main(login_file, output_path):
    flickr = login(login_file)

    for i, photo_set in enumerate(flickr.walk_photosets()):
        set_id = id = photo_set.get('id')

        set_info = {
            'id' : set_id,
            'title' : photo_set.find('title').text,
            'description' : photo_set.find('description').text,
            'date_create' : photo_set.get('date_create'),
            'date_update' : photo_set.get('date_update'),
            'photo_ids': list(getPhotoSetList(flickr, set_id))
        }

        write_set(i, output_path, set_id, set_info)


def getPhotoSetList(flickr, set_id):
    print('? set {}'.format(set_id))
    return [photo.get('id') for photo in flickr.walk_set(set_id)]


def write_set(i, output_path, set_id, set_info):
    filename = os.path.join(output_path, 'sets', set_id + '.json')

    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    with open(filename, 'w') as file:
        file.write(json.dumps(set_info, indent=2))

    print('+ {} {} {}'.format(i, set_id, filename))


if __name__ == '__main__':
    main(argv[1], argv[2])
