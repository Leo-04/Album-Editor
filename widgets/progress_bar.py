from tkinter import *


class ProgressBar(Canvas):
    """
    A simple progress bar
    """

    orient: str = HORIZONTAL
    loop_time: int = 10
    loop_speed: float = +0.01
    loop_width: float = 1/8
    percentage: float = 0

    def __init__(self, master=None, cnf=None, **kwargs):
        Canvas.__init__(self, master, self.custom_config(cnf, **kwargs), highlightthickness=0)

        self.bar = self.create_rectangle(0, 0, 0, 0, fill=self["highlightcolor"], outline="")
        self.after_loop = None

        self.bind("<Configure>", lambda e: self.on_resize())

    def custom_config(self, cnf=None, **kwargs) -> dict[str, ...]:
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

        if "orient" in cnf:
            self.orient = cnf.pop("orient")

        if "loop_time" in cnf:
            self.loop_time = cnf.pop("loop_time")

        if "loop_speed" in cnf:
            self.loop_speed = cnf.pop("loop_speed")

        if "loop_width" in cnf:
            self.loop_width = cnf.pop("loop_width")

        if "percentage" in cnf:
            self.percentage = cnf.pop("percentage")

        return cnf

    def cget(self, key: str) -> any:
        """Get a value from a given key"""

        if "orient" == key:
            return self.orient

        elif "loop_time" == key:
            return self.loop_time

        elif "loop_speed" == key:
            return self.loop_speed

        elif "loop_width" == key:
            return self.loop_width

        elif "percentage" == key:
            return self.percentage

        else:
            return Canvas.cget(self, key)

    __getitem__ = cget

    def __setitem__(self, key, value):
        self.configure({key: value})

    def keys(self):
        return Canvas.keys(self) + ["orient", "loop_time", "loop_speed", "loop_width", "percentage"]

    def on_resize(self):
        """Resize event callback"""

        self.itemconfig(self.bar, fill=self["highlightcolor"])

        if self.percentage >= 0:
            if self.orient == HORIZONTAL:
                self.coords(self.bar, 0, 0, self.winfo_width() * self.percentage, self.winfo_height())
            else:
                self.coords(self.bar, 0, 0, self.winfo_width(), self.winfo_height() * self.percentage)

    def get(self) -> float:
        """Get the percentage"""

        return self.percentage

    def set(self, value: float):
        """Set the percentage"""

        self.percentage = value
        self.on_resize()

        if value < 0 and self.after_loop is None:
            self.percentage -= self.loop_speed
            self.loop()

    def loop(self):
        """Cause the bar to start doing the loop animation"""

        if self.percentage < 0:
            self.percentage += self.loop_speed

            if self.percentage >= 0:
                self.percentage = -0.01
                self.loop_speed = -self.loop_speed
            if self.percentage < -1:
                self.percentage = -1
                self.loop_speed = -self.loop_speed

            width = self.loop_width
            if width < 1:
                width *= self.winfo_width()

            if self.orient == HORIZONTAL:
                x = (abs(self.percentage)-0.01) * (self.winfo_width()-width)
                self.coords(self.bar, x, 0, x + width, self.winfo_height())
            else:
                y = (abs(self.percentage)-0.01) * (self.winfo_height()-width)
                self.coords(self.bar, 0, y, self.winfo_width(), y + width)

            self.after_loop = self.after(self.loop_time, self.loop)
        else:
            self.loop_speed = abs(self.loop_speed)
            self.after_loop = None
#
