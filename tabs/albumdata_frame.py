from tkinter import *
from PIL import Image

from modules import metadata


class AlbumDataFrame(Frame):
    """
    A simple frame containing data that is global for an album
    """

    artist_name: Entry
    album_name: Entry
    album_date: Entry
    image_preview: Button
    image: Image = None
    thumbnail: PhotoImage = None

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.artist_name = Entry(self)
        self.album_name = Entry(self)
        self.album_date = Entry(self)
        self.image_preview = Button(
            self, text="IMAGE PREVIEW",
            command=lambda: self.winfo_toplevel().event_generate("<<SelectImage>>", when="tail")
        )

        Label(self, text="Album Name:").grid(row=0, column=0, sticky=NSEW, pady=10, padx=10)
        Label(self, text="Artist Name:").grid(row=1, column=0, sticky=NSEW, pady=10, padx=10)
        Label(self, text="Album Date:").grid(row=2, column=0, sticky=NSEW, pady=10, padx=10)
        self.album_name.grid(row=0, column=1, sticky=NSEW, ipady=10, pady=(10, 0), padx=10)
        self.artist_name.grid(row=1, column=1, sticky=NSEW, ipady=10, padx=10)
        self.album_date.grid(row=2, column=1, sticky=NSEW, ipady=10, padx=10)
        self.image_preview.grid(row=3, column=0, columnspan=2, sticky=NSEW, pady=10, padx=10)

        self.rowconfigure(3, weight=1)
        self.columnconfigure(1, weight=1)

        self.bind("<Configure>", lambda e: self.on_resize())

    def on_resize(self):
        """Callback for resize event"""

        self.update()

        self.thumbnail = metadata.thumbnail(self.image, (
            self.image_preview.winfo_width(),
            self.image_preview.winfo_height()
        ))
        if self.thumbnail is None:
            self.image_preview.config(text="IMAGE PREVIEW")
        else:
            self.image_preview.config(text="", image=self.thumbnail)

    def load_image(self, filename: str):
        """Loads an image from a file"""

        self.image = Image.open(filename)
        self.on_resize()

    def load_from_file(self, filename: str):
        """Loads an image from a music file"""

        self.image = metadata.load_image(filename)
        track = metadata.get_track_data_from_filename(filename)

        if track is not None:
            self.on_resize()
            self.album_name.delete(0, END)
            self.artist_name.delete(0, END)
            self.album_date.delete(0, END)
            self.album_name.insert(0, track.album)
            self.artist_name.insert(0, track.artist)
            self.album_date.insert(0, track.date)

    def get(self) -> tuple[Image, str, str, str]:
        """Gets the global data"""

        return self.image, self.album_name.get(), self.artist_name.get(), self.album_date.get()
#
