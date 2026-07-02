from PySide6.QtWidgets import QMainWindow, QStackedWidget, QWidget
from ui_menu_page import MenuPage
from ui_tutorial_overlay import TutorialOverlay

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows 新手教程")
        self.resize(900, 650)

        # 扁平化背景
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F3F3F3;
            }
        """)

        # 堆叠只用于目录，全屏教程另开窗口
        self.stack = QStackedWidget()
        self.menu_page = MenuPage(self.start_chapter)
        self.stack.addWidget(self.menu_page)

        self.setCentralWidget(self.stack)
        self.stack.setCurrentIndex(0)

    def start_chapter(self, chapter_name):
        self.hide()
        self.overlay = TutorialOverlay(chapter_name, self.show_menu)
        self.overlay.show()

    def show_menu(self):
        self.show()
        self.stack.setCurrentIndex(0)