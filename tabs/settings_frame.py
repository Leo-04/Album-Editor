import shutil
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename

from modules import metadata
from widgets.listview import ListView
from widgets.dialogs import showinfo

CROSS = "\u274C"
ADD = "\u2795"


class SettingsFrame(Frame):
    """A setting frame"""

    settings: dict
    themes: ListView
    ffmpeg_button: Button
    ffprobe_button: Button

    def __init__(self, master, settings: dict):
        Frame.__init__(self, master, bd=2)
        self.settings = settings

        self.themes = ListView(
            self, columns=("Theme",),
            auto_expand=(0,),
            sashrelief="raised", sashwidth=5, title_relief="raised", title_padx=10, title_pady=5,
            widths=[100], height=150, bd=2, relief="ridge"
        )
        theme_scroll_bar = ttk.Scrollbar(self, command=self.themes.yview)
        self.themes.yscrollcommand = theme_scroll_bar.set

        self.ffmpeg_button = Button(self, text="FFMpeg: " + str(settings["ffmpeg"]), command=lambda: self.choose("ffmpeg"))
        self.ffprobe_button = Button(self, text="FFProbe: " + str(settings["ffprobe"]), command=lambda: self.choose("ffprobe"))

        self.themes.grid(row=0, column=0, sticky=NSEW)
        theme_scroll_bar.grid(row=0, column=1, sticky=NS)
        self.ffmpeg_button.grid(row=1, column=0, columnspan=2, sticky=NSEW, padx=10, pady=10, ipady=10)
        self.ffprobe_button.grid(row=2, column=0, columnspan=2, sticky=NSEW, padx=10, pady=10, ipady=10)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.bind("<Map>", lambda e: self.on_show())
        self.themes.bind("<<Selected>>", self.theme_select)

    def choose(self, name):
        """Callback for choosing ffprobe/ffmpeg path"""

        # Check if we can find it
        if shutil.which(name):
            file = shutil.which(name)
        else:
            file = askopenfilename(filetypes=[("Executable", ".exe"), ("All", "*")])

        if file:
            self.settings[name] = file
            self.ffmpeg_button["text"] = "FFMpeg: " + str(self.settings["ffmpeg"])
            self.ffprobe_button["text"] = "FFProbe: " + str(self.settings["ffprobe"])

            metadata.Paths.ffmpeg = self.settings["ffmpeg"]
            metadata.Paths.ffprobe = self.settings["ffprobe"]

    def theme_select(self, event: Event):
        """Callback for selecting a theme"""

        if event.y != self.themes.selected:
            self.themes.select(event.y)
            self.settings["theme"] = self.themes.values[self.themes.get_selected()][0]

            showinfo("Theme", "Restarted needed")

    def on_show(self):
        """Update values when shown"""

        self.themes.clear()
        for path in self.settings["themes"]:
            self.themes.add([path])
        self.themes.select(self.settings["themes"].index(self.settings["theme"]))
        self.themes.update_all()

    def get_settings(self) -> dict:
        """Returns the new settings"""

        return self.settings
#
