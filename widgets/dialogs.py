from tkinter import *
from tkinter import _get_default_root


class DialogWindow(Toplevel):
    """A simple dalog window"""

    value: any
    variable: Variable

    default_value: any
    root: Tk | Toplevel
    width: int
    height: int
    focus_widget: Widget | None = None

    def __init__(self,
                 title: str = "",
                 root: Tk | Toplevel = None,
                 width: int = 300,
                 height: int = 200,
                 custom_title: bool = False,
                 close_on_deselect: bool = False,
                 default_value: any = None):

        if root is None:
            root = _get_default_root()
        else:
            root = root.winfo_toplevel()

        Toplevel.__init__(self, root, class_='DialogWindow')
        self.withdraw()
        self.title(title)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.config(relief="ridge", bd=1)
        self.geometry("%sx%s" % (width, height))

        self.variable = Variable(self)
        self.value = default_value
        self.default_value = default_value
        self.root = root
        self.width = width
        self.height = height

        if custom_title:
            self.overrideredirect(True)
        else:
            self.transient(root)
            self.resizable(False, False)

        if close_on_deselect:
            self.bind("<FocusOut>", lambda e: self.default())

        self.bind("<Escape>", lambda e: self.default())

        self.set(default_value)

    def close(self):
        """Callback for when window closes"""

        self.default()

    def default(self):
        """Sets the value of `variable` to a default value"""

        self.variable.set(self.default_value)
        self.value = self.default_value

    def set(self, value: any):
        """
        Sets the value
        """
        self.variable.set(value)
        self.value = value

    def position(self):
        """Position the dalog in the middle of the window"""

        # This is duplicated to stop flickering
        self.geometry("+%s+%s" % (
            self.root.winfo_x() + (self.root.winfo_width() - self.winfo_width()) // 2,
            self.root.winfo_y() + (self.root.winfo_height() - self.winfo_height()) // 2,
        ))
        self.deiconify()
        self.update()
        self.update_idletasks()
        self.geometry("+%s+%s" % (
            self.root.winfo_x() + (self.root.winfo_width() - self.winfo_width()) // 2,
            self.root.winfo_y() + (self.root.winfo_height() - self.winfo_height()) // 2,
        ))

    def get(self, force_focus: bool = True, no_move: bool = True) -> any:
        """
        Opens the Dialog to get a value from the user

        Parameters:
            force_focus: bool
                Forces focus onto the dialog
                Makes sure that you cannot select other windows while it is open

            no_move: bool
                Forces the dialog to be unmovable

        Returns:
            The value the user selected
            If the operation was canceled, `self.default_value` is returned
        """

        self.set(self.default_value)

        self.position()
        self.focus()
        if force_focus:
            self.grab_set()
        if no_move:
            self.grab_set_global()

        if self.focus_widget is None:
            self.focus_force()
        else:
            self.focus_widget.focus_force()

        self.wait_variable(self.variable)

        if force_focus:
            self.grab_release()
        self.withdraw()

        return self.value


class OptionDialog(DialogWindow):
    """A simple option dialog window"""

    yes_no_cancel = (("Yes", True), ("No", False), ("Cancel", None))
    yes_no = (("Yes", True), ("No", False))
    ok_cancel = (("Ok", True), ("Cancel", None))
    retry_cancel = (("Retry", True), ("Cancel", None))
    ok = (("Ok", True),)

    message: Message
    buttons: Frame

    def __init__(self,
                 title: str,
                 message: str,
                 options: list[tuple[str, any]] = ok,
                 default: any = None,
                 default_on_return: any = True,
                 root: Tk | Toplevel = None,
                 width: int = 300,
                 height: int = 200,
                 close_on_deselect: bool = False):
        DialogWindow.__init__(self, title, root, width, height, False, close_on_deselect, default)

        self.message = Message(self, name="message", text=message, width=width, justify=CENTER)
        self.buttons = Frame(self, name="button_frame", relief="raised", bd=1)

        for option in options:
            if type(option) in [tuple, list]:
                item = option[0]
                value = option[1]
            else:
                item = option
                value = option

            Button(self.buttons, text=item, command=lambda val=value: self.set(val)).pack(side=LEFT, fill=X, padx=10, pady=10, expand=1)

        self.message.pack(side=TOP, fill=BOTH, expand=1)
        self.buttons.pack(side=BOTTOM, fill=X)

        self.bind("<Return>", lambda e: self.set(default_on_return))

    def set_message(self, string):
        self.message["text"] = string


class InputDialog(DialogWindow):
    """A simple dialog with an input field"""

    def __init__(self,
                 title: str,
                 message: str,
                 validate: callable = lambda s: True,
                 default: any = None,
                 insert: str = "",
                 root: Tk | Toplevel = None,
                 width: int = 400,
                 height: int = 150,
                 close_on_deselect: bool = False):
        DialogWindow.__init__(self, title, root, width, height, False, close_on_deselect, default)

        self.message = Label(self, name="message", text=message)
        self.entry = Entry(self, name="entry", validate='all', validatecommand=(self.register(validate), '%P'))
        self.ok = Button(self, name="ok", text="Ok", command=lambda: self.set(self.entry.get()))
        self.cancel = Button(self, name="cancel", text="Cancel", command=self.default)

        self.insert = insert
        self.type = type
        self.focus_widget = self.entry

        self.message.pack(side=TOP, fill=BOTH, expand=1, padx=10, pady=10)
        self.entry.pack(side=TOP, fill=X, padx=10)
        self.ok.pack(side=LEFT, fill=X, expand=1, padx=10, pady=10)
        self.cancel.pack(side=RIGHT, fill=X, expand=1, padx=10, pady=10)

        self.bind("<Return>", lambda e: self.set(self.entry.get()))
        self.entry.bind("<Return>", lambda e: self.set(self.entry.get()))

    # @override
    def get(self, force_focus=True, no_move=True) -> any:
        """Overwritten method"""

        self.entry.delete(0, END)
        self.entry.insert(0, self.insert)
        self.entry.focus_force()

        return DialogWindow.get(self, force_focus, no_move)


def dialog(dialog_window):
    result = dialog_window.get()
    dialog_window.destroy()

    return result


def showinfo(title: str = "", message: str = "", **options):
    """Shows information to the user"""

    return dialog(OptionDialog(title, message, OptionDialog.ok, **options))


def askokcancel(title: str = "", message: str = "", **options):
    """Shows asks the user to pick ok or cancel"""

    return dialog(OptionDialog(title, message, OptionDialog.ok_cancel, **options))


def askyesno(title: str = "", message: str = "", **options):
    """Shows asks the user to pick yes or no"""

    return dialog(OptionDialog(title, message, OptionDialog.yes_no, **options))


def askstring(title: str = "", message: str = "", **options):
    """Asks the user for a string"""

    return dialog(InputDialog(title, message, **options))


def askint(title: str = "", message: str = "", **options):
    """Asks the user for an integer"""

    return dialog(InputDialog(title, message, validate=lambda s: s.isdigit(), **options))


def askfloat(title: str = "", message: str = "", **options):
    """Asks the user for a float"""

    def is_float(element):
        try:
            float(element)
            return True
        except ValueError:
            return False

    return dialog(InputDialog(title, message, validate=is_float, **options))
