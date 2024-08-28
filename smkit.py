import argparse
from utils.modules_management import load_module


def main():
    parser = argparse.ArgumentParser(description="Social Media Kit")
    parser.add_argument('--module', type=str, help='Specify the module (e.g., negapedia)')
    parser.add_argument('--pages', nargs='+', type=str, help='Specify the pages to post about')
    parser.add_argument('--mode', type=str, choices=['comparison', 'summary'], help='Specify the mode to analise topics')
    parser.add_argument('--post_type', nargs='+', type=str, choices=['twitter', 'facebook', 'web'], help='Specify the type of post')
    parser.add_argument('--message', type=str, help='Specify a custom message for the post')
    parser.add_argument('--language', type=str, choices=['en', 'it'], default='en', help='Specify the language for the post')
    parser.add_argument('--minimum_article_modified_date', type=str, help='Specify the minimum article modified date for filtering pages (YYYY-MM-DD)')
    parser.add_argument('--base_directory', type=str, help='Specify the filesystem website base directory (e.g., /var/www/negapedia/en/html)')
    parser.add_argument('--base_url', type=str, help='Specify the website base url (e.g., http://en.negapedia.org)')
    parser.add_argument('--remove_suffix', action='store_true', help='Remove .html or .htm suffixes from URLs')

    args = parser.parse_args()

    # args = {
    #     "module": "negapedia",
    #     # "module": None,
    #     # "mode": "comparison",
    #     "mode": "summary",
    #     "post_type": [
    #         "web",
    #         # "facebook",
    #         # "twitter",
    #                   ],
    #     "message": None,
    #     "language": 'en',
    #     # "pages": [
    #     #     "./virtual_local_server/var/www/negapedia/en/html/articles/Barack_Obama.html.zip",
    #     #     # "./virtual_local_server/var/www/negapedia/en/html/articles/Donald_Trump.html.zip",
    #     #     # "./virtual_local_server/var/www/negapedia/en/html/articles/George_W._Bush.html.zip",
    #     #     # "./virtual_local_server/var/www/negapedia/en/html/articles/Joe_Biden.html.zip"
    #     # ],
    #     # "pages": [
    #     #     "./virtual_local_server/var/www/negapedia/it/html"
    #     # ],
    #     "pages": [
    #         # "http://it.negapedia.org/articles/Joe_Biden",
    #         "http://it.negapedia.org/articles/Donald_Trump",
    #         # "http://it.negapedia.org/articles/Barack_Obama",
    #         # "https://techcrunch.com/2024/08/10/after-global-it-meltdown-crowdstrike-courts-hackers-with-action-figures-and-gratitude/",
    #         # "https://www.ilpost.it/2024/08/18/governo-germania-automobili/",
    #         # "https://www.buzzfeed.com/sarahaspler/women-who-make-six-figures-are-sharing-their-jobs-1",
    #         # "https://ahrefs.com/blog/it/backlink-seo/",
    #         # "https://www.w3schools.com/tags/tag_meta.asp",
    #         # "https://www.bbc.com/news/articles/cj08mn24jplo",
    #         # "https://www.thetimes.com/sport/tennis/article/jannik-sinner-escapes-drugs-ban-failed-tests-tennis-world-no1-ksp89hmnc",
    #     ],
    #     "minimum_article_modified_date": None,
    #     "base_directory": None,
    #     "base_url": None,
    #     "remove_suffix": False,
    # }
    # args = argparse.Namespace(**args)

    if args.module:
        try:
            module_instance = load_module(args.module.lower())
            module_instance.handle_module(args)
        except ImportError as e:
            print(e)
            exit(1)
    else:
        generic_module = load_module('generic')
        generic_module.handle_module(args)


if __name__ == "__main__":
    main()
