from PyQt5 import QtCore, QtGui, QtWidgets

from gui.misc import *
from gui.scroll_area import ScrollArea

import const

import file_watcher
File = file_watcher.File



class FileDialog(QtWidgets.QDialog):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.setSizeGripEnabled(True)
        self.setWindowFlag(QtCore.Qt.MSWindowsFixedSizeDialogHint, False)
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.resize(400, 300)

        self.label_icon = QtWidgets.QLabel()
        self.setPixmap(icon.daisy2().pixmap(32, 32))
        self.label_icon.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)

        self.label_text = QtWidgets.QLabel()
        self.label_text.setWordWrap(True)

        self.items_layout = QtWidgets.QVBoxLayout()
        self.items_layout.setAlignment(QtCore.Qt.AlignTop)
        self.items_layout.setContentsMargins(5, 5, 5, 5)
        self.items_layout.setSpacing(2)

        container_widget = QtWidgets.QWidget()
        container_widget.setLayout(self.items_layout)

        self.scroll_area = ScrollArea(container_widget)

        btn_accept = QtWidgets.QPushButton(icon.accept(), "Yes")
        btn_accept.clicked.connect(self.accept)
        btn_reject = QtWidgets.QPushButton(icon.deny(), "No")
        btn_reject.clicked.connect(self.reject)

        l_btn = QtWidgets.QHBoxLayout()
        l_btn.setAlignment(QtCore.Qt.AlignRight)
        l_btn.addStretch(1)
        l_btn.addWidget(btn_accept, 0)
        l_btn.addWidget(btn_reject, 0)
        l_btn_margins = l_btn.contentsMargins()
        l_btn_margins.setTop(15)
        l_btn.setContentsMargins(l_btn_margins)

        l = QtWidgets.QGridLayout()
        l.setContentsMargins(15, 15, 15, 15)
        l.addWidget(self.label_icon, 0, 0, 2, 1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        l.addWidget(self.label_text, 0, 1, 1, 1)
        l.addWidget(self.scroll_area, 1, 1, 1, 1)
        l.addLayout(l_btn, 2, 0, 1, 2)
        self.setLayout(l)

        self.setText = self.label_text.setText
        self.text = self.label_text.text

    def setPixmap(self, pixmap: QtGui.QPixmap) -> None:
        self.label_icon.setPixmap(pixmap)
        self.label_icon.sizeHint = lambda: pixmap.size()

    def initFilenames(self, files: list[File]) -> None:
        font = QtGui.QFont(FONT_FAMILY_MONOSPACE)
        for f in files:
            l = QtWidgets.QLabel(f.relpath, self)
            l.setFont(font)
            self.items_layout.addWidget(l)

    @staticmethod
    def run(parent, pixmap: QtGui.QPixmap, title: str, msg: str, files: list[File]) -> bool:
        d = FileDialog(parent)
        d.setWindowTitle(f'{title} - {const.APP_NAME}')
        d.setText(msg)
        d.setPixmap(pixmap)
        d.initFilenames(files)
        return bool(d.exec())
