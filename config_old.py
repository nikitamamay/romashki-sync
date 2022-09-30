import os
import sys

APPDATA_PATH: str = os.path.join(os.getenv("APPDATA"), "RomashkiSync")

if sys.platform != "win32":
    print(f'Your current platform is "{sys.platform}". Only "win32" is supported for now. Sorry.')
    sys.exit(1)


class Config():
    def __init__(self):
        self._local_folder_path = ''
        self._gdrive_folder_path = ''
        self._files_info_path = ''
        # self._server_url = r"http://example.com"
        # self._personal_key = r"abcdef1234567890"

    def read_config_file(self, filepath: os.PathLike) -> 'Config':
        filepath = os.path.abspath(filepath)

        if not os.path.exists(filepath):
            raise Exception("Specified config file doesn't exist!")

        if not os.path.isfile(filepath):
            raise Exception("Specified config file is not a file!")

        with open(filepath, "r", encoding="utf-8") as f:
            self._init_from_str(f.read())

        return self

    def _init_from_str(self, config_data: str) -> None:
        d = {}
        for line in config_data.splitlines(False):
            if line.strip() != "":
                key, value = line.split("\t", 1)
                d[key] = value
        self._set_local_folder_path(os.path.normpath(d["local_folder_path"]))
        self._set_gdrive_folder_path(os.path.normpath(d["gdrive_folder_path"]))
        self._set_files_info_path(os.path.normpath(d["files_info_path"]))

    def get_local_folder_path(self) -> str:
        return self._local_folder_path

    def get_gdrive_folder_path(self) -> str:
        return self._gdrive_folder_path

    def get_files_info_path(self) -> str:
        return self._files_info_path

    def _set_local_folder_path(self, value: str) -> None:
        self._local_folder_path = value

    def _set_gdrive_folder_path(self, value: str) -> None:
        self._gdrive_folder_path = value

    def _set_files_info_path(self, value: str) -> None:
        self._files_info_path = value

    def check(self) -> bool:
        if self.get_local_folder_path() == "":
            raise Exception(f'Local folder\'s path is not specified!')
        path = os.path.abspath(self.get_local_folder_path())

        if not Config.exists(path) and not Config.is_folder_creatable(path):
            raise Exception(f'Folder "{path}" cannot be created!')

        if self.get_gdrive_folder_path() == "":
            raise Exception(f'Google Drive folder\'s path is not specified!')
        path = os.path.abspath(self.get_gdrive_folder_path())

        if not Config.exists(path) and not Config.is_folder_creatable(path):
            raise Exception(f'Folder "{path}" cannot be created!')

        if self.get_files_info_path() == "":
            raise Exception(f'Files info file\'s path is not specified!')
        path = os.path.abspath(self.get_files_info_path())

        if not Config.exists(path) and not Config.is_file_creatable(path):
            raise Exception(f'File "{path}" cannot be created!')

        ### send something like:
        # url = f'{CONFIG["server_url"]}/check-user?key={CONFIG["personal_key"]}'
        # state += 4 * (1 - int( is_user_valid(CONFIG["personal_key"]) ))

        return True

    def is_valid(self) -> bool:
        try:
            self.check()
            return True
        except Exception as e:
            return False

    @staticmethod
    def is_folder_creatable(filepath: str) -> bool:
        filepath = os.path.abspath(filepath)
        drive = os.path.splitdrive(filepath)[0]
        if not os.path.exists(drive):
            return False
        while not os.path.exists(filepath):
            filepath = os.path.dirname(filepath)
        return True

    @staticmethod
    def is_file_creatable(filepath: str) -> bool:
        return Config.is_folder_creatable(os.path.dirname(os.path.abspath(filepath)))

    @staticmethod
    def create_folder(filepath: str) -> None:
        filepath = os.path.abspath(filepath)
        if not os.path.isdir(filepath):
            os.makedirs(filepath)

    @staticmethod
    def create_file(filepath: str) -> None:
        Config.create_folder(os.path.dirname(os.path.abspath(filepath)))
        with open(filepath, "a", encoding='utf-8') as f:
            pass

    @staticmethod
    def exists(filepath: str) -> bool:
        return os.path.exists(filepath)

    @staticmethod
    def ensure_appdata_folder() -> None:
        if not os.path.isdir(APPDATA_PATH):
            os.makedirs(APPDATA_PATH)






if __name__ == "__main__":
    r = Config.is_file_creatable("D:/abc/sdlkf/sakldjf/file.txt")
    print(r)
