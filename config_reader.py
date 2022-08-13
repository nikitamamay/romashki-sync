
import os


DEFAULT_CONFIG = {
    "local_folder_path": r"C:\RomashkiData\Project123",
    "gdrive_folder_path": r"G:\My Drive\RomashkiData\CloudProject123",
    "files_info_path": r".files_info.json",
    "server_url": r"http://example.com",
    "personal_key": r"abcdef1234567890",
}

CONFIG = dict.copy(DEFAULT_CONFIG)


def parse_config(config_data: str) -> None:
    for line in config_data.splitlines(False):
        if line.strip() != "":
            key, value = line.split("\t", 1)
            CONFIG[key] = value
    CONFIG["local_folder_path"] = os.path.normpath(CONFIG["local_folder_path"])
    CONFIG["gdrive_folder_path"] = os.path.normpath(CONFIG["gdrive_folder_path"])
    CONFIG["files_info_path"] = os.path.normpath(CONFIG["files_info_path"])


def read_config_file(filepath: os.PathLike):
    with open(filepath, "r", encoding="utf-8") as f:
        parse_config(f.read())


def check_config() -> int:
    state = 0

    state += 1 * (1 - int( os.path.isdir(CONFIG["local_folder_path"]) ))
    state += 2 * (1 - int( os.path.isdir(CONFIG["gdrive_folder_path"]) ))

    ### send something like:
    # url = f'{CONFIG["server_url"]}/check-user?key={CONFIG["personal_key"]}'
    # state += 4 * (1 - int( is_user_valid(CONFIG["personal_key"]) ))

    return state

