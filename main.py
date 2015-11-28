import curses


def main(stdscr):
    stdscr.clear()

    stdscr.refresh()
    stdscr.getkey()


if __name__ == '__main__':
    curses.wrapper(main)
