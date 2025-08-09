def format_bytes(bytes):
    """
    바이트 단위를 가장 적합한 단위(B, KB, MB, GB, TB, PB)로 변환
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    size = bytes
    unit_index = 0
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    return f"{size:.2f}{units[unit_index]}"

def format_network_speed(bytes_per_sec):
    """
    네트워크 속도(바이트/초)를 가장 적합한 단위(B/s, KB/s, MB/s, GB/s)로 변환
    """
    units = ['B/s', 'KB/s', 'MB/s', 'GB/s']
    speed = bytes_per_sec
    unit_index = 0
    while speed >= 1024 and unit_index < len(units) - 1:
        speed /= 1024
        unit_index += 1
    return f"{speed:.2f}{units[unit_index]}"
