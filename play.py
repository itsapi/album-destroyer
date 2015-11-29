import os
import time
from contextlib import contextmanager
from ctypes import *
import pyaudio
import wave


MUSIC_LENGTH = 25


ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
    pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)


def play_wave(filename, stop):
    CHUNK = 1024

    try:
        wf = wave.open(filename, 'rb')
    except FileNotFoundError:
        return

    with noalsaerr():
        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(CHUNK)

        start = time.time()
        while data != '' and time.time() < start + MUSIC_LENGTH and not stop.is_set():
            stream.write(data)
            data = wf.readframes(CHUNK)

        stream.stop_stream()
        stream.close()

        p.terminate()


if __name__ == '__main__':
    import sys
    get_and_play(sys.argv[1])
