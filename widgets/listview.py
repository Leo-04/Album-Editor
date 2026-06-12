from tkinter import *
import bisect
from tkinter.font import Font


class ListView(Frame):
    panel: PanedWindow
    columns: list[tuple[Frame, list[Label]]]

    show_columns: bool = True
    auto_expand: tuple[int, ...] = None
    resizable: bool = True
    fixed_columns: tuple[int, ...] = None
    min_widths: tuple[int, ...] = None
    select_background: str = None
    select_foreground: str = None
    foreground: str = None
    widths: tuple[int, ...] = None
    title_height: int = None
    title_border: int = 2
    title_padx: int = 0
    title_pady: int = 0
    title_relief: ["raised", "sunken", "flat", "ridge", "solid", "groove"] = "raised"
    item_height: None | int = None
    item_border: int = 0
    item_padx: int = 0
    item_pady: int = 3
    item_relief: ["raised", "sunken", "flat", "ridge", "solid", "groove"] = "flat"
    show_drag: list[int] = None
    show_drag_item: list[int] = None

    img_1x1: PhotoImage
    values: list
    selected: None | int
    current_index: int
    yscrollcommand: callable
    after_id: None | str
    drag_frame: Toplevel
    drag_frame_labels: list[Label]

    def __init__(self, master=None, cnf=None, **kwargs):
        Frame.__init__(self, master, class_="ListView", border=0)
        box = Listbox()
        self.select_background = self.option_get("selectbackground", "ListView") or box["selectbackground"]
        self.select_foreground = self.option_get("selectforeground", "ListView") or box["selectforeground"]
        self.foreground = self.option_get("foreground", "ListView") or box["foreground"]
        self.font = self.option_get("font", "ListView") or box["font"]
        box.destroy()
        del box

        cnf, columns = self.custom_config(cnf, **kwargs)
        if columns is None:
            columns = ("",)

        self.auto_expand = self.auto_expand or (0,)
        self.fixed_columns = self.fixed_columns or ()
        self.min_widths = self.min_widths or ()
        self.widths = self.widths or ()
        self.show_drag = self.show_drag or []
        self.show_drag_item = self.show_drag_item or []

        self.panel = PanedWindow(self, cnf, name="panel")
        self.panel.pack(fill=BOTH, expand=1)

        self.drag_frame = Toplevel(self, name="drag-frame")
        self.drag_frame_labels = []
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

    def create_columns(self, columns: tuple[str | dict, ...]):
        """Create the columns"""

        self.columns = [
            (Frame(self, name="column-" + str(i)), [])
            for i, column in enumerate(columns)
        ]

        for child in self.drag_frame.winfo_children():
            child.grid_forget()

        for i, (frame, labels) in enumerate(self.columns):
            if isinstance(columns[i], dict):
                title = Label(frame, {
                    "name": "titleLabel",
                    "image": self.img_1x1,
                    "compound": CENTER,
                } | columns[i])
            else:
                title = Label(frame, compound=CENTER, text=str(columns[i]), name="titleLabel", image=self.img_1x1)

            if self.title_height is None:
                self.title_height = Font(font=title.cget("font")).metrics("linespace") + self.title_pady * 2 + self.title_border * 2

            title.config(
                height=self.title_height,
                relief=self.title_relief,
                border=self.title_border,
                padx=self.title_padx,
                pady=self.title_pady,
            )

            title.bind("<MouseWheel>", self.on_scroll)
            title.bind("<Button-4>", lambda e: self.event_generate("<<Back>>", subwindow=e.widget))
            title.bind("<Button-5>", lambda e: self.event_generate("<<Forwards>>", subwindow=e.widget))

            if self.show_columns:
                title.place(x=0, y=0, relwidth=1, height=self.title_height)

            label = Label(self.drag_frame, name="dragLabel-" + str(i), image=self.img_1x1, height=self.item_height)

            if i < len(self.widths) and self.widths[i] is not None:
                label.config(width=self.widths[i])

            if type(self.auto_expand) in [tuple, list] and i in self.auto_expand:
                self.drag_frame.columnconfigure(i, weight=1)

            if i in self.min_widths and i < len(self.min_widths) and self.min_widths[i] is not None:
                label.config(width=self.min_widths[i])

            self.drag_frame_labels.append(label)

        for i, (frame, labels) in enumerate(self.columns):
            frame.bind("<MouseWheel>", self.on_scroll)

            options = {}
            if i < len(self.widths) and self.widths[i] is not None:
                options["width"] = self.widths[i]

            if type(self.auto_expand) in [tuple, list]:
                options["stretch"] = "always" if i in self.auto_expand else "never"

            if i in self.min_widths and i < len(self.min_widths) and self.min_widths[i] is not None:
                options["minsize"] = self.min_widths[i]

            self.panel.add(frame, sticky=NSEW, **options)

    def custom_config(self, cnf: dict[str, any] | None, **kwargs) -> tuple[dict[str, any], tuple[str | dict, ...]]:
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

        if "title_padx" in cnf:
            self.title_padx = cnf.pop("title_padx")

        if "title_pady" in cnf:
            self.title_pady = cnf.pop("title_pady")

        if "title_height" in cnf:
            self.item_height = cnf.pop("title_height")

        if "title_relief" in cnf:
            self.title_relief = cnf.pop("title_relief")

        if "title_border" in cnf:
            self.title_border = cnf.pop("title_border")

        if "item_padx" in cnf:
            self.item_padx = cnf.pop("item_padx")

        if "item_pady" in cnf:
            self.item_pady = cnf.pop("item_pady")

        if "item_height" in cnf:
            self.item_height = cnf.pop("item_height")

        if "item_relief" in cnf:
            self.item_relief = cnf.pop("item_relief")

        if "item_border" in cnf:
            self.item_border = cnf.pop("item_border")

        if "show_drag" in cnf:
            self.show_drag = cnf.pop("show_drag")

        if "show_drag_item" in cnf:
            self.show_drag_item = cnf.pop("show_drag_item")

        return cnf, columns

    def configure(self, cnf: dict[str, any] | None = None, **kwargs) -> any:
        """Configure this widget"""

        cnf, columns = self.custom_config(cnf, **kwargs)

        ret = self.panel.configure(cnf)

        if columns:
            for (frame, labels) in self.columns:
                self.panel.remove(frame)
                for label in labels:
                    label.destroy()

                frame.destroy()

            self.create_columns(columns)
            self.update_all()
            return

        self.un_select()
        for (frame, labels) in self.columns:
            for label in labels:
                label.config(bg=self.panel["bg"], font=self.font, fg=self.foreground)

        return ret

    config = configure

    def cget(self, key: str) -> any:
        """Get a value from a given key"""

        if "columns" == key:
            return [
                {key: frame.nametowidget("titleLabel").cget(key) for key in frame.nametowidget("titleLabel").keys()}
                for (frame, labels) in self.columns
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

        elif "item_border" == key:
            return self.item_border

        elif "title_padx" == key:
            return self.title_padx

        elif "title_pady" == key:
            return self.title_pady

        elif "title_height" == key:
            return self.title_height

        elif "title_relief" == key:
            return self.title_relief

        elif "title_border" == key:
            return self.title_border

        elif "show_drag" == key:
            return self.show_drag

        else:
            return Frame.cget(self, key)

    __getitem__ = cget

    def __setitem__(self, key, value):
        self.configure({key: value})

    def keys(self):
        return Frame.keys(self) + [
            "show_columns", "show_drag",
            "auto_expand", "resizable", "fixed_columns",
            "min_widths", "widths",
            "select_bg", "select_background",
            "select_fg", "select_foreground", "foreground",
            "font",
            "item_padx", "item_pady", "item_height", "item_relief", "item_border",
            "title_padx", "title_pady", "title_height", "title_relief", "title_border",
        ]

    def get(self, index: int) -> tuple[str] | None:
        """Gets a row's value from the list at a given index"""

        if index is None:
            return None

        if index < 0:
            index += len(self)

        if index < 0 or len(self) <= index:
            return None

        return self.values[index]

    def add(self, values: tuple[str | dict, ...] | list[str | dict, ...], update: bool = True, key: callable = None):
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

        max_height = self.winfo_height() - self.title_height

        font = Font(font=self.font)

        if self.item_height is None:
            item_height = font.metrics("linespace") or 0
        else:
            item_height = self.item_height

        label_height = item_height + 2 * self.item_pady + 2 * self.item_border

        height = 0
        self.rows = 0

        while height <= max_height + label_height:
            row = self.rows
            for column, (frame, labels) in enumerate(self.columns):
                if row >= len(labels):
                    label = Label(
                        frame,
                        font=font,
                        foreground=self.foreground,
                        bg=self["bg"],
                        name="label-" + str(row),
                        pady=self.item_pady,
                        padx=self.item_padx,
                        border=self.item_border,
                        relief=self.item_relief,
                        compound=CENTER,
                        image=self.img_1x1,
                        height=item_height
                    )
                    label.place(x=0, y=row * label_height + self.title_height, relwidth=1, height=label_height)
                    label.bind("<ButtonRelease-1>", lambda e, r=row, c=column: self.on_release(e, r, c))
                    label.bind("<B1-Motion>", lambda e, r=row, c=column: self.after(1, self.on_drag, e, r, c))
                    label.bind("<Button-3>", lambda e, r=row, c=column: self.on_rclick(e, r, c))
                    label.bind("<MouseWheel>", self.on_scroll)
                    label.bind("<Up>", lambda e, c=column, r=row: (
                        self.event_generate("<<Up>>", when="tail", x=c, y=self.current_index + r)
                    ))
                    label.bind("<Down>", lambda e, c=column, r=row: (
                        self.event_generate("<<Down>>", when="tail", x=c, y=self.current_index + r)
                    ))
                    label.bind("<Button-4>", lambda e, c=column, r=row: self.event_generate("<<Back>>", x=c, y=r))
                    label.bind("<Button-5>", lambda e, c=column, r=row: self.event_generate("<<Forwards>>", x=c, y=r))

                    labels.append(label)
                else:
                    labels[row].place(x=0, y=row * label_height + self.title_height, relwidth=1, height=label_height)

            height += label_height
            self.rows += 1

        for frame, labels in self.columns:
            for label in labels[self.rows:]:
                label.place_forget()

        self.update_labels_text()
        self.update_scrollbar()

    def on_drag(self, event: Event, row: int, column: int):
        """Event callback for button 1 mouse motion"""

        if (
                not self.show_drag
                or column not in self.show_drag
        ) and (
                not self.show_drag_item
                or column not in self.show_drag_item
        ):
            return

        self.drag_frame.lift()

        if self.show_drag_item and column in self.show_drag_item:
            for label in self.drag_frame_labels:
                label.grid_forget()

            label = self.drag_frame_labels[column]
            label.grid(
                row=0,
                column=0,
                sticky=NSEW,
                columnspan=len(self.columns) + 1
            )
            label.lift()

            width = event.widget.winfo_width()
        else:
            for i, label in enumerate(self.drag_frame_labels):
                label.grid(row=0, column=i, sticky=NSEW, padx=self.panel.cget("sashwidth"))

            width = self.panel.winfo_width()

        for i, (frame, labels) in enumerate(self.columns):
            label = frame.nametowidget("label-" + str(row))
            for key in event.widget.configure():
                try:
                    self.drag_frame_labels[i].configure({key: event.widget.cget(key)})
                except TclError as err: print(err)

            self.drag_frame_labels[i].configure(
                text=label["text"],
                image=label["image"]
            )

        self.drag_frame.geometry("{w}x{h}+{x}+{y}".format(
            x=event.x_root + 1,  # event.widget.winfo_x() + event.x - self.panel.winfo_x(),
            y=event.y_root + 1,  # event.widget.winfo_y() + event.y - self.panel.winfo_y(),
            w=width,
            h=event.widget.winfo_height(),
        ))

        self.drag_frame.deiconify()

    def on_release(self, event: Event, row: int, column: int):
        """Event callback for mouse release"""

        is_dragged = self.drag_frame.winfo_ismapped()

        self.drag_frame.withdraw()
        self.after(10, self.drag_frame.withdraw)

        event.widget.focus()
        index = self.current_index + row

        dragged_widget: Misc = event.widget.master.winfo_containing(event.x_root, event.y_root)
        if dragged_widget is None:
            return

        dragged_index = None
        for frame, labels in self.columns:
            for i, label in enumerate(labels):
                if label.winfo_id() == dragged_widget.winfo_id():
                    dragged_index = self.current_index + i
                    break

            if dragged_index is not None:
                break

        if dragged_index is None:
            return

        if self.show_columns and dragged_index < 0:
            dragged_index = 0

        if dragged_index >= 0 and len(self) and index < len(self) and 0 <= event.x <= self.winfo_width():
            if index == dragged_index:
                if not is_dragged:
                    self.event_generate("<<Selected>>", when="tail", x=column, y=index)
            else:
                self.event_generate("<<Drag>>", when="tail", x=column, y=index, serial=dragged_index)

    def on_rclick(self, event: Event, row: int, column: int):
        """Event callback for mouse right click"""

        event.widget.focus()
        index = self.current_index + row

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
        row = 0

        while index < len(self) and row <= self.rows:
            values = self.values[index]

            if index >= self.current_index:
                for column, (frame, labels) in enumerate(self.columns):
                    if row < len(labels):
                        label = labels[row]

                        if isinstance(values[column], dict):
                            label.configure(values[column])
                        else:
                            label["image"] = self.img_1x1
                            label["text"] = str(values[column])

                row += 1
            index += 1

        for column, (frame, labels) in enumerate(self.columns):
            for label in labels[row:]:
                label["image"] = self.img_1x1
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

        for (column, labels) in self.columns:
            row = self.selected - self.current_index
            if 0 <= row:
                for label in labels:
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

        row = index - self.current_index

        # set bg
        if 0 <= row <= self.rows:
            for (column, labels) in self.columns:
                if row < len(labels):
                    label = labels[row]
                    label["bg"] = self.select_background
                    label["fg"] = self.select_foreground
