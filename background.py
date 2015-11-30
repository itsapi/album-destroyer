import os
import glob
import threading
from random import randint
from PIL import Image
from io import BytesIO
from urllib import request
from youtube_dl import YoutubeDL

import lastfm
import play
import convert_image
from youtube import youtube_search


THUMBSIZE = 20
BASE = 'videos'


def image_diff(image):
    diff = {}
    prev_row = {}
    for dy, row in enumerate(image[::-1]):
        diff[len(image) - dy - 1] = {}
        for dx, col in enumerate(row):
            if not prev_row.get(dx) == col:
                prev_row[dx] = diff[len(image) - dy - 1][dx] = col
    return diff


def get_image_from_url(url):
    try:
        return Image.open(BytesIO(request.urlopen(url).read()))
    except AttributeError:
        return


def get_and_play(mbid, queue):
    play_barrier = threading.Barrier(2)
    pause_music = threading.Event()
    stop_song = threading.Event()

    album = lastfm.get_album_info(mbid)

    image = None
    for i in range(20):
        image = get_image_from_url(album['image'])
        if image:
            break
    if not image:
        print('No Image Found')
        return

    image.thumbnail((THUMBSIZE, THUMBSIZE), Image.ANTIALIAS)
    image = convert_image.convert_image(image)
    data = convert_image.get_escape_codes(image)
    diff = image_diff(data)

    for track in album['tracks']:
        videos = youtube_search(album['title'], album['artist'], track)

        for video in videos:
            try:
                opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'outtmpl': '{}/%(id)s.tmp'.format(BASE),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'wav'
                    }]
                }

                with YoutubeDL(opts) as ydl:
                    ydl.download([video[1]])

            except Exception as e:
                print('Failed', e)
                continue
            else:
                queue.put((album, image, diff, play_barrier, pause_music, stop_song))
                play_barrier.wait()
                play.play_wave('{}/{}.wav'.format(BASE, video[1]), pause_music, stop_song)
                return
            finally:
                try:
                    for f in glob.glob(video[1] + '.{wav,tmp,part}'):
                        os.remove(os.path.join(BASE, f))
                except OSError as e:
                    print('Error:', e)


def queue_next_song(queue, albums):
    mbid = albums[randint(0, len(albums)-1)]

    t = threading.Thread(target=get_and_play, args=(mbid, queue))
    t.daemon = True
    t.start()
