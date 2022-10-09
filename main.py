import sys
import os

from gui.app_gui import GUIApplication
from gui.misc import critical


app = GUIApplication(sys.argv)

try:
    app.read_last_project_if_exists()
except Exception as e:
    critical(e)

sys.exit(app.exec())
