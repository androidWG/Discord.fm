class BaseInstall:
    def get_executable_path(self):
        pass

    def get_startup(self):
        pass

    def set_startup(self, new_value: bool, exe_path: str) -> bool:
        pass

    def install(self, path: str):
        pass
