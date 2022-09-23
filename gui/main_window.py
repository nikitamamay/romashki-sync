from PyQt5 import QtCore, QtGui, QtWidgets

from gui.misc import *
from gui.change_representation import *
from gui.file_info_dialog import *
from gui.config_window import *

import file_watcher
File = file_watcher.File


class MainWindow(QtWidgets.QMainWindow):
    exitSignal = QtCore.pyqtBoundSignal()
    changeSignal = QtCore.pyqtBoundSignal()
    raised = QtCore.pyqtBoundSignal()

    def __init__(self, config: Config, parent = None) -> None:
        super().__init__(parent)

        self.CONFIG = config

        self.fc_last_sync: file_watcher.FilesCollection = file_watcher.get_last_sync(self.CONFIG.get_files_info_path(), self.CONFIG.get_gdrive_folder_path())

        ### FileWatcher for local directory works strange: doesn't see changes in files, but sees file creation/deletion
        # self.fw2 = QtCore.QFileSystemWatcher([self.CONFIG.get_gdrive_folder_path()], self)
        # self.fw2.directoryChanged.connect(self.change_detected)

        self.setMinimumSize(500, 200)
        self.setGeometry(
            self.screen().size().width() - 800 - 20,
            self.screen().size().height() - 325 - 50,
            800,
            325
        )

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
        self.a_about = QtWidgets.QAction(icon.daisy(), "About", self.menubar)
        self.menu_window.addAction(self.a_about)
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

    # def timerEvent(self, event: QtCore.QTimerEvent) -> None:
    #     if self.is_active:
    #         self.showChanges()
    #     return super().timerEvent(event)

    def look_for_changes(self) -> None:
        fc_local = file_watcher.FilesCollection(self.CONFIG.get_local_folder_path())
        fc_gdrive = file_watcher.FilesCollection(self.CONFIG.get_gdrive_folder_path())

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
                f'<p>Some files <br><br><code>{text_oldgdrive}</code><br><br>are older in "{self.CONFIG.get_gdrive_folder_path()}" than they are presented as <code>last_sync</code> state.</p> \
                <p>The issue may be caused by GDrive still not downloaded new files from cloud. Wait for it.</p> \
                <p>Or if it is not the case, make sure to threat this error properly.</p>'
            )

        if len(old_local) > 0:
            text_oldlocal = "<br>".join([f.relpath for f in old_local])
            QtWidgets.QMessageBox.warning(
                self,
                "Old files detected",
                f'<p>Some files <br><br><code>{text_oldlocal}</code><br><br>are older in "{self.CONFIG.get_local_folder_path()}" than they are presented as <code>last_sync</code> state.</p> \
                <p>The issue may be caused by the User not downloaded files that are newer in the cloud.</p> \
                <p>Or if it is not the case, make sure to threat this error properly.</p>'
            )

        intersections = file_watcher.get_intersections(new_local, new_gdrive)

        self.reprs_list_widget_newlocal.init_representations(new_local)
        self.reprs_list_widget_newgdrive.init_representations(new_gdrive)
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
                        f'Are you sure to copy {len(checked_new_local)} file(s)<br>from <code>{self.CONFIG.get_local_folder_path()}</code><br>to <code>{self.CONFIG.get_gdrive_folder_path()}</code> ?',
                        checked_new_local
                    ) == True:
                files_copied = file_watcher.copy_files_array(checked_new_local, self.CONFIG.get_local_folder_path(), self.CONFIG.get_gdrive_folder_path())
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
                        f'Are you sure to copy {len(checked_old_local)} file(s)<br>from <code>{self.CONFIG.get_gdrive_folder_path()}</code><br>to <code>{self.CONFIG.get_local_folder_path()}</code> ?',
                        checked_old_local
                    ) == True:
                files_copied = file_watcher.copy_files_array(checked_old_local, self.CONFIG.get_gdrive_folder_path(), self.CONFIG.get_local_folder_path())
                print("Copied from CLOUD to LOCAL:", files_copied)
                self.fc_last_sync.update_partially(files_copied)
            else:
                print("Abort.")
                check_changes = False

        file_watcher.save_last_sync(self.CONFIG.get_files_info_path(), self.fc_last_sync)

        if check_changes:
            self.look_for_changes()

    def change_detected(self):
        print("change detected.")
        # self.tray_icon.showMessage(
        #     "G-Drive has changed",
        #     f'Some files in {self.CONFIG.get_gdrive_folder_path()} are changed.',
        #     TrayIcon.MessageIcon.Information,
        #     10000
        # )
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

    app = QtWidgets.QApplication([])

    # window = MainWindow(CONFIG)

    # window.raiseOnTop()

    # d = FileDialog()
    # d.setText("Are you sure? " * 30)
    # d.show()


    # print(d.result())

    exit(app.exec())
