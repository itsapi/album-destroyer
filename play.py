import os
import time
import pyaudio
import wave


def play_wave(filename, length=10):
    CHUNK = 1024

    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(CHUNK)

    start = time.time()
    while data != '' and time.time() < start + length:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()

    p.terminate()


def get_and_play(url):
    try:
        os.system('youtube-dl -x --audio-format=wav -o song.tmp {}'.format(url))
    except:
        pass
    else:
        play_wave('song.wav')
        return True
    finally:
        try:
            os.system('rm song.wav')
        except:
            pass



if __name__ == '__main__':
    import sys
    get_and_play(sys.argv[1])
