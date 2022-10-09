from PyQt5 import QtCore, QtGui, QtWidgets

import sys

from gui.misc import *
from gui.change_representation import *
from gui.file_info_dialog import *
from gui.config_window import *

import config
import application
import config_reader

import file_watcher
File = file_watcher.File


class MainWindow(QtWidgets.QMainWindow):
    exitSignal = QtCore.pyqtBoundSignal()
    changeSignal = QtCore.pyqtBoundSignal()
    raised = QtCore.pyqtBoundSignal()

    def __init__(self, app: application.Application, parent = None) -> None:
        super().__init__(parent)

        self._app = app

        self.is_project_initted = False
        self.fc_last_sync = None

        self.setMinimumSize(500, 200)

        self.menubar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menubar)

        self.menu_recent_projects = QtWidgets.QMenu("Recent projects", self)

        self.menu_project = QtWidgets.QMenu("Project", self)
        self.menu_project.addAction(icon.new_document(), "Create new", self._app.create_project)
        self.menu_project.addAction(icon.folder(), "Open", self._app.open_project)
        self.menu_project.addMenu(self.menu_recent_projects)
        self.menu_project.addSeparator()
        self.menu_project.addAction(icon.cog(), "Configure", self._app.configure)
        self.menu_project.addSeparator()
        self.menu_project.addAction(icon.save(), "Save", self._app.save_project)
        self.menu_project.addAction(icon.save_as(), "Save as...", self._app.save_project_as)
        self.menu_project.addSeparator()
        self.menu_project.addAction(icon.cancel(), "Close project", self._app.close_project)
        self.a_recent_projects = self.menubar.addMenu(self.menu_project)

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
        self.menu_window.addAction(QtGui.QIcon("icons/cancel.png"), "Exit", self._app.exit)
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
        # self.gridlayout.addWidget(self.le_msg, 1, 0, 1, 3)
        self.gridlayout.addWidget(self.btn_sync, 3, 0, 1, 1)
        self.c_widget.setLayout(self.gridlayout)

        self.setCentralWidget(self.c_widget)

        self.apply_app_config()
        self.init_recent_projects_list()

        self.window_close_project()

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
        self._app.get_app_config().set_always_on_top(state)
        self._app.save_app_config_delayed()

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

    def apply_geometry(self, x: int, y: int, w: int, h: int) -> None:
        if x != 0 or y != 0:
            x = max(0, min(self.screen().geometry().width() - w, x))
            y = max(0, min(self.screen().geometry().height() - h, y))
            self.move(x, y)
        self.resize(w, h)

    def apply_app_config(self) -> None:
        self.apply_geometry(*self._app.get_app_config().get_geometry())
        self.setAlwaysOnTop(self._app.get_app_config().get_always_on_top())

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self._app.get_app_config().set_geometry(self.get_pos_and_size())
        self._app.save_app_config_delayed()
        return super().resizeEvent(a0)

    def moveEvent(self, a0: QtGui.QMoveEvent) -> None:
        self._app.get_app_config().set_geometry(self.get_pos_and_size())
        self._app.save_app_config_delayed()
        return super().moveEvent(a0)

    # def timerEvent(self, event: QtCore.QTimerEvent) -> None:
    #     if self.is_active:
    #         self.showChanges()
    #     return super().timerEvent(event)

    def window_init_project(self) -> None:
        self.fc_last_sync: file_watcher.FilesCollection = file_watcher.get_last_sync(
            self._app.get_project_config().get_files_info_path(),
            self._app.get_project_config().get_gdrive_folder_path()
        )
        ### FileWatcher for local directory works strange: doesn't see changes in files, but sees file creation/deletion
        # self.fw2 = QtCore.QFileSystemWatcher([self.CONFIG.get_gdrive_folder_path()], self)
        # self.fw2.directoryChanged.connect(self.change_detected)

        # self.is_active = True
        # self.startTimer(1000)
        self.is_project_initted = True

        self.init_recent_projects_list()

        self.setWindowTitle(f'{os.path.basename(self._app.get_project_config().get_filepath())} - {const.APP_NAME}')
        self.centralWidget().setEnabled(True)

        self.look_for_changes()

    def window_close_project(self) -> None:
        self.fc_last_sync = None
        self.is_project_initted = False
        self.reprs_list_widget_newlocal.clear_representations()
        self.reprs_list_widget_newgdrive.clear_representations()
        self.reprs_list_widget_oldgdrive.clear_representations()
        self.centralWidget().setEnabled(False)
        self.setWindowTitle(const.APP_NAME)

    def init_recent_projects_list(self) -> None:
        def action_f(cfg_path__: str):
            def f():
                self.window_close_project()
                try:
                    self._app.read_project(cfg_path__)
                    self._app.init_project()
                except Exception as e:
                    return critical(e)
            return f

        while len(self.menu_recent_projects.actions()) > 0:
            self.menu_recent_projects.removeAction(self.menu_recent_projects.actions()[0])
        for path in reversed(self._app.get_app_config().get_last_projects_paths_list()):
            if not (path is None or path == ""):
                self.menu_recent_projects.addAction(
                    path,
                    action_f(path)
                )

    def look_for_changes(self) -> None:
        if not self.is_project_initted: return

        fc_local = file_watcher.FilesCollection(self._app.get_project_config().get_local_folder_path())
        fc_gdrive = file_watcher.FilesCollection(self._app.get_project_config().get_gdrive_folder_path())

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
                f'<p>Some files <br><br><code>{text_oldgdrive}</code><br><br>are older in "{self._app.get_project_config().get_gdrive_folder_path()}" than they are presented as <code>last_sync</code> state.</p> \
                <p>The issue may be caused by GDrive still not downloaded new files from cloud. Wait for it.</p> \
                <p>Or if it is not the case, make sure to threat this error properly.</p>'
            )

        if len(old_local) > 0:
            text_oldlocal = "<br>".join([f.relpath for f in old_local])
            QtWidgets.QMessageBox.warning(
                self,
                "Old files detected",
                f'<p>Some files <br><br><code>{text_oldlocal}</code><br><br>are older in "{self._app.get_project_config().get_local_folder_path()}" than they are presented as <code>last_sync</code> state.</p> \
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
        if not self.is_project_initted: return

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
                        f'Are you sure to copy {len(checked_new_local)} file(s)<br>from <code>{self._app.get_project_config().get_local_folder_path()}</code><br>to <code>{self._app.get_project_config().get_gdrive_folder_path()}</code> ?',
                        checked_new_local
                    ) == True:
                files_copied = file_watcher.copy_files_array(checked_new_local, self._app.get_project_config().get_local_folder_path(), self._app.get_project_config().get_gdrive_folder_path())
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
                        f'Are you sure to copy {len(checked_old_local)} file(s)<br>from <code>{self._app.get_project_config().get_gdrive_folder_path()}</code><br>to <code>{self._app.get_project_config().get_local_folder_path()}</code> ?',
                        checked_old_local
                    ) == True:
                files_copied = file_watcher.copy_files_array(checked_old_local, self._app.get_project_config().get_gdrive_folder_path(), self._app.get_project_config().get_local_folder_path())
                print("Copied from CLOUD to LOCAL:", files_copied)
                self.fc_last_sync.update_partially(files_copied)
            else:
                print("Abort.")
                check_changes = False

        file_watcher.save_last_sync(self._app.get_project_config().get_files_info_path(), self.fc_last_sync)

        if check_changes:
            self.look_for_changes()

    def change_detected(self):
        print("change detected.")

    def get_pos_and_size(self) -> list[int, int, int, int]:
        return [self.x(), self.y(), self.width(), self.height()]



if __name__ == "__main__":
    # import file_watcher
    # import config_reader
    # import sys

    # CONFIG = config_reader.CONFIG

    # if len(sys.argv) != 2:
    #     print("Error: config path is not specified!")
    #     sys.exit()

    # config_reader.read_config_file(sys.argv[1])

    app = QtWidgets.QApplication([])

    # window = MainWindow(CONFIG)

    # window.raiseOnTop()

    # d = FileDialog()
    # d.setText("Are you sure? " * 30)
    # d.show()


    # print(d.result())

    sys.exit(app.exec())
