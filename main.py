from urllib import request
from PIL import Image
from io import BytesIO
from random import randint
from time import sleep
from difflib import SequenceMatcher as SM

import convert_image
import lastfm
from youtube import youtube_search
from play import get_and_play
from console import *
from nbinput import NonBlockingInput


THUMBSIZE = 20


class Input:
    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.value = ''

    def add(self, char):
        print(POS_STR(self.y, self.x + len(self.value), char), end='')
        self.value += char

    def remove(self):
        print(POS_STR(self.y, self.x + len(self.value) - 1, ' '), end='')
        self.value = self.value[:-1]

    def set(self, value):
        print(POS_STR(self.y, self.x, ' ' * len(self.value)), end='')
        print(POS_STR(self.y, self.x, value), end='')
        self.value = value


def play_music(album):
    found = False
    for track in album['tracks']:
        videos = youtube_search(album['title'], album['artist'], track)

        for video in videos:
            print(video[0])
            if get_and_play(video[1]):
                found = True
                break

        if found: break


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

    answer = Input(HEIGHT - 1, 0)

    def checkscore(album):
        titleR = SM(None, answer.value.lower(), album['title'].lower()).ratio()
        artistR = SM(None, answer.value.lower(), album['artist'].lower()).ratio()

        if titleR > .8 or artistR > .8:
            outcome = HEIGHT
            print(CLS + 'Correct answer!')
        else:
            print(CLS + 'Incorrect answer :-(')


    with NonBlockingInput() as nbi:
        while True:
            if offset >= HEIGHT:
                print(CLS)

                mbid = albums[randint(0, len(albums)-1)]
                album = lastfm.get_album_info(mbid)

                play_music(album)

                image = get_image_from_url(album['image'])
                image.thumbnail((THUMBSIZE, THUMBSIZE), Image.ANTIALIAS)
                image = convert_image.convert_image(image)

                offset = 0 - len(image)

            offset = scroll_image(image, offset)

            char = nbi.char()

            if char == '\b':
                answer.remove()
            elif char == '\n':
                checkscore(album)
                answer.set('')
            elif char:
                answer.add(char)

            sleep(0.2)


if __name__ == '__main__':
    try:
        main()
    finally:
        print(SHOW_CUR)
