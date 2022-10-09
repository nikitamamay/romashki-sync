import config
import sys
from delayed_handler import DelayedHandler


class Application:
    def __init__(self) -> None:
        self._app_cfg = config.AppConfig()
        self._prj_cfg = None  # config.ProjectConfig()

        self.delayed_handler = DelayedHandler()
        self._task_save_app_config = self.delayed_handler.create_task(self.save_app_config, 0.5)

    def get_app_config(self) -> config.AppConfig:
        return self._app_cfg

    def get_project_config(self) -> config.ProjectConfig:
        return self._prj_cfg

    def set_project_config(self, c: config.ProjectConfig) -> None:
        self._prj_cfg = c
        if not c is None:
            self._app_cfg.add_project_path(self._prj_cfg.get_filepath())
        else:
            self._app_cfg.add_project_path(None)
        self.save_app_config_delayed()

    def configure(self) -> None:
        raise Exception("Reimplement this!")

    def init_project(self) -> None:
        self._prj_cfg: config.ProjectConfig
        if self._prj_cfg is None:
            raise Exception("Config is None")
        if not self._prj_cfg.is_valid():
            raise Exception("Config is not valid")

        config.ensure_folder(self._prj_cfg.get_local_folder_path())
        config.ensure_folder(self._prj_cfg.get_gdrive_folder_path())
        config.ensure_file(self._prj_cfg.get_files_info_path())
        config.ensure_file(self._prj_cfg.get_filepath())

    def open_project(self) -> None:
        raise Exception("Reimplement this!")

    def read_project(self, path: str) -> None:
        raise Exception("Reimplement this!")

    def create_project(self) -> None:
        self.close_project()
        self.set_project_config(config.ProjectConfig())

    def close_project(self) -> None:
        self.set_project_config(None)

    def save_project(self) -> None:
        raise Exception("Reimplement this!")

    def save_project_as(self) -> None:
        raise Exception("Reimplement this!")

    def read_last_project_if_exists(self) -> None:
        if self._app_cfg.has_last_project_path():
            path = self._app_cfg.get_last_project_path()
            if not path is None:
                self.read_project(path)

    def save_app_config(self) -> None:
        self._app_cfg.save()

    def save_app_config_delayed(self) -> None:
        self.delayed_handler.do_task(self._task_save_app_config)

    def exit() -> None:
        sys.exit(0)


