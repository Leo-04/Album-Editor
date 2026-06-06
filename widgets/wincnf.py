from tkinter import Tk
import ctypes, os
from ctypes import byref, sizeof, c_int


class WindowCnf:
    """
    Configure the style of windows' windows

    If not on windows, configurations call will be ignored
    """

    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_WINDOW_CORNER_PREFERENCE = WIN_CORNER = 33
    DWMWA_BORDER_COLOR = BD_COLOR = BD = 34
    DWMWA_CAPTION_COLOR = TITLE_BG = 35
    DWMWA_TEXT_COLOR = TITLE_FG = 36

    WIN_CORNER_DEFAULT = DEFAULT = 0
    WIN_CORNER_SQUARE = SQUARE = 1
    WIN_CORNER_ROUND = ROUND = 2
    WIN_CORNER_SMALL_ROUND = SMALL_ROUND = 3

    CNF = {
        "fg": TITLE_FG,
        "title_fg": TITLE_FG,
        "foreground": TITLE_FG,
        "title_foreground": TITLE_FG,
        "text_color": TITLE_FG,

        "bg": TITLE_BG,
        "title_bg": TITLE_BG,
        "background": TITLE_BG,
        "title_background": TITLE_BG,
        "caption_color": TITLE_BG,

        "bd": BD_COLOR,
        "bd_color": BD_COLOR,
        "border_color": BD_COLOR,
        "border": BD_COLOR,

        "window_corner_preference": WIN_CORNER,
        "window_corner": WIN_CORNER,
        "win_corner_preference": WIN_CORNER,
        "win_corner": WIN_CORNER,
        "corner": WIN_CORNER
    }

    fg: int | str | list[int] | tuple[int, int, int]
    title_fg: int | str | list[int] | tuple[int, int, int]
    foreground: int | str | list[int] | tuple[int, int, int]
    title_foreground: int | str | list[int] | tuple[int, int, int]
    text_color: int | str | list[int] | tuple[int, int, int]

    bg: int | str | list[int] | tuple[int, int, int]
    title_bg: int | str | list[int] | tuple[int, int, int]
    background: int | str | list[int] | tuple[int, int, int]
    title_background: int | str | list[int] | tuple[int, int, int]
    caption_color: int | str | list[int] | tuple[int, int, int]

    bd: int | str | list[int] | tuple[int, int, int]
    bd_color: int | str | list[int] | tuple[int, int, int]
    border_color: int | str | list[int] | tuple[int, int, int]
    border: int | str | list[int] | tuple[int, int, int]

    window_corner_preference: int
    window_corner: int
    win_corner_preference: int
    win_corner: int
    corner: int

    win_95: bool
    windows_95: bool
    win95: bool
    windows95: bool

    root: Tk
    hwnd: int

    def __init__(self, root: Tk):
        self.root = root

        self.root.update()
        if os.name != 'nt':
            print(self.__class__.__name__, "only works on windows")
            return

        self.hwnd = ctypes.windll.user32.GetParent(root.winfo_id())

    def __setattr__(self, name, value):
        if name.lower() in WindowCnf.CNF:
            self.config({name.lower(): value})
        elif name.lower() in ["win95", "windows95", "win_95", "windows95"]:
            self.config(win95=value)
        else:
            object.__setattr__(self, name, value)

    def config(self, cnf=None, **kwargs):
        """Configure settings"""

        if os.name != 'nt':
            return print(self.__class__.__name__, "only works on windows")

        if cnf is not None:
            kwargs.update(cnf)

        for item in kwargs:
            item = str(item).lower()

            if item in WindowCnf.CNF:
                value = kwargs[item]

                if type(value) != int:
                    value = WindowCnf.get_color(value)

                ctypes.windll.dwmapi.DwmSetWindowAttribute(self.hwnd, WindowCnf.CNF[item], byref(c_int(value)), sizeof(c_int))

            elif item in ["win95", "windows95", "win_95", "windows95"]:
                ctypes.windll.Uxtheme.SetWindowTheme(self.hwnd, " " if kwargs[item] else 0, " " if kwargs[item] else 0)

            else:
                print("Unknown option:", item)

    @staticmethod
    def get_color(color: int | list[int] | tuple[int, int, int] | str) -> int:
        """Gets the color for any valid color type"""

        if type(color) == int:
            return color
        elif type(color) in [list, tuple]:
            return WindowCnf.get_rgb(*color)
        elif type(color) == str:
            return WindowCnf.get_hex(color)

    @staticmethod
    def get_hex(tk_hex: str) -> int:
        """Gets the color from a hex string"""

        if tk_hex.startswith("#"):
            tk_hex = tk_hex[1:]

        while len(tk_hex) < 8:
            tk_hex += "0"

        return WindowCnf.get_rgb(
            int(tk_hex[0:2], 16),
            int(tk_hex[2:4], 16),
            int(tk_hex[4:6], 16),
            int(tk_hex[7:8], 16)
        )

    @staticmethod
    def get_rgb(r: int, g: int, b: int, a: int) -> int:
        """Gets the color from r, g, b, a values"""

        num = r | (g << 8) | (b << 16) | (a << 48)
        return num
