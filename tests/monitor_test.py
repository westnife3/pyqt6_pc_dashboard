import sys
from PyQt6.QtWidgets import QApplication

def print_monitor_info():
    app = QApplication(sys.argv)
    screens = app.screens()
    primary_screen = app.primaryScreen() # Get the primary screen object
    
    print(f"시스템에 연결된 모니터 수: {len(screens)}")

    for i, screen in enumerate(screens):
        print(f"\n--- 모니터 {i+1} (인덱스 {i}) ---")
        print(f"화면 이름: {screen.name()}")
        print(f"해상도: {screen.geometry().width()}x{screen.geometry().height()}")
        
        # Check if the current screen object is the same as the primary screen object
        is_primary = (screen == primary_screen)
        print(f"메인 모니터 여부: {is_primary}")

    sys.exit(0)

if __name__ == "__main__":
    print_monitor_info()
