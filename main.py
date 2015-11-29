import threading
import sys
from math import cos, sin, radians
from random import random
from time import sleep
from queue import Queue
from difflib import SequenceMatcher as SM

import lastfm
import convert_image
from colors import *
from console import *
from nbinput import NonBlockingInput
from background import queue_next_song


SCORE = 0
TOTAL = 0

BLACK = '\033[30m'
WHITE = '\033[37m'
END = '\033[0m'


class Input:
    def __init__(self, y, x, border=False):
        self.y = y
        self.x = x
        self.value = ''
        self.border = border

    def render(self, char='●'):
        out = END + WHITE + POS_STR(self.y, self.x, ' ' + self.value + ' ')
        if self.border:
            out += POS_STR(self.y-1, self.x-1, char * (4 + len(self.value))) + ' '
            out += POS_STR(self.y+1, self.x-1, char * (4 + len(self.value))) + ' '
            out += POS_STR(self.y, self.x-1, char + ' ')
            out += POS_STR(self.y, self.x+len(self.value)+2, char + ' ')
        print(out + END + MOVE_CURSOR(0, 0) + BLACK)

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


def annimate_death(y, x):
    for fy in range(HEIGHT - 1, y, -1):
        print(POS_STR(fy, x, colorStr('|', fg=RED, bg=YELLOW, style=BOLD)), end='')
        sys.stdout.flush()
        sleep(.01)

    for d in range(5):
        d *= d
        out = ''
        for a in range(30):
            a *= 360/30

            bg = YELLOW if (random() * d) < 5 else RED

            ax = x + 2*int(random() * d * cos(radians(a)))
            ay = y + int(random() * d * sin(radians(a)))
            ay1 = min(HEIGHT-1, max(1, ay))
            ay2 = min(HEIGHT-1, max(1, ay-1))
            out += POS_STR(ay1, ax, colorStr('**', fg=RED, bg=bg, style=BOLD))
            out += POS_STR(ay2, ax, colorStr('**', fg=RED, bg=bg, style=BOLD))
        print(out, end='')
        sleep(.01)


def display_image(y, x, diff):
    out = POS_STR(y - 1, x, CLS_END_LN) if y > 0 else ''

    for dy, row in list(diff.items())[::-1]:
        if not (0 <= y + dy < HEIGHT - 2):
            continue

        for dx, col in row.items():
            out += POS_STR(y + dy, x + 2 * dx, col)

    return out


def sidebar_info(album, status):
    return (POS_STR(int(HEIGHT / 2) + 3, 2, 'Last round results:') +
            POS_STR(int(HEIGHT / 2) + 4, 2, status or 'No answer entered') +
            POS_STR(int(HEIGHT / 2) + 5, 2, '{} - {}'.format(album['title'], album['artist'])) +
            POS_STR(int(HEIGHT / 2) + 6, 2, 'Score {} of {}'.format(SCORE, TOTAL)))


def scroll_image(diff, image, offset):
    print(END + display_image(offset, int(WIDTH / 2 - len(image[0])), diff) + BLACK)

    return offset + 1


def checkscore(album, answer):
    titleR = SM(None, answer.value.lower(), album['title'].lower()).ratio()
    artistR = SM(None, answer.value.lower(), album['artist'].lower()).ratio()

    return titleR > .8 or artistR > .8


def main(username):
    global TOTAL, SCORE

    offset = HEIGHT
    answer = Input(int(HEIGHT / 2), 1, border=True)
    albums = lastfm.load_n_albums(username)
    album = None
    status = None

    queue = Queue()
    queue_next_song(queue, albums)
    stop_last_song = threading.Event()

    i = 0
    with NonBlockingInput() as nbi:
        while True:
            if offset >= HEIGHT:
                if album:
                    print(END + WHITE + sidebar_info(album, status) + END + BLACK)
                    status = None
                    sleep(2)

                TOTAL += 1

                stop_last_song.set()
                queue_next_song(queue, albums)

                album, image, diff, play_barrier, pause_music, stop_last_song = queue.get(block=True)

                play_barrier.wait()

                answer.set('')
                print(CLS)
                answer.render()

                offset = 0 - len(image)

            if i % 15 == 0:
                offset = scroll_image(diff, image, offset)
            i += 1

            char = nbi.char()
            if char == chr(127):
                answer.remove()
            elif char == chr(10):
                if checkscore(album, answer):
                    annimate_death(offset + int(len(image) / 2), int(WIDTH / 2))
                    offset = HEIGHT
                    SCORE += 1
                    status = 'Correct answer!'
                else:
                    status = 'Incorrect answer :-('
            elif char == chr(27):
                char = 0
                msg = '---- PAUSED (esc to close, q to quit game) ----'
                print(END + WHITE + sidebar_info(album, status) + END + BLACK)
                print(WHITE + POS_STR(2, int((WIDTH-len(msg))/2), msg) + END)
                pause_music.set()
                while not char in (chr(27), chr(113)):
                    char = nbi.char()
                print(POS_STR(2, int((WIDTH-len(msg))/2), int((WIDTH-len(msg))/2) * ' ') + BLACK)
                pause_music.clear()
                if char == chr(113):
                    sys.exit(0)
            elif char:
                answer.add(char)

            sleep(0.01)


if __name__ == '__main__':
    try:
        msg = 'Game is loading...'
        print(HIDE_CUR + CLS + POS_STR(int(HEIGHT/2), int((WIDTH-len(msg))/2), msg) + BLACK)
        main(sys.argv[1])
    finally:
        print(SHOW_CUR, '{}/{}'.format(SCORE, TOTAL))
