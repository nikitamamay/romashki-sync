from PyQt5 import QtCore, QtGui, QtWidgets

import file_watcher
File = file_watcher.File

APP_NAME = "RomashkiSync"

FONT_FAMILY_MONOSPACE = "Consolas"

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
    def local():
        return QtGui.QIcon("icons/computer.png")
    def cloud():
        return QtGui.QIcon("icons/network_cloud.png")
    def cloud_old():
        return QtGui.QIcon("icons/network_cloud_old.png")
    def cloud_to_local():
        return QtGui.QIcon("icons/cloud_to_local.png")
    def local_to_cloud():
        return QtGui.QIcon("icons/local_to_cloud.png")



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

        self.setFont(QtGui.QFont(FONT_FAMILY_MONOSPACE))
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

    def setState(self, state: int):
        if state == 1:
            self.setStyleSheet("color: red")
        else:
            raise Exception(f'Unsupported state: {state}')

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

        self.pixmap = None

        self.layout_reprs = QtWidgets.QVBoxLayout()
        self.layout_reprs.setSpacing(2)
        self.layout_reprs.setContentsMargins(2, 2, 2, 2)
        self.layout_reprs.setAlignment(QtCore.Qt.AlignTop)

        self.container_reprs = QtWidgets.QWidget()
        self.container_reprs.setLayout(self.layout_reprs)
        self.container_reprs.paintEvent = lambda event: self.container_paintEvent(self.container_reprs, event)

        self.scroll_area = ScrollArea(self.container_reprs)
        self.scroll_area.setMinimumHeight(40)

        self.checkbox_all = QtWidgets.QCheckBox("Select All")
        self.checkbox_all.setTristate(False)
        self.checkbox_all.clicked.connect(self.set_state_to_all)

        self.layout_ = QtWidgets.QGridLayout()
        self.layout_.setSpacing(2)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.addWidget(self.checkbox_all, 1, 0, 1, 1)
        self.layout_.addWidget(self.scroll_area, 2, 0, 1, 1)
        self.setLayout(self.layout_)

    def container_paintEvent(self, container, a0: QtGui.QPaintEvent) -> None:
        if self.pixmap:
            painter = QtGui.QPainter()
            painter.begin(container)
            p_w_min = 32
            margin = min(20, (container.height() - p_w_min) / 2)
            p_w = max(min(128, container.width(), container.height()) - 2 * margin, p_w_min)
            painter.drawPixmap(container.width() - p_w - margin, margin, p_w, p_w, self.pixmap)
            painter.end()
        return super().paintEvent(a0)

    def init_representations(self, files: list[File]) -> None:
        self.clear_representations()
        for f in files:
            self.add_file_repr(f)
        self.check_tristate()

    def clear_representations(self) -> None:
        while len(self.reprs) > 0:
            self.layout_reprs.removeWidget(self.reprs.pop())

    def apply_intersections(self, l: list[File]) -> None:
        for f in l:
            for r in self.reprs:
                if r.file_obj.relpath == f.relpath:
                    r.setState(1)

    def add_file_repr(self, f: File) -> None:
        w = ChangeRepresentationWidget(f)
        self.layout_reprs.addWidget(w)
        self.reprs.append(w)
        w.toggled.connect(self.check_tristate)

    def set_state_to_all(self, state: bool) -> None:
        for r in self.reprs:
            r.setChecked(state)
        self.check_tristate()

    def get_checked_files(self) -> list[File]:
        l: list[File] = []
        for r in self.reprs:
            if r.isChecked():
                l.append(r.file_obj)
        return l

    def check_tristate(self) -> None:
        if len(self.reprs) > 0:
            state = self.reprs[0].isChecked()
            for i in range(1, len(self.reprs)):
                if self.reprs[i].isChecked() != state:
                    self.checkbox_all.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
                    return
            self.checkbox_all.setCheckState([
                QtCore.Qt.CheckState.Unchecked,
                QtCore.Qt.CheckState.Checked
            ][int(state)])
        else:
            self.checkbox_all.setCheckState(QtCore.Qt.CheckState.Unchecked)


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
        d.setWindowTitle(f'{title} - {APP_NAME}')
        d.setText(msg)
        d.setPixmap(pixmap)
        d.initFilenames(files)
        return bool(d.exec())


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

        self.config = config

        self.local_folder_path = self.config["local_folder_path"]
        self.gdrive_folder_path = self.config["gdrive_folder_path"]
        self.fc_last_sync: file_watcher.FilesCollection = file_watcher.get_last_sync(self.config["files_info_path"], self.gdrive_folder_path)

        # FileWatcher for local directory works strange: doesn't see changes in files, but sees file creation/deletion
        self.fw2 = QtCore.QFileSystemWatcher([self.gdrive_folder_path], self)
        self.fw2.directoryChanged.connect(self.change_detected)

        self.setMinimumSize(500, 200)
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

        self.reprs_list_widget_newlocal = ChangeRepresentationListWidget(self)
        self.reprs_list_widget_newlocal.pixmap = icon.local().pixmap(32, 32)
        self.reprs_list_widget_newgdrive = ChangeRepresentationListWidget(self)
        self.reprs_list_widget_newgdrive.pixmap = icon.cloud().pixmap(32, 32)
        self.reprs_list_widget_oldgdrive = ChangeRepresentationListWidget(self)
        self.reprs_list_widget_oldgdrive.pixmap = icon.cloud_old().pixmap(32, 32)

        self.le_msg = QtWidgets.QLineEdit()
        self.le_msg.setPlaceholderText("Message...")

        self.btn_sync = QtWidgets.QPushButton(icon.update(), "Sync")
        self.btn_sync.clicked.connect(self.sync)

        self.c_widget = QtWidgets.QWidget()
        self.gridlayout = QtWidgets.QGridLayout()
        self.gridlayout.addWidget(self.reprs_list_widget_newlocal, 0, 0, 1, 2)
        self.gridlayout.addWidget(self.reprs_list_widget_newgdrive, 0, 2, 1, 2)
        self.gridlayout.addWidget(self.reprs_list_widget_oldgdrive, 0, 4, 1, 2)
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

        new_local = file_watcher.FilesCollection.find_newer(fc_local, self.fc_last_sync)
        old_local = file_watcher.FilesCollection.find_newer(self.fc_last_sync, fc_local)
        new_gdrive = file_watcher.FilesCollection.find_newer(fc_gdrive, self.fc_last_sync)
        old_gdrive = file_watcher.FilesCollection.find_newer(self.fc_last_sync, fc_gdrive)

        # Is it OK ?
        # Actually, no: files can be in both new_gdrive and old_local => duplicates
        new_gdrive.extend(old_local)

        print("---")
        print("Newer on PC (Upload to cloud):", new_local)
        print("Newer on Cloud (Download from cloud OR Remove from cloud):", new_gdrive)
        # print("Older on PC (Download from cloud):", old_local)
        print("Older on Cloud (Wait for GDrive to download OR Error):", old_gdrive)
        print("---")

        if len(old_gdrive) > 0:
            text_oldgdrive = "<br>".join([f.relpath for f in old_gdrive])
            self.reprs_list_widget_oldgdrive.show()
            QtWidgets.QMessageBox.warning(
                self,
                "Old files detected",
                f'<p>Some files <br><br><code>{text_oldgdrive}</code><br><br>are older in "{self.gdrive_folder_path}" than they are presented as <code>last_sync</code> state.</p> \
                <p>The issue may be caused by GDrive still not downloaded new files from cloud. Wait for it.</p> \
                <p>Or if it is not the case, make sure to threat this error properly.</p>'
            )

        if len(old_local) > 0:
            text_oldlocal = "<br>".join([f.relpath for f in old_local])
            QtWidgets.QMessageBox.warning(
                self,
                "Old files detected",
                f'<p>Some files <br><br><code>{text_oldlocal}</code><br><br>are older in "{self.local_folder_path}" than they are presented as <code>last_sync</code> state.</p> \
                <p>The issue may be caused by the User not downloaded files that are newer in the cloud.</p> \
                <p>Or if it is not the case, make sure to threat this error properly.</p>'
            )

        intersections = file_watcher.get_intersections(new_local, new_gdrive)

        self.reprs_list_widget_newlocal.init_representations(new_local)
        self.reprs_list_widget_newgdrive.init_representations(new_gdrive)
        # self.reprs_list_widget_oldlocal.init_representations(old_local)
        self.reprs_list_widget_oldgdrive.init_representations(old_gdrive)

        self.reprs_list_widget_newlocal.apply_intersections(intersections)
        self.reprs_list_widget_newgdrive.apply_intersections(intersections)

    def sync(self) -> None:
        checked_new_local = self.reprs_list_widget_newlocal.get_checked_files()
        checked_old_local = self.reprs_list_widget_newgdrive.get_checked_files()
        print('Checked as "Upload to cloud":', checked_new_local)
        print('Checked as "Download to PC":', checked_old_local)

        check_changes = True

        if len(checked_new_local) > 0:
            if FileDialog.run(
                        self,
                        icon.local_to_cloud().pixmap(96, 32),
                        "from LOCAL to CLOUD",
                        f'Are you sure to copy {len(checked_new_local)} file(s)<br>from <code>{self.local_folder_path}</code><br>to <code>{self.gdrive_folder_path}</code> ?',
                        checked_new_local
                    ) == True:
                files_copied = file_watcher.copy_files_array(checked_new_local, self.local_folder_path, self.gdrive_folder_path)
                print("Copied from LOCAL to CLOUD:", files_copied)
                self.fc_last_sync.update_partially(files_copied)
            else:
                print("Abort.")
                check_changes = False

        if len(checked_old_local) > 0:
            if FileDialog.run(
                        self,
                        icon.cloud_to_local().pixmap(96, 32),
                        "from CLOUD to LOCAL",
                        f'Are you sure to copy {len(checked_old_local)} file(s)<br>from <code>{self.gdrive_folder_path}</code><br>to <code>{self.local_folder_path}</code> ?',
                        checked_old_local
                    ) == True:
                files_copied = file_watcher.copy_files_array(checked_old_local, self.gdrive_folder_path, self.local_folder_path)
                print("Copied from CLOUD to LOCAL:", files_copied)
                self.fc_last_sync.update_partially(files_copied)
            else:
                print("Abort.")
                check_changes = False

        file_watcher.save_last_sync(self.config["files_info_path"], self.fc_last_sync)

        if check_changes:
            self.look_for_changes()

    def change_detected(self):
        self.tray_icon.showMessage(
            "G-Drive has changed",
            f'Some files in {self.gdrive_folder_path} are changed.',
            TrayIcon.MessageIcon.Information,
            10000
        )
        # self.raiseOnTop()
        # self.look_for_changes()


if __name__ == "__main__":
    # import file_watcher
    # import config_reader
    # import sys

    # CONFIG = config_reader.CONFIG

    # if len(sys.argv) != 2:
    #     print("Error: config path is not specified!")
    #     exit()

    # config_reader.read_config_file(sys.argv[1])

    app = Application([])

    # window = MainWindow(CONFIG)

    # window.raiseOnTop()

    d = FileDialog()
    d.setText("Are you sure? " * 30)
    d.show()

    app.exec()
    print(d.result())

    exit()
