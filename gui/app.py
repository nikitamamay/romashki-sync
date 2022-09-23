from PyQt5 import QtCore, QtGui, QtWidgets

import os
from gui.config_window import *
from gui.main_window import *

from gui.misc import *

import config



class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent = None) -> None:
        super().__init__(icon.daisy(), parent)

        self.menu = QtWidgets.QMenu("Actions")

        self.a_raise = QtWidgets.QAction(icon.daisy2(), "Raise")
        self.menu.addAction(self.a_raise)
        self.a_exit = QtWidgets.QAction(icon.cancel(), "Exit")
        self.menu.addAction(self.a_exit)

        self.setContextMenu(self.menu)
        self.setToolTip(APP_NAME)


class Application(QtWidgets.QApplication):
    def __init__(self, argv: 'list[str]') -> None:
        super().__init__(argv)
        self.setWindowIcon(icon.daisy2())
        self.setApplicationName(APP_NAME)
        self.setApplicationDisplayName(APP_NAME)

        self.CONFIG = config.Config()

        if len(argv) == 1:
            print("No config file path specified. Needs configuring.")
        elif len(argv) == 2:
            filepath = argv[1]
            print(f'Reading config file: "{filepath}"')
            self.CONFIG.read_config_file(filepath)
        else:
            print('Usage:\n\tprogram [file.cfg]\n\nfile.cfg is a path to config file.')
            exit()

        self.cw = ConfigWindow(self.CONFIG)

        self.tray_icon = TrayIcon()
        self.tray_icon.show()
        self.tray_icon.a_exit.triggered.connect(self.exit)

        if not self.CONFIG.is_valid():
            self.configure()

        self.mw = MainWindow(self.CONFIG)
        self.mw.a_about.triggered.connect(self.about)

        self.tray_icon.activated.connect(
            lambda reason: self.mw.toggle() if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger else 0)
        self.tray_icon.messageClicked.connect(self.mw.raiseOnTop)
        self.tray_icon.a_raise.triggered.connect(self.mw.raiseOnTop)

        self.mw.raiseOnTop()

    def configure(self):
        self.cw.exec()

        try:
            self.CONFIG.check()
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
                exit()

    def about(self) -> None:
        QtWidgets.QMessageBox.about(self.mw, "About RomashkiSync", PROGRAM_ABOUT)
