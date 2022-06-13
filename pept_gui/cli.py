"""CLI interface for pept_gui project.

Be creative! do whatever you want!

- Install click or typer and create a CLI app
- Use builtin argparse
- Start a web application
- Import things from your .base module
"""

from PyQt5.QtWidgets import (
    QApplication
)
import sys
from .base import Window
def main():  # pragma: no cover
    """
    The main function executes on commands:
    `python -m pept_gui` and `$ pept_gui `.

    This is your program's entry point.

    You can change this function to do whatever you want.
    Examples:
        * Run a test suite
        * Run a server
        * Do some other stuff
        * Run a command line application (Click, Typer, ArgParse)
        * List all available tasks
        * Run an application (Flask, FastAPI, Django, etc.)
    """
    print("This will do something")
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())