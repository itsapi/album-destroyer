import config
import json
import urllib.request


page = 0
def get_tracks(user):
    global page
    page += 1

    url = 'http://ws.audioscrobbler.com/2.0/?method=user.getRecentTracks&api_key={}&format=json&user={}&page={}'.format(config.api_key, user, page)
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

    return albums


def get_album_info(mbid):

    url = 'http://ws.audioscrobbler.com/2.0/?method=album.getInfo&api_key={}&format=json&mbid={}'.format(config.api_key, mbid)
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

    return title, artist, image


if __name__ == '__main__':
    albums = get_tracks('ollsllo')
    print(get_album_info(albums[0]))
