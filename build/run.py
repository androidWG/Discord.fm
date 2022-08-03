import importlib
import platform

import util
import globals

if __name__ == "__main__":
    version = globals.get_version(parsed=True)
    if util.arg_exists("-d", "--debug"):
        print("\033[93m\033[1mWARNING: Building debug version\033[0m")

    if platform.system() == "Windows":
        module = importlib.import_module("windows")
    elif platform.system() == "Darwin":
        module = importlib.import_module("macos")
    elif platform.system() == "Linux":
        module = importlib.import_module("linux")
    else:
        raise NotImplementedError("System is not supported")

    build_tool = module.instance()(version=version)
    build_tool.prepare_files()
    build_tool.build()

    if not util.arg_exists("--no-installer"):
        build_tool.make_installer()

    build_tool.cleanup()

    print(f"Finished building version {version}")
