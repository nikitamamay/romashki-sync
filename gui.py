from PyQt5 import QtCore, QtGui, QtWidgets


APP_NAME = "RomashkiSync"


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


class Application(QtWidgets.QApplication):
    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        self.setWindowIcon(icon.daisy2())
        self.setApplicationName(APP_NAME)
        self.setApplicationDisplayName(APP_NAME)


class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent = None) -> None:
        super().__init__(icon.daisy(), parent)

        self.menu = QtWidgets.QMenu("Actions")
        self.menu.addAction(QtGui.QIcon("icons/cancel.png"), "Exit", exit)

        self.setContextMenu(self.menu)
        self.setToolTip(APP_NAME)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(300, 100)

        self.tray_icon = TrayIcon(self)
        self.tray_icon.show()
        self.tray_icon.activated.connect(lambda reason: self.toggle() if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger else 0)
        self.tray_icon.messageClicked.connect(self.raiseOnTop)

        a_raise = QtWidgets.QAction(icon.daisy2(), "Raise", self.tray_icon.menu)
        a_raise.triggered.connect(self.raiseOnTop)
        self.tray_icon.menu.insertAction(self.tray_icon.menu.actions()[0], a_raise)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menu1 = QtWidgets.QMenu("Actions", self)
        self.a_toggle_on_top = QtWidgets.QAction("Always on top", self.menubar)
        self.a_toggle_on_top.setCheckable(True)
        self.a_toggle_on_top.toggled.connect(self.setAlwaysOnTop)  # a_toggle_on_top.isChecked()
        self.menu1.addAction(self.a_toggle_on_top)
        self.menu1.addSeparator()
        self.menu1.addAction(QtGui.QIcon("icons/cancel.png"), "Exit", exit)
        self.menubar.addMenu(self.menu1)

        self.setMenuBar(self.menubar)

    def raiseOnTop(self):
        self.show()
        self.activateWindow()

    def setAlwaysOnTop(self, state: bool) -> None:
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, state)
        self.a_toggle_on_top.setChecked(state)
        self.show()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        event.ignore()
        self.setGeometry(self.geometry())
        self.hide()

    def toggle(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()

