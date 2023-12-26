import sys
import json
import curses

def jsonmenu(stdscr, j):
    curses.curs_set(False)
    sel = 0
    pressed = None

    while True:
        stdscr.clear()

        menu_width = min(30, curses.COLS / 2)

        for i in range(curses.LINES):
            stdscr.addch(i, menu_width - 1, '|')
        stdscr.refresh()

        elem = False
        match j:
            case {}:
                items = [(k[:menu_width], v) for k, v in j.items()]
            case [*_]:
                items = [(f'[{i}]', x) for i, x in enumerate(j)]
            case _:
                items = [('---', j)]
                elem = True
        menu = curses.newpad(len(items), menu_width)

        for i, item in enumerate(items):
            menu.addstr(i, 0, item[0])

        menu.addstr(sel, 0, items[sel][0], curses.A_REVERSE)
        menu.refresh(0, 0, 0, 0, curses.LINES - 1, menu_width - 2)

        outlines = json.dumps(items[sel][1], indent=4).split('\n')
        disp = curses.newpad(len(outlines), max(len(x) for x in outlines)+1)
        for i, line in enumerate(outlines):
            disp.addstr(i, 0, line)
        disp.refresh(0, 0, 0, menu_width + 1, curses.LINES - 1, curses.COLS - 1)

        while True:
            dims = curses.LINES, curses.COLS
            if pressed is None:
                pressed = stdscr.getkey()
                curses.update_lines_cols()
                if dims != (curses.LINES, curses.COLS):
                    break
            match pressed:
                case 'j':
                    menu.addstr(sel, 0, items[sel][0])
                    sel = (sel + 1) % len(items)
                case 'k':
                    menu.addstr(sel, 0, items[sel][0])
                    sel = (sel - 1) % len(items)
                case 'l':
                    pressed = None
                    if not elem:
                        while not jsonmenu(stdscr, items[sel][1]):
                            pass
                        break
                case 'h':
                    return True
                case 'q':
                    sys.exit(0)
                case _:
                    pressed = None
                    continue
            pressed = None

            menu.addstr(sel, 0, items[sel][0], curses.A_REVERSE)
            if sel < curses.LINES - 4 or len(items) < curses.LINES:
                scroll = 0
            else:
                scroll = min(sel + 4 - curses.LINES, len(items) - curses.LINES)
            menu.refresh(scroll, 0, 0, 0, curses.LINES - 1, menu_width - 2)

            outlines = json.dumps(items[sel][1], indent=4).split('\n')
            disp.clear()
            disp.refresh(0, 0, 0, menu_width, curses.LINES - 1, curses.COLS - 1)
            disp = curses.newpad(len(outlines), max(len(x) for x in outlines)+1)
            for i, line in enumerate(outlines):
                disp.addstr(i, 0, line)
            disp.refresh(0, 0, 0, menu_width + 1, curses.LINES - 1, curses.COLS - 1)


if __name__ == '__main__':
    with open('test.json') as f:
        j = json.load(f)
        curses.wrapper(jsonmenu, j)
