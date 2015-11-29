import sys
import threading
from time import sleep
from queue import Queue
from difflib import SequenceMatcher as SM

import lastfm
import convert_image
from console import *
from nbinput import NonBlockingInput
from background import queue_next_song


class Input:
    def __init__(self, y, x, border=False):
        self.y = y
        self.x = x
        self.value = ''
        self.border = border

    def render(self):
        self.draw(' ')
        self.draw()

    def draw(self, char='●'):
        print(POS_STR(self.y, self.x, ' ' + self.value + ' '), end='')
        if self.border:
            print(POS_STR(self.y-1, self.x-1, char * (4 + len(self.value))) + ' ', end='')
            print(POS_STR(self.y+1, self.x-1, char * (4 + len(self.value))) + ' ', end='')
            print(POS_STR(self.y, self.x-1, char + ' '), end='')
            print(POS_STR(self.y, self.x+len(self.value)+2, char + ' '), end='')
        print(MOVE_CURSOR(HEIGHT, 0), end='')

    def add(self, char):
        self.value += char
        self.render()

    def remove(self):
        self.value = self.value[:-1]
        self.render()

    def set(self, value):
        self.value = value
        self.render()


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
    albums = lastfm.get_albums(sys.argv[1])
    offset = HEIGHT

    answer = Input(int(HEIGHT / 2) - 5, 1, border=True)

    def checkscore(album):
        titleR = SM(None, answer.value.lower(), album['title'].lower()).ratio()
        artistR = SM(None, answer.value.lower(), album['artist'].lower()).ratio()

        if titleR > .8 or artistR > .8:
            outcome = HEIGHT
            print(POS_STR(int(HEIGHT / 2), 2, 'Correct answer!'))
        else:
            print(POS_STR(int(HEIGHT / 2), 2, 'Incorrect answer :-('))

    queue = Queue()
    queue_next_song(queue, albums)
    stop_last_song = threading.Event()

    i = 0
    with NonBlockingInput() as nbi:
        while True:
            if offset >= HEIGHT:
                print(CLS)
                answer.render()

                stop_last_song.set()
                queue_next_song(queue, albums)

                album, image, play_barrier, stop_last_song = queue.get(block=True)
                play_barrier.wait()

                offset = 0 - len(image)

            if i % 5 == 0:
                offset = scroll_image(image, offset)
            i += 1

            char = nbi.char()
            if char == chr(127):
                answer.remove()
            elif char == chr(10):
                checkscore(album)
                answer.set('')
            elif char:
                answer.add(char)

            sleep(0.01)


if __name__ == '__main__':
    try:
        main()
    finally:
        print(SHOW_CUR)
