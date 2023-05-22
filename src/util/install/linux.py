from util.install import BaseInstall


# TODO: Make this a real class
class LinuxInstall(BaseInstall):
    def get_startup(self):
        return True


def instance():
    return LinuxInstall
