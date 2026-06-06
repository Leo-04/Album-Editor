from tkinter import *


class Notebook(Frame):
    """A custom notebook widget"""

    side: (TOP, BOTTOM, LEFT, RIGHT)
    padx: int
    pady: int
    panel_size: int
    button_frame: Frame

    def __init__(self, master=None, cnf=None, **kwargs):
        self.side = TOP
        self.padx = 0
        self.pady = 0
        self.panel_size = 300
        self.button_frame = None

        Frame.__init__(self, master, self.custom_config(cnf, **kwargs), class_="Notebook")

        self.button_frame = Frame(self, name="buttons", bd=1, relief="ridge", width=self.panel_size, height=self.panel_size)
        self.button_frame.propagate(False)

        self.custom_config({"side": self.side})

        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

    def custom_config(self, cnf: dict[str, any] | None, **kwargs) -> dict[str, any]:
        """
        Configure custom options

        Parameters:
            cnf: dict | None
            kwargs: dict
                The configurations

        Returns:
            The configurations to pass to tkinter
        """

        if cnf is None:
            cnf = {}
        cnf.update(kwargs)

        if "side" in cnf:
            self.side = cnf.pop("side")

            if self.button_frame is not None:
                self.button_frame.grid(
                    row         =2  if self.side == BOTTOM          else 0,
                    column      =2  if self.side == RIGHT           else 0,
                    rowspan     =3  if self.side in [LEFT, RIGHT]   else 1,
                    columnspan  =3  if self.side in [BOTTOM, TOP]   else 1,
                    sticky      =NS if self.side in [LEFT, RIGHT]   else EW
                )

        if "padx" in cnf:
            self.padx = cnf.pop("padx")

        if "pady" in cnf:
            self.pady = cnf.pop("pady")

        if "panel_size" in cnf:
            self.panel_size = cnf.pop("panel_size")

            if self.button_frame is not None:
                self.button_frame.config(width=self.panel_size, height=self.panel_size)

        return cnf

    def cget(self, key: str) -> any:
        """Get a value from a given key"""

        if "padx" == key:
            return self.padx

        elif "pady" == key:
            return self.pady

        elif "panel_size" == key:
            return self.panel_size

        elif "side" == key:
            return self.side

        else:
            return Frame.cget(self, key)

    __getitem__ = cget

    def __setitem__(self, key, value):
        self.configure({key: value})

    def keys(self):
        return Frame.keys(self) + ["side", "panel_size", "padx", "pady"]

    def add(self, cnf=None, **kwargs) -> Button:
        """
        Adds a widget to the notebook

        Options:
            frame: Widget
                The widget to add
            side:
                The direction to pack the tab button
            fill:
                The direction to fill the button

        Returns:
            A new button that was created for the frame
            Its command is a function to select the frame
        """

        if cnf is None:
            cnf = {}
        cnf.update(kwargs)

        frame = None
        if "frame" in cnf:
            frame = cnf.pop("frame")

        side = TOP if self.side in (LEFT, RIGHT) else LEFT
        if "side" in cnf:
            side = cnf.pop("side")

        fill = X if self.side in (LEFT, RIGHT) else Y
        if "fill" in cnf:
            fill = cnf.pop("fill")

        button = Button(self.button_frame, cnf, relief="flat")
        button.config(command=lambda b=button, f=frame: self.show_frame(f, b))
        button.pack(side=side, fill=fill)

        return button

    def select(self, index: int):
        """Call the command of the button at the given index"""

        self.tk.call(self.button_frame.pack_slaves()[index]["command"])

    def show_frame(self, frame: Widget, button: Button):
        """Shows a frame and configures the selected button"""

        for b in self.button_frame.pack_slaves():
            b["relief"] = "flat"

        for f in self.grid_slaves(1, 1):
            f.grid_forget()

        if frame is not None:
            frame.grid(row=1, column=1, sticky=NSEW, padx=self.padx, pady=self.pady)

        button["relief"] = "sunken"
