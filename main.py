import sys
import os

from gui.app import GUIApplication


app = GUIApplication(sys.argv)

sys.exit(app.exec())
