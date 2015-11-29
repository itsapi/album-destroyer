import sys
import threading
import sys
from time import sleep
from queue import Queue
from difflib import SequenceMatcher as SM

import lastfm
import convert_image
from console import *
from nbinput import NonBlockingInput
from background import queue_next_song


SCORE = 0
TOTAL = 0


class Input:
    def __init__(self, y, x, border=False):
        self.y = y
        self.x = x
        self.value = ''
        self.border = border

    def render(self, char='●'):
        print(POS_STR(self.y, self.x, ' ' + self.value + ' '), end='')
        if self.border:
            print(POS_STR(self.y-1, self.x-1, char * (4 + len(self.value))) + ' ', end='')
            print(POS_STR(self.y+1, self.x-1, char * (4 + len(self.value))) + ' ', end='')
            print(POS_STR(self.y, self.x-1, char + ' '), end='')
            print(POS_STR(self.y, self.x+len(self.value)+2, char + ' '), end='')
        print(MOVE_CURSOR(HEIGHT, 0), end='')

    def add(self, char):
        self.render(' ')
        self.value += char
        self.render()

    def remove(self):
        self.render(' ')
        self.value = self.value[:-1]
        self.render()

    def set(self, value):
        self.render(' ')
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


def scroll_image(diff, image, offset):
    print(HIDE_CUR + display_image(offset, int(WIDTH / 2 - len(image[0])), diff) + SHOW_CUR)

    return offset + 1


def checkscore(album, answer):
    titleR = SM(None, answer.value.lower(), album['title'].lower()).ratio()
    artistR = SM(None, answer.value.lower(), album['artist'].lower()).ratio()

    return titleR > .8 or artistR > .8


def main(username):
    global TOTAL, SCORE

    offset = HEIGHT
    answer = Input(int(HEIGHT / 2) - 5, 1, border=True)
    albums = lastfm.load_n_albums(username)

    queue = Queue()
    queue_next_song(queue, albums)
    stop_last_song = threading.Event()

    i = 0
    with NonBlockingInput() as nbi:
        while True:
            if offset >= HEIGHT:
                answer.set('')
                print(CLS)
                answer.render()
                TOTAL += 1

                stop_last_song.set()
                queue_next_song(queue, albums)

                album, image, diff, play_barrier, stop_last_song = queue.get(block=True)

                play_barrier.wait()

                offset = 0 - len(image)

            if i % 15 == 0:
                offset = scroll_image(diff, image, offset)
            i += 1

            char = nbi.char()
            if char == chr(127):
                answer.remove()
            elif char == chr(10):
                if checkscore(album, answer):
                    offset = HEIGHT
                    SCORE += 1
                    print(POS_STR(int(HEIGHT / 2), 2, 'Correct answer! (enter to continue)'))
                    input()
                else:
                    print(POS_STR(int(HEIGHT / 2), 2, 'Incorrect answer :-('))
            elif char:
                answer.add(char)

            sleep(0.01)


if __name__ == '__main__':
    try:
        main(sys.argv[1])
    finally:
        print(SHOW_CUR, '{}/{}'.format(SCORE, TOTAL))
