import sys
import os
import importlib
import platform

sys.path.append(os.path.abspath("src"))
import util
import globals

if __name__ == "__main__":
    version = globals.get_version(parsed=True)
    debug = util.arg_exists("-d", "--debug")
    if debug:
        print("\033[93m\033[1mWARNING: Building debug version\033[0m")

    if platform.system() == "Windows":
        module = importlib.import_module("windows")
    elif platform.system() == "Darwin":
        module = importlib.import_module("macos")
    elif platform.system() == "Linux":
        module = importlib.import_module("linux")
    else:
        raise NotImplementedError("System is not supported")

    build_tool = module.instance()(version=version, debug=debug)
    build_tool.prepare_files()

    if not util.arg_exists("--installer-only", "-I"):
        build_tool.build()
        print("Skipping installer build")

    if not util.arg_exists("--build-only", "-B"):
        print("Skipping app build")
        build_tool.make_installer()

    build_tool.cleanup()

    print(f"Finished building version {version}")
