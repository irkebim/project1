"""
IRKE BIM 애드온 개발을 위한 메인 진입점
이 스크립트는 test.py와 release.py의 상위 진입점 역할을 합니다.
"""

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="IRKE BIM 애드온 개발 도구")
    
    # 서브파서 설정
    subparsers = parser.add_subparsers(dest="command", help="수행할 명령")
    
    # 테스트 서브파서
    test_parser = subparsers.add_parser("test", help="개발 모드에서 애드온 테스트")
    test_parser.add_argument('--disable_watch', default=False, action='store_true', 
                       help='파일 변경 시 자동 리로드 비활성화')
    
    # 릴리즈 서브파서
    release_parser = subparsers.add_parser("release", help="애드온 릴리즈 생성")
    release_parser.add_argument('--disable_zip', default=False, action='store_true', 
                         help='zip 압축 없이 폴더로 릴리즈')
    release_parser.add_argument('--with_version', default=False, action='store_true', 
                         help='릴리즈 파일 이름에 버전 번호 추가')
    release_parser.add_argument('--with_timestamp', default=False, action='store_true', 
                         help='릴리즈 파일 이름에 타임스탬프 추가')
    release_parser.add_argument('--as_addon', default=False, action='store_true',
                         help='확장이 아닌 애드온으로 릴리즈')
    
    # 인자 파싱
    args = parser.parse_args()
    
    # 명령 실행
    if args.command == "test":
        from test import test_addon
        test_addon(enable_watch=not args.disable_watch)
        
    elif args.command == "release":
        from release import release_addon
        release_addon(
            need_zip=not args.disable_zip,
            with_timestamp=args.with_timestamp,
            with_version=args.with_version,
            is_extension=not args.as_addon
        )
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()