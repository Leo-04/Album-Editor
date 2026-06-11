from widgets.style import LIGHT, DARK, SYSTEM

SYSTEM_THEME = SYSTEM + """
.!playerframe.!sidebuttons.!volumeslider{
    tool-tip: Volume slider;
}
.!playerframe.!actionbuttons.shuffle{
    tool-tip: Shuffle;
}
.!playerframe.!actionbuttons.previous{
    tool-tip: Previous Song;
}
.!playerframe.!actionbuttons.next{
    tool-tip: Next Song;
}
.!playerframe.!actionbuttons.play{
    tool-tip: Play / Pause;
}
.!playerframe.!actionbuttons.loop{
    tool-tip: Repeat;
}
.!notebook.!songsframe.!optionmenu{
    tool-tip: Filter Type;
}
"""

ICON = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00@\x00\x00\x00@\x04\x03\x00\x00\x00XGl\xed\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\x06PLTE\xff\xff\xff\x00\x00\x00U\xc2\xd3~\x00\x00\x00\tpHYs\x00\x00\x0e\xc2\x00\x00\x0e\xc2\x01\x15(J\x80\x00\x00\x00\x84IDATH\xc7\xed\xd5K\n\xc0 \x0c\x04\xd0\xc9\r\xcc\xfd/[\xac-~\'C7\x05\xc1l}\x18\x13\x88\xc1fa\xee\x12\xc4\xe4\x06\x11y\x80\'\x05(\xa9\x80\x90\x16,I.S\x02@\x82\x97\x04\xa0\x90\x10dr\xc0\x01\xdb\x03\xebG\x7f\x02\xe3\xdf0\x01\x17\xc0\x14p\x01\xec+\x98\x86\xb7\x07\xe610\xe7 5\x0f\xa6\xc0"\x00\x060gX\x02p\xd0TN@m\x1d\x03C\xb6`+H`"\x83\xde;\x10\x17\x14\x11\x9e\xff\x1d\xc0\x05\xf3\x87\x1d\xdeo\xac\x0cz\x00\x00\x00\x00IEND\xaeB`\x82'

APP_THEME = SYSTEM_THEME + """
WindowTitle{
    foreground: var(--fg);
    background: var(--fg);
    highlightColor: var(--select_bg);
    border: 1;
}
ListView.Frame.Label{
    font: var(--font) var(--small-font-size);
}
ListView.Frame.titleLabel{
    font: var(--font) var(--large-font-size) bold;
}
.!notebook.buttons.Button {
    font: var(--font) var(--large-font-size);
}
.!notebook.Labelframe {
    font: var(--font) var(--large-font-size) bold;
}
.!notebook.Labelframe.Button, .!notebook.Labelframe.Label{
    font: var(--font) var(--medium-font-size) bold;
}
.!notebook.Labelframe.Entry{
    font: var(--font) var(--small-font-size) bold;
}
.!addtoplaylistwindow.ListView*Label, .!notebook.!playlistframe.ListView.Frame.Label{
    font: var(--font) var(--medium-font-size) bold;
}
.!infowindow.Labelframe{
    font: var(--font) var(--small-font-size) bold;
}
.!infowindow.Labelframe.Label, .!infowindow.Labelframe.Button, .!infowindow.Button{
    font: var(--font) var(--medium-font-size) bold;
}
.!playerframe.!sidebuttons.!volumeslider{
    tool-tip: Volume slider;
}
.!playerframe.!actionbuttons.shuffle{
    tool-tip: Shuffle;
}
.!playerframe.!actionbuttons.previous{
    tool-tip: Previous Song;
}
.!playerframe.!actionbuttons.next{
    tool-tip: Next Song;
}
.!playerframe.!actionbuttons.play{
    tool-tip: Play / Pause;
}
.!playerframe.!actionbuttons.loop{
    tool-tip: Repeat;
}
.!notebook.!songsframe.!optionmenu{
    tool-tip: Filter Type;
}
.!notebook.!playlistframe.!treelist*Button{
    font: var(--font) var(--medium-font-size);
}
"""

LIGHT_THEME = LIGHT + APP_THEME
DARK_THEME = DARK + APP_THEME

ABOUT = """\
Version 2.0

An Open-Source music metadata editor

Repo: https://github.com/Leo-04/Album-Editor

ffmpeg must be installed separately

Dependencies:
- python3
- tkinter
- pillow
- ffmpeg + ffprobe (binary)\
"""

MUSIC_EXTS = {
    ".3gp", ".aa", ".aac", ".aax", ".act", ".aiff", ".alac", ".amr", ".ape", ".au", ".awb", ".dss", ".dvf",
    ".flac", ".gsm", ".iklax", ".ivs", ".m4a", ".m4b", ".m4p", ".mmf", ".movpkg", ".mp3", ".mpc", ".msv",
    ".nmf", ".ogg, .oga, .mogg", ".opus", ".ra, .rm", ".raw", ".rf64", ".sln", ".tta", ".voc", ".vox", ".wav",
    ".wma", ".wv", ".webm", ".8svx", ".cda"
}
