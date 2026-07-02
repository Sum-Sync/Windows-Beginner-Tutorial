"""
Windows 新手教程 —— 入口文件
by:FireFly_Sync
GPL-3.0
"""
import sys
from PySide6.QtWidgets import QApplication
from ui_main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())