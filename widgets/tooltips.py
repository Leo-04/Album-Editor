from tkinter import *
from tkinter import _get_default_root
from tkinter.font import Font


class ToolTips(Label):
    """
    A label that will appear above a widget with overflowing text
    Alternatively if the widgets option "tool-tip" is set,
     will display that when hovered over
    """

    after_id: None | str
    root: Tk | Toplevel
    widgets: dict[Widget, str]
    delay: int

    def __init__(self, root=None, cnf=None, widgets=None, delay=500, **kwargs):
        if root is None:
            root = _get_default_root()
        else:
            root = root.winfo_toplevel()

        if cnf is not None:
            kwargs.update(cnf)

        self.window = Toplevel(root, class_="ToolTips")
        self.window.overrideredirect(True)
        self.window.withdraw()

        self.after_id = None
        self.root = root
        self.widgets = widgets or {}
        self.delay = delay

        Label.__init__(self, self.window, kwargs, name="label")
        self.pack(fill=BOTH, expand=True)

        self.root.bind("<Motion>", self.motion)

    def add_widgets(self, widgets: dict[Widget, str]):
        """Adds custom tool-tips to widgets"""

        self.widgets.update(widgets)

    def motion(self, event: Event):
        """Event callback for motion"""

        self.window.withdraw()

        if self.after_id is not None:
            self.after_cancel(self.after_id)
        self.after_id = self.after(self.delay, self.hovered)

    def get_size(self, text: str, font: str | Font):
        """Get the size of text for a given font"""

        font = Font(self.root, font)
        line_height = font.metrics("linespace")
        num_lines = text.count("\n") + 1

        return font.measure(text), line_height * num_lines

    def show(self, text: str):
        """Shows the tool-tip label under mouse with the given text"""

        self["text"] = text
        self.window.deiconify()
        self.window.update()

        w, h = self.get_size(text, self["font"])
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()

        self.window.geometry("%ix%i+%i+%i" % (w + 10, h + 10, x + 10, y + 10))

    def hovered(self):
        """Event callback for when mouse has stayed in one spot for given delay"""

        self.after_id = None

        widget: Widget = self.root.winfo_containing(*self.root.winfo_pointerxy())
        tool_tip = widget.option_get("tool-tip", "*" + widget._name) if widget else None

        if tool_tip:
            self.show(tool_tip)

        elif widget in self.widgets:
            self.show(str(self.widgets[widget]))

        elif isinstance(widget, (Label, Button, Message)):
            text = str(widget["text"])
            widget_size = widget.winfo_width(), widget.winfo_height()
            size = self.get_size(text, widget["font"])

            if widget_size[0] < size[0] or widget_size[1] < size[1]:
                self.show(text)

        elif isinstance(widget, Entry):
            text = widget.get()
            widget_size = widget.winfo_width(), widget.winfo_height()
            size = self.get_size(text, widget["font"])

            if widget_size[0] < size[0] or widget_size[1] < size[1]:
                self.show(text)

        elif widget is not None:
            print(widget)
#
