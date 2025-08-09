import psutil

class SystemMonitor:
    def __init__(self):
        # 네트워크 속도 계산을 위한 초기값 설정
        self.last_net_stats = psutil.net_io_counters()

    def get_cpu_usage(self):
        """전체 CPU 사용률을 반환합니다."""
        # percpu=True로 각 코어의 사용률을 리스트로 반환
        return psutil.cpu_percent(interval=None, percpu=True)

    def get_ram_usage(self):
        """RAM 사용률을 백분율로 반환합니다."""
        return psutil.virtual_memory().percent
    
    def get_network_stats(self):
        """네트워크 업로드/다운로드 속도를 바이트 단위로 반환합니다."""
        current_net_stats = psutil.net_io_counters()
        sent = current_net_stats.bytes_sent - self.last_net_stats.bytes_sent
        recv = current_net_stats.bytes_recv - self.last_net_stats.bytes_recv
        self.last_net_stats = current_net_stats
        return sent, recv

    def get_disk_io(self):
        """디스크 I/O를 바이트 단위로 반환합니다."""
        return psutil.disk_io_counters()

