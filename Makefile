PHONY: build

pyinstaller_ver = 5.4.1

ifeq ($(OS),Windows_NT)
	PLATFORM = win
	VENV_PATH := venv
	PY_EXEC := python
	PYTHON := .\$(VENV_PATH)\Scripts\$(PY_EXEC)
	PYINSTALLER = $(VENV_PATH)\Lib\site-packages\pyinstaller-$(pyinstaller_ver)-py3.10.egg\PyInstaller\__main__.py

	DEL_COMMAND := rmdir /s /q
else
	VENV_PATH := venv
	PY_EXEC := python3
	PYTHON := ./$(VENV_PATH)/bin/$(PY_EXEC)
	PYINSTALLER = $(VENV_PATH)/Lib/site-packages/pyinstaller-$(pyinstaller_ver)-py3.10.egg/PyInstaller/__main__.py

	DEL_COMMAND := rm -rf

	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Linux)
		PLATFORM = linux
	endif
	ifeq ($(UNAME_S),Darwin)
		PLATFORM = macos
	endif
endif

pip = $(PYTHON) -m pip
activate = $(VENV_PATH)/Scripts/activate

$(activate): requirements.txt
	$(PY_EXEC) -m venv venv
	$(pip) install -r requirements.txt
	$(pip) install black

ifeq ($(PLATFORM), win)
	$(pip) install pywin32
	$(PYTHON) venv\Scripts\pywin32_postinstall.py -install
endif
ifeq ($(PLATFORM), macos)
	$(pip) install aquaui
endif
ifeq ($(PLATFORM), linux)
	$(pip) install PyYAML requirements-parser
endif

$(PYINSTALLER): $(activate)
# Build PyInstaller from source, install form pip if not on Windows
# This prevents antiviruses from marking the app as a virus
ifeq ($(PLATFORM),win)
	-$(DEL_COMMAND) pyinstaller

	git clone https://github.com/pyinstaller/pyinstaller.git
	cd pyinstaller && \
		git checkout tags/v$(pyinstaller_ver)
	cd pyinstaller\bootloader && \
		..\.$(PYTHON) ./waf distclean all
	$(pip) install wheel
	cd pyinstaller && \
		.$(PYTHON) setup.py install

	$(DEL_COMMAND) pyinstaller
endif
ifeq ($(PLATFORM),linux)
	@echo Current platform is Linux, not installing PyInstaller
else
	$(pip) install PyInstaller
endif

black:
	@echo Running black formatter
	$(PYTHON) -m black src

setup: $(activate)
	@echo Set up Discord.fm

run: $(activate)
	cd src && \
		.$(PYTHON) main.py

run_settings: $(activate)
	cd src && \
		.$(PYTHON) ui.py

build: $(activate) $(PYINSTALLER) black
	$(PYTHON) build/run.py

clean:
	$(DEL_COMMAND) __pycache__
	$(DEL_COMMAND) venv