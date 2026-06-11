import platform
import subprocess
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename

from modules import metadata
from modules.metadata import TrackData
from widgets.dialogs import showinfo, askstring, askint
from widgets.listview import ListView

from PIL import Image

CROSS = "\u274C"
GRIP = "\u283F"

IMAGE_EXTS = {ex for ex, f in Image.registered_extensions().items() if f in Image.OPEN}

GRIP_INDEX = 0
TRACK = 1
THUMBNAIL = 2
TITLE = 3
ALBUM = 4
ARTIST = 5
DATE = 6
CROSS_INDEX = 7
IMAGE = 8
LENGTH = 9


class TracksFrame(Frame):
    """
    A simple frame of tracks
    """

    tracks: ListView
    start_index: Spinbox

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.tracks = ListView(
            self, columns=(GRIP, "#", "Art", "Title", "Album", "Artist", "Date", " "),
            auto_expand=(TITLE, ALBUM, ARTIST),
            title_relief="raised", title_padx=10, title_pady=5,
            widths=[25, 50, 100, 150, 150, 150, 75, 25],
            show_drag=[GRIP_INDEX], show_drag_item=[THUMBNAIL, TITLE, ALBUM, ARTIST, DATE],
            item_height=100, item_relief="ridge", item_border=1,
            sashrelief="raised", sashwidth=5,
        )

        scroll_bar = ttk.Scrollbar(self, command=self.tracks.yview)
        self.tracks.yscrollcommand = scroll_bar.set

        self.tracks.grid(row=1, column=0, columnspan=2, sticky=NSEW)
        scroll_bar.grid(row=1, column=3, sticky=NS)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)

        self.tracks.bind("<<Selected>>", self.on_select)
        self.tracks.bind("<<Drag>>", self.on_drag)
        self.tracks.bind("<<Info>>", self.on_info)

    def get_tracks(self) -> list[tuple[int, str, str, str, str, Image.Image, str, str]]:
        """
        Gets the list of tracks

        Returns:
            A list of track data including:
                Track number
                Track title
                Track album
                Track artist
                Track length
                Track image
                Track length
        """

        return [(
            int(track[TRACK]),
            track[TITLE],
            track[ALBUM],
            track[ARTIST],
            track[DATE],
            track[IMAGE],
            str(track[LENGTH]),
            track[-1],
        ) for i, track in enumerate(self.tracks.values)]

    def add(self, track: TrackData):
        """Adds a track to the list"""

        image = metadata.load_image(track.filename)
        thumbnail = metadata.thumbnail(image, (self.tracks.cget("item_height"), self.tracks.cget("item_height")))

        self.tracks.add([
            GRIP,
            str(track.number),
            {"image": thumbnail, "text": ""} if thumbnail else "No Image",
            track.title,
            track.album,
            track.artist,
            track.date,
            CROSS,
            image,
            track.length,
            track.filename,
        ])

    def on_drag(self, event: Event):
        """Callback for drag event"""

        column = event.x

        from_ = event.y
        to = event.serial

        if column == GRIP_INDEX:
            self.tracks.values.insert(to, self.tracks.values.pop(from_))

            if self.tracks.selected == from_:
                self.tracks.un_select()
                self.tracks.select(to)

            self.tracks.update_all()

        elif column == THUMBNAIL:
            thumbnail = list(self.tracks.get(from_))[THUMBNAIL]
            image = list(self.tracks.get(from_))[IMAGE]
            values = list(self.tracks.get(to))
            if values is not None:
                values[THUMBNAIL] = thumbnail
                values[IMAGE] = image
                self.tracks.set(to, tuple(values))

        elif column in [TITLE, ALBUM, ARTIST, DATE]:
            text = list(self.tracks.get(from_))[column]
            values = list(self.tracks.get(to))
            if values is not None:
                values[column] = text
                self.tracks.set(to, tuple(values))

    def on_select(self, event: Event):
        """Callback for selected event"""

        index = event.y
        column = event.x

        if column == TRACK:
            track = askint("Track Number", "New Track Number of Track:")

            values = list(self.tracks.get(index))
            if track and values is not None:
                values[TRACK] = track
                self.tracks.set(index, tuple(values))

        elif column == THUMBNAIL:
            filename = askopenfilename(filetypes=[("Image Files", " ".join(IMAGE_EXTS)), ("Any", "*")])
            if filename:
                image = Image.open(filename)
                thumbnail = metadata.thumbnail(image, (self.tracks.cget("item_height"), self.tracks.cget("item_height")))

                values = list(self.tracks.get(index))
                if values is not None:
                    values[THUMBNAIL] = {"image": thumbnail, "text": ""}
                    values[IMAGE] = image
                    self.tracks.set(index, tuple(values))

        elif column == TRACK:
            name = askstring("New Name", "New Title of Track:")
            values = list(self.tracks.get(index))
            if name and values is not None:
                values[TRACK] = name
                self.tracks.set(index, tuple(values))

        elif column == ALBUM:
            album = askstring("New Album", "New Album of Track:")
            values = list(self.tracks.get(index))
            if album and values is not None:
                values[ALBUM] = album
                self.tracks.set(index, tuple(values))

        elif column == ARTIST:
            artist = askstring("New Artist", "New Artist of Track:")
            values = list(self.tracks.get(index))
            if artist and values is not None:
                values[ARTIST] = artist
                self.tracks.set(index, tuple(values))

        elif column == DATE:
            date = askstring("New Date", "New Date of Track:")
            values = list(self.tracks.get(index))
            if date and values is not None:
                values[DATE] = date
                self.tracks.set(index, tuple(values))

        elif column == CROSS_INDEX:
            self.tracks.values.pop(index)

        self.tracks.update_all()

    def on_info(self, event: Event):
        """Callback for left click event"""

        index = event.y
        image = self.tracks.get(index)[IMAGE]

        menu = Menu(self, tearoff=0, bd=0, relief="flat")
        menu.add_command(label="Show File Location", command=lambda i=index: self.show_file_location(i), underline=4)
        if image is not None:
            menu.add_separator()
            menu.add_command(label="Save Image", command=lambda art=image: self.save_art(art), underline=7)
            menu.add_separator()
            menu.add_command(label="Remove Image", command=lambda i=index: self.remove_image(i), underline=7)

        try:
            menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
        finally:
            menu.grab_release()

    def remove_image(self, index: int):
        """Removes an image from the given index"""

        values = list(self.tracks.get(index))
        if values is not None:
            values[THUMBNAIL] = "No Image"
            values[IMAGE] = None
            self.tracks.set(index, tuple(values))

    def save_art(self, image: Image):
        """Callback to save the art of a given track"""

        if image is None:
            return

        file = asksaveasfilename(defaultextension="." + image.format, filetypes=[("Image Type", "." + image.format), ("Any", "*")])
        if file:
            image.save(file)

    def show_file_location(self, index: int):
        """Shows the file location of track file with given index"""

        folder = str(self.tracks.get(index)[-1].parent)

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
