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


def look_for_changes():
    fc_local = file_watcher.FilesCollection(CONFIG["local_folder_path"])
    fc_gdrive = file_watcher.FilesCollection(CONFIG["gdrive_folder_path"])

    new_local = file_watcher.FilesCollection.find_newer(fc_local, fc_gdrive)
    old_local = file_watcher.FilesCollection.find_newer(fc_gdrive, fc_local)

    print("Newer on PC (Upload to cloud):", new_local)
    print("Older on PC (Remove from cloud OR Download to PC):", old_local)

    if len(new_local) > 0:
        if input('Enter "yes" to copy new files from LOCAL to CLOUD.\nLocal --> Cloud\n> ') == "yes":
            file_watcher.copy_files_array(new_local, fc_local.path, fc_gdrive.path)
            print("Copied.")
        else:
            print("Abort.")

    if len(old_local) > 0:
        if input('Enter "yes" to copy new files from CLOUD to LOCAL.\nCloud --> Local\n> ') == "yes":
            file_watcher.copy_files_array(old_local, fc_gdrive.path, fc_local.path)
            print("Copied.")
        else:
            print("Abort.")




while True:
    i = input("look for changes? > ")
    if i == "exit":
        exit()
    look_for_changes()


# app = gui.Application([])

# window = gui.MainWindow()

# def f():
#     window.showChanges()

# window.dw = file_watcher.DirectoryWatcher(CONFIG["local_folder_path"], fc_local)
# window.show()


# exit(app.exec())



