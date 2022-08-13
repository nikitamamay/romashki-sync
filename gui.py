from PyQt5 import QtCore, QtGui, QtWidgets

from file_watcher import DirectoryWatcher, File


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
    def accept():
        return QtGui.QIcon("icons/tick.png")
    def deny():
        return QtGui.QIcon("icons/cross.png")


class Application(QtWidgets.QApplication):
    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        self.setWindowIcon(icon.daisy2())
        self.setApplicationName(APP_NAME)
        self.setApplicationDisplayName(APP_NAME)


class ChangeWidget(QtWidgets.QWidget):
    def __init__(self, change_obj: File, parent = None) -> None:
        super().__init__(parent)

        self.change_obj = change_obj

        self.label = QtWidgets.QLabel(self.change_obj.basename())
        self.btn_accept = QtWidgets.QPushButton(icon.accept(), "Accept")
        self.btn_deny = QtWidgets.QPushButton(icon.deny(), "Deny (Ignore)")

        self.layout_ = QtWidgets.QHBoxLayout()
        self.layout_.setSpacing(1)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.addWidget(self.label, stretch=1)
        self.layout_.addWidget(self.btn_accept)
        self.layout_.addWidget(self.btn_deny)
        self.setLayout(self.layout_)


class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent = None) -> None:
        super().__init__(icon.daisy(), parent)

        self.menu = QtWidgets.QMenu("Actions")
        self.a_exit = QtWidgets.QAction(QtGui.QIcon("icons/cancel.png"), "Exit")
        self.menu.addAction(self.a_exit)

        self.setContextMenu(self.menu)
        self.setToolTip(APP_NAME)


class MainWindow(QtWidgets.QMainWindow):
    exitSignal = QtCore.pyqtBoundSignal()
    changeSignal = QtCore.pyqtBoundSignal()

    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(300, 100)

        self.tray_icon = TrayIcon(self)
        self.tray_icon.show()
        self.tray_icon.activated.connect(lambda reason: self.toggle() if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger else 0)
        self.tray_icon.messageClicked.connect(self.raiseOnTop)
        self.tray_icon.a_exit.triggered.connect(self.exit)

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
        self.menu1.addAction(QtGui.QIcon("icons/cancel.png"), "Exit", self.exit)
        self.menubar.addMenu(self.menu1)

        self.setMenuBar(self.menubar)

        self.layout_ = QtWidgets.QVBoxLayout()
        self.layout_.setSpacing(1)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.setAlignment(QtCore.Qt.AlignTop)

        self.groupBox = QtWidgets.QGroupBox("Local")
        self.groupBox.setLayout(self.layout_)
        self.setCentralWidget(self.groupBox)

        self.dw: DirectoryWatcher = None
        self.is_active = True
        self.startTimer(1000)

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

    def exit(self):
        self.exitSignal.emit()
        self.tray_icon.hide()
        self.close()

    def timerEvent(self, event: QtCore.QTimerEvent) -> None:
        if self.is_active:
            self.showChanges()
        return super().timerEvent(event)

    def clear(self):
        for i in range(self.layout_.count()):
            self.layout_.removeWidget(self.layout_.itemAt(0).widget())

    def showChanges(self):
        self.clear()
        to_load, to_delete = self.dw.find_change()
        for f in to_load:
            w = ChangeWidget(f)
            self.layout_.addWidget(w)
        for f in to_delete:
            w = ChangeWidget(f)
            self.layout_.addWidget(w)

