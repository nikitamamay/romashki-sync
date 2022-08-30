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

window = gui.MainWindow(CONFIG)

# window.raiseOnTop()
window.show()

exit(app.exec())



