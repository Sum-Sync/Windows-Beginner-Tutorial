import json
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt

class MenuPage(QWidget):
    def __init__(self, start_chapter_callback):
        super().__init__()
        self.start_chapter = start_chapter_callback
        self.setStyleSheet("background-color: #F3F3F3;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        title = QLabel("🌐 Windows 新手教程")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #1e1e2e;")
        layout.addWidget(title)

        subtitle = QLabel("点击任意章节开始学习")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 16px; color: #555;")
        layout.addWidget(subtitle)

        # 扁平按钮样式
        btn_style = """
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                padding: 18px 25px;
                font-size: 18px; color: #1e1e1e;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #E8E8E8;
                border-color: #A0A0A0;
            }
            QPushButton:pressed {
                background-color: #D0D0D0;
            }
        """

        # 加载教程数据（使用脚本所在目录的绝对路径）
        chapter_titles = []
        try:
            # 获取本文件所在的目录（即 bin 文件夹）
            base_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(base_dir, "tutorial_data.json")
            print(f"[DEBUG] 尝试加载 JSON: {json_path}")   # 可在控制台看到路径
            if not os.path.exists(json_path):
                raise FileNotFoundError(f"文件不存在: {json_path}")
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            chapter_titles = [ch["title"] for ch in data["chapters"]]
        except Exception as e:
            QMessageBox.warning(
                self, "错误",
                f"加载教程数据失败:\n{e}\n\n请确保 tutorial_data.json 与此程序在同一文件夹内。"
            )
            chapter_titles = ["示例章节1", "示例章节2"]

        for name in chapter_titles:
            btn = QPushButton(name)
            btn.setStyleSheet(btn_style)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, n=name: self.start_chapter(n))
            layout.addWidget(btn)

        layout.addStretch()

        # 免责声明
        disc_btn = QPushButton("免责声明与关于")
        disc_btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                color: #888; font-size: 14px;
                text-decoration: underline;
            }
            QPushButton:hover { color: #333; }
        """)
        disc_btn.setCursor(Qt.PointingHandCursor)
        disc_btn.clicked.connect(self.show_disclaimer)
        layout.addWidget(disc_btn, alignment=Qt.AlignCenter)

    def show_disclaimer(self):
        QMessageBox.about(
            self,
            "免责声明与版权",
            "<h2>Windows 新手教程</h2>"
            "<p>本软件免费开源，仅用于教育目的。</p >"
            "<p><b>免责声明：</b>虚拟操作不修改真实系统，开发者不对误操作负责。</p >"
            "<p><b>版权：</b>由 <b>你的名字</b> 开发，使用 GPL-3.0 许可证。<br>"
            "允许自由传播、修改，但必须保留原作者署名。<br>"
            "严禁任何形式的商业倒卖。</p >"
        )