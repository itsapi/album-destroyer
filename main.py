from urllib import request
from PIL import Image
from io import BytesIO
from random import randint
from time import sleep

import convert_image
import lastfm
from console import *


THUMBSIZE = 20

def get_image_from_url(url):
    return Image.open(BytesIO(request.urlopen(url).read()))

def display_image(y, x, image):
    out = POS_STR(y - 1, x, CLS_END_LN) if y > 0 else ''
    for dy, row in enumerate(image[::-1]):
        if (0 < y + len(image) - dy < HEIGHT - 1):
            out += POS_STR(y + len(image) - dy - 1, x, ''.join(row))
    return out


def scroll_image(image, interval=0.2):
    data = convert_image.get_escape_codes(image)
    y = 0 - len(image)
    print(HIDE_CUR + CLS)
    while y < HEIGHT:
        y += 1
        print(display_image(y, int(WIDTH / 2 - len(image[0])), data))
        sleep(interval)
    print(SHOW_CUR)

def main():
    albums = lastfm.get_tracks('ollsllo')

    album = lastfm.get_album_info(albums[randint(0, len(albums)-1)])

    image = get_image_from_url(album[2])
    image.thumbnail((THUMBSIZE, THUMBSIZE), Image.ANTIALIAS)
    scroll_image(convert_image.convert_image(image))

if __name__ == '__main__':
    main()
