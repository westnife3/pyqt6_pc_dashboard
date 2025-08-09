from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QBrush, QPen, QColor
from PyQt6.QtCore import Qt, QSize, QPointF

class CircularProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.max_value = 100
        self.setMinimumSize(100, 100)

    def set_value(self, value):
        if 0 <= value <= self.max_value:
            self.value = value
            self.update() # 위젯 다시 그리기

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        center = QPointF(rect.center())
        radius = min(rect.width(), rect.height()) / 2 - 10

        # 배경 원 그리기
        painter.setPen(QPen(QColor(44, 62, 80), 8, Qt.PenCapStyle.RoundCap))
        painter.drawEllipse(center, radius, radius)

        # 진행률 아크 그리기
        pen_color = QColor("#3498db")
        painter.setPen(QPen(pen_color, 8, Qt.PenCapStyle.RoundCap))
        
        start_angle = 90 * 16 # 12시 방향에서 시작
        span_angle = -self.value * 360 / self.max_value * 16
        
        painter.drawArc(
            int(center.x() - radius), int(center.y() - radius), 
            int(radius * 2), int(radius * 2),
            start_angle, span_angle
        )

