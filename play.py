import os
import time
import pyaudio
import wave


def play_wave(filename, length=10):
    CHUNK = 1024

    try:
        wf = wave.open(filename, 'rb')
    except FileNotFoundError:
        return False

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

    return True


def get_and_play(url):
    success = False

    try:
        os.system('youtube-dl -x --audio-format=wav -o song.tmp {} > /dev/null 2>&1'.format(url))
    except:
        pass
    else:
        success = play_wave('song.wav')
    finally:
        try:
            os.system('rm song.wav > /dev/null 2>&1')
        except:
            pass

    return success



if __name__ == '__main__':
    import sys
    get_and_play(sys.argv[1])
