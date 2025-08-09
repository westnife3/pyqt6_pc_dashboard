1. 애플리케이션 구조 (QStackedWidget)
이 앱은 QStackedWidget을 상속받아 만들어졌어요. QStackedWidget은 여러 위젯을 겹쳐 놓고, 인덱스를 통해 특정 위젯만 보이게 하는 기능을 제공합니다. 이 애플리케이션에서는 로딩 화면(인덱스 0)과 메인 대시보드(인덱스 1) 두 가지 화면을 관리하는 데 사용됩니다.

self.loading_screen: 앱 시작 시 나타나는 로딩 화면.

self.main_dashboard_widget: 로딩이 끝난 후 나타나는 실제 대시보드 화면.

self.setCurrentIndex(0): 처음에는 로딩 화면을 표시합니다.

self.setCurrentIndex(1): 로딩이 완료되면 메인 대시보드로 전환합니다.

2. 로딩 화면 (LoadingScreen & PieChartSpinner)
사용자 경험을 위해 시스템 정보를 불러오는 동안 "로딩 중..."이라는 메시지와 함께 애니메이션을 보여줘요.

PieChartSpinner: QTimer를 사용하여 10ms마다 update_angle 함수를 호출하고, paintEvent에서 각도에 따라 파이 조각을 그립니다.

LoadingScreen: PieChartSpinner와 "로딩 중..." 라벨을 담는 컨테이너 역할을 합니다.

3. 메인 대시보드 UI (setup_main_ui 함수)
이 함수는 대시보드의 전체 레이아웃과 위젯을 설정합니다.

create_section_frame: 각 정보 섹션(System Information, Uptime, Disk Usage 등)을 시각적으로 구분하기 위해 테두리가 있는 프레임(QFrame)을 만들고 제목(QLabel)을 추가하는 함수입니다.

pyqtgraph: 그래프를 그리는 데 사용되는 라이브러리입니다. CPU, RAM, 네트워크, 디스크 I/O 사용량을 실시간으로 시각화하는 데 활용됩니다.

CircularProgressBar: 원형 진행바를 그리기 위해 별도로 정의된 커스텀 위젯입니다. 디스크 사용률을 시각적으로 보여주는 데 사용됩니다.

4. 데이터 업데이트 (initialize_app & update_all_data 함수)
앱의 동적인 데이터 업데이트는 두 단계로 이루어져요.

initialize_app: 앱이 시작되면 호출되는 함수입니다.

get_static_system_info(): CPU, GPU, OS와 같이 변하지 않는 정보를 한 번만 불러옵니다.

QTimer.singleShot(2000, self.initialize_app): 로딩 화면을 최소 2초간 보여주기 위해 사용했던 코드인데, 최근 수정으로 로딩 후 바로 메인 화면으로 전환되도록 변경되었습니다.

self.update_timer: 1초마다 update_all_data 함수를 호출하는 타이머를 시작합니다.

update_all_data: 1초마다 반복적으로 호출되며, psutil 등의 라이브러리를 사용해 실시간으로 변하는 시스템 정보를 가져와 각 위젯을 업데이트합니다.

5. 기타 유용한 기능
show_on_specific_monitor: 특정 모니터에 애플리케이션을 표시할 수 있게 해주는 유틸리티 함수입니다. target="ZeroMOD"는 "ZeroMOD"라는 이름의 모니터에 앱을 띄우라는 의미입니다.

threading.Thread: 외부 IP를 가져오는 작업처럼 시간이 걸릴 수 있는 작업을 메인 UI 스레드와 분리하여 처리하기 위해 스레드를 사용했습니다. 이는 UI가 멈추는 것을 방지하는 좋은 방법입니다.
