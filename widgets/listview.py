from tkinter import *
import bisect
from tkinter.font import Font


class ListView(Frame):
    panel: PanedWindow
    columns: list[Frame]

    title_height: int
    show_columns: bool
    auto_expand: tuple[int, ...]
    resizable: bool
    fixed_columns: tuple[int, ...]
    min_widths: tuple[int, ...]
    select_background: str
    select_foreground: str
    foreground: str
    widths: tuple[int, ...]
    item_height: None | int
    item_border: int
    item_padx: int
    item_pady: int
    item_relief: ["raised", "sunken", "flat", "ridge", "solid", "groove"]
    show_drag: list[int]

    title_cnf: dict[str, any]

    img_1x1: PhotoImage
    values: list
    selected: None | int
    current_index: int
    yscrollcommand: callable
    after_id: None | str
    drag_frame: Toplevel

    def __init__(self, master=None, cnf=None, **kwargs):
        self.auto_expand = (0,)
        self.item_height = None
        self.item_border = 0
        self.item_padx = 0
        self.item_pady = 3
        self.item_relief = "flat"
        self.resizable = True
        self.fixed_columns = ()
        self.min_widths = ()
        self.widths = ()
        self.show_columns = True
        self.show_drag = []

        Frame.__init__(self, master, class_="ListView", border=0)
        box = Listbox()
        self.select_background = self.option_get("selectbackground", "ListView") or box["selectbackground"]
        self.select_foreground = self.option_get("selectforeground", "ListView") or box["selectforeground"]
        self.foreground = self.option_get("foreground", "ListView") or box["foreground"]
        self.font = self.option_get("font", "ListView") or box["font"]
        box.destroy()
        del box

        cnf, title_cnf, columns = self.custom_config(cnf, **kwargs)
        if columns is None:
            columns = ("",)
        self.title_cnf = title_cnf

        self.panel = PanedWindow(self, cnf, name="panel")
        self.panel.pack(fill=BOTH, expand=1)

        self.drag_frame = Toplevel(self, name="drag-frame")
        self.drag_frame.withdraw()
        self.drag_frame.overrideredirect(True)

        self.img_1x1 = PhotoImage(width=1, height=1)
        self.values = []
        self.selected = None
        self.current_index = 0
        self.yscrollcommand = lambda *args: None

        self.rows = 0
        self.create_columns(columns)

        self.after_id = None
        self.bind("<Configure>", lambda e: self.on_resize())
        self.bind("<Map>", lambda e: self.on_resize_after())
        self.panel.bind("<MouseWheel>", self.on_scroll)

    def create_columns(self, columns: tuple[str, ...]):
        """Create the columns"""

        self.columns = [Frame(self, name="column-" + str(i)) for i, column in enumerate(columns)]

        for child in self.drag_frame.winfo_children():
            child.grid_forget()

        heights = {0}
        for i, frame in enumerate(self.columns):
            title = Label(frame, self.title_cnf, name="titleLabel", text=columns[i])
            title.bind("<MouseWheel>", self.on_scroll)
            title.bind("<Button-4>", lambda e: self.event_generate("<<Back>>", subwindow=e.widget))
            title.bind("<Button-5>", lambda e: self.event_generate("<<Forwards>>", subwindow=e.widget))

            if self.show_columns:
                title.grid(row=0, column=0, sticky=EW)
                title.update()
                heights.add(title.winfo_height() + int(str(title["bd"])) * 2 + int(str(title["pady"])) * 2)

            label = Label(self.drag_frame, name="dragLabel-"+str(i))

            if i < len(self.widths) and self.widths[i] is not None:
                label["width"] = self.widths[i]

            if type(self.auto_expand) in [tuple, list] and i in self.auto_expand:
                self.drag_frame.columnconfigure(i, weight=1)

            if i in self.min_widths and i < len(self.min_widths) and self.min_widths[i] is not None:
                label["width"] = self.min_widths[i]

            label.grid(row=0, column=i, sticky=NSEW, padx=self.panel.cget("sashwidth"))

        if self.show_columns:
            self.title_height = max(heights)
        else:
            self.title_height = 0

        for i, frame in enumerate(self.columns):
            frame.columnconfigure(0, weight=1)
            frame.bind("<MouseWheel>", self.on_scroll)

            options = {}
            if i < len(self.widths) and self.widths[i] is not None:
                options["width"] = self.widths[i]

            if type(self.auto_expand) in [tuple, list]:
                options["stretch"] = "always" if i in self.auto_expand else "never"

            if i in self.min_widths and i < len(self.min_widths) and self.min_widths[i] is not None:
                options["minsize"] = self.min_widths[i]

            self.panel.add(frame, sticky=NSEW, **options)

    def custom_config(self, cnf: dict[str, any] | None, **kwargs) -> tuple[dict[str, any], dict[str, any], tuple[str, ...]]:
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

        columns = None
        if "columns" in cnf:
            columns = cnf.pop("columns")

        if "show_columns" in cnf:
            self.show_columns = cnf.pop("show_columns")

        if "auto_expand" in cnf:
            self.auto_expand = cnf.pop("auto_expand")

        if "resizable" in cnf:
            self.resizable = cnf.pop("resizable")

        if "fixed_columns" in cnf:
            self.fixed_columns = cnf.pop("fixed_columns")

        if "min_widths" in cnf:
            self.min_widths = cnf.pop("min_widths")

        if "widths" in cnf:
            self.widths = cnf.pop("widths")

        if "select_bg" in cnf:
            self.select_background = cnf.pop("select_bg")

        if "select_background" in cnf:
            self.select_background = cnf.pop("select_background")

        if "select_bg" in cnf:
            self.select_foreground = cnf.pop("select_bg")

        if "select_foreground" in cnf:
            self.select_foreground = cnf.pop("select_foreground")

        if "foreground" in cnf:
            self.select_foreground = cnf.pop("foreground")

        if "font" in cnf:
            self.font = cnf.pop("font")

        if "item_padx" in cnf:
            self.item_padx = cnf.pop("item_padx")

        if "item_pady" in cnf:
            self.item_pady = cnf.pop("item_pady")

        if "item_height" in cnf:
            self.item_height = cnf.pop("item_height")

        if "item_relief" in cnf:
            self.item_relief = cnf.pop("item_relief")

        if "show_drag" in cnf:
            self.show_drag = cnf.pop("show_drag")

        title_cnf = {}
        for item in list(cnf):
            if item.startswith("title_"):
                title_cnf[item[6:]] = cnf[item]
                cnf.pop(item)

        return cnf, title_cnf, columns

    def configure(self, cnf: dict[str, any] | None = None, **kwargs) -> any:
        """Configure this widget"""

        cnf, title_cnf, columns = self.custom_config(cnf, **kwargs)
        self.title_cnf.update(title_cnf)

        ret = self.panel.configure(cnf)

        if columns:
            for frame in self.columns:
                self.panel.remove(frame)
                frame.destroy()

            # Will use `self.title_cnf`
            self.create_columns(columns)
            self.update_all()
            return

        self.un_select()
        for frame in self.columns:
            for label in frame.grid_slaves():
                label: Label
                if label.winfo_name() != "titleLabel":
                    label.config(bg=self.panel["bg"], font=self.font, fg=self.foreground)

        if title_cnf:
            for frame in self.columns:
                frame.nametowidget("titleLabel").config(title_cnf)

        return ret

    config = configure

    def cget(self, key: str) -> any:
        """Get a value from a given key"""

        if "columns" == key:
            return [
                frame.nametowidget("titleLabel")["text"]
                for frame in self.columns
            ]

        elif "show_columns" == key:
            return self.show_columns

        elif "auto_expand" == key:
            return self.auto_expand

        elif "resizable" == key:
            return self.resizable

        elif "fixed_columns" == key:
            return self.fixed_columns

        elif "min_widths" == key:
            return self.min_widths

        elif "widths" == key:
            return self.widths

        elif "select_bg" == key:
            return self.select_background

        elif "select_background" == key:
            return self.select_background

        elif "select_bg" == key:
            return self.select_foreground

        elif "select_foreground" == key:
            return self.select_foreground

        elif "foreground" == key:
            return self.select_foreground

        elif "font" == key:
            return self.font

        elif "item_padx" == key:
            return self.item_padx

        elif "item_pady" == key:
            return self.item_pady

        elif "item_height" == key:
            return self.item_height

        elif "item_relief" == key:
            return self.item_relief

        elif "show_drag" == key:
            return self.show_drag

        elif key.startswith("title_"):
            for frame in self.columns:
                return frame.nametowidget("titleLabel").cget(key[6:])

        else:
            return Frame.cget(self, key)

    __getitem__ = cget

    def __setitem__(self, key, value):
        self.configure({key: value})

    def keys(self):
        return Frame.keys(self) + [
            "show_columns", "auto_expand", "resizable", "fixed_columns", "min_widths", "widths", "select_bg", "select_background",
            "select_bg", "select_foreground", "foreground", "font", "item_padx", "item_pady", "item_height", "item_relief", "show_drag"
        ] + ["title_" + key for frame in self.columns for key in frame.nametowidget("titleLabel").keys()]

    def get(self, index: int) -> tuple[str] | None:
        """Gets a row's value from the list at a given index"""

        if index is None:
            return None

        if index < 0:
            index += len(self)

        if index < 0 or len(self) <= index:
            return None

        return self.values[index]

    def add(self, values: tuple[str, ...] | list[str, ...], update: bool = True, key: callable = None):
        """
        Adds a row to the listview

        Parameters:
            values: tuple[str, ...]
                The row values to add

            update: bool
                Weather to update the listview when adding

            key: callable
                A sorting key to use when inserting
                If None, will add to the end of the list
        """

        values = tuple(values) + ("",) * max(0, len(self.columns) - len(values))
        if key is not None:
            bisect.insort(self.values, values, key=key)
        else:
            self.values.append(values)

        if update:
            self.update_all()

    def remove(self, index: int, update: bool = True):
        """
        Removes a row from the listview

        Parameters:
            index: int
                The index of the row to remove

            update: bool
                Weather to update the listview when adding
        """

        self.values.remove(index)

        if update:
            self.update_all()

    def set(self, index: int, values: tuple[str, ...], update: bool = True, key: callable = None):
        """
        Sets row in the listview

        Parameters:
            index: int
                The index of the row to remove

            values: tuple[str, ...]
                The row values to set

            update: bool
                Weather to update the listview when adding

            key: callable
                A sorting key to use when inserting
                If None, will add to the end of the list
        """

        values = tuple(values) + ("",) * max(0, len(self.columns) - len(values))

        if key is not None:
            self.remove(index, update=False)
            bisect.insort(self.values, values, key=key)
        else:
            self.values[index] = values

        if update:
            self.update_all()

    def clear(self):
        """Clears all values of the listview"""

        self.un_select()
        self.values.clear()
        self.update_all()

    def update_all(self):
        """Update all values of the listview"""

        self.yview("scroll", 0)

    def __len__(self):
        """Gets the number of values in the listview"""

        return len(self.values)

    def on_resize(self):
        """Resize event callback"""

        self.panel.pack_forget()
        if self.after_id:
            self.after_cancel(self.after_id)

        self.after_id = self.after(100, self.on_resize_after)

    def on_resize_after(self):
        """Resize event callback"""

        self.after_id = None
        self.panel.pack(fill=BOTH, expand=1)

        if self.winfo_ismapped() and self.winfo_viewable():
            self.update_label_sizes()
            self.update_all()

    def on_scroll(self, event: Event):
        """User scrolling event callback"""

        if event.delta > 0:
            self.yview("scroll", -4, "units")
        elif event.delta < 0:
            self.yview("scroll", 4, "units")
        else:
            self.yview("scroll", 0, "units")

    def update_label_sizes(self):
        """Updates the number of labels needed to cover the entire listview region"""

        font = Font(font=self.font)
        max_height = self.winfo_height() - self.title_height

        if self.item_height is None:
            item_height = font.metrics("linespace")
        else:
            item_height = self.item_height

        label_height = item_height + 2*self.item_pady + 2*self.item_border

        height = 0
        old_rows = self.rows
        self.rows = 0

        while height <= max_height + label_height:
            pos = self.rows + 1
            for column, frame in enumerate(self.columns):
                if not len(frame.grid_slaves(pos, 0)):
                    label = Label(
                        frame,
                        font=font,
                        foreground=self.foreground,
                        bg=self["bg"],
                        name="label-" + str(pos),
                        pady=self.item_pady,
                        padx=self.item_padx,
                        border=self.item_border,
                        relief=self.item_relief,
                        compound=CENTER,
                        image=self.img_1x1,
                        height=item_height
                    )
                    label.grid(row=pos, column=0, sticky="NEW")
                    label.bind("<ButtonRelease-1>", self.on_release)
                    label.bind("<B1-Motion>", lambda e: self.after(1, self.on_drag, e))
                    label.bind("<Button-3>", self.on_rclick)
                    label.bind("<MouseWheel>", self.on_scroll)
                    label.bind("<Up>", lambda e, c=column: (
                        self.event_generate("<<Up>>", when="tail", x=c, y=self.current_index + e.widget.grid_info()["row"] - 1)
                    ))
                    label.bind("<Down>", lambda e, c=column: (
                        self.event_generate("<<Down>>", when="tail", x=c, y=self.current_index + e.widget.grid_info()["row"] - 1)
                    ))
                    label.bind("<Button-4>", lambda e: self.event_generate("<<Back>>", subwindow=e.widget))
                    label.bind("<Button-5>", lambda e: self.event_generate("<<Forwards>>", subwindow=e.widget))
                    label.x = column
                    label.y = pos - 1
            height += label_height
            self.rows += 1

        for row in range(self.rows, old_rows):
            for frame in self.columns:
                for widget in frame.grid_slaves(row, 0):
                    if widget.winfo_name() != "titleLabel":
                        widget.destroy()

        self.update_labels_text()
        self.update_scrollbar()

    def on_drag(self, event: Event):
        row = event.widget.grid_info()["row"]
        master = event.widget.master
        column = self.columns.index(master)

        if not self.show_drag or column not in self.show_drag:
            return

        self.drag_frame.lift()

        for i, frame in enumerate(self.columns):
            labels = self.drag_frame.grid_slaves(row=0, column=i)
            if labels:
                for key in event.widget.configure():
                    labels[0].configure({key: event.widget.cget(key)})
                labels[0].config(text=frame.nametowidget("label-" + str(row))["text"])

        self.drag_frame.geometry("{w}x{h}+{x}+{y}".format(
            x=event.x_root, #event.widget.winfo_x() + event.x - self.panel.winfo_x(),
            y=event.y_root, #event.widget.winfo_y() + event.y - self.panel.winfo_y(),
            w=self.panel.winfo_width(),
            h=event.widget.winfo_height(),
        ))

        self.drag_frame.deiconify()

    def on_release(self, event: Event):
        """Event callback for mouse release"""

        event.widget.focus()

        row = event.widget.grid_info()["row"]
        master = event.widget.master
        column = self.columns.index(master)
        index = self.current_index + row - 1

        x = event.x_root - master.winfo_rootx()
        y = event.y_root - master.winfo_rooty()
        dragged_to = master.grid_location(x, y)
        dragged_index = self.current_index + dragged_to[1] - 1

        if self.show_columns and dragged_index == -1:
            dragged_index = 0

        if dragged_index >= 0 and len(self) and index < len(self) and 0 <= x <= self.winfo_width():
            if index == dragged_index:
                if not self.drag_frame.winfo_ismapped():
                    self.event_generate("<<Selected>>", when="tail", x=column, y=index)
            else:
                self.event_generate("<<Drag>>", when="tail", x=column, y=index, serial=dragged_index)

        self.drag_frame.withdraw()

    def on_rclick(self, event):
        """Event callback for mouse right click"""

        event.widget.focus()

        row = event.widget.grid_info()["row"]
        column = self.columns.index(event.widget.master)
        index = self.current_index + row - 1

        if 0 <= index < len(self):
            self.event_generate("<<Info>>", when="tail", x=column, y=index)

    def yview(self, cmd: str, value: int, *_):
        """Event callback for scrolling"""

        self.update_labels_text()
        self.un_select()

        if cmd == "moveto":
            value = min(max(float(value), 0), 1)
            self.current_index = int(value * (len(self) - 2))

        elif cmd == "scroll":
            value = int(float(value))
            self.current_index += value

        else:
            print(cmd, value, _)
            return

        self.current_index = max(min(self.current_index, len(self) - (self.rows - 2)), 0)

        self.select(self.selected)
        self.update_labels_text()
        self.update_scrollbar()

    def update_labels_text(self):
        """Update the labels text"""

        index = 0
        row = 1

        while index < len(self) and row <= self.rows:
            values = self.values[index]

            if index >= self.current_index:
                for column, frame in enumerate(self.columns):
                    labels = frame.grid_slaves(row, 0)
                    if labels:
                        label = labels[0]
                        label["text"] = values[column]

                row += 1
            index += 1

        for row in range(row, self.rows + 2):
            for column, frame in enumerate(self.columns):
                labels = frame.grid_slaves(row, 0)
                if labels:
                    label = labels[0]
                    label["text"] = ""

    def update_scrollbar(self):
        """Update the scrollbar"""

        if len(self) == 0:
            from_p = 0
            to_p = 1
        else:
            from_p = self.current_index / (len(self))
            to_p = (self.current_index + self.rows - 2) / (len(self))

        self.yscrollcommand(from_p, to_p)

    def get_selected(self) -> int | None:
        """Gets the currently selected row"""

        return self.selected

    def un_select(self):
        """Unselect the selected row"""

        if self.selected is None or self.select_background is None:
            return

        for column in self.columns:
            row = self.selected - self.current_index + 1
            if 0 <= row:
                for label in column.grid_slaves(row=row, column=0):
                    if label.winfo_name() != "titleLabel":
                        label["bg"] = self["bg"]
                        label["fg"] = self.foreground

    def show(self, index: int):
        """Scroll down to show the given index"""

        sel_index = self.get_selected()
        self.un_select()
        self.current_index = max(min(index - self.rows // 2, len(self) - 1), 0)
        self.select(sel_index)
        self.update_all()

    def select(self, index: int):
        """Select the given index"""

        if index is None or index >= len(self) or index < 0:
            return

        self.un_select()
        self.selected = index

        row = index - self.current_index + 1

        # set bg
        if self.select_background is not None and 0 <= row <= self.rows:
            for column in self.columns:
                for label in column.grid_slaves(row=row, column=0):
                    if label.winfo_name() != "titleLabel":
                        label["bg"] = self.select_background
                        label["fg"] = self.select_foreground
