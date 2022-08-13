import sys
import os
from time import sleep

import config_reader

import file_watcher

import gui

### Loading config

CONFIG = config_reader.CONFIG

if len(sys.argv) <= 1:
    raise Exception("Config file path is not specified")

path = os.path.abspath(sys.argv[1])

if not os.path.exists(path):
    raise Exception("Specified config file doesn't exist!")
if not os.path.isfile(path):
    raise Exception("Specified config file is not a file!")

config_reader.read_config_file(path)



fcs = file_watcher.load_files_info(CONFIG["files_info_path"])
if len(fcs) != 2:
    fc_local = file_watcher.FilesCollection(CONFIG["local_folder_path"])
    fc_gdrive = file_watcher.FilesCollection(CONFIG["gdrive_folder_path"])
    file_watcher.save_files_info(CONFIG["files_info_path"], [fc_local, fc_gdrive])
else:
    fc_local, fc_gdrive = fcs

### !!! "target" file list has to be synchronized through web-server !!!
#target = files_gdrive

# pc_to_cloud = file_watcher.find_newer(files_local, files_gdrive)
# cloud_to_pc = file_watcher.find_newer(files_gdrive, files_local)

# print("Newer on PC (Upload to cloud):", pc_to_cloud)
# print("Older on PC (Remove from cloud OR Download to PC):", cloud_to_pc)


# for path_rel in pc_to_cloud:
#     file_watcher.copy_file(CONFIG["local_folder_path"] + os.path.sep + path_rel, CONFIG["gdrive_folder_path"] + os.path.sep + path_rel)

# for path_rel in cloud_to_pc:
#     file_watcher.copy_file(CONFIG["gdrive_folder_path"] + os.path.sep + path_rel, CONFIG["local_folder_path"] + os.path.sep + path_rel)


# file_watcher.DirectoryWatcher()






app = gui.Application([])

window = gui.MainWindow()

def f():
    window.showChanges()

window.dw = file_watcher.DirectoryWatcher(CONFIG["local_folder_path"], fc_local)
window.show()


exit(app.exec())
