import psutil
import wmi
import requests
import socket
import platform
import time

class SystemMonitor:
    def __init__(self):
        # 네트워크 속도 계산을 위한 초기값 설정
        self.last_net_stats = psutil.net_io_counters()
        self.last_disk_stats = psutil.disk_io_counters()
        self.boot_time = psutil.boot_time()

    def get_static_system_info(self):
        """OS, CPU, GPU, BOARD 등 정적 시스템 정보를 반환합니다."""
        try:
            wmi_obj = wmi.WMI()
            os_info = wmi_obj.Win32_OperatingSystem()[0]
            proc_info = wmi_obj.Win32_Processor()[0]
            gpu_info = wmi_obj.Win32_VideoController()[0]
            board_info = wmi_obj.Win32_BaseBoard()[0]
            
            os_name = os_info.Name.encode('utf-8').split(b'|')[0].decode('utf-8').strip()
            os_version = f"{os_info.Version} ({os_info.BuildNumber})"
            
            disks = []
            for i, disk in enumerate(wmi_obj.Win32_DiskDrive()):
                disk_name = disk.Model.strip()
                partitions = [p for p in disk.associators("Win32_DiskDriveToDiskPartition")]
                for partition in partitions:
                    if partition:
                        logical_disks = [ld for ld in partition.associators("Win32_LogicalDiskToPartition")]
                        for ld in logical_disks:
                            if ld.DriveType == 3: # 3은 로컬 디스크를 의미
                                disks.append({
                                    "name": f"DISK{i} - {disk_name}",
                                    "device_id": ld.DeviceID
                                })
            
            return {
                "os": f"OS | {os_name} {os_version}",
                "cpu": f"CPU | {proc_info.Name}",
                "gpu": f"GPU | {gpu_info.Name}",
                "board": f"BOARD | {board_info.Product}",
                "disks": disks
            }
        except Exception as e:
            print(f"Failed to get WMI info: {e}")
            return None

    def get_cpu_usage(self):
        """전체 CPU 사용률을 반환합니다."""
        return psutil.cpu_percent(interval=None, percpu=True)

    def get_ram_usage(self):
        """RAM 사용률을 백분율로 반환합니다."""
        return psutil.virtual_memory().percent
    
    def get_disk_usage(self, device_id):
        """특정 디스크의 사용량을 반환합니다."""
        try:
            usage = psutil.disk_usage(device_id)
            return usage.used, usage.total, usage.percent
        except Exception:
            return 0, 0, 0
    
    def get_uptime(self):
        """시스템 부팅 후 경과 시간을 문자열로 반환합니다."""
        uptime_seconds = int(time.time() - self.boot_time)
        days = uptime_seconds // (24 * 3600)
        hours = (uptime_seconds % (24 * 3600)) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        return f"{days} day{'s' if days != 1 else ''}, {hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_network_stats(self):
        """네트워크 업로드/다운로드 속도를 바이트 단위로 반환하고, 총량을 업데이트합니다."""
        current_net_stats = psutil.net_io_counters()
        sent = current_net_stats.bytes_sent - self.last_net_stats.bytes_sent
        recv = current_net_stats.bytes_recv - self.last_net_stats.bytes_recv
        self.last_net_stats = current_net_stats
        return sent, recv, current_net_stats.bytes_sent, current_net_stats.bytes_recv
    
    def get_disk_io(self):
        """디스크 I/O를 바이트 단위로 반환하고, 총량을 업데이트합니다."""
        new_disk_stats = psutil.disk_io_counters()
        read_speed = new_disk_stats.read_bytes - self.last_disk_stats.read_bytes
        write_speed = new_disk_stats.write_bytes - self.last_disk_stats.write_bytes
        self.last_disk_stats = new_disk_stats
        return read_speed, write_speed
    
    def get_ips(self):
        """내부/외부 IP 주소를 반환합니다."""
        internal_ip = "127.0.0.1"
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            internal_ip = s.getsockname()[0]
            s.close()
        except Exception:
            pass
            
        external_ip = "Fetching..."
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            response.raise_for_status()
            external_ip = response.json().get('ip')
        except requests.exceptions.RequestException:
            external_ip = "Failed to fetch"
        except Exception:
            external_ip = "Error"
        
        return internal_ip, external_ip
