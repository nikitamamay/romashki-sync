from PyQt5 import QtCore, QtGui, QtWidgets

import file_watcher
File = file_watcher.File

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
    def __init__(self, file_obj: File, parent = None) -> None:
        super().__init__(parent)

        self.file_obj = file_obj

        self.setFont(QtGui.QFont("Consolas"))
        self.setText(self.file_obj.basename())
        self.setToolTip(self.file_obj.relpath)

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


class ChangeRepresentationListWidget(QtWidgets.QWidget):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.reprs: list[ChangeRepresentationWidget] = []

        self.layout_reprs = QtWidgets.QVBoxLayout()
        self.layout_reprs.setSpacing(2)
        self.layout_reprs.setContentsMargins(2, 2, 2, 2)
        self.layout_reprs.setAlignment(QtCore.Qt.AlignTop)

        self.container_reprs = QtWidgets.QWidget()
        self.container_reprs.setLayout(self.layout_reprs)

        self.scroll_area = ScrollArea(self.container_reprs)

        self.btn_select_all = QtWidgets.QPushButton(icon.checkbox_on(), "Select all")
        self.btn_select_all.clicked.connect(lambda: self.set_state_to_all(True))

        self.btn_deselect_all = QtWidgets.QPushButton(icon.checkbox_off(), "Deselect all")
        self.btn_deselect_all.clicked.connect(lambda: self.set_state_to_all(False))

        self.layout_ = QtWidgets.QGridLayout()
        self.layout_.setSpacing(2)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.addWidget(self.btn_select_all, 0, 0, 1, 1)
        self.layout_.addWidget(self.btn_deselect_all, 0, 1, 1, 1)
        self.layout_.addWidget(self.scroll_area, 1, 0, 1, 2)
        self.setLayout(self.layout_)

    def init_representations(self, files: list[File]) -> None:
        self.clear_representations()
        for f in files:
            self.add_file_repr(f)

    def clear_representations(self) -> None:
        while len(self.reprs) > 0:
            self.layout_reprs.removeWidget(self.reprs.pop())

    def add_file_repr(self, f: File) -> None:
        w = ChangeRepresentationWidget(f)
        self.layout_reprs.addWidget(w)
        self.reprs.append(w)

    def set_state_to_all(self, state: bool) -> None:
        for r in self.reprs:
            r.setChecked(state)

    def get_checked_files(self) -> list[File]:
        l: list[File] = []
        for r in self.reprs:
            if r.isChecked():
                l.append(r.file_obj)
        return l


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


class MainWindow(QtWidgets.QMainWindow):
    exitSignal = QtCore.pyqtBoundSignal()
    changeSignal = QtCore.pyqtBoundSignal()
    raised = QtCore.pyqtBoundSignal()

    def __init__(self, config: dict, parent = None) -> None:
        super().__init__(parent)

        self.local_folder_path = config["local_folder_path"]
        self.gdrive_folder_path = config["gdrive_folder_path"]

        self.setMinimumSize(300, 100)
        self.setGeometry(
            self.screen().size().width() - 800 - 20,
            self.screen().size().height() - 325 - 50,
            800,
            325
        )

        self.tray_icon = TrayIcon(self)
        self.tray_icon.show()
        self.tray_icon.activated.connect(lambda reason: self.toggle() if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger else 0)
        self.tray_icon.messageClicked.connect(self.raiseOnTop)
        self.tray_icon.a_exit.triggered.connect(self.exit)
        self.tray_icon.a_raise.triggered.connect(self.raiseOnTop)

        self.menubar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menubar)

        self.menu_sync = QtWidgets.QMenu("Synchronization", self)
        self.menu_sync.addAction(icon.magnifier(), "Look for changes", self.look_for_changes)
        self.menu_sync.addAction(icon.update(), "Sync", self.sync)
        self.menubar.addMenu(self.menu_sync)

        self.menu_window = QtWidgets.QMenu("Window", self)
        self.a_toggle_on_top = QtWidgets.QAction("Always on top", self.menubar)
        self.a_toggle_on_top.setCheckable(True)
        self.a_toggle_on_top.toggled.connect(self.setAlwaysOnTop)  # a_toggle_on_top.isChecked()
        self.menu_window.addAction(self.a_toggle_on_top)
        self.menu_window.addAction(icon.daisy(), "About", self.about)
        self.menu_window.addSeparator()
        self.menu_window.addAction(QtGui.QIcon("icons/cancel.png"), "Exit", self.exit)
        self.menubar.addMenu(self.menu_window)

        self.reprs_list_widget1 = ChangeRepresentationListWidget(self)
        self.reprs_list_widget2 = ChangeRepresentationListWidget(self)

        self.le_msg = QtWidgets.QLineEdit()
        self.le_msg.setPlaceholderText("Message...")

        self.btn_sync = QtWidgets.QPushButton(icon.update(), "Sync")
        self.btn_sync.clicked.connect(self.sync)

        self.c_widget = QtWidgets.QWidget()
        self.gridlayout = QtWidgets.QGridLayout()
        self.gridlayout.addWidget(self.reprs_list_widget1, 0, 0, 1, 2)
        self.gridlayout.addWidget(self.reprs_list_widget2, 0, 2, 1, 2)
        self.gridlayout.addWidget(self.le_msg, 1, 0, 1, 3)
        self.gridlayout.addWidget(self.btn_sync, 1, 3, 1, 1)
        self.c_widget.setLayout(self.gridlayout)

        self.setCentralWidget(self.c_widget)

        # self.is_active = True
        # self.startTimer(1000)

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        super().showEvent(a0)
        self.look_for_changes()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        event.ignore()
        self.hide()

    def setAlwaysOnTop(self, state: bool) -> None:
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, state)
        self.a_toggle_on_top.setChecked(state)
        self.raiseOnTop()

    def about(self) -> None:
        QtWidgets.QMessageBox.about(
            self,
            "About RomashkiSync",
            """
            <p><b>RomashkiSync</b> is a file synchronization program.</p>
            <p>...</p>
            <p>&copy; Mamay Nikita, 2022.</p>
            """
        )

    def raiseOnTop(self) -> None:
        if self.isMaximized():
            self.showMaximized()
        else:
            self.showNormal()
        self.activateWindow()
        self.raise_()

    def toggle(self) -> None:
        if self.isHidden() or self.isMinimized():
            self.raiseOnTop()
        else:
            self.hide()

    def exit(self) -> None:
        self.close()
        self.exitSignal.emit()
        self.tray_icon.hide()

    def timerEvent(self, event: QtCore.QTimerEvent) -> None:
        if self.is_active:
            self.showChanges()
        return super().timerEvent(event)

    def look_for_changes(self) -> None:
        fc_local = file_watcher.FilesCollection(self.local_folder_path)
        fc_gdrive = file_watcher.FilesCollection(self.gdrive_folder_path)

        new_local = file_watcher.FilesCollection.find_newer(fc_local, fc_gdrive)
        old_local = file_watcher.FilesCollection.find_newer(fc_gdrive, fc_local)

        print("Newer on PC (Upload to cloud):", new_local)
        print("Older on PC (Remove from cloud OR Download to PC):", old_local)

        self.reprs_list_widget1.init_representations(new_local)
        self.reprs_list_widget2.init_representations(old_local)

    def sync(self) -> None:
        checked_new_local = self.reprs_list_widget1.get_checked_files()
        checked_old_local = self.reprs_list_widget2.get_checked_files()
        print('Checked as "Upload to cloud":', checked_new_local)
        print('Checked as "Download to PC":', checked_old_local)

        if len(checked_new_local) > 0:
            text_new_local = "<br>".join([f.relpath for f in checked_new_local])
            if QtWidgets.QMessageBox.question(
                        self,
                        "from LOCAL to CLOUD",
                        f'Are you sure to copy files <br><br><code>{text_new_local}</code><br><br>from "{self.local_folder_path}"<br>to "{self.gdrive_folder_path}"?',
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                    ) == QtWidgets.QMessageBox.Yes:
                file_watcher.copy_files_array(checked_new_local, self.local_folder_path, self.gdrive_folder_path)
                print("Copied.")
            else:
                print("Abort.")

        if len(checked_old_local) > 0:
            text_old_local = "<br>".join([f.relpath for f in checked_old_local])
            if QtWidgets.QMessageBox.question(
                        self,
                        "from CLOUD to LOCAL",
                        f'Are you sure to copy files <br><br><code>{text_old_local}</code><br><br>from "{self.gdrive_folder_path}"<br>to "{self.local_folder_path}"?',
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                    ) == QtWidgets.QMessageBox.Yes:
                file_watcher.copy_files_array(checked_old_local, self.gdrive_folder_path, self.local_folder_path)
                print("Copied.")
            else:
                print("Abort.")

        self.look_for_changes()


if __name__ == "__main__":
    import file_watcher
    import config_reader
    import sys

    CONFIG = config_reader.CONFIG

    if len(sys.argv) != 2:
        print("Error: config path is not specified!")
        exit()

    config_reader.read_config_file(sys.argv[1])

    app = Application([])

    window = MainWindow(CONFIG)

    window.raiseOnTop()

    exit(app.exec())
