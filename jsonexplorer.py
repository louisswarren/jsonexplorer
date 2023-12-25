import sys
import json
import curses

class Menu:
    def __init__(self, cmenu):
        self.cmenu = cmenu
        self.selection = 0
        for i, item in enumerate(self.items):
            self.cmenu.addstr(i, 0, item)
            if i == curses.LINES - 1:
                break

        self.select(0)

    def select(self, n):
        self.cmenu.addstr(self.selection, 0, self.items[self.selection])
        self.selection = n
        self.cmenu.addstr(self.selection, 0, self.items[self.selection], curses.A_REVERSE)
        self.cmenu.refresh()

    def poll(self, stdscr):
        while True:
            match stdscr.getkey():
                case 'j':
                    self.select((self.selection + 1) % len(self.items))
                case 'k':
                    self.select((self.selection - 1) % len(self.items))

class ObjectMenu(Menu):
    def __init__(self, obj, cmenu):
        self.obj = obj
        self.items = list(obj.keys())
        super().__init__(cmenu)

class ArrayMenu(Menu):
    def __init__(self, array, cmenu):
        self.array = array
        self.items = [f'[{i}]' for i in range(len(array))]
        super().__init__(cmenu)

class Element(Menu):
    def __init__(self, cmenu):
        self.items = ['---']
        super().__init__(cmenu)


def jsonmenu(stdscr, j):
    while True:
        stdscr.clear()

        menu_width = min(30, curses.COLS / 2)

        for i in range(curses.LINES):
            stdscr.addch(i, menu_width - 1, '|')
        stdscr.refresh()

        cur = j
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

        sel = 0
        menu.addstr(sel, 0, items[sel][0], curses.A_REVERSE)
        menu.refresh(0, 0, 0, 0, curses.LINES - 1, menu_width - 2)

        outlines = json.dumps(items[sel][1], indent=4).split('\n')
        disp = curses.newpad(len(outlines), max(len(x) for x in outlines)+1)
        for i, line in enumerate(outlines):
            disp.addstr(i, 0, line)
        disp.refresh(0, 0, 0, menu_width + 1, curses.LINES - 1, curses.COLS - 1)

        while True:
            pressed = stdscr.getkey()
            match pressed:
                case 'j':
                    menu.addstr(sel, 0, items[sel][0])
                    sel = (sel + 1) % len(items)
                case 'k':
                    menu.addstr(sel, 0, items[sel][0])
                    sel = (sel - 1) % len(items)
                case 'l':
                    if not elem:
                        jsonmenu(stdscr, items[sel][1])
                        break
                case 'h':
                    return
                case _:
                    continue
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


    disp.refresh(0, 0, 0, menu_width, curses.LINES, curses.COLS)

    if isinstance(j, dict):
        m = ObjectMenu(j, menu)
        m.poll(stdscr)


if __name__ == '__main__':
    with open('test.json') as f:
        curses.wrapper(jsonmenu, json.load(f))
