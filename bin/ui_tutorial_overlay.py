import json
import os
from PySide6.QtWidgets import (
    QWidget, QApplication, QPushButton, QLabel, QVBoxLayout,
    QFileIconProvider
)
from PySide6.QtCore import (
    Qt, QRect, QPoint, QPropertyAnimation, QEasingCurve, QTimer,
    QFileInfo, Property, QSize
)
from PySide6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPixmap, QCursor, QPainterPath,
    QIcon
)
# ---------- 内置教程数据（使用假图标坐标） ----------
# 我们将在桌面固定位置绘制图标，坐标对应这里的 rect
BUILTIN_CHAPTERS = {
    "1. 认识鼠标（演示+交互）": [
        {"action": "demo_move", "pos": [200, 200], "text": "这是鼠标指针，你可以移动它。", "target": None},
        {"action": "demo_click", "pos": [100, 100], "text": "左键单击‘此电脑’图标。", "target": [80, 80, 80, 80]},
        {"action": "interactive", "required": "click", "rect": [80, 80, 80, 80],
         "text": "现在请你亲自单击‘此电脑’图标。"},
        {"action": "interactive", "required": "right_click", "rect": [200, 80, 80, 80],
         "text": "右键点击‘回收站’图标。"},
        {"action": "interactive", "required": "double_click", "rect": [320, 80, 80, 80], "text": "双击‘浏览器’图标。"}
    ],
    "2. 窗口操作（演示）": [
        {"action": "demo_move", "pos": [400, 200], "text": "窗口会出现在屏幕中央。", "target": None},
        {"action": "demo_click", "pos": [700, 10], "text": "单击右上角关闭按钮。", "target": [680, 0, 100, 30]},
    ]
}

# 假图标数据：名称, x, y, 宽, 高
FAKE_ICONS = [
    ("此电脑", 80, 80),
    ("回收站", 200, 80),
    ("浏览器", 320, 80),
    ("文档", 440, 80),
    ("设置", 560, 80),
]


# ---------- 全屏叠加层 ----------
class TutorialOverlay(QWidget):
    def __init__(self, chapter_name, back_callback):
        super().__init__()
        self.back_callback = back_callback
        self.steps = []
        self.current_step = 0
        self._demo_mouse_pos = QPoint(100, 100)
        self.anim = None
        self.interactive = False
        self.required_action = None
        self.target_rect = QRect()
        self.click_start = None
        self._highlight_flash = False

        # 全屏透明窗口
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        # 创建假图标控件（放在叠加层之上，但鼠标可穿透？需要可点击）
        self.icon_widgets = []
        self._create_fake_icons()

        # 气泡提示
        self.bubble = QLabel("", self)
        self.bubble.setWordWrap(True)
        self.bubble.setStyleSheet(
            "background: rgba(255,255,255,230); border-radius: 15px; "
            "padding: 15px; font-size: 16px; color: #1e1e1e;"
        )
        self.bubble.hide()

        # 退出按钮
        self.exit_btn = QPushButton("✕ 退出教程", self)
        self.exit_btn.setStyleSheet(
            "background: rgba(0,0,0,150); color: white; border-radius: 5px; padding: 5px;"
        )
        self.exit_btn.clicked.connect(self.exit_tutorial)
        self.exit_btn.move(screen.width() - 120, 20)

        # 加载数据
        self.load_chapter(chapter_name)
        self.showFullScreen()

    def _create_fake_icons(self):
        """创建假图标控件，使用系统图标"""
        provider = QFileIconProvider()
        icon_map = {
            "此电脑": provider.icon(QFileIconProvider.Computer),
            "回收站": provider.icon(QFileIconProvider.Folder),  # 暂代
            "浏览器": self._get_edge_icon(provider),
            "文档": provider.icon(QFileIconProvider.Folder),
            "设置": self._get_control_icon(provider),
        }

        for name, x, y in FAKE_ICONS:
            icon = icon_map.get(name)
            if not icon or icon.isNull():
                # 后备：用文件夹图标
                icon = provider.icon(QFileIconProvider.Folder)

            lbl = QLabel(self)
            lbl.setPixmap(icon.pixmap(64, 64))
            lbl.setFixedSize(80, 80)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.move(x, y)
            lbl.setStyleSheet("background: transparent;")
            lbl.show()
            self.icon_widgets.append(lbl)

            # 图标下方文字
            text_lbl = QLabel(name, self)
            text_lbl.setAlignment(Qt.AlignCenter)
            text_lbl.setStyleSheet("color: white; font-size: 12px; background: transparent;")
            text_lbl.setFixedWidth(80)
            text_lbl.move(x, y + 80)
            text_lbl.show()

    def _get_edge_icon(self, provider):
        paths = [
            "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
            "C:/Program Files/Microsoft/Edge/Application/msedge.exe"
        ]
        for p in paths:
            if os.path.exists(p):
                return provider.icon(QFileInfo(p))
        return provider.icon(QFileIconProvider.File)

    def _get_control_icon(self, provider):
        p = "C:/Windows/System32/control.exe"
        if os.path.exists(p):
            return provider.icon(QFileInfo(p))
        return provider.icon(QFileIconProvider.File)

    # ---------- 属性动画 ----------
    def get_demo_mouse_pos(self):
        return self._demo_mouse_pos

    def set_demo_mouse_pos(self, pos):
        self._demo_mouse_pos = pos
        self.update()

    demo_mouse_pos = Property(QPoint, get_demo_mouse_pos, set_demo_mouse_pos)

    # ---------- 章节加载 ----------
    def load_chapter(self, chapter_name):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_paths = [
            os.path.join(base_dir, "tutorial_data.json"),
            "tutorial_data.json"
        ]
        loaded = False
        for jp in json_paths:
            if os.path.exists(jp):
                try:
                    with open(jp, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    for ch in data.get("chapters", []):
                        if ch["title"] == chapter_name:
                            self.steps = ch["steps"]
                            loaded = True
                            break
                except Exception:
                    pass
        if not loaded:
            self.steps = BUILTIN_CHAPTERS.get(chapter_name, [])
        self.current_step = 0
        self.execute_step(0)

    def execute_step(self, index):
        if index >= len(self.steps):
            self.bubble.hide()
            self.interactive = False
            self.update()
            QTimer.singleShot(1500, self.exit_tutorial)
            return

        step = self.steps[index]
        action = step.get("action", "")
        self.bubble.hide()

        if action.startswith("demo_"):
            self.interactive = False
            self.setMouseTracking(False)
            self._demo_mouse_pos = QPoint(100, 100)
            self._run_demo(step)
        elif action == "interactive":
            self.interactive = True
            self.required_action = step.get("required", "click")
            rect = step.get("rect", [0, 0, 100, 100])
            self.target_rect = QRect(rect[0], rect[1], rect[2], rect[3])
            self.bubble.setText(step.get("text", ""))
            self.bubble.adjustSize()
            # 定位气泡
            bx = self.target_rect.right() + 10
            by = self.target_rect.top() - self.bubble.height() - 10
            if by < 0:
                by = self.target_rect.bottom() + 10
            self.bubble.move(bx, by)
            self.bubble.show()
            self.setMouseTracking(True)
            self.setCursor(Qt.ArrowCursor)
            self.update()

    # ---------- 自动演示 ----------
    def _run_demo(self, step):
        pos = step.get("pos", [0, 0])
        target = step.get("target")
        text = step.get("text", "")
        end_point = QPoint(pos[0], pos[1])

        if target and len(target) == 4:
            self.target_rect = QRect(target[0], target[1], target[2], target[3])
        else:
            self.target_rect = QRect()

        self.anim = QPropertyAnimation(self, b"demo_mouse_pos")
        self.anim.setDuration(1000)
        self.anim.setStartValue(self._demo_mouse_pos)
        self.anim.setEndValue(end_point)
        self.anim.setEasingCurve(QEasingCurve.InOutCubic)
        self.anim.finished.connect(lambda: self._demo_finished(step, end_point))
        self.anim.start()

        self.bubble.setText(text)
        self.bubble.adjustSize()
        self.bubble.move(end_point.x() + 25, end_point.y() - self.bubble.height() // 2)
        self.bubble.show()
        self.update()

    def _demo_finished(self, step, end_point):
        action = step.get("action", "")
        if action in ("demo_click", "demo_double"):
            self._flash_highlight()
        QTimer.singleShot(800, self.next_step)

    def _flash_highlight(self):
        self._highlight_flash = True
        self.update()
        QTimer.singleShot(300, self._reset_flash)

    def _reset_flash(self):
        self._highlight_flash = False
        self.update()

    # ---------- 交互事件 ----------
    def mouseMoveEvent(self, event):
        if self.interactive and self.required_action == "move_to":
            if self.target_rect.contains(event.pos()):
                self._on_user_completed()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if self.interactive:
            if event.button() == Qt.LeftButton and self.required_action in ("click", "double"):
                if self.target_rect.contains(event.pos()):
                    self.click_start = event.pos()
            elif event.button() == Qt.RightButton and self.required_action == "right_click":
                if self.target_rect.contains(event.pos()):
                    self._on_user_completed()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.interactive and self.required_action == "click":
            if self.click_start and self.target_rect.contains(event.pos()):
                self._on_user_completed()
        self.click_start = None
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.interactive and self.required_action == "double_click":
            if self.target_rect.contains(event.pos()):
                self._on_user_completed()
        super().mouseDoubleClickEvent(event)

    def _on_user_completed(self):
        self.interactive = False
        self.bubble.hide()
        self.setMouseTracking(False)
        self.setVisible(False)
        QApplication.processEvents()
        QTimer.singleShot(600, self._restore_and_next)

    def _restore_and_next(self):
        self.setVisible(True)
        self.next_step()

    def next_step(self):
        self.current_step += 1
        self.execute_step(self.current_step)

    def exit_tutorial(self):
        if self.anim and self.anim.state() == QPropertyAnimation.Running:
            self.anim.stop()
        self.hide()
        self.back_callback()

    # ---------- 绘制 ----------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 全屏半透明背景
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))

        # 高亮镂空
        if not self.target_rect.isNull():
            full_path = QPainterPath()
            full_path.addRect(self.rect())
            full_path.addRect(self.target_rect)
            painter.setClipPath(full_path)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 120))
            painter.setClipping(False)

            # 边框
            if self._highlight_flash:
                pen = QPen(QColor("#FFD700"), 3)
            else:
                pen = QPen(QColor("#0078D4"), 2)
            painter.setPen(pen)
            painter.drawRect(self.target_rect)

        # 虚拟鼠标（演示模式）
        if not self.interactive:
            cursor = QCursor(Qt.ArrowCursor).pixmap()
            if cursor:
                painter.drawPixmap(self._demo_mouse_pos, cursor)

        painter.end()