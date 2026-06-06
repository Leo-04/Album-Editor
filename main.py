import os
import sys

from app import App


def main():
    app = App(sys.argv[1:])
    app.mainloop()
    os._exit(0)


if __name__ == "__main__":
    main()
