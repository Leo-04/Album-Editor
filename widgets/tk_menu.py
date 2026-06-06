from tkinter import Frame, Label, Button, LEFT


class TkMenu(Frame):
    """A simple button menubar"""

    def __init__(self, master, *commands, **kwargs):
        Frame.__init__(self, master, {"bd": 2, "relief": "raised"}, **kwargs, class_="TkMenu")

        for cmd in commands:
            if cmd is None:
                self.add_seperator()
            else:
                self.add_command(**cmd)

    def add_seperator(self, cnf: dict = None, **kwargs) -> Label:
        """Adds a seperator"""

        cnf = {"padx": 20, "side": LEFT} | (cnf or {}) | kwargs
        side = cnf.pop("side")

        label = Label(self, cnf)
        label.pack(side=side)
        return label

    def add_command(self, cnf: dict = None, **kwargs) -> Button:
        """Adds a button to the menu"""

        cnf = {"padx": 10, "pady": 2, "relief": "flat", "bd": 0, "side": LEFT, "hotkey": None} | (cnf or {}) | kwargs
        side = cnf.pop("side")
        hotkey = cnf.pop("hotkey")

        button = Button(self, cnf)
        button.pack(side=side)
        button.bind("<ButtonPress-1>", lambda e: button.config(relief="sunken"))
        button.bind("<ButtonRelease-1>", lambda e: button.config(relief="flat"))

        self.winfo_toplevel().bind_all(hotkey, lambda e, b=button: b.invoke())

        return button
