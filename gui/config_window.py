from PyQt5 import QtCore, QtGui, QtWidgets

from config import Config
from gui.misc import *

import os


class ConfigWindow(QtWidgets.QDialog):
    def __init__(self, config: Config, parent = None) -> None:
        super().__init__(parent)
        self.setWindowTitle('Config - ' + APP_NAME)

        self.CONFIG = config

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.resize(600, 200)

        self.le1 = LineEdit(self.CONFIG.get_local_folder_path())
        self.le1.setPlaceholderText(r"C:\RomashkiData\Project123")
        self.le1.textChanged.connect(
            lambda: (
                self.CONFIG._set_local_folder_path(self.le1.text()),
                self.check_config()
        ))

        btn1 = QtWidgets.QPushButton(icon.folder(), "Select")
        btn1.clicked.connect(self.select_folder1)

        self.le2 = LineEdit(self.CONFIG.get_gdrive_folder_path())
        self.le2.setPlaceholderText(r"G:\My Drive\RomashkiData\CloudProject123")
        self.le2.textChanged.connect(
            lambda: (
                self.CONFIG._set_gdrive_folder_path(self.le2.text()),
                self.check_config()
        ))

        btn2 = QtWidgets.QPushButton(icon.folder(), "Select")
        btn2.clicked.connect(self.select_folder2)

        self.le3 = LineEdit(self.CONFIG.get_files_info_path())
        self.le3.setPlaceholderText(r"C:\RomashkiData\Project123.files_info.json")
        self.le3.textChanged.connect(
            lambda: (
                self.CONFIG._set_files_info_path(self.le3.text()),
                self.check_config()
        ))

        btn3 = QtWidgets.QPushButton(icon.file(), "Select")
        btn3.clicked.connect(self.select_file1)

        btn_confirm = QtWidgets.QPushButton(icon.accept(), "Save?")
        # btn_confirm.clicked.connect(self.confirm)

        layout_ = QtWidgets.QGridLayout()
        # layout_.setAlignment(QtCore.Qt.AlignTop)
        layout_.addWidget(QtWidgets.QLabel("Local folder: "), 0, 0, 1, 1)
        layout_.addWidget(self.le1, 0, 1, 1, 1)
        layout_.addWidget(btn1, 0, 2, 1, 1)
        layout_.addWidget(QtWidgets.QLabel("Google Drive folder: "), 1, 0, 1, 1)
        layout_.addWidget(self.le2, 1, 1, 1, 1)
        layout_.addWidget(btn2, 1, 2, 1, 1)
        layout_.addWidget(QtWidgets.QLabel("Files information file: "), 2, 0, 1, 1)
        layout_.addWidget(self.le3, 2, 1, 1, 1)
        layout_.addWidget(btn3, 2, 2, 1, 1)
        # layout_.addWidget(btn_confirm, 3, 0, 1, 3, QtCore.Qt.AlignBottom)
        self.setLayout(layout_)

        self.check_config()

    def selectFolder(self) -> str:
        fd = QtWidgets.QFileDialog()
        fd.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
        fd.exec()
        if not fd.result() == 0:
            return fd.selectedFiles()[0]
        return ''

    def selectFile(self) -> str:
        fd = QtWidgets.QFileDialog()
        fd.setFileMode(QtWidgets.QFileDialog.FileMode.AnyFile)
        fd.exec()
        if not fd.result() == 0:
            return fd.selectedFiles()[0]
        return ''

    def select_folder1(self) -> None:
        path = self.selectFolder()
        if not path:
            return
        path = os.path.abspath(path)
        if not Config.is_folder_creatable(path):
            QtWidgets.QMessageBox.critical(self, "Error", f'Specified folder<br><code>{path}</code><br>is not creatable.')
        self.le1.setText(path)
        self.CONFIG._set_local_folder_path(path)

    def select_folder2(self) -> None:
        path = self.selectFolder()
        if not path:
            return
        path = os.path.abspath(path)
        if not Config.is_folder_creatable(path):
            QtWidgets.QMessageBox.critical(self, "Error", f'Specified folder<br><code>{path}</code><br>is not creatable.')
        self.le2.setText(path)
        self.CONFIG._set_gdrive_folder_path(path)

    def select_file1(self) -> None:
        path = self.selectFile()
        if not path:
            return
        path = os.path.abspath(path)
        if not Config.is_file_creatable(path):
            QtWidgets.QMessageBox.critical(self, "Error", f'Specified file<br><code>{path}</code><br>is not creatable.')
        self.le3.setText(path)
        self.CONFIG._set_local_folder_path(path)

    def check_config(self) -> None:
        path = self.le1.text()
        if not os.path.isabs(path):
            self.le1.setState(-1, "Specify an absolute path!")
        else:
            if os.path.isdir(path):
                self.le1.setState(0, "The folder exists")
            else:
                if Config.is_folder_creatable(path):
                    self.le1.setState(1, "New folder will be created")
                else:
                    self.le1.setState(-1, "The folder cannot be created!")

        path = self.le2.text()
        if not os.path.isabs(path):
            self.le2.setState(-1, "Specify an absolute path!")
        else:
            if os.path.isdir(path):
                self.le2.setState(0, "The folder exists")
            else:
                if Config.is_folder_creatable(path):
                    self.le2.setState(1, "New folder will be created")
                else:
                    self.le2.setState(-1, "The folder cannot be created!")

        path = self.le3.text()
        if not os.path.isabs(path):
            self.le3.setState(-1, "Specify an absolute path!")
        else:
            if os.path.isfile(path):
                self.le3.setState(0, "The file exists")
            else:
                if Config.is_folder_creatable(path):
                    self.le3.setState(1, "New file will be created")
                else:
                    self.le3.setState(-1, "The file cannot be created!")


    # def confirm(self) -> None:
    #     try:
    #         self.CONFIG.check()
    #         self.close()
    #     except Exception as e:
    #         QtWidgets.QMessageBox.critical(self, "Error!", f'Error: {str(e)}')



if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    w = ConfigWindow(Config())

    w.show()

    app.exec()