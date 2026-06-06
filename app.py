import json
import os
import sys
from tkinter import *
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename, askdirectory

from modules import metadata
from tabs.albumdata_frame import AlbumDataFrame
from tabs.settings_frame import SettingsFrame
from tabs.tracks_frame import TracksFrame

from widgets.dialogs import showinfo, askyesno
from widgets.progress_bar import ProgressBar
from widgets.tk_menu import TkMenu
from widgets.tooltips import ToolTips
from widgets.wincnf import WindowCnf
from widgets.style import Style
from widgets.notebook import Notebook

from resources import *


def dir_path(local_path: str):
    """
    Finds the path of the current executable file or script

    Parameters:
        local_path: str | PathLike
            The local path to a file or folder

    Returns:
        The full absolute path to the file / folder
    """

    # Check if this script exists
    if os.path.exists(__file__):
        exe = __file__

    # If not, then we have probably been compiled and is located in sys.executable
    else:
        exe = sys.executable

    # Get the path
    return os.path.join(os.path.dirname(exe), local_path)


class App(Tk):
    """
    Main application instance
    """

    def __init__(self, argv: list[str]):
        """
        Creates an application instance

        Parameters:
            argv: list[str]
                The command line arguments
        """

        # Config window
        Tk.__init__(self)
        Label(
            self, name="splashScreen", text="Loading...", font=(None, 50), bg="black", fg="light grey"
        ).place(x=0, y=0, relwidth=1, relheight=1)

        self.minsize(600, 700)
        self.geometry("600x700")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.title("AlbumEditor")
        self.cnf = WindowCnf(self)
        image = PhotoImage(data=ICON)
        self.iconphoto(True, image)
        self.style = Style(self)
        # Load data
        self.check_paths_exist()
        settings = self.load_settings()
        self.load_theme_from_settings(settings)

        self.tips = ToolTips(self, highlightthickness=1)
        menubar = TkMenu(
            self,
            dict(text="Load Album Data From Track", hotkey="<Control-l>", command=self.load_data),
            dict(text="Add Tracks", hotkey="<Control-o>", command=self.add_tracks),
            None,
            dict(text="Output To Folder", hotkey="<Control-d>", command=self.output),
            dict(text="Save Album Art", hotkey="<Control-s>", command=self.save_art),
        )
        self.tabs = Notebook(self, panel_size=50)
        self.album_data = AlbumDataFrame(self.tabs)
        self.settings = SettingsFrame(self.tabs, settings)
        self.tracks = TracksFrame(self.tabs)
        self.progress = ProgressBar(self, bd=3, relief="sunken", height=30)

        self.tabs.add(text="💽 Album Data ", frame=self.album_data)
        self.tabs.add(text="\u2630 Tracks ", frame=self.tracks)
        self.tabs.add(text="⚙️ Settings ", frame=self.settings, side=RIGHT)

        menubar.grid(row=0, column=0, sticky=NSEW)
        self.tabs.grid(row=1, column=0, sticky=NSEW)
        self.progress.grid(row=2, column=0, sticky=NSEW)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.tabs.select(0)

        if metadata.Paths.ffmpeg is None:
            metadata.Paths.ffmpeg = settings["ffmpeg"]
        if metadata.Paths.ffprobe is None:
            metadata.Paths.ffprobe = settings["ffprobe"]

        if metadata.Paths.ffmpeg is None:
            showinfo("Error", "FFMpeg is not found\nPlease check the settings to give the correct path")
        if metadata.Paths.ffprobe is None:
            showinfo("Error", "FFProbe is not found\nPlease check the settings to give the correct path")

        self.bind("<<SelectImage>>", lambda e: self.load_image())

    def add_tracks(self):
        """Callback to add tracks"""

        files = askopenfilenames(filetypes=[("Music files", " ".join(MUSIC_EXTS)), ("Any", "*")])
        if not files:
            return

        for i, file in enumerate(files):
            track = metadata.get_track_data_from_filename(file, i + 1)
            self.tracks.add(track)
            self.progress.set(i / len(files))
            self.update()
        self.progress.set(0)

    def load_data(self):
        """Callback to load data from a track"""

        file = askopenfilename(filetypes=[("Music files", " ".join(MUSIC_EXTS)), ("Any", "*")])
        if file:
            self.album_data.load_from_file(file)

    def load_image(self):
        """Callback to load an image"""

        file = askopenfilename(filetypes=[("Image Files", " ".join(IMAGE_EXTS)), ("Any", "*")])
        if file:
            self.album_data.load_image(file)

    def save_art(self):
        """Callback to save the art currently loaded"""

        if self.album_data.image is None:
            return

        file = asksaveasfilename(filetypes=[("Image Type", self.album_data.image.format), ("Any", "*")])
        if file:
            self.album_data.image.save(file)

    def output(self):
        """Callback to do the output"""

        folder = askdirectory()
        if not folder:
            return

        image, album_name, artist_name, date = self.album_data.get()

        if image:
            image_path = os.path.join(folder, "art.png")
            image.save(image_path)
        else:
            image_path = None

        tracks = self.tracks.get_tracks()
        for track_number, track_title, filename, length in tracks:
            output = os.path.join(folder, filename.name)
            try:
                print(output)
                metadata.save_metadata(
                    filename,
                    output,
                    image_path,
                    track_number,
                    track_title,
                    album_name,
                    artist_name,
                    date,
                    length
                )
            except Exception as err:
                print(err)
                showinfo("Failed to save metadata", "Failed to save metadata")

            self.progress.set(track_number / len(tracks))
            self.update()
        self.progress.set(0)

    def close(self):
        """Callback for close event"""

        if askyesno("Quit", "Are you sure you want to quit?", default=True):
            try:
                json.dump(self.settings.get_settings(), open(dir_path("data/settings.json"), "w"))
            except Exception as err:
                showinfo("Error", "Could not save settings\nError: " + str(err))

            self.destroy()

    def check_paths_exist(self):
        """
        Check if the application's data paths exist
        Creates data and themes folders if they do not exist
        Creates the 3 basic themes if they do not exist

        If any error occurs, then an information window is shown
        """

        if not os.path.exists(dir_path("data/")):
            try:
                os.mkdir(dir_path("data/"))
                os.mkdir(dir_path("data/themes"))
            except Exception as err:
                showinfo("Error", "Cannot create data folder\nError: " + str(err), root=self)

        # Check for each default theme
        try:
            if not os.path.exists(dir_path("data/themes/system")):
                with open(dir_path("data/themes/system"), "w") as fp:
                    fp.write(SYSTEM_THEME)

            if not os.path.exists(dir_path("data/themes/light")):
                with open(dir_path("data/themes/light"), "w") as fp:
                    fp.write(LIGHT_THEME)

            if not os.path.exists(dir_path("data/themes/dark")):
                with open(dir_path("data/themes/dark"), "w") as fp:
                    fp.write(DARK_THEME)

        except Exception as err:
            showinfo("Error", "Cannot create themes folder\nError: " + str(err), root=self)

    def load_settings(self) -> dict:
        """
        Attempts to load the settings for the data path
        If any error occurs, then an information window is shown

        Returns:
            The settings
        """

        # Load settings
        try:
            settings = json.load(open(dir_path("data/settings.json")))

            # Error if format is wrong
            if (
                    type(settings["theme"]) != str
                    or (type(settings["ffmpeg"]) != str
                        and settings["ffmpeg"] is not None)
                    or (type(settings["ffprobe"]) != str
                        and settings["ffprobe"] is not None)
            ):
                raise TypeError()
        except Exception as err:
            settings = {
                "theme": "dark",
                "ffmpeg": None,
                "ffprobe": None,
            }

            self.load_theme_from_settings(settings)
            showinfo("Error", "Could not load settings\nError: " + str(err), root=self)

        return settings

    def load_theme_from_settings(self, settings: dict):
        """
        Load the currently selected theme from settings,
        Default to dark mode if any error occurs

        Parameters:
            settings: dict
                The applications settings loaded from a json file
        """

        # Load style
        settings["themes"] = []
        try:
            settings["themes"] = os.listdir(dir_path("data/themes/"))
            path = dir_path("data/themes/" + settings["theme"])
            self.style.load(open(path).read(), path)
        except Exception as err:
            self.style.load(DARK_THEME, "DarkTheme")
            showinfo("Error", f"Could not load theme {'`'}{settings['theme']}{'`'}\nError: \n{err}")

        # Configure window styles
        try:
            if self.style.get("WindowTitle", "foreground"):
                self.cnf.fg = self.style.get("WindowTitle", "foreground")
            if self.style.get("*WindowTitle", "background"):
                self.cnf.bg = self.style.get("*WindowTitle", "background")
            if self.style.get("WindowTitle", "highlightColor"):
                self.cnf.bd = self.style.get("WindowTitle", "highlightColor")

            self.cnf.corner = WindowCnf.SQUARE
        except Exception as err:
            # These can go wrong in so many more ways, just ignore the error
            print("ERROR:", err)
