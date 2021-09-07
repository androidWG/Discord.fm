import sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtCore import QFile, QIODevice, Slot


@Slot()
def say_hello():
    print("Hello!!")


def start_ui():
    app = QApplication(sys.argv)

    ui_file_name = "settings.ui"
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
        print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
        sys.exit(-1)

    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()
    if not window:
        print(loader.errorString())
        sys.exit(-1)
    window.show()

    # Connect button methods
    service_btn = window.findChild(QPushButton, "serviceBtn")
    service_btn.clicked.connect(say_hello)

    sys.exit(app.exec())


if __name__ == "__main__":
    start_ui()
