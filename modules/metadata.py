import json
import shutil
import subprocess
from datetime import datetime

from PIL import Image, UnidentifiedImageError, ImageFile
from PIL import ImageTk
import os
from io import BytesIO
from pathlib import Path
import re


class Paths:
    """Hard paths for ffmpeg"""

    ffmpeg: str = shutil.which("ffmpeg")
    ffprobe: str = shutil.which("ffprobe")


class TrackData:
    """
    Basic data for a track
    """

    number: int
    title: str
    album: str
    artist: str
    folder: Path
    filename: Path
    date: str
    length: int

    def __init__(self, track_number: int, title: str, album: str, artist: str, folder: Path, filename: Path, date: str, length: int):
        self.number = track_number
        self.title = title
        self.album = album
        self.artist = artist
        self.folder = folder
        self.filename = filename
        self.length = length
        self.date = date

    def get_len(self) -> str:
        """Gets the length as a formatted string"""

        h = int(self.length) // (60 * 60)
        m = (int(self.length) // 60) % 60
        s = int(self.length) % 60

        return "%02d:%02d:%02d" % (h, m, s)

    def __repr__(self):
        return "[%i]'%s' %s {%s} %s" % (self.number, self.title, self.artist, self.album, self.get_len())

    def __iter__(self):
        return iter([self.number, self.title, self.album, self.artist, self.get_len(), self.filename, self.folder])


def get_track_data_from_filename(file_path: Path | str, index: int = 1) -> TrackData | None:
    """
    Tries to get track data from a file_path

    Tries to get track data from a file
    If we are able to open the tags, but none are present, we use the folder data & `index` as default values

    Args:
        file_path: Pathlike
            The path to the file

        index: int
            the position the file is listed in

    Returns:
        The track data from the file OR None

    """

    file_path = Path(file_path)
    track_number = index
    title = file_path.stem
    album = file_path.parent.name
    artist = "\u2047\uFF1F Unknown Artist \uFF1F\u2047"
    folder = file_path.parent.absolute()
    file_path = file_path.absolute()
    date = str(datetime.now().year)

    result = subprocess.run(
        [
            Paths.ffprobe,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format", str(file_path)
        ],
        capture_output=True,
        creationflags=0 if os.name != 'nt' else subprocess.CREATE_NO_WINDOW
    )

    tags = {}
    try:
        string_result = result.stdout.decode("UTF-8")
        json_result = json.loads(string_result)

        length = float(json_result["format"]["duration"])
        tags = json_result["format"]["tags"]
    except IndexError:
        pass
    except KeyError:
        pass
    except json.JSONDecodeError:
        pass

    for tag in ["artist", "albumartist", "author", "Albumartist", "Artist", "AlbumArtist", "Author"]:
        if tag in tags:
            artist = tags[tag]
            break

    for tag in ["album", "Album"]:
        if tag in tags:
            album = tags[tag]
            break

    for tag in ["year", "Year", "date", "Date"]:
        if tag in tags:
            date = tags[tag]
            break

    for tag in ["title", "Title"]:
        if tag in tags:
            title = tags[tag]
            break

    for tag in ["tracknumber", "track", "number", "Tracknumber", "TrackNumber", "Track", "Number", "trck"]:
        if tag in tags:
            number = re.search(r'\d+', tags[tag])
            if number:
                track_number = int(number.group())
                break

    return TrackData(track_number, title, album, artist, folder, file_path, date, length)


def load_image(file_path: Path | str) -> ImageFile:
    """
    Loads image data from a music file

    Tries to open a music file and find an image, extracting it to a PIL Image.
    If the image cannot be opened, or if there is no image tag, None is returned

    Args:
        file_path: str | PathLike
            A string or path like object to the file

    Returns:
        The image data loaded or None
    """

    result = subprocess.run(
        [
            Paths.ffmpeg,
            "-hide_banner",
            "-i", str(file_path),
            "-an",
            "-vcodec", "copy",
            "-f", "image2pipe",
            "pipe:1",
            "-v", "error"
        ],
        capture_output=True,
        creationflags=0 if os.name != 'nt' else subprocess.CREATE_NO_WINDOW
    )

    byte_array = BytesIO(result.stdout)

    try:
        return Image.open(byte_array)
    except UnidentifiedImageError:
        print("Cant open tag:", file_path, result.stdout)

    return None


def thumbnail(img: Image.Image, size: tuple[int, int] | list[int]) -> ImageTk.PhotoImage | None:
    """
    Loads a PhotoImage from a music file and resizes it

    Tries to open a music file and find an image extracting it to a PIL Image and resizing it, then convert it to a PhotoImage.
    If the image cannot be opened, or if there is no image tag, None is returned

    Args:
        img: Image.ImageFile
            A image

        size: tuple[int, int]
            A 2 tuple int that contains the width and height of the image

    Returns:
        The loaded image or None
    """

    if img is None:
        return

    image = Image.new('RGBA', size, (0, 0, 0, 0))
    img = img.copy()
    img.thumbnail(size, Image.Resampling.LANCZOS)

    img_w, img_h = img.size
    w, h = image.size
    center = ((w - img_w) // 2, (h - img_h) // 2)
    image.paste(img, center)

    return ImageTk.PhotoImage(image)


def save_metadata(filename: str, output: str, image: str | None, track: int, title: str, album: str, artist: str, year: str, length: str):
    """
    Copy the given input file to the given output file with the given metadata

    Parameters:
        filename: str
            The input file

        output: str
            The ouput file

        image: str | None
            An optional image

        track: int
        title: str
        album: str
        artist: str
        year: str
        length: str
            The given metadata
    """

    if image is not None:
        cmd = [
            Paths.ffmpeg,
            "-i", str(filename),
            "-i", image,
            "-map", "0:0",
            "-map", "1:0",
            "-c", "copy",
            "-id3v2_version", "3",
            "-ss", "0",
            "-t", length,
            '-metadata:s:v', "title=Album cover",
            '-metadata:s:v', "comment=Cover (front)",
            "-metadata", "track=" + str(track),
            "-metadata", "title=" + str(title),
            "-metadata", "album=" + str(album),
            "-metadata", "artist=" + str(artist),
            "-metadata", "year=" + str(year),
            "-metadata", "date=" + str(year),
            "-f", str(filename).split(".")[-1],
            str(output)
        ]
    else:
        cmd = [
            Paths.ffmpeg,
            "-i", str(filename),
            "-c", "copy",
            "-id3v2_version", "3",
            "-ss", "0",
            "-t", length,
            "-metadata", "track=" + str(track),
            "-metadata", "title=" + str(title),
            "-metadata", "album=" + str(album),
            "-metadata", "artist=" + str(artist),
            "-metadata", "year=" + str(year),
            "-metadata", "date=" + str(year),
            "-f", str(filename).split(".")[-1],
            str(output)
        ]

    process = subprocess.run(
        cmd,
        capture_output=True,
        check=False
    )

    if process.returncode:
        raise Exception(process.stderr.decode("UTF-8"))

#
