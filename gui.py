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
    def checkbox_on():
        return QtGui.QIcon("icons/check_box.png")
    def checkbox_off():
        return QtGui.QIcon("icons/check_box_uncheck.png")


class Application(QtWidgets.QApplication):
    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        self.setWindowIcon(icon.daisy2())
        self.setApplicationName(APP_NAME)
        self.setApplicationDisplayName(APP_NAME)


class ScrollArea(QtWidgets.QScrollArea):
    def __init__(self, widget: QtWidgets.QWidget = None, parent=None) -> None:
        super().__init__(parent=parent)
        self.setSizeAdjustPolicy(QtWidgets.QScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.setWidgetResizable(True)
        if widget:
            self.setWidget(widget)


class ChangeRepresentationWidget(QtWidgets.QCheckBox):
    def __init__(self, change_obj: File, parent = None) -> None:
        super().__init__(parent)

        self.change_obj = change_obj

        self.setFont(QtGui.QFont("Consolas"))
        self.setText(self.change_obj.basename())
        self.setToolTip(self.change_obj.relpath)

        self.menu = QtWidgets.QMenu(self.text())
        self.menu.addAction(icon.daisy(), self.text())
        # self.a_ignored = QtWidgets.QAction("Ignore")
        # self.a_ignored.setCheckable(True)
        # self.a_ignored.triggered.connect(self.toggleIgnored)
        # self.menu.addAction(self.a_ignored)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        self.menu.move(event.globalPos())
        self.menu.show()

    # def isIgnored(self) -> bool:
    #     return self._ignore

    # def setIgnored(self, flag: bool) -> None:
    #     self._ignore = flag

    #     self.a_ignored.setChecked(self._ignore)

    #     f = self.font()
    #     f.setItalic(self._ignore)
    #     self.setFont(f)

    # def toggleIgnored(self) -> None:
    #     self.setIgnored(not self.isIgnored())


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
    raised = QtCore.pyqtBoundSignal()

    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(300, 100)
        self.setGeometry(
            self.screen().size().width() - 800 - 20,
            self.screen().size().height() - 325 - 50,
            800, 325)

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

        self.layout_reprs1 = QtWidgets.QVBoxLayout()
        self.layout_reprs1.setSpacing(2)
        self.layout_reprs1.setContentsMargins(2, 2, 2, 2)
        self.layout_reprs1.setAlignment(QtCore.Qt.AlignTop)

        self.layout_reprs2 = QtWidgets.QVBoxLayout()
        self.layout_reprs2.setSpacing(2)
        self.layout_reprs2.setContentsMargins(2, 2, 2, 2)
        self.layout_reprs2.setAlignment(QtCore.Qt.AlignTop)

        self.group_box1 = QtWidgets.QWidget()
        self.group_box1.setLayout(self.layout_reprs1)

        self.group_box2 = QtWidgets.QWidget()
        self.group_box2.setLayout(self.layout_reprs2)

        self.scroll_area1 = ScrollArea(self.group_box1)
        self.scroll_area2 = ScrollArea(self.group_box2)

        self.btn_select_all = QtWidgets.QPushButton(icon.checkbox_on(), "Select all")
        self.btn_deselect_all = QtWidgets.QPushButton(icon.checkbox_off(), "Deselect all")

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.btn_select_all)
        btn_layout.addWidget(self.btn_deselect_all)
        btn_layout.addStretch(1)

        self.c_widget = QtWidgets.QWidget()
        self.gridlayout = QtWidgets.QGridLayout()
        self.gridlayout.addLayout(btn_layout, 1, 1, 1, 1)
        self.gridlayout.addWidget(self.scroll_area1, 2, 1, 1, 1)
        self.gridlayout.addWidget(self.scroll_area2, 2, 2, 1, 1)
        self.c_widget.setLayout(self.gridlayout)

        self.setCentralWidget(self.c_widget)

        # self.dw: DirectoryWatcher = None
        # self.is_active = True
        # self.startTimer(1000)

    def raiseOnTop(self):
        self.show()
        self.activateWindow()
        # self.raised.emit()

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
        self.close()
        self.exitSignal.emit()
        self.tray_icon.hide()

    def timerEvent(self, event: QtCore.QTimerEvent) -> None:
        if self.is_active:
            self.showChanges()
        return super().timerEvent(event)

    def clear(self):
        for i in range(self.layout_reprs1.count()):
            self.layout_reprs1.removeWidget(self.layout_reprs1.itemAt(0).widget())
        for i in range(self.layout_reprs2.count()):
            self.layout_reprs2.removeWidget(self.layout_reprs2.itemAt(0).widget())

    def init_representations(self, l1: list[File], l2: list[File]):
        self.clear()
        for f in l1:
            w = ChangeRepresentationWidget(f, self)
            self.layout_reprs1.addWidget(w)
        for f in l2:
            w = ChangeRepresentationWidget(f, self)
            self.layout_reprs2.addWidget(w)

    # def showChanges(self):
    #     self.clear()
    #     to_load, to_delete = self.dw.find_change()
    #     for f in to_load:
    #         w = ChangeRepresentationWidget(f)
    #         self.layout_.addWidget(w)
    #     for f in to_delete:
    #         w = ChangeRepresentationWidget(f)
    #         self.layout_.addWidget(w)


if __name__ == "__main__":
    import file_watcher
    import config_reader
    import sys

    CONFIG = config_reader.CONFIG

    if len(sys.argv) != 2:
        print("Error: config path is not specified!")
        exit()

    config_reader.read_config_file(sys.argv[1])


    fc = file_watcher.FilesCollection(CONFIG["local_folder_path"])


    app = Application([])

    window = MainWindow()

    window.init_representations(fc.files, fc.files)


    window.raiseOnTop()

    exit(app.exec())
