# IRKE BIM Extension

This is the Blender Extension for BIM Modeling.
Built modularly for stability and future expansion.

## 개요

IRKE BIM은 Blender 4.4에서 건축 모델링을 위한 확장 기능입니다.
모듈화된 방식으로 구축되어 안정성과 확장성을 높였습니다.

## 설치 방법

1. 릴리즈 파일에서 최신 릴리즈를 다운로드합니다.
2. Blender 4.4를 실행합니다.
3. Edit > Preferences > Add-ons > Install... 메뉴를 선택합니다.
4. 다운로드한 zip 파일을 선택합니다.
5. 설치 후 애드온을 활성화합니다.

## 개발 환경 설정

개발을 위해서는 다음과 같이 환경을 설정하세요:

1. 이 저장소를 클론합니다.
2. `config.ini` 파일에서 Blender 경로와 애드온 경로를 설정합니다.
3. `test.py`를 실행하여 개발 모드에서 테스트합니다.

```bash
python test.py
```

## 릴리즈 빌드

릴리즈 빌드는 다음 명령으로 생성할 수 있습니다:

```bash
python release.py --with_version --with_timestamp
```

## 파일 구조

- `config.py` - 애드온 전역 설정 및 메타데이터
- `default_values.py` - 오퍼레이터 설정 및 기본값
- `operators/` - 실제 기능 구현 (큐브 생성 등)
- `panels/` - UI 패널 및 인터페이스
- `preferences/` - 사용자 설정 관리
- `utils/` - 모듈 관리 및 자동 리로드 등 유틸리티

## 라이선스

GPL-3.0-or-later