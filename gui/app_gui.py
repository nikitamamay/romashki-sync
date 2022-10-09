from PyQt5 import QtCore, QtGui, QtWidgets

import sys
import os

from gui.config_window import *
from gui.main_window import *
from gui.misc import *

import config_reader
import const
import application


class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent = None) -> None:
        super().__init__(icon.daisy(), parent)

        self.menu = QtWidgets.QMenu("Actions")

        self.a_raise = QtWidgets.QAction(icon.daisy2(), "Raise")
        self.menu.addAction(self.a_raise)
        self.a_exit = QtWidgets.QAction(icon.cancel(), "Exit")
        self.menu.addAction(self.a_exit)

        self.setContextMenu(self.menu)
        self.setToolTip(const.APP_NAME)


class GUIApplication(QtWidgets.QApplication, application.Application):
    def __init__(self, argv: 'list[str]') -> None:
        QtWidgets.QApplication.__init__(self, argv)
        application.Application.__init__(self)

        self.setWindowIcon(icon.daisy2())
        self.setApplicationName(const.APP_NAME)
        self.setApplicationDisplayName(const.APP_NAME)

        self.cw = ProjectConfigWindow()

        self.tray_icon = TrayIcon()
        self.tray_icon.show()
        self.tray_icon.a_exit.triggered.connect(self.exit)

        self.mw = MainWindow(self)
        self.mw.a_about.triggered.connect(self.about)

        self.tray_icon.activated.connect(
            lambda reason: self.mw.toggle() if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger else 0)
        self.tray_icon.messageClicked.connect(self.mw.raiseOnTop)
        self.tray_icon.a_raise.triggered.connect(self.mw.raiseOnTop)

    def configure(self):
        if not self._prj_cfg is None:
            self.cw.set_project_config(self._prj_cfg)
            self.cw.exec()

            try:
                self._prj_cfg.check()
                self.set_project_config(self._prj_cfg)
                self.init_project()
            except Exception as e:
                btn = QtWidgets.QMessageBox.critical(
                    self.cw,
                    "Config is not valid",
                    f'Error: {str(e)}<br><br>Do you want to correct your config or discard the changes?',
                    QtWidgets.QMessageBox.StandardButton.Retry | QtWidgets.QMessageBox.StandardButton.Abort,
                    QtWidgets.QMessageBox.StandardButton.Abort
                )
                if btn == QtWidgets.QMessageBox.StandardButton.Retry:
                    self.configure()
                else:
                    self.close_project()
        else:
            return critical(
                "There is no project to configure. Create a new project or open an existing one.",
                "No project to configure",
                parent=self.mw
            )

    def init_project(self) -> None:
        application.Application.init_project(self)
        self.mw.window_init_project()
        self.mw.raiseOnTop()

    def read_project(self, path: str) -> None:
        self.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            self.set_project_config(config.ProjectConfig.read_from_file(path))
        except Exception as e:
            return critical(e)
        finally:
            self.restoreOverrideCursor()

    def open_project(self) -> None:
        path = QtWidgets.QFileDialog.getOpenFileName(
            self.mw,
            "Open a project",
            filter="Project config files (*.cfg);;JSON files (*.json);;All files (*)")[0]
        if path != "":
            try:
                self.read_project(path)
            except Exception as e:
                return critical(e, parent=self.mw)
            self.init_project()

    def create_project(self) -> None:
        application.Application.create_project(self)
        self.configure()

    def close_project(self) -> None:
        application.Application.close_project(self)
        self.mw.window_close_project()

    def save_project(self) -> None:
        if self._prj_cfg is None:
            return critical("There is no project config file to save.", parent=self.mw)
        if self._prj_cfg.get_filepath() != "":
            return critical("Project config file has no path specified", parent=self.mw)
        self._prj_cfg.save()


    def save_project_as(self) -> None:
        if self._prj_cfg is None:
            return critical("There is no project config file to save.", parent=self.mw)
        path = QtWidgets.QFileDialog.getSaveFileName(
            self.mw,
            "Save the project as...",
            filter="Project config files (*.cfg);;JSON files (*.json);;All files (*)")[0]
        if path != "":
            path = os.path.abspath(path)
            if config_reader.is_file_creatable(path):
                self._prj_cfg.set_filepath(path)
                self.save_project()
                self.init_project()
            else:
                return critical(
                    f'File "{path}" is not creatable',
                    "File saving error",
                    parent=self.mw
                )

    def read_last_project_if_exists(self) -> None:
        application.Application.read_last_project_if_exists(self)
        if not self._prj_cfg is None:
            self.init_project()

    def about(self) -> None:
        QtWidgets.QMessageBox.about(self.mw, "About RomashkiSync", PROGRAM_ABOUT)

    def exit(self) -> None:
        self.save_app_config()
        self.mw.close()
        self.tray_icon.hide()
        sys.exit(0)
