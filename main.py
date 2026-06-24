import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel

app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("未开发完全-Windows-新手教程中文单语言版")
window.setGeometry(100, 100, 800, 500)  # 左、上、宽、高

label = QLabel(
    '这个项目目前还只是起步阶段,我只有孤身一人,您可以加入我的队伍,让我变成我们!\nThis project is still just getting started, and I\'m all alone. You can join my team and turn me into \'us\'!')
label.setStyleSheet("font-size: 18px; padding: 20px;")
window.setCentralWidget(label)

window.show()
sys.exit(app.exec())