import sys
import os

from gui.app_gui import GUIApplication


app = GUIApplication(sys.argv)

app.read_last_if_exists()

sys.exit(app.exec())
