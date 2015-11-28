import os
import pyaudio
import wave


def play_wave(filename):
    CHUNK = 1024

    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(CHUNK)

    while data != '':
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()

    p.terminate()


def get_and_play(url):
    os.system('youtube-dl -x --audio-format=wav -o song.tmp {}'.format(url))
    play_wave('song.wav')
    os.system('rm song.wav')


if __name__ == '__main__':
    import sys
    get_and_play(sys.argv[1])
