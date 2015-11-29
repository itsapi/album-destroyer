import sys
import os
import json
import time
import urllib.request

import config
from console import *


page = 0
def get_albums(user):
    global page
    page += 1

    url = 'http://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&api_key={}&format=json&user={}&page={}'.format(config.LASTFM_API_KEY, user, page)
    with urllib.request.urlopen(url) as f:
        result = f.read()

    data = json.loads(result.decode())['recenttracks']

    tracks = data['track']
    attr = data['@attr']

    albums_ = map(lambda t: t['album']['mbid'], tracks)

    albums = []
    for album in albums_:
        if album not in albums and album is not '':
            albums.append(album)

    return albums, attr


def load_n_albums(username):
    scrobbles_d = 'scrobbles'
    scrobbles_f = os.path.join('scrobbles', username + '.json')

    if not os.path.exists(scrobbles_d):
        os.mkdir(scrobbles_d)

    albums = None
    if os.path.isfile(scrobbles_f):
        with open(scrobbles_f, 'r') as f:
            data = json.load(f)

        date = data['date']
        if date + (24 * 60 * 60) > time.time():
            albums = data['albums']

    if not albums:
        print('Loading last.fm Scrobbles. ..' + BACK(), end='')
        albums, attr = get_albums(username)
        for page in range(min(50, int(attr['totalPages']))):
            print(':.' + LEFT(), end='')
            sys.stdout.flush()
            time.sleep(.1)
            albums += get_albums(username)[0]

        with open(scrobbles_f, 'w') as f:
            json.dump({'albums': albums, 'date': time.time()}, f)

    return albums


def get_album_info(mbid):

    url = 'http://ws.audioscrobbler.com/2.0/?method=album.getInfo&api_key={}&format=json&mbid={}'.format(config.LASTFM_API_KEY, mbid)
    with urllib.request.urlopen(url) as f:
        result = f.read()

    data = json.loads(result.decode())

    images = data['album']['image']
    smallest_size = 5
    smallest = None
    for image in images:
        try:
            size = ('small', 'medium', 'large', 'extralarge', 'mega').index(image['size'])
        except ValueError:
            size = 5

        if size < smallest_size and image['#text'] is not '':
            smallest_size = size
            smallest = image['#text']

    title = data['album']['name']
    artist = data['album']['artist']
    image = smallest

    tracks = data['album']['tracks']

    return {
        'title': title,
        'artist': artist,
        'image': image,
        'tracks': tracks
    }


if __name__ == '__main__':
    albums = get_tracks('ollsllo')
    print(get_album_info(albums[0]))
