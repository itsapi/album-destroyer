import sys
import os


def getTerminalSize():
    import os
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
    return int(cr[1]), int(cr[0])


WIDTH, HEIGHT = getTerminalSize()
CLS = '\033[2J'
CLS_END = '\033[0J'
CLS_END_LN = '\033[0K'
REDRAW = '\033[0;0f'
HIDE_CUR = '\033[?25l'
SHOW_CUR = '\033[?25h'
MOVE_CURSOR = lambda y, x: '\033[{};{}H'.format(y, x)
SAVE_CUR = '\033[s'
RESTORE_CUR = '\033[u'
POS_STR = lambda y, x, s: '\033[{};{}H{}'.format(y+1, x+1, s)
UP = lambda n=1: '\033[{}A'.format(n)
DOWN = lambda n=1: '\033[{}B'.format(n)
RIGHT = lambda n=1: '\033[{}C'.format(n)
BACK = LEFT = lambda n=1: '\033[{}D'.format(n)
