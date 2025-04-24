from framework import release_addon

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--disable_zip', default=False, action='store_true', 
                        help='If true, release the addon into a plain folder and do not zip it')
    parser.add_argument('--with_version', default=False, action='store_true', 
                        help='Append the addon version number to the released zip file name')
    parser.add_argument('--with_timestamp', default=False, action='store_true', 
                        help='Append a timestamp to the zip file name')
    parser.add_argument('--as_addon', default=False, action='store_true',
                        help='Release as addon instead of extension')
    args = parser.parse_args()
    
    release_addon(
        need_zip=not args.disable_zip,
        with_timestamp=args.with_timestamp,
        with_version=args.with_version,
        is_extension=not args.as_addon
    )