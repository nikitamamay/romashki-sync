from PyQt5 import QtCore, QtGui, QtWidgets
import sys

import traceback

FONT_FAMILY_MONOSPACE = "Consolas"

PROGRAM_ABOUT = """
<p><b>RomashkiSync</b> is a file synchronization program.</p>
<p>...</p>
<p>&copy; Mamay Nikita, 2022.</p>
"""

MSGBOX_PARENT = None

class icon():
    def daisy():
        return QtGui.QIcon("icons/daisy.png")
    def daisy2():
        return QtGui.QIcon("icons/daisy2.png")
    def daisy_error():
        return QtGui.QIcon("icons/daisy_error.png")
    def daisy_local():
        return QtGui.QIcon("icons/daisy_local.png")
    def daisy_cloud():
        return QtGui.QIcon("icons/daisy_cloud.png")
    def daisy_both():
        return QtGui.QIcon("icons/daisy_both.png")
    def daisy_update():
        return QtGui.QIcon("icons/daisy_update.png")
    def accept():
        return QtGui.QIcon("icons/tick.png")
    def deny():
        return QtGui.QIcon("icons/cross.png")
    def cancel():
        return QtGui.QIcon("icons/cancel.png")
    def checkbox_on():
        return QtGui.QIcon("icons/check_box.png")
    def checkbox_off():
        return QtGui.QIcon("icons/check_box_uncheck.png")
    def magnifier():
        return QtGui.QIcon("icons/magnifier.png")
    def update():
        return QtGui.QIcon("icons/update.png")
    def local():
        return QtGui.QIcon("icons/computer.png")
    def cloud():
        return QtGui.QIcon("icons/network_cloud.png")
    def cloud_old():
        return QtGui.QIcon("icons/network_cloud_old.png")
    def cloud_to_local():
        return QtGui.QIcon("icons/cloud_to_local.png")
    def local_to_cloud():
        return QtGui.QIcon("icons/local_to_cloud.png")
    def folder():
        return QtGui.QIcon("icons/folder.png")
    def file():
        return QtGui.QIcon("icons/page_white_code.png")
    def new_document():
        return QtGui.QIcon("icons/page_white_add.png")
    def save():
        return QtGui.QIcon("icons/save.png")
    def save_as():
        return QtGui.QIcon("icons/save_as.png")
    def cog():
        return QtGui.QIcon("icons/cog.png")



class LineEdit(QtWidgets.QLineEdit):
    def __init__(self, text = "", parent = None):
        super().__init__(text, parent)

    def setState(self, state: int = 0, tooltip: str = ""):
        color = ["red", "green", "blue"][state + 1]
        self.setStyleSheet(f"color: {color};")
        self.setToolTip(tooltip)


def geometry_as_list(g: QtCore.QRect) -> list[int, int, int, int]:
    return [g.left(), g.top(), g.width(), g.height()]


def critical(msg_or_error, title = "Error!", parent = None) -> None:
    if isinstance(msg_or_error, BaseException):
        msg = f"""<pre>{traceback.format_exc()}</pre>"""
    else:
        msg = str(msg_or_error)
    QtWidgets.QMessageBox.critical(parent, title, msg)



if __name__ == "__main__":
    try:
        raise Exception("skdfjsdlf")
    except Exception as e:
        critical(e)