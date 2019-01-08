import flickrapi
from plflickr import login
import json
import dateutil.parser
from xml.etree import ElementTree
import os
from sys import argv, exc_info
import urllib.request
import pandas as pd


def main(login_file, output_path):

    flickr = login(login_file)

    licInfo = flickr.photos_licenses_getInfo().find('licenses')
    licenses = { lic.get('id') : { 'name' : lic.get('name'), 'url' : lic.get('url') }
                 for lic in licInfo }

    photos = flickr.walk(
        user_id = 'me',
        extras = 'url_o,url_m,date_taken,date_upload,geo,original_format,description,license')

    fields = ['id', 'title', 'url_o', 'url_m', 'datetaken', 'dateupload', 'originalformat']

    index = pd.DataFrame(columns=['path', 'format', 'has_orignal', 'has_medium', 'title'])
    index.index.name = 'id'

    for i, photo in enumerate(photos):
        info = {field : str(photo.get(field))
                for field in fields }
        info['description'] = photo.find('description').text
        info['is_public'] = int(photo.get('ispublic'))
        info['is_friend'] = int(photo.get('isfriend'))
        info['is_family'] = int(photo.get('isfamily'))

        id = photo.get('id')
        date_taken = dateutil.parser.parse(photo.get('datetaken'))

        file_prefix = '{0:%Y}/{0:%m}/{1}'.format(date_taken, id)
        path = os.path.join(output_path, file_prefix)
        filename = path + '.json'

        print('> {} {}'.format(i, file_prefix))

        if os.path.exists(filename):
            print('- {} {}'.format(i, file_prefix))
        else:
            license_id = photo.get('license')
            info['license'] = {
                'id' : license_id,
                'name' : licenses[license_id]['name'],
                'url' : licenses[license_id]['url'] }

            photoInfo = flickr.photos_getInfo(photo_id = id).find('photo')
            tags = photoInfo.find('tags')
            info['tags'] = [tag.text for tag in tags]

            locationInfo = photoInfo.find('location')
            if locationInfo:
                location  = { place.tag : place.text for place in locationInfo }
                for geo_field in ['latitude', 'longitude', 'accuracy']:
                    location[geo_field] = locationInfo.get(geo_field)
                info['location'] = location


            try:
                photoExif = flickr.photos_getExif(photo_id = id).find('photo')
                info['exif'] = {'{}:{}'.format(exif.get('tagspace'), exif.get('label')) :
                                exif.find('raw').text
                                for exif in photoExif}
            except:
                print('! {} {} getExif {}'.format(i, id, exc_info()[0]))

            write_json(i, info, filename)

        if info['originalformat'] != '':
            has_orignal = write_image(i, info['url_o'], path, 'o', info['originalformat'])
            has_medium = write_image(i, info['url_m'], path, 'm', info['originalformat'])
        else:
            has_orignal = False
            has_medium = False
            print('! {} {} originalformat={}'.format(i, id, info['originalformat']))

        index.loc[id] = {
            'path' : file_prefix,
            'format' : info['originalformat'],
            'has_orignal' : int(has_orignal),
            'has_medium' : int(has_medium),
            'title': info['title']}

        print('< {} {}'.format(i, file_prefix), flush=True)

    write_index(index, output_path)


def write_json(i, info, filename):
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    if os.path.exists(filename):
        status = '-'
    else:
        with open(filename, 'w') as file:
            file.write(json.dumps(info, indent=2))
            status = '+'

    print('{} {} {}'.format(status, i, filename))


def write_image(i, url, path, size, format):
    if not url.startswith('https://'):
        return False

    filename = '{}.{}.{}'.format(path, size, format)

    if os.path.exists(filename):
        status = '-'
    else:
        try:
            urllib.request.urlretrieve(url, filename)
            status = '+'
        except:
            status = '!'

    print('{} {} {} {}'.format(status, i, url, filename))
    return True


def write_index(index, output_path):
    index.to_csv(os.path.join(output_path, 'index.csv'))


if __name__ == '__main__':
    main(argv[1], argv[2])
