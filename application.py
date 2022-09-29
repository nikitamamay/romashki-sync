import config


class Application:
    def __init__(self) -> None:
        self._app_cfg = config.AppConfig()
        self._prj_cfg = config.ProjectConfig()

        if self._app_cfg.has_last_project_path():
            path = self._app_cfg.get_last_project_path()
            self._prj_cfg = config.ProjectConfig(path)

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
        config.create_folder(self._prj_cfg.get_local_folder_path())
        config.create_folder(self._prj_cfg.get_gdrive_folder_path())
        config.create_file(self._prj_cfg.get_files_info_path())
        config.create_file(self._prj_cfg.get_filepath())
        self._prj_cfg.save()
        self._app_cfg.add_project_path(self._prj_cfg.get_filepath())


