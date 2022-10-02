import os
import sys

from config_reader import  *
import const


APP_CONFIG_FOLDER = get_user_config_folder(const.APP_CONFIG_FOLDER_NAME)
APP_CONFIG_FILE_PATH = os.path.join(APP_CONFIG_FOLDER, const.APP_CONFIG_FILE_NAME)


class ProjectConfig(ConfigReader):
    def __init__(self) -> None:
        super().__init__({
            "local_folder_path": '',
            "gdrive_folder_path": '',
            "files_info_path": '',
            # "server_url": r"http://example.com",
            # "personal_key": r"abcdef1234567890",
        })

    @staticmethod
    def read_from_file(filepath: str) -> 'ProjectConfig':
        pc = ProjectConfig()
        pc.set_filepath(filepath)
        pc.reload()
        return pc

    def get_local_folder_path(self) -> str:
        return self._cfg["local_folder_path"]

    def get_gdrive_folder_path(self) -> str:
        return self._cfg["gdrive_folder_path"]

    def get_files_info_path(self) -> str:
        return self._cfg["files_info_path"]

    def _set_local_folder_path(self, value: str) -> None:
        self._cfg["local_folder_path"] = value

    def _set_gdrive_folder_path(self, value: str) -> None:
        self._cfg["gdrive_folder_path"] = value

    def _set_files_info_path(self, value: str) -> None:
        self._cfg["files_info_path"] = value

    def check(self) -> bool:
        if self.get_local_folder_path() == "":
            raise Exception(f'Local folder\'s path is not specified')
        path = os.path.abspath(self.get_local_folder_path())

        if not exists(path) and not is_folder_creatable(path):
            raise Exception(f'Folder "{path}" cannot be created')

        if do_paths_intersect(self.get_local_folder_path(), self.get_gdrive_folder_path()):
            raise Exception(f'Local folder\'s path and Google Drive folder\'s path are intersecting')

        if self.get_gdrive_folder_path() == "":
            raise Exception(f'Google Drive folder\'s path is not specified')
        path = os.path.abspath(self.get_gdrive_folder_path())

        if not exists(path) and not is_folder_creatable(path):
            raise Exception(f'Folder "{path}" cannot be created')

        if self.get_files_info_path() == "":
            raise Exception(f'Files info file\'s path is not specified')
        path = os.path.abspath(self.get_files_info_path())

        if not exists(path) and not is_file_creatable(path):
            raise Exception(f'File "{path}" cannot be created')

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



class AppConfig(ConfigReader):
    def __init__(self) -> None:
        super().__init__({
            "last_projects": [],
            "geometry": [0, 0, 800, 325],
            "always_on_top": False,
        })
        self.set_filepath(APP_CONFIG_FILE_PATH)
        self.reload()

    def get_last_project_path(self) -> str:
        if self.has_last_project_path():
            return self._cfg["last_projects"][-1]
        return ""

    def has_last_project_path(self) -> bool:
        return len(self._cfg["last_projects"]) != 0

    def add_project_path(self, filepath: str) -> None:
        if filepath != "":
            if filepath in self._cfg["last_projects"]:
                self._cfg["last_projects"].remove(filepath)
            self._cfg["last_projects"].append(filepath)
            self.save()

    def get_last_projects_paths_list(self) -> list[str]:
        return self._cfg["last_projects"]

    def get_geometry(self) -> list[int, int, int, int]:
        return self._cfg["geometry"]

    def set_geometry(self, g: list[int, int, int, int]) -> None:
        self._cfg["geometry"].clear()
        self._cfg["geometry"].extend(g)

    def get_always_on_top(self) -> bool:
        return self._cfg["always_on_top"]

    def set_always_on_top(self, state: bool) -> None:
        self._cfg["always_on_top"] = state


if __name__ == "__main__":
    pass
    # r = Config.is_file_creatable("D:/abc/sdlkf/sakldjf/file.txt")
    # print(r)
