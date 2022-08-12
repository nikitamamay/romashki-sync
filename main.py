import sys
import os

import config_reader

import file_watcher


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


files_local = file_watcher.get_files_collection(file_watcher.get_files(CONFIG["local_folder_path"]))
files_gdrive = file_watcher.get_files_collection(file_watcher.get_files(CONFIG["gdrive_folder_path"]))

### !!! "target" file list has to be synchronized through web-server !!!
#target = files_gdrive

pc_to_cloud = file_watcher.find_newer(files_local, files_gdrive)
cloud_to_pc = file_watcher.find_newer(files_gdrive, files_local)

print("Newer on PC (Upload to cloud):", pc_to_cloud)
print("Older on PC (Remove from cloud OR Download to PC):", cloud_to_pc)


for path_rel in pc_to_cloud:
    file_watcher.copy_file(CONFIG["local_folder_path"] + os.path.sep + path_rel, CONFIG["gdrive_folder_path"] + os.path.sep + path_rel)

for path_rel in cloud_to_pc:
    file_watcher.copy_file(CONFIG["gdrive_folder_path"] + os.path.sep + path_rel, CONFIG["local_folder_path"] + os.path.sep + path_rel)


