from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QTimer
from data.system_monitor import SystemMonitor
from ui.custom_widgets import CircularProgressBar
from utils.helpers import format_bytes, format_network_speed

class DashboardApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Dashboard")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #2c3e50; color: #ecf0f1;")

        # 시스템 모니터링 클래스 인스턴스 생성
        self.monitor = SystemMonitor()

        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        # 전체 레이아웃 설정
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 타이틀 라벨
        title_label = QLabel("PC Dashboard")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; padding: 20px;")
        main_layout.addWidget(title_label)

        # 위젯들을 담을 수평 레이아웃
        widget_layout = QHBoxLayout()
        main_layout.addLayout(widget_layout)

        # CPU 위젯
        cpu_frame = self.create_metric_frame("CPU Usage")
        self.cpu_progress = CircularProgressBar(cpu_frame)
        self.cpu_label = QLabel("0%")
        self.setup_progress_widget(cpu_frame, self.cpu_progress, self.cpu_label, "CPU")
        widget_layout.addWidget(cpu_frame)

        # RAM 위젯
        ram_frame = self.create_metric_frame("RAM Usage")
        self.ram_progress = CircularProgressBar(ram_frame)
        self.ram_label = QLabel("0%")
        self.setup_progress_widget(ram_frame, self.ram_progress, self.ram_label, "RAM")
        widget_layout.addWidget(ram_frame)
        
        # 네트워크 속도 위젯
        network_frame = self.create_metric_frame("Network Speed")
        network_layout = QVBoxLayout(network_frame)
        self.upload_label = QLabel("Upload: 0 B/s")
        self.download_label = QLabel("Download: 0 B/s")
        self.upload_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.download_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        network_layout.addWidget(self.upload_label)
        network_layout.addWidget(self.download_label)
        widget_layout.addWidget(network_frame)

    def create_metric_frame(self, title):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("background-color: #34495e; border-radius: 10px;")
        
        frame_layout = QVBoxLayout(frame)
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        frame_layout.addWidget(title_label)
        
        return frame

    def setup_progress_widget(self, parent, progress_bar, value_label, name):
        layout = QVBoxLayout(parent)
        
        progress_bar.set_value(0)
        progress_bar.setFixedSize(150, 150)

        value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("font-size: 16px;")

        layout.addWidget(progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        layout.addWidget(name_label)
        
    def setup_timer(self):
        # 1초마다 데이터 업데이트 타이머 설정
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_all_data)
        self.timer.start(1000)

    def update_all_data(self):
        # CPU 사용률 업데이트
        cpu_percent = self.monitor.get_cpu_usage()
        self.cpu_progress.set_value(int(sum(cpu_percent) / len(cpu_percent)))
        self.cpu_label.setText(f"{int(sum(cpu_percent) / len(cpu_percent))}%")

        # RAM 사용률 업데이트
        ram_percent = self.monitor.get_ram_usage()
        self.ram_progress.set_value(int(ram_percent))
        self.ram_label.setText(f"{int(ram_percent)}%")
        
        # 네트워크 속도 업데이트
        sent, recv = self.monitor.get_network_stats()
        self.upload_label.setText(f"Upload: {format_network_speed(sent)}")
        self.download_label.setText(f"Download: {format_network_speed(recv)}")

