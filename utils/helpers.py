def format_bytes(bytes_value):
    """
    바이트 단위를 가장 적합한 단위(B, KB, MB, GB, TB, PB)로 변환
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    size = bytes_value
    unit = units.pop(0)
    while size >= 1024 and units:
        unit = units.pop(0)
        size /= 1024
    return f"{size:.2f}{unit}"

def format_network_speed(bytes_value):
    """네트워크 속도를 읽기 쉬운 단위로 변환합니다. (초당)"""
    return format_bytes(bytes_value) + "/s"
