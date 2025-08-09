def format_bytes(bytes_value, units=["Bytes", "KB", "MB", "GB"]):
    """
    바이트 값을 읽기 쉬운 단위로 변환합니다.
    예: 1024 -> 1.00 KB
    """
    if bytes_value == 0:
        return "0 Bytes"
    
    unit_index = 0
    while bytes_value >= 1024 and unit_index < len(units) - 1:
        bytes_value /= 1024.0
        unit_index += 1
        
    return f"{bytes_value:.2f} {units[unit_index]}"

def format_network_speed(bytes_value):
    """네트워크 속도를 읽기 쉬운 단위로 변환합니다. (초당)"""
    return format_bytes(bytes_value) + "/s"

