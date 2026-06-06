from tkinter import *
from tkinter import ttk
from modules import parser

# Parser rules

style_tokens = [
    ('Var', r'var\([a-zA-Z0-9_.!*-]+\)'),
    ('Name', r'[a-zA-Z0-9_.!*-]+'),
    ('OpenTags', r'\{'),
    ('CloseTags', r'\}'),
    ('Tag', r'\:'),
    ('Comma', r'\,'),
    ('String', r'"([^\\"]*(\\.)?)*"'),
    ('SKIP', r'(\s+)|(?:/\*(.*?)\*/)'),
    ('Value', r'[^;]+'),
    ('SemiColon', r';'),
]

style_groups = {
    "<Names>": {"any": [["Name", "Comma", "<Names>"], "Name"]},
    "<Def>": ["<Names>", "OpenTags", {"multiple": "<Body>"}, "CloseTags"],
    "<Body>": ["Name", "Tag", "<Value>", "SemiColon"],
    "<Value>": {"multiple": {"any": ["SKIP", "String", "Var", "Value", "Name", "Comma", "Tag", "CloseTags", "OpenTags"]}},
    "<File>": {"multiple": "<Def>"}
}

r"""
Var "var\([a-zA-Z0-9_.!*-]+\)"
Name "[a-zA-Z0-9_.!*-]+"
OpenTags "\{"
CloseTags "\}"
Tag "\:"
Comma "\,"
String "\"([^\\"]*(\\.)?)*\""
SKIP "(\s+)|(?:/\*(.*?)\*/)"
Value "[^;]+"
SemiColon ";"

<Names> ::= (Name Comma <Names> | Name);
<Def> ::= <Names> OpenTags <Body>* CloseTags;
<Body> ::= Name Tag <Value> SemiColon;
<Value> ::= (SKIP | String | Var | Value | Name | Comma | Tag | CloseTags | OpenTags)*;
<File> ::= <Def>*;
"""


class StyleParser:
    @staticmethod
    def parse_file(file: parser.Statement) -> list[tuple[list[str], dict[str, str]]]:
        """Parses a <File> Statement"""

        variables = {}
        assert file.name == "<File>"

        defs = []
        for statement in file.value:
            defs.append(StyleParser.parse_def(statement, variables))

        return defs

    @staticmethod
    def parse_def(statement: parser.Statement, variables: dict[str, str]) -> tuple[list[str], dict[str, str]]:
        """Parses a <Def> Statement"""

        assert statement.name == "<Def>"

        names = StyleParser.parse_names(statement.value[0])
        value_pairs = StyleParser.parse_body(statement.value[2], variables)

        return names, value_pairs

    @staticmethod
    def parse_body(body: list[parser.Statement], variables: dict[str, str]):
        """Parses a list of <Body> Statements"""

        value_pairs = {}

        for statement in body:
            assert statement.name == "<Body>"
            assert statement.value[0].type == "Name"

            name = statement.value[0].value
            value = StyleParser.parse_value(statement.value[2], variables)

            value_pairs[name] = value
            variables[name] = value

        return value_pairs

    @staticmethod
    def parse_value(values: parser.Statement, variables: dict[str, str]) -> str:
        """Parses a <Value> statement"""

        assert values.name == "<Value>"

        value = ""
        for val in values.value:
            if val.type == "SKIP" and value == "":
                pass
            elif val.type == "Var":
                var_name = val.value[4:-1]
                if var_name in variables:
                    var_name = variables[var_name]

                value += var_name
            else:
                value += val.value

        return value

    @staticmethod
    def parse_names(statement: parser.Statement | parser.Token | list[...]) -> list[str]:
        """Parses a <Names> statement"""

        if isinstance(statement, parser.Statement) and statement.name == "<Names>":
            return StyleParser.parse_names(statement.value)
        if isinstance(statement, parser.Token) and statement.type == "Name":
            return [statement.value]
        elif isinstance(statement, list):
            return StyleParser.parse_names(statement[0]) + StyleParser.parse_names(statement[2])
        else:
            raise Exception(f"Invalid token for name: {statement}")


class Style:
    """
    A style configuration class for tkinter widgets

    Similar to ttk.Style but uses `Tk.option_*`
    To set defaults for widgets

    Due to limitation we still have to use `ttk.Style` for scrollbars
    """

    root: Tk
    style: ttk.Style

    def __init__(self, root: Tk):
        self.root = root
        self.style = ttk.Style(self.root)

    def load(self, string: str, filename: str):
        """
        Loads a style from a string

        Parameters:
            string: str
                The string
            filename: str
                The filename
        """

        tokens = parser.tokenize(string, style_tokens, filename)
        statements = parser.parse_statements("<File>", style_groups, tokens)
        defs = StyleParser.parse_file(statements)

        all_values = {}
        widget_values = {}
        class_values = {}

        i = 0
        for names, d in defs:
            for name in names:
                for option, value in d.items():

                    if name == "*":
                        all_values[option] = value
                    elif name[0] == ".":
                        if self.root.winfo_name() + name not in widget_values:
                            widget_values[self.root.winfo_name() + name] = []
                        widget_values[self.root.winfo_name() + name].append((option, value))
                    else:
                        if name not in class_values:
                            class_values[name] = []
                        class_values[name].append((option, value))

                    self.set(name, option, value)
                    i += self.get(name, option) != value

        self.sort_out_awkward_widgets()

    def set(self, pathname: str, option: str, value: str):
        """
        Sets an option for a given widget name

        Parameters:
            pathname: str
                The pathname of the widget
                Path-name's can be in the form:
                "*" -> for all widgets
                "WidgetName" -> for a widget class "WidgetName"
                ".!OtherWidgetName.WidgetName" -> for the absolute path to "WidgetName"

            option: str
                The option to set

            value: str
                The value of the option
        """

        if len(pathname):
            if pathname == "*":
                self.root.option_add("*" + option, value, "startupFile")
            elif pathname[0] == ".":
                self.root.option_add(self.root.winfo_name() + pathname + "." + option, value, "startupFile")
            else:
                self.root.option_add("*" + pathname + "." + option, value, "startupFile")

            self.sort_out_awkward_widgets()

    def get(self, pathname: str, option: str):
        """Gets the option for a given pathname (see `Style.set` for explanation on path-names)"""

        if pathname == "*":
            return self.root.option_get(option, "*")
        elif pathname[0] == ".":
            return self.root.option_get(option, self.root.winfo_name() + pathname)
        else:
            return self.root.option_get(option, "*" + pathname)

    def sort_out_awkward_widgets(self):
        """Sort out scrollbars"""

        fg = self.get("Scrollbar", "foreground")
        bg = self.get("Scrollbar", "background")
        abg = self.get("Scrollbar", "activeBackground")

        if fg and bg and abg:
            self.style.theme_use("alt")
            self.style.configure(
                "TScrollbar",
                gripcount=2,
                background=abg,
                darkcolor=bg,
                lightcolor=fg,
                troughcolor=bg,
                bordercolor=bg,
                arrowcolor=fg,
            )
            self.style.map(
                "TScrollbar",
                background=[
                    ("disabled", bg),
                    ("active", abg)
                ]
            )

            self.root["bg"] = bg


# Default themes

LIGHT = """\
* {
    --fg: #333333;
    --bg: #CCCCCC;
    --select_fg: #333333;
    --select_bg: #00FFFF;

    --input_bg: #EEEEEE;

    --disabled_fg: #989898;
    --disabled_bg: #555555;

    --font: consolas;
    --small-font-size: 10;
    --medium-font-size: 15;
    --large-font-size: 20;

    foreground: var(--fg);
    background: var(--bg);

    troughColor: var(--input_bg);

    activeBackground: #999999;
    activeForeground: var(--fg);

    disabledForeground: var(--disabled_fg);

    highlightColor: var(--select_bg);
    highlightBackground: var(--select_bg);

    selectForeground: var(--select_fg);
    selectBackground: var(--select_bg);
    selectColor: var(--select_bg);

    insertBackground: var(--select_fg);

    font: var(--font) var(--small-font-size);
}
Spinbox {
    buttonBackground: #DDDDDD;
    disabledBackground: var(--disabled_bg);
    readonlyBackground: #DDDDDD;
}
Menu {
    activeForeground: var(--select_fg);
    activeBackground: var(--select_bg);

    font: TkDefaultFont 8;
}
Menubutton{
    highlightBackground: #DDDDDD;
    highlightColor: #DDDDDD;
}
Text{
    inactiveSelectBackground: var(--select_bg);
}
Entry, Text{
    background: var(--input_bg);
}
Listbox {
    activeStyle: underline;
}
"""
DARK = """\
* {
    --fg: #DDDDDD;
    --bg: #2B2B2B;
    --select_fg: #FFFFFF;
    --select_bg: #0000FF;

    --input_bg: #3F3F3F;

    --disabled_fg: #989898;
    --disabled_bg: #555555;

    --font: consolas;
    --small-font-size: 10;
    --medium-font-size: 15;
    --large-font-size: 20;

    foreground: var(--fg);
    background: var(--bg);

    troughColor: var(--input_bg);

    activeBackground: #999999;
    activeForeground: var(--fg);

    disabledForeground: var(--disabled_fg);

    highlightColor: var(--select_bg);
    highlightBackground: var(--select_bg);

    selectForeground: var(--select_fg);
    selectBackground: var(--select_bg);
    selectColor: var(--select_bg);

    insertBackground: var(--select_fg);

    font: var(--font) var(--small-font-size);
}
Spinbox {
    buttonBackground: #222222;
    disabledBackground: var(--disabled_bg);
    readonlyBackground: #222222;
}
Menu {
    activeForeground: var(--select_fg);
    activeBackground: var(--select_bg);

    font: TkDefaultFont 8;
}
Menubutton{
    highlightBackground: var(--bg);
    highlightColor: var(--bg);
}
Text{
    inactiveSelectBackground: var(--select_bg);
}
Entry, Text{
    background: var(--input_bg);
}
Listbox {
    activeStyle: underline;
}
"""
SYSTEM = ""
