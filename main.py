import urllib.request
from PIL import Image
from io import BytesIO
from random import randint

from convert_image import convert_image
import lastfm


THUMBSIZE = 20

def get_image_from_url(url):
    return Image.open(BytesIO(urllib.request.urlopen(url).read()))

def main():
    albums = lastfm.get_tracks('ollsllo')

    while True:
        album = lastfm.get_album_info(albums[randint(0, len(albums)-1)])

        image = get_image_from_url(album[2])
        image.thumbnail((THUMBSIZE, THUMBSIZE), Image.ANTIALIAS)
        print(convert_image(image))
        input()
        print(album)

if __name__ == '__main__':
    main()
