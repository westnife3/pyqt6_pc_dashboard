import sys
import threading
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, QFrame, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

import pyqtgraph as pg

from ui.custom_widgets import CircularProgressBar
from utils.helpers import format_bytes, format_network_speed
from data.system_monitor import SystemMonitor

class DashboardApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Dashboard")
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(43, 43, 43, 191); color: white; padding: 10px;")

        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)
        
        self.title_font = QFont("Arial", 12)
        self.title_font.setBold(True)
        self.content_font = QFont("Arial", 16)
        
        # 시스템 모니터링 클래스 인스턴스 생성
        self.monitor = SystemMonitor()
        
        # UI 섹션 프레임 생성
        self.system_info_frame, system_info_layout = self.create_section_frame("System Information")
        self.system_info_layout = system_info_layout
        main_layout.addWidget(self.system_info_frame, stretch=2)
        
        self.uptime_frame, uptime_layout = self.create_section_frame("Uptime")
        self.uptime_label = QLabel("Loading...", font=self.content_font)
        self.uptime_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        uptime_layout.addWidget(self.uptime_label)
        main_layout.addWidget(self.uptime_frame, stretch=1)
        
        self.disk_usage_frame, disk_usage_layout = self.create_section_frame("Disk Usage")
        self.disk_usage_layout = disk_usage_layout
        self.disk_widgets = {}
        main_layout.addWidget(self.disk_usage_frame, stretch=2)

        self.cpu_cores_frame, cpu_cores_layout = self.create_section_frame("CPU Core Usage")
        self.num_cores = 0
        
        self.core_graph_widget = pg.PlotWidget()
        self.core_graph_widget.setBackground("#2b2b2b")
        self.core_graph_widget.showGrid(x=False, y=True)
        self.core_graph_widget.setYRange(0, 100)
        self.core_graph_widget.setMinimumHeight(150)
        self.core_graph_widget.hideAxis('bottom')
        self.core_graph_widget.hideAxis('left')
        
        self.core_bar_graph_item = pg.BarGraphItem(x=[], height=[], width=0.8, brush='#ffff00')
        self.core_graph_widget.addItem(self.core_bar_graph_item)
        
        cpu_cores_layout.addWidget(self.core_graph_widget)
        main_layout.addWidget(self.cpu_cores_frame, stretch=1)

        self.disk_io_frame, disk_io_layout = self.create_section_frame("Disk I/O")
        self.create_disk_io_widget("DISK READ", disk_io_layout, "read")
        self.create_disk_io_widget("DISK WRITE", disk_io_layout, "write")
        main_layout.addWidget(self.disk_io_frame, stretch=2)

        self.cpu_mem_frame, cpu_mem_layout = self.create_section_frame("CPU & Memory Usage")
        cpu_mem_h_layout = QHBoxLayout()
        cpu_mem_layout.addLayout(cpu_mem_h_layout)

        self.create_cpu_ram_widget(cpu_mem_h_layout, "cpu")
        self.create_cpu_ram_widget(cpu_mem_h_layout, "ram")
        main_layout.addWidget(self.cpu_mem_frame, stretch=2)
        
        self.network_frame, network_layout = self.create_section_frame("Network Usage")
        self.create_ip_labels(network_layout)
        self.create_network_widget("↑", network_layout, "sent")
        self.create_network_widget("↓", network_layout, "received")
        main_layout.addWidget(self.network_frame, stretch=2)
        
        # 데이터 업데이트를 위한 타이머 설정
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_all_data)
        self.update_timer.start(1000)
        
        # 초기 데이터 로드를 위한 변수 설정
        self.sent_data = []
        self.received_data = []
        self.cpu_data = []
        self.ram_data = []
        self.disk_read_data = []
        self.disk_write_data = []
        self.max_history = 100
        
        # 정적 시스템 정보 초기 로드
        self.get_static_system_info()
        threading.Thread(target=self.get_external_ip).start()
        
        # 모니터 선택 기능
        self.show_on_specific_monitor(target="ZeroMOD")

    def get_static_system_info(self):
        """SystemMonitor 클래스에서 정적 정보를 가져와 UI에 표시합니다."""
        info = self.monitor.get_static_system_info()
        if info:
            self.system_info_layout.addWidget(QLabel(info["os"], font=self.content_font))
            self.system_info_layout.addWidget(QLabel(info["cpu"], font=self.content_font))
            self.system_info_layout.addWidget(QLabel(info["gpu"], font=self.content_font))
            self.system_info_layout.addWidget(QLabel(info["board"], font=self.content_font))
            
            for disk in info["disks"]:
                used, total, percent = self.monitor.get_disk_usage(disk["device_id"])
                
                disk_container = QWidget()
                disk_layout = QVBoxLayout(disk_container)
                
                self.create_disk_widget(disk["name"], used, total, percent, disk_layout, disk["device_id"])
                
                self.disk_usage_layout.addWidget(disk_container)
            
            # CPU 코어 수 초기화
            cpu_percents = self.monitor.get_cpu_usage()
            self.num_cores = len(cpu_percents)
            self.core_bar_graph_item.setOpts(x=list(range(self.num_cores)), height=[0]*self.num_cores)
            
    def create_section_frame(self, title):
        frame = QWidget()
        frame.setStyleSheet("border: 1px dashed #666666;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        title_label = QLabel(f" {title} ")
        title_label.setFont(self.title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_label.setStyleSheet("""
            QLabel {
                background-color: #00ffb4; 
                color: #2b2b2b;
                border: none;
                border-radius: 5px; 
                padding: 5px 10px;
                margin-bottom: 5px;
            }
        """)
        title_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        layout.addWidget(title_label)
        return frame, layout
        
    def create_disk_widget(self, name, used, total, percent, parent_layout, device_id):
        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 14))
        parent_layout.addWidget(name_label)
        usage_layout = QHBoxLayout()
        circular_bar = CircularProgressBar()
        circular_bar.set_value(percent)
        circular_bar.setFixedSize(60, 60)
        usage_layout.addWidget(circular_bar)
        
        usage_info_layout = QVBoxLayout()
        size_label = QLabel(f"{format_bytes(used)} / {format_bytes(total)}")
        size_label.setFont(QFont("Arial", 20))
        usage_info_layout.addWidget(size_label)
        
        progress_bar = QProgressBar()
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 4px;
                background-color: #444444;
                text-align: center;
                color: #2b2b2b;
                font-size: 16px;
            }
            QProgressBar::chunk {
                background-color: #00ffb4;
            }
        """)
        progress_bar.setRange(0, 100)
        progress_bar.setValue(int(percent))
        progress_bar.setTextVisible(True)
        usage_info_layout.addWidget(progress_bar)
        
        usage_layout.addLayout(usage_info_layout)
        parent_layout.addLayout(usage_layout)

        self.disk_widgets[device_id] = {
            "size_label": size_label,
            "progress_bar": progress_bar,
            "circular_bar": circular_bar
        }
    
    def create_ip_labels(self, parent_layout):
        self.ip_label = QLabel("IP | Fetching...", font=self.content_font)
        self.ip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        parent_layout.addWidget(self.ip_label)

    def get_external_ip(self):
        """SystemMonitor 클래스에서 IP 주소를 가져와 UI에 표시합니다."""
        internal_ip, external_ip = self.monitor.get_ips()
        self.ip_label.setText(f"IP | {external_ip} ({internal_ip})")
        
    def create_network_widget(self, title, parent_layout, data_type):
        container = QWidget()
        container_layout = QHBoxLayout(container)
        text_layout = QVBoxLayout()
        
        title_label = QLabel(f" {title} ")
        title_label.setFont(self.title_font)
        
        speed_label = QLabel("0.00KB/s")
        speed_label.setFont(QFont("Arial", 20))

        total_label = QLabel("0.00B")
        total_label.setFont(QFont("Arial", 12))
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(speed_label)
        text_layout.addWidget(total_label)
        
        container_layout.addLayout(text_layout)
        
        chart_widget = pg.PlotWidget()
        chart_widget.setBackground("#2b2b2b")
        chart_widget.showGrid(x=False, y=False)
        chart_widget.hideAxis('bottom')
        chart_widget.hideAxis('left')
        chart_widget.setMinimumHeight(60)
        
        if data_type == "sent":
            pen = pg.mkPen(color='#0000FF', width=2)
            self.sent_speed_label = speed_label
            self.sent_total_label = total_label  # Total label 추가
            self.sent_plot_data_item = chart_widget.plot(pen=pen)
        else:
            pen = pg.mkPen(color='#FF0000', width=2)
            self.received_speed_label = speed_label
            self.received_total_label = total_label  # Total label 추가
            self.received_plot_data_item = chart_widget.plot(pen=pen)
        
        container_layout.addWidget(chart_widget, stretch=1)
        parent_layout.addWidget(container)

    def create_cpu_ram_widget(self, parent_layout, data_type):
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        percent_label = QLabel("0%")
        percent_label.setFont(QFont("Arial", 24))
        percent_label.setFixedWidth(80)
        percent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        chart_widget = pg.PlotWidget()
        chart_widget.setBackground("#2b2b2b")
        chart_widget.showGrid(x=False, y=False)
        chart_widget.hideAxis('bottom')
        chart_widget.hideAxis('left')
        chart_widget.setMinimumHeight(60)
        chart_widget.setYRange(0, 100)
        
        if data_type == "cpu":
            pen = pg.mkPen(color='#ffff00', width=2)
            self.cpu_percent_label = percent_label
            self.cpu_plot_data_item = chart_widget.plot(pen=pen)
        else:
            pen = pg.mkPen(color='#ff0000', width=2)
            self.ram_percent_label = percent_label
            self.ram_plot_data_item = chart_widget.plot(pen=pen)
        
        container_layout.addWidget(percent_label)
        container_layout.addWidget(chart_widget, stretch=1)
        
        parent_layout.addWidget(container, stretch=1)
        
    def create_disk_io_widget(self, title, parent_layout, data_type):
        container = QWidget()
        container_layout = QHBoxLayout(container)
        text_layout = QVBoxLayout()
        title_label = QLabel(f" {title} ")
        title_label.setFont(self.title_font)
        data_label = QLabel("0.00KB/s")
        data_label.setFont(QFont("Arial", 20))
        text_layout.addWidget(title_label)
        text_layout.addWidget(data_label)
        container_layout.addLayout(text_layout)
        chart_widget = pg.PlotWidget()
        chart_widget.setBackground("#2b2b2b")
        chart_widget.showGrid(x=False, y=False)
        chart_widget.hideAxis('bottom')
        chart_widget.hideAxis('left')
        chart_widget.setMinimumHeight(60)
        if data_type == "read":
            pen = pg.mkPen(color='#3498db', width=2)
            self.disk_read_label = data_label
            self.disk_read_plot_data_item = chart_widget.plot(pen=pen)
        else:
            pen = pg.mkPen(color='#e74c3c', width=2)
            self.disk_write_label = data_label
            self.disk_write_plot_data_item = chart_widget.plot(pen=pen)
        container_layout.addWidget(chart_widget, stretch=1)
        parent_layout.addWidget(container)

    def update_all_data(self):
        # Uptime 업데이트
        self.uptime_label.setText(self.monitor.get_uptime())
        
        # 디스크 사용률 업데이트
        for device_id, widgets in self.disk_widgets.items():
            used, total, percent = self.monitor.get_disk_usage(device_id)
            if total > 0:
                widgets["size_label"].setText(f"{format_bytes(used)} / {format_bytes(total)}")
                widgets["progress_bar"].setValue(int(percent))
                widgets["circular_bar"].set_value(percent)
                
        # CPU 코어 사용률 업데이트
        cpu_percents = self.monitor.get_cpu_usage()
        if self.num_cores == 0:
            self.num_cores = len(cpu_percents)
            self.core_bar_graph_item.setOpts(x=list(range(self.num_cores)), height=[0]*self.num_cores)

        x_values = list(range(self.num_cores))
        y_values = [p for p in cpu_percents]
        self.core_bar_graph_item.setOpts(x=x_values, height=y_values)
        
        # 네트워크 사용량 업데이트
        sent_rate, received_rate, sent_total, received_total = self.monitor.get_network_stats()
        
        self.sent_speed_label.setText(f"{format_network_speed(sent_rate)}")
        self.sent_total_label.setText(f"{format_bytes(sent_total)}")
        self.received_speed_label.setText(f"{format_network_speed(received_rate)}")
        self.received_total_label.setText(f"{format_bytes(received_total)}")
        
        self.sent_data.append(sent_rate)
        self.received_data.append(received_rate)
        self.sent_plot_data_item.setData(self.sent_data)
        self.received_plot_data_item.setData(self.received_data)

        # 디스크 I/O 업데이트
        read_speed, write_speed = self.monitor.get_disk_io()
        
        self.disk_read_label.setText(f"{format_network_speed(read_speed)}")
        self.disk_write_label.setText(f"{format_network_speed(write_speed)}")
        self.disk_read_data.append(read_speed)
        self.disk_write_data.append(write_speed)
        self.disk_read_plot_data_item.setData(self.disk_read_data)
        self.disk_write_plot_data_item.setData(self.disk_write_data)

        # CPU/RAM 사용량 그래프 업데이트
        cpu_usage = sum(self.monitor.get_cpu_usage()) / len(self.monitor.get_cpu_usage()) if self.monitor.get_cpu_usage() else 0
        ram_usage = self.monitor.get_ram_usage()
        self.cpu_data.append(cpu_usage)
        self.ram_data.append(ram_usage)
        self.cpu_percent_label.setText(f"{cpu_usage:.0f}%")
        self.ram_percent_label.setText(f"{ram_usage:.0f}%")
        self.cpu_plot_data_item.setData(self.cpu_data)
        self.ram_plot_data_item.setData(self.ram_data)

        # 데이터 히스토리 관리
        if len(self.sent_data) > self.max_history:
            self.sent_data.pop(0)
            self.received_data.pop(0)
            self.cpu_data.pop(0)
            self.ram_data.pop(0)
            self.disk_read_data.pop(0)
            self.disk_write_data.pop(0)
    
    def show_on_specific_monitor(self, target="main"):
        screens = QApplication.instance().screens()
        primary_screen = QApplication.instance().primaryScreen()

        print("현재 연결된 모니터 목록:")
        for i, screen in enumerate(screens):
            screen_name = screen.name()
            resolution = f"{screen.size().width()}x{screen.size().height()}"
            is_primary = " (주 모니터)" if screen == primary_screen else ""
            print(f"  - 모니터 {i}: 이름='{screen_name}', 해상도='{resolution}'{is_primary}")

        target_screen = None
        
        if target == "main":
            target_screen = primary_screen
        else:
            for screen in screens:
                if screen.name() == target or f"{screen.size().width()}x{screen.size().height()}" == target:
                    target_screen = screen
                    break
        
        if target_screen is None:
            print(f"경고: 지정된 모니터 '{target}'를 찾을 수 없습니다. 주 모니터에 표시합니다.")
            target_screen = primary_screen

        screen_geometry = target_screen.geometry()
        self.move(screen_geometry.topLeft())
        self.setFixedSize(screen_geometry.size())
        self.showFullScreen()
