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
    parser.add_argument('--pages', nargs='+', type=str, help='Specify the pages to post about')
    parser.add_argument('--date', type=str, help='Specify the date for filtering pages (YYYY-MM-DD)')

    args = parser.parse_args()

    # args = {
    #     # "module": "negapedia",
    #     "module": None,
    #     # "mode": "comparison",
    #     "mode": "summary",
    #     "post_type": [
    #         "web",
    #         "facebook",
    #         "twitter",
    #                   ],
    #     "message": None,
    #     "language": None,
    #     # "pages": [
    #     #     "./virtual_local_server/var/www/negapedia/en/html/articles/Barack_Obama.html.zip",
    #     #     "./virtual_local_server/var/www/negapedia/en/html/articles/Donald_Trump.html.zip",
    #     #     "./virtual_local_server/var/www/negapedia/en/html/articles/George_W._Bush.html.zip",
    #     #     "./virtual_local_server/var/www/negapedia/en/html/articles/Joe_Biden.html.zip"
    #     # ],
    #     # "pages": [
    #     #     "./virtual_local_server/var/www/negapedia/en/html"
    #     # ],
    #     "pages": [
    #         "http://it.negapedia.org/articles/Joe_Biden",
    #         "http://it.negapedia.org/articles/Donald_Trump",
    #         "http://it.negapedia.org/articles/Barack_Obama",
    #         # "https://techcrunch.com/2024/08/10/after-global-it-meltdown-crowdstrike-courts-hackers-with-action-figures-and-gratitude/",
    #         # "https://www.ilpost.it/2024/08/18/governo-germania-automobili/",
    #         # "https://www.buzzfeed.com/sarahaspler/women-who-make-six-figures-are-sharing-their-jobs-1",
    #         # "https://ahrefs.com/blog/it/backlink-seo/",
    #         # "https://www.w3schools.com/tags/tag_meta.asp",
    #     ],
    #     "date": None
    # }
    # args = argparse.Namespace(**args)

    if args.module:
        if args.module.lower() == 'negapedia':
            handle_negapedia_module(args)
        else:
            print(f"Module {args.module} not supported.")
    else:
        handle_generic_module(args)


if __name__ == "__main__":
    main()
