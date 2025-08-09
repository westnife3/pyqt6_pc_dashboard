
### 📋 프로젝트 요약: PC 대시보드 만들기 및 자동 실행 설정

-----

### 1\. 프로그램 개발: PyQt6 기반 PC 대시보드

  * **기술 스택:**

      * **PyQt6**: GUI(그래픽 사용자 인터페이스) 개발
      * **psutil**: CPU, 메모리, 디스크, 네트워크 등 시스템 정보 수집
      * **pyqtgraph**: 실시간 데이터를 시각화하는 그래프 생성
      * **wmi**: Windows Management Instrumentation을 사용하여 시스템 정보(OS, GPU 등) 수집
      * **requests, socket**: 네트워크 및 IP 주소 정보 수집

  * **주요 기능:**

      * CPU, RAM 사용률 실시간 그래프
      * 개별 CPU 코어 사용량 막대 그래프
      * 디스크 사용량(용량, 퍼센트), 디스크 I/O 속도 그래프
      * 네트워크 송수신 속도, 총 사용량 및 IP 주소 표시
      * PC 부팅 후 경과 시간(Uptime) 표시

  * **개발 환경:**

      * 윈도우 환경
      * python3.13
      * 필요 packages 는 requirements.txt 참고

-----

### 2\. 실행 파일(.exe) 생성

  * **도구:** **PyInstaller**
  * **목적:** 파이썬 스크립트(.py)를 독립 실행형 파일(.exe)로 변환하여 파이썬이 설치되지 않은 환경에서도 실행 가능하게 함.
  * **사용 명령어:**
    ```sh
    pyinstaller --onefile --windowed --name "PC_Dashboard" --hidden-import=PyQt6.sip main.py
    ```
      * `--onefile`: 모든 의존성을 하나의 `.exe` 파일로 묶음.
      * `--windowed`: 실행 시 검은색 콘솔 창이 뜨지 않게 함.
      * `--name "PC_Dashboard"`: 실행 파일 이름을 `PC_Dashboard.exe`로 지정.
      * `--hidden-import=PyQt6.sip`: PyInstaller가 자동으로 찾지 못하는 PyQt6의 숨겨진 모듈을 명시적으로 포함시켜 오류를 방지.

-----

### 3\. 모니터 선택 기능 구현 및 오류 해결

  * **문제점:** 모니터 인덱스(0, 1, 2...)는 PC 환경에 따라 변경될 수 있어 안정적이지 않음.
  * **해결책:** `QScreen`의 **이름**(`screen.name()`) 또는 **해상도**(`480x1920`)를 기준으로 모니터를 선택하는 로직을 구현.
  * **코드 수정:**
    ```python
    # 모니터 이름으로 지정
    self.show_on_specific_monitor(target="ZeroMOD")

    # 해상도로 지정
    self.show_on_specific_monitor(target="480x1920")
    ```
  * **추가 오류 해결:** `AttributeError: 'QScreen' object has no attribute 'isPrimary'` 오류를 `screen == primary_screen`으로 객체를 직접 비교하는 방식으로 해결.

-----

### 4\. PC 부팅 시 자동 실행 설정

  * **도구:** **Windows 작업 스케줄러(Task Scheduler)**
  * **목적:** PC 시작 시 `PC_Dashboard.exe`를 자동으로 실행.
  * **최종 설정:**
    1.  **트리거(Trigger)**: **사용자 로그온 시** (시스템 시작 시보다 안정적).
    2.  **동작(Action)**: `PC_Dashboard.exe` 파일의 전체 경로와 시작 위치를 정확하게 지정.
    3.  **권한**: **"가장 높은 수준의 권한으로 실행"** 옵션에 체크.

