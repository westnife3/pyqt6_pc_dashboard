### 📂 기능 분리 구조 요약

### 0. Struct

```c

pc_dashboard/
├── main.py                 # 프로그램 실행
├── ui/
│   ├── dashboard_app.py    # 메인 GUI 로직
│   └── custom_widgets.py   # 원형 진행률 바
├── data/
│   └── system_monitor.py   # 시스템 데이터 수집
└── utils/
    └── helpers.py          # 보조 함수
```

### 1. main.py

- 역할: 애플리케이션의 시작점입니다.

- QApplication 인스턴스를 생성하고, DashboardApp 객체를 만든 뒤 메인 이벤트 루프를 실행하는 역할만 담당합니다.

- 어떤 비즈니스 로직이나 UI 구성 코드도 포함하지 않습니다.

-----

### 2. ui/dashboard_app.py

역할: 사용자 인터페이스(UI)를 구성하고 관리합니다.

각종 위젯(레이블, 그래프, 프로그레스바 등)을 생성하고 배치하며, UI에 표시될 데이터를 SystemMonitor 객체로부터 가져와 업데이트합니다.

데이터 수집 로직은 전혀 포함하지 않습니다. 오직 화면에 표시하는 역할만 합니다.

-----

### 3. data/system_monitor.py
역할: 시스템 데이터를 수집하고 처리합니다.

CPU, RAM, 디스크, 네트워크 등 PC의 다양한 시스템 정보를 가져오는 모든 함수가 이 클래스에 모여 있습니다.

ui/dashboard_app.py에서 필요한 데이터를 요청하면, 이 파일이 해당 데이터를 계산해서 반환해 줍니다. UI에 대한 정보는 전혀 모릅니다.

-----

### 4. utils/helpers.py

역할: 여러 곳에서 공통적으로 사용되는 유틸리티 함수를 모아둡니다.

format_bytes와 같이 바이트 단위를 가독성 좋은 형식으로 바꿔주는 함수들이 여기에 포함되어 있습니다.

특정 기능에 종속되지 않고, 여러 파일에서 재사용할 수 있는 보조 기능들을 담고 있습니다.

-----

✨ 요약
main.py: 프로그램 실행

ui/dashboard_app.py: UI 화면 그리기

data/system_monitor.py: 데이터 수집 및 계산

utils/helpers.py: 공통 유틸리티 기능

이렇게 분리된 구조 덕분에, 예를 들어 SystemMonitor에서 데이터를 가져오는 방식이 바뀌어도 dashboard_app.py의 UI 코드에는 거의 영향을 주지 않아 코드 수정이 훨씬 용이해집니다.
