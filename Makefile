ifeq ($(OS),Windows_NT)
    PLATFORM = win
    VENV_PATH := venv/Scripts
    PY_EXEC := python
else
    VENV_PATH := venv/bin
    PY_EXEC := python3

    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Linux)
        PLATFORM = linux
    endif
    ifeq ($(UNAME_S),Darwin)
        PLATFORM = macos
    endif
endif

pip = ./$(VENV_PATH)/pip
python = ./$(VENV_PATH)/$(PY_EXEC)
activate = $(VENV_PATH)/activate

pyinstaller = $(VENV_PATH)/Lib/site-packages/PyInstaller/__main__.py

$(activate): requirements.txt
    $(PY_EXEC) -m venv venv
    $(pip) install -r requirements.txt

	ifeq ($(PLATFORM), windows)
		$(pip) install pywin32
		$(PY_EXEC) venv/Scripts/pywin32_postinstall.py -install
    ifeq ($(PLATFORM), macos)
        $(pip) install aquaui
    endif
    ifeq ($(PLATFORM), linux)
        $(pip) install PyYAML requirements-parser
    endif

$(pyinstaller): $(activate)
# Build PyInstaller from source, install form pip if not on Windows
# This prevents antiviruses from marking the app as a virus
    ifeq ($(PLATFORM),win)
        git clone --branch master https://github.com/pyinstaller/pyinstaller.git
        cd pyinstaller
        git checkout fbf7948be85177dd44b41217e9f039e1d176de6b
        cd bootloader
        $(python) ./waf distclean all
        cd..
        .$(python) setup.py install
    endif
    ifeq ($(PLATFORM),linux)
    	echo "Current platform is Linux, not installing PyInstaller"
    else
    	$(pip) install PyInstaller
    endif

run: $(activate)
    $(python) main.py

build: $(activate) $(pyinstaller)
    $(python) build/build.py

clean:
    rm -rf __pycache__
    rm -rf venv