import config
import sys
from delayed_handler import DelayedHandler


class Application:
    def __init__(self) -> None:
        self._app_cfg = config.AppConfig()
        self._prj_cfg = config.ProjectConfig()

        if self._app_cfg.has_last_project_path():
            path = self._app_cfg.get_last_project_path()
            self._prj_cfg = config.ProjectConfig.read_from_file(path)

        self.delayed_handler = DelayedHandler()
        self._task_save_all_configs = self.delayed_handler.create_task(self.save_all_configs, 0.5)

    def get_app_config(self) -> config.AppConfig:
        return self._app_cfg

    def get_project_config(self) -> config.ProjectConfig:
        return self._prj_cfg

    def set_project_config(self, c: config.ProjectConfig) -> None:
        self._prj_cfg = c
        self._app_cfg.add_project_path(self._prj_cfg.get_filepath())

    def init_project(self) -> None:
        self._prj_cfg: config.ProjectConfig
        self._app_cfg: config.AppConfig
        config.ensure_folder(self._prj_cfg.get_local_folder_path())
        config.ensure_folder(self._prj_cfg.get_gdrive_folder_path())
        config.ensure_file(self._prj_cfg.get_files_info_path())
        config.ensure_file(self._prj_cfg.get_filepath())
        self._prj_cfg.save()
        self._app_cfg.add_project_path(self._prj_cfg.get_filepath())

    def save_all_configs_delayed(self) -> None:
        self.delayed_handler.do_task(self._task_save_all_configs)

    def save_all_configs(self) -> None:
        self._app_cfg.save()
        if self._prj_cfg.is_valid():
            self._prj_cfg.save()

        print("saved")

    def exit() -> None:
        sys.exit(0)


