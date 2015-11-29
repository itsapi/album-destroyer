import os
import threading
from random import randint
from PIL import Image
from io import BytesIO
from urllib import request

import lastfm
import play
import convert_image
from youtube import youtube_search


THUMBSIZE = 20


def get_image_from_url(url):
    try:
        return Image.open(BytesIO(request.urlopen(url).read()))
    except AttributeError:
        return


def get_and_play(mbid, queue):
    play_barrier = threading.Barrier(2)

    album = lastfm.get_album_info(mbid)

    image = None
    for i in range(5):
        image = get_image_from_url(album['image'])
        if image:
            break
    if not image:
        return

    image.thumbnail((THUMBSIZE, THUMBSIZE), Image.ANTIALIAS)
    image = convert_image.convert_image(image)

    for track in album['tracks']:
        videos = youtube_search(album['title'], album['artist'], track)

        for video in videos:
            # print(video[0])
            try:
                os.system('youtube-dl -x --audio-format=wav -o %\(id\)s.tmp {} > /dev/null 2>&1'.format(video[1]))
            except Exception as e:
                print('Failed', e)
                continue
            else:
                queue.put((album, image, play_barrier))
                play_barrier.wait()
                print(video[0], 'Playing')
                play.play_wave('{}.wav'.format(video[1]))
                play_barrier.wait()
                return
            finally:
                try:
                    os.system('rm song.wav song.tmp > /dev/null 2>&1')
                except Exception as e:
                    print('Error:', e)
                    pass


def queue_next_song(queue, albums):
    mbid = albums[randint(0, len(albums)-1)]

    t = threading.Thread(target=get_and_play, args=(mbid, queue))
    t.daemon = True
    t.start()
