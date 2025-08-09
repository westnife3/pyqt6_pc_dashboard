import sys
from PyQt6.QtWidgets import QApplication
from ui.dashboard_app import DashboardApp

# 프로그램의 시작점
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = DashboardApp()
    dashboard.show()
    sys.exit(app.exec())

