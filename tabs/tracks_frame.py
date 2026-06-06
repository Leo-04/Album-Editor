import platform
import subprocess
import sys
from tkinter import *
from tkinter import ttk

from modules import metadata
from modules.metadata import TrackData
from widgets.dialogs import showinfo, askstring
from widgets.listview import ListView

CROSS = "\u274C"
GRIP = "\u283F"


class TracksFrame(Frame):
    """
    A simple frame of tracks
    """

    tracks: ListView
    start_index: Spinbox

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.start_index = Spinbox(self, from_=0, to=sys.maxsize, command=self.update_track_numbers)
        self.start_index.delete(0, END)
        self.start_index.insert(0, "1")
        self.start_index.config(state="readonly")

        self.tracks = ListView(
            self, columns=("#", "Title", "File Path", " "),
            auto_expand=(1, 2),
            sashrelief="raised", sashwidth=5, title_relief="raised", title_padx=10, title_pady=5,
            widths=[None, 150, 150], show_drag=[0]
        )

        scroll_bar = ttk.Scrollbar(self, command=self.tracks.yview)
        self.tracks.yscrollcommand = scroll_bar.set

        Label(self, text="Start Track Number:").grid(row=0, column=0, sticky=NSEW)
        self.start_index.grid(row=0, column=1, columnspan=3, sticky=NSEW)
        self.tracks.grid(row=1, column=0, columnspan=2, sticky=NSEW)
        scroll_bar.grid(row=1, column=3, sticky=NS)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

        self.tracks.bind("<<Selected>>", self.on_select)
        self.tracks.bind("<<Drag>>", self.on_drag)
        self.start_index.bind("<MouseWheel>", lambda e: self.start_index.invoke(
            "buttonup" if e.delta > 0 else "buttondown"
        ))

    def get_tracks(self) -> list[tuple[int, str, str, str]]:
        """
        Gets the list of tracks

        Returns:
            A list of track data including:
                Track number
                Track title
                Track filename
                Track length
        """

        try:
            int(self.start_index.get())
        except ValueError:
            showinfo("Error", "Invalid start index:\n" + self.start_index.get())

        return [(
            i + int(self.start_index.get()),
            track[1],
            track[-1].filename,
            str(track[-1].length)
        ) for i, track in enumerate(self.tracks.values)]

    def add(self, track: TrackData):
        """Adds a track to the list"""

        self.tracks.add([GRIP, track.title, track.filename, CROSS, track])

        self.update_track_numbers()

    def update_track_numbers(self):
        """Updates the track number beside each track"""

        try:
            start = int(self.start_index.get())
        except ValueError:
            showinfo("Error", "Invalid start index:\n" + self.start_index.get())
            start = 1

        for i in range(len(self.tracks.values)):
            self.tracks.values[i] = (GRIP + " " + str(start + i), *self.tracks.values[i][1:])

        self.tracks.update_all()

    def on_drag(self, event: Event):
        """Callback for drag event"""

        column = event.x
        if column != 0:
            return

        from_ = event.y
        to = event.serial

        self.tracks.values.insert(to, self.tracks.values.pop(from_))

        if self.tracks.selected == from_:
            self.tracks.un_select()
            self.tracks.select(to)

        self.update_track_numbers()

    def on_select(self, event: Event):
        """Callback for selected event"""

        index = event.y
        column = event.x

        if column == 1:
            name = askstring("New Name", "New Title of Track:")
            values = list(self.tracks.get(index))
            if name and values is not None:
                values[1] = name
                self.tracks.set(index, tuple(values))

        elif column == 2:
            folder = str(self.tracks.get(index)[-1].filename.parent)

            plat = platform.system()
            if plat == "Windows":
                cmd = ['explorer', folder]
            elif plat == "Linux":
                cmd = ['xdg-open', folder]
            elif plat == "Darwin":
                cmd = ['open', folder]
            else:
                showinfo("Unknown OS", "Don't know what da hell you running this on lol")
                return

            subprocess.Popen(cmd)

        elif column == 3:
            self.tracks.values.pop(index)

        self.update_track_numbers()
