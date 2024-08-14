import argparse
from modules.negapedia_module import handle_negapedia_module
from modules.generic_module import handle_generic_module


def main():
    parser = argparse.ArgumentParser(description="Social Media Kit")
    parser.add_argument('--module', type=str, help='Specify the module (e.g., negapedia)')
    parser.add_argument('--mode', type=str, choices=['comparison', 'summary'], help='Specify the mode to analise topics')
    parser.add_argument('--post_type', nargs='+', type=str, choices=['twitter', 'facebook', 'web'], help='Specify the type of post')
    parser.add_argument('--message', type=str, help='Specify a custom message for the post')
    parser.add_argument('--language', type=str, help='Specify the language for the post (e.g., en, it)')
    parser.add_argument('--urls', nargs='+', type=str, help='Specify the URLs to post about')
    parser.add_argument('--date', type=str, help='Specify the date for filtering pages (YYYY-MM-DD)')

    args = parser.parse_args()

    if args.module:
        if args.module.lower() == 'negapedia':
            handle_negapedia_module(args)
        else:
            print(f"Module {args.module} not supported.")
    else:
        handle_generic_module(args)


if __name__ == "__main__":
    main()
