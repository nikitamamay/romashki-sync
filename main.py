import sys
import os

from gui.app import GUIApplication


app = GUIApplication(sys.argv)

exit(app.exec())
