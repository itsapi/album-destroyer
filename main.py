from urllib import request
from PIL import Image
from io import BytesIO
from random import randint
from time import sleep


import convert_image
import lastfm
from console import *
from nbinput import NonBlockingInput


THUMBSIZE = 20


def get_image_from_url(url):
    return Image.open(BytesIO(request.urlopen(url).read()))


def display_image(y, x, diff):
    out = POS_STR(y - 1, x, CLS_END_LN) if y > 0 else ''

    for dy, row in list(diff.items())[::-1]:
        if not (0 <= y + dy < HEIGHT - 2):
            continue

        for dx, col in row.items():
            out += POS_STR(y + dy, x + 2 * dx, col)

    return out


def image_diff(image):
    diff = {}
    prev_row = {}
    for dy, row in enumerate(image[::-1]):
        diff[len(image) - dy - 1] = {}
        for dx, col in enumerate(row):
            if not prev_row.get(dx) == col:
                prev_row[dx] = diff[len(image) - dy - 1][dx] = col
    return diff


def scroll_image(image, offset):
    data = convert_image.get_escape_codes(image)
    diff = image_diff(data)

    print(HIDE_CUR + display_image(offset, int(WIDTH / 2 - len(image[0])), diff) + SHOW_CUR)

    return offset + 1


def main():
    albums = lastfm.get_tracks('ollsllo')
    offset = HEIGHT

    with NonBlockingInput() as nbi:
        while True:
            if offset >= HEIGHT:
                album = lastfm.get_album_info(albums[randint(0, len(albums)-1)])
                image = get_image_from_url(album[2])
                image.thumbnail((THUMBSIZE, THUMBSIZE), Image.ANTIALIAS)
                image = convert_image.convert_image(image)

                offset = 0 - len(image)

            offset = scroll_image(image, offset)

            char = str(nbi.char()).lower()

            sleep(0.2)


if __name__ == '__main__':
    try:
        print(CLS)
        main()
    finally:
        print(SHOW_CUR)
