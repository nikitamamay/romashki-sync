from PyQt5 import QtCore, QtGui, QtWidgets

import sys
import os

from gui.config_window import *
from gui.main_window import *

from gui.misc import *

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

        self.cw = ProjectConfigWindow(self._prj_cfg)

        self.tray_icon = TrayIcon()
        self.tray_icon.show()
        self.tray_icon.a_exit.triggered.connect(self.exit)

        self.mw = MainWindow(self)
        self.mw.a_about.triggered.connect(self.about)

        self.tray_icon.activated.connect(
            lambda reason: self.mw.toggle() if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger else 0)
        self.tray_icon.messageClicked.connect(self.mw.raiseOnTop)
        self.tray_icon.a_raise.triggered.connect(self.mw.raiseOnTop)


        if self._prj_cfg.is_valid():
            self.init_project()
        else:
            self.configure()

    def configure(self):
        self.cw.exec()

        try:
            self._prj_cfg.check()
            self.set_project_config(self._prj_cfg)
            self.init_project()
        except Exception as e:
            btn = QtWidgets.QMessageBox.critical(
                self.cw,
                "Config is not valid",
                f'Error: {str(e)}<br><br>Do you want to correct your config or exit the program?',
                QtWidgets.QMessageBox.StandardButton.Retry | QtWidgets.QMessageBox.StandardButton.Close,
                QtWidgets.QMessageBox.StandardButton.Close
            )
            if btn == QtWidgets.QMessageBox.StandardButton.Retry:
                self.configure()
            else:
                sys.exit()

    def init_project(self) -> None:
        application.Application.init_project(self)
        self.mw.init_project()
        self.mw.raiseOnTop()

    def about(self) -> None:
        QtWidgets.QMessageBox.about(self.mw, "About RomashkiSync", PROGRAM_ABOUT)

    def exit(self) -> None:
        self.save_all_configs()
        self.mw.close()
        self.tray_icon.hide()
        sys.exit(0)
