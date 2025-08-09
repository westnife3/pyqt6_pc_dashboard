from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QPointF

class CircularProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.used_percent = 0
        self.bar_color = QColor("#00ffb4")
        self.background_color = QColor("#334444")
        self.text_color = QColor("#ffffff")
        self.setMinimumSize(80, 80)
        
    def set_value(self, percent):
        self.used_percent = percent
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen_width = 8
        rect = self.rect().adjusted(pen_width, pen_width, -pen_width, -pen_width)
        
        pen_bg = QPen(self.background_color, pen_width)
        pen_bg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_bg)
        painter.drawEllipse(rect)
        
        pen_progress = QPen(self.bar_color, pen_width)
        pen_progress.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_progress)

        start_angle = 90 * 16
        span_angle = -int(self.used_percent * 3.6 * 16)

        painter.drawArc(rect, start_angle, span_angle)
