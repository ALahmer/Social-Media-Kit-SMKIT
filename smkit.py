import argparse
from utils.modules_management import load_module
import logging
from utils.logger_setup import LoggerSetup
import sys


def main():
    LoggerSetup(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Social Media Kit")
    parser.add_argument('--module', type=str, help='Specify the module (e.g., negapedia)')
    parser.add_argument('--pages', nargs='+', type=str, help='Specify the pages to post about', required=True)
    parser.add_argument('--mode', type=str, choices=['summary', 'comparison', 'ranking'], help='Specify the mode to analyse topics', required=True)
    parser.add_argument('--post_type', nargs='+', type=str, choices=['twitter', 'facebook', 'web'], help='Specify the type of post', required=True)
    parser.add_argument('--message', type=str, help='Specify a custom message for the post')
    parser.add_argument('--language', type=str, choices=['en', 'it'], default='en', help='Specify the language for the post')
    parser.add_argument('--minimum_article_modified_date', type=str, help='Specify the minimum article modified date for filtering pages (YYYY-MM-DD)')
    parser.add_argument('--base_directory', type=str, help='Specify the filesystem website base directory (e.g., /var/www/negapedia/en/html)')
    parser.add_argument('--base_url', type=str, help='Specify the website base url (e.g., http://en.negapedia.org)')
    parser.add_argument('--remove_suffix', action='store_true', help='Remove .html or .htm suffixes from URLs')
    parser.add_argument('--number_of_words_that_matter_to_extract', type=int, help='Number of important words to extract')
    parser.add_argument('--number_of_conflict_awards_to_extract', type=int, help='Number of conflict awards to extract')
    parser.add_argument('--number_of_polemic_awards_to_extract', type=int, help='Number of polemic awards to extract')
    parser.add_argument('--number_of_social_jumps_to_extract', type=int, help='Number of social jumps to extract')
    parser.add_argument('--ranking_fields', nargs='+', choices=['recent_conflict_levels', 'recent_polemic_levels', 'mean_conflict_level', 'mean_polemic_level'], help='Specify fields to use for ranking. If no choice is made all ranking fields will be used for the ranking')

    args = parser.parse_args()

    if args.module:
        try:
            module_instance = load_module(args.module.lower())
            module_instance.handle_module(args)
        except ImportError as e:
            logging.error(e)
            sys.exit(1)
    else:
        generic_module = load_module('generic')
        generic_module.handle_module(args)


if __name__ == "__main__":
    main()
