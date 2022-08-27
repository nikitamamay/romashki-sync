import sys
import os

import config_reader

import file_watcher

import gui

### Loading config

CONFIG = config_reader.CONFIG

if len(sys.argv) <= 1:
    raise Exception("Config file path is not specified")

config_filepath = os.path.abspath(sys.argv[1])

if not os.path.exists(config_filepath):
    raise Exception("Specified config file doesn't exist!")
if not os.path.isfile(config_filepath):
    raise Exception("Specified config file is not a file!")

config_reader.read_config_file(config_filepath)

local_folder_path = CONFIG["local_folder_path"]
gdrive_folder_path = CONFIG["gdrive_folder_path"]


app = gui.Application([])

window = gui.MainWindow()


def look_for_changes():
    fc_local = file_watcher.FilesCollection(local_folder_path)
    fc_gdrive = file_watcher.FilesCollection(gdrive_folder_path)

    new_local = file_watcher.FilesCollection.find_newer(fc_local, fc_gdrive)
    old_local = file_watcher.FilesCollection.find_newer(fc_gdrive, fc_local)

    print("Newer on PC (Upload to cloud):", new_local)
    print("Older on PC (Remove from cloud OR Download to PC):", old_local)

    window.init_representations(new_local, old_local)




a1 = gui.QtWidgets.QAction("Look for changes")
a1.triggered.connect(look_for_changes)
window.menubar.addAction(a1)


def f():
    new_local, old_local = window.get_checked()
    print('Checked as "Upload to cloud":', new_local)
    print('Checked as "Download to PC":', old_local)


    if len(new_local) > 0:
        text_new_local = "<br>".join([f.relpath for f in new_local])
        if gui.QtWidgets.QMessageBox.question(window, "from LOCAL to CLOUD", f'Are you sure to copy files <br><br><code>{text_new_local}</code><br><br>from "{local_folder_path}"<br>to "{gdrive_folder_path}"?', gui.QtWidgets.QMessageBox.Yes | gui.QtWidgets.QMessageBox.No) == gui.QtWidgets.QMessageBox.Yes:
            file_watcher.copy_files_array(new_local, local_folder_path, gdrive_folder_path)
            print("Copied.")
        else:
            print("Abort.")

    if len(old_local) > 0:
        text_old_local = "<br>".join([f.relpath for f in old_local])
        if gui.QtWidgets.QMessageBox.question(window, "from CLOUD to LOCAL", f'Are you sure to copy files <br><br><code>{text_old_local}</code><br><br>from "{gdrive_folder_path}"<br>to "{local_folder_path}"?', gui.QtWidgets.QMessageBox.Yes | gui.QtWidgets.QMessageBox.No) == gui.QtWidgets.QMessageBox.Yes:
            file_watcher.copy_files_array(old_local, gdrive_folder_path, local_folder_path)
            print("Copied.")
        else:
            print("Abort.")

    look_for_changes()


a2 = gui.QtWidgets.QAction("Sync")
a2.triggered.connect(f)
window.menubar.addAction(a2)

# window.raiseOnTop()
window.show()

exit(app.exec())



