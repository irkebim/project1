from framework import test_addon

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--disable_watch', default=False, action='store_true', 
                        help='Do not reload addon when file changed')
    args = parser.parse_args()
    
    test_addon(enable_watch=not args.disable_watch)