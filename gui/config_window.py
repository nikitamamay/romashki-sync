from PyQt5 import QtCore, QtGui, QtWidgets

import config
import const
from gui.misc import *

import os


class ProjectConfigWindow(QtWidgets.QDialog):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.setWindowTitle('Config - ' + const.APP_NAME)

        self._project_cfg = None

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.resize(600, 200)

        self.le4 = LineEdit()
        self.le4.setPlaceholderText(r"C:\RomashkiData\Project123.config.json")
        self.le4.textEdited.connect(self.check_config)

        btn4 = QtWidgets.QPushButton(icon.file(), "Select")
        btn4.clicked.connect(self.select_file_cfg)

        self.le1 = LineEdit()
        self.le1.setPlaceholderText(r"C:\RomashkiData\Project123")
        self.le1.textEdited.connect(self.check_config)

        btn1 = QtWidgets.QPushButton(icon.folder(), "Select")
        btn1.clicked.connect(self.select_folder1)

        self.le2 = LineEdit()
        self.le2.setPlaceholderText(r"G:\My Drive\RomashkiData\CloudProject123")
        self.le2.textEdited.connect(self.check_config)

        btn2 = QtWidgets.QPushButton(icon.folder(), "Select")
        btn2.clicked.connect(self.select_folder2)

        self.le3 = LineEdit()
        self.le3.setPlaceholderText(r"C:\RomashkiData\Project123.files_info.json")
        self.le3.textEdited.connect(self.check_config)

        btn3 = QtWidgets.QPushButton(icon.file(), "Select")
        btn3.clicked.connect(self.select_file1)

        btn_confirm = QtWidgets.QPushButton(icon.accept(), "Save")
        btn_confirm.clicked.connect(self.confirm)

        layout_ = QtWidgets.QGridLayout()
        # layout_.setAlignment(QtCore.Qt.AlignTop)
        layout_.addWidget(QtWidgets.QLabel("Project config file: "), 0, 0, 1, 1)
        layout_.addWidget(self.le4, 0, 1, 1, 1)
        layout_.addWidget(btn4, 0, 2, 1, 1)
        layout_.addWidget(QtWidgets.QLabel("Local folder: "), 1, 0, 1, 1)
        layout_.addWidget(self.le1, 1, 1, 1, 1)
        layout_.addWidget(btn1, 1, 2, 1, 1)
        layout_.addWidget(QtWidgets.QLabel("Google Drive folder: "), 2, 0, 1, 1)
        layout_.addWidget(self.le2, 2, 1, 1, 1)
        layout_.addWidget(btn2, 2, 2, 1, 1)
        layout_.addWidget(QtWidgets.QLabel("Files information file: "), 3, 0, 1, 1)
        layout_.addWidget(self.le3, 3, 1, 1, 1)
        layout_.addWidget(btn3, 3, 2, 1, 1)
        layout_.addWidget(btn_confirm, 4, 0, 1, 3, QtCore.Qt.AlignBottom)
        self.setLayout(layout_)

    def set_project_config(self, pconfig: config.ProjectConfig) -> None:
        self._project_cfg = pconfig
        self.le4.setText(self._project_cfg.get_filepath())
        self.le1.setText(self._project_cfg.get_local_folder_path())
        self.le2.setText(self._project_cfg.get_gdrive_folder_path())
        self.le3.setText(self._project_cfg.get_files_info_path())
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
        if not config.is_folder_creatable(path):
            return critical(f'Specified folder<br><code>{path}</code><br>is not creatable.', parent=self)
        self.le1.setText(path)
        self.check_config()

    def select_folder2(self) -> None:
        path = self.selectFolder()
        if not path:
            return
        path = os.path.abspath(path)
        if not config.is_folder_creatable(path):
            return critical(f'Specified folder<br><code>{path}</code><br>is not creatable.', parent=self)
        self.le2.setText(path)
        self.check_config()

    def select_file1(self) -> None:
        path = self.selectFile()
        if not path:
            return
        path = os.path.abspath(path)
        if not config.is_file_creatable(path):
            return critical(f'Specified file<br><code>{path}</code><br>is not creatable.', parent=self)
        self.le3.setText(path)
        self.check_config()

    def select_file_cfg(self) -> None:
        path = self.selectFile()
        if not path:
            return
        path = os.path.abspath(path)
        if not config.is_file_creatable(path):
            return critical(f'Specified file<br><code>{path}</code><br>is not creatable.', parent=self)
        self.le4.setText(path)
        self.check_config()

    def read_form(self) -> None:
        self._project_cfg.set_filepath(self.le4.text())
        self._project_cfg._set_local_folder_path(self.le1.text())
        self._project_cfg._set_gdrive_folder_path(self.le2.text())
        self._project_cfg._set_files_info_path(self.le3.text())

    def check_config(self) -> None:
        self.read_form()

        path = self.le1.text()
        if not os.path.isabs(path):
            self.le1.setState(-1, "Specify an absolute path!")
        else:
            if os.path.isdir(path):
                self.le1.setState(0, "The folder exists")
            else:
                if config.is_folder_creatable(path):
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
                if config.is_folder_creatable(path):
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
                if config.is_folder_creatable(path):
                    self.le3.setState(1, "New file will be created")
                else:
                    self.le3.setState(-1, "The file cannot be created!")

        path = self.le4.text()
        if not os.path.isabs(path):
            self.le4.setState(-1, "Specify an absolute path!")
        else:
            if os.path.isfile(path):
                self.le4.setState(0, "The file exists")
            else:
                if config.is_folder_creatable(path):
                    self.le4.setState(1, "New file will be created")
                else:
                    self.le4.setState(-1, "The file cannot be created!")


    def confirm(self) -> None:
        try:
            self.read_form()
            self._project_cfg.check()
            self.close()
        except Exception as e:
            return critical(e, parent=self)



if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    w = ProjectConfigWindow()
    w.set_project_config(config.ProjectConfig())

    w.show()

    app.exec()
