import sys
import threading
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QProgressBar, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

import pyqtgraph as pg
import psutil
import time
import requests
import socket
import platform
import wmi

from ui.custom_widgets import CircularProgressBar
from utils.helpers import format_bytes

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
        self.num_cores = psutil.cpu_count(logical=True)
        self.core_usage_labels = []
        
        self.core_graph_widget = pg.PlotWidget()
        self.core_graph_widget.setBackground("#2b2b2b")
        self.core_graph_widget.showGrid(x=False, y=True)
        self.core_graph_widget.setYRange(0, 100)
        self.core_graph_widget.setMinimumHeight(150)
        self.core_graph_widget.hideAxis('bottom')
        self.core_graph_widget.hideAxis('left')
        
        self.core_bar_graph_item = pg.BarGraphItem(x=list(range(self.num_cores)), height=[0]*self.num_cores, width=0.8, brush='#ffff00')
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
        self.last_net_stats = psutil.net_io_counters()
        self.last_disk_stats = psutil.disk_io_counters()
        self.sent_data = []
        self.received_data = []
        self.cpu_data = []
        self.ram_data = []
        self.disk_read_data = []
        self.disk_write_data = []
        self.max_history = 100
        
        self.boot_time = psutil.boot_time()
        
        self.get_static_system_info()
        threading.Thread(target=self.get_external_ip).start()
        
        # 모니터 선택 기능 (원래 코드의 기능 유지)
        self.show_on_specific_monitor(target="ZeroMOD")

    # 시스템 정적 정보 (OS, CPU, GPU, BOARD 등)를 가져오는 메서드
    def get_static_system_info(self):
        try:
            wmi_obj = wmi.WMI()
            
            os_info = wmi_obj.Win32_OperatingSystem()[0]
            proc_info = wmi_obj.Win32_Processor()[0]
            gpu_info = wmi_obj.Win32_VideoController()[0]
            board_info = wmi_obj.Win32_BaseBoard()[0]
            
            os_name = os_info.Name.encode('utf-8').split(b'|')[0].decode('utf-8').strip()
            os_version = f"{os_info.Version} ({os_info.BuildNumber})"
            
            self.system_info_layout.addWidget(QLabel(f"OS | {os_name} {os_version}", font=self.content_font))
            self.system_info_layout.addWidget(QLabel(f"CPU | {proc_info.Name}", font=self.content_font))
            self.system_info_layout.addWidget(QLabel(f"GPU | {gpu_info.Name}", font=self.content_font))
            self.system_info_layout.addWidget(QLabel(f"BOARD | {board_info.Product}", font=self.content_font))
            
            for i, disk in enumerate(wmi_obj.Win32_DiskDrive()):
                disk_name = disk.Model.strip()
                partitions = [p for p in disk.associators("Win32_DiskDriveToDiskPartition")]
                
                for partition in partitions:
                    if partition:
                        logical_disks = [ld for ld in partition.associators("Win32_LogicalDiskToPartition")]
                        for ld in logical_disks:
                            if ld.DriveType == 3:
                                usage = psutil.disk_usage(ld.DeviceID)

                                disk_container = QWidget()
                                disk_layout = QVBoxLayout(disk_container)
                                
                                display_name = f"DISK{i} - {disk_name}"
                                
                                self.create_disk_widget(display_name, usage.used, usage.total, usage.percent, disk_layout, ld.DeviceID)
                                
                                self.disk_usage_layout.addWidget(disk_container)
            
        except Exception as e:
            print(f"Failed to get WMI info: {e}")
            self.system_info_layout.addWidget(QLabel("WMI is not available or failed to load.", font=self.content_font))

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

    def get_internal_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def get_external_ip(self):
        self.internal_ip = self.get_internal_ip()
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            response.raise_for_status()
            external_ip = response.json().get('ip')
            self.ip_label.setText(f"IP | {external_ip} ({self.internal_ip})")
        except requests.exceptions.RequestException:
            self.ip_label.setText(f"IP | Failed to fetch ({self.internal_ip})")
        except Exception:
            self.ip_label.setText(f"IP | Error ({self.internal_ip})")
        
    def create_network_widget(self, title, parent_layout, data_type):
        container = QWidget()
        container_layout = QHBoxLayout(container)
        text_layout = QVBoxLayout()
        title_label = QLabel(f"{title}")
        title_label.setFont(QFont("Arial", 24))
        title_label.setFixedWidth(50)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if data_type == "sent":
            title_label.setStyleSheet("color: blue;")
        else:
            title_label.setStyleSheet("color: red;")
        data_layout = QVBoxLayout()
        speed_label = QLabel("0.00KB/s")
        speed_label.setFont(QFont("Arial", 20))
        total_label = QLabel("0.00GB")
        total_label.setFont(self.content_font)
        data_layout.addWidget(speed_label)
        data_layout.addWidget(total_label)
        container_layout.addWidget(title_label)
        container_layout.addLayout(data_layout)
        chart_widget = pg.PlotWidget()
        chart_widget.setBackground("#2b2b2b")
        chart_widget.showGrid(x=False, y=False)
        chart_widget.hideAxis('bottom')
        chart_widget.hideAxis('left')
        chart_widget.setMinimumHeight(60)
        if data_type == "sent":
            pen = pg.mkPen(color='#0000FF', width=2)
            self.sent_speed_label = speed_label
            self.sent_total_label = total_label
            self.sent_plot_data_item = chart_widget.plot(pen=pen)
        else:
            pen = pg.mkPen(color='#FF0000', width=2)
            self.received_speed_label = speed_label
            self.received_total_label = total_label
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
        uptime_seconds = int(time.time() - self.boot_time)
        days = uptime_seconds // (24 * 3600)
        hours = (uptime_seconds % (24 * 3600)) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        self.uptime_label.setText(f"{days} day{'s' if days != 1 else ''}, {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # 디스크 사용률 업데이트
        for device_id, widgets in self.disk_widgets.items():
            try:
                usage = psutil.disk_usage(device_id)
                widgets["size_label"].setText(f"{format_bytes(usage.used)} / {format_bytes(usage.total)}")
                widgets["progress_bar"].setValue(int(usage.percent))
                widgets["circular_bar"].set_value(usage.percent)
            except Exception as e:
                print(f"Error updating disk usage for {device_id}: {e}")
                
        # CPU 코어 사용률 업데이트
        cpu_percents = psutil.cpu_percent(interval=None, percpu=True)
        x_values = list(range(self.num_cores))
        y_values = [p for p in cpu_percents]
        self.core_bar_graph_item.setOpts(x=x_values, height=y_values)
        
        # 네트워크 사용량 업데이트
        new_net_stats = psutil.net_io_counters()
        sent_rate_kb = (new_net_stats.bytes_sent - self.last_net_stats.bytes_sent) / 1024
        received_rate_kb = (new_net_stats.bytes_recv - self.last_net_stats.bytes_recv) / 1024
        sent_total_gb = new_net_stats.bytes_sent / (1024 ** 3)
        received_total_gb = new_net_stats.bytes_recv / (1024 ** 3)
        
        self.sent_speed_label.setText(f"{sent_rate_kb:.2f}KB/s")
        self.sent_total_label.setText(f"{sent_total_gb:.2f}GB")
        self.received_speed_label.setText(f"{received_rate_kb:.2f}KB/s")
        self.received_total_label.setText(f"{received_total_gb:.2f}GB")
        
        self.sent_data.append(sent_rate_kb)
        self.received_data.append(received_rate_kb)
        self.sent_plot_data_item.setData(self.sent_data)
        self.received_plot_data_item.setData(self.received_data)
        self.last_net_stats = new_net_stats

        # 디스크 I/O 업데이트
        new_disk_stats = psutil.disk_io_counters()
        read_speed_kb = (new_disk_stats.read_bytes - self.last_disk_stats.read_bytes) / 1024
        write_speed_kb = (new_disk_stats.write_bytes - self.last_disk_stats.write_bytes) / 1024
        self.disk_read_label.setText(f"{read_speed_kb:.2f}KB/s")
        self.disk_write_label.setText(f"{write_speed_kb:.2f}KB/s")
        self.disk_read_data.append(read_speed_kb)
        self.disk_write_data.append(write_speed_kb)
        self.disk_read_plot_data_item.setData(self.disk_read_data)
        self.disk_write_plot_data_item.setData(self.disk_write_data)
        self.last_disk_stats = new_disk_stats

        # CPU/RAM 사용량 그래프 업데이트
        cpu_usage = psutil.cpu_percent(interval=None)
        ram_usage = psutil.virtual_memory().percent
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
    
    # 모니터 정보를 출력하고, 지정된 모니터에 대시보드를 표시하는 함수
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
