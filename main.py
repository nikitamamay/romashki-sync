import sys
import os

from gui.app import Application


app = Application(sys.argv)

exit(app.exec())
