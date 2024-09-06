from .base_module import BaseModule
from schemas.negapedia_pageinfo import NegapediaPageInfo
from typing import Any, List, Optional, Dict, Union
from utils.input_validation_management import get_input_parameter_web_urls
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils.env_management import load_from_env
import matplotlib
from datetime import datetime
import logging
import re
import json
import sys

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os


class NegapediaModule(BaseModule):
    module = 'negapedia'
    extraction_settings = {}

    def handle_module(self, args: Any) -> None:
        """
        Handle the main logic for the negapedia module based on the input arguments.

        Args:
            args (Any): The arguments passed to the module.
        """
        # Check for required arguments
        if not args.pages or not args.post_type or not args.mode or not args.language:
            logging.error("Pages, Post Type, Mode and Language are required for negapedia module posting.")
            sys.exit(1)

        # Check if the mode is 'summary' and warn if more than one page is provided
        if args.mode == 'summary':
            if len(args.pages) > 1:
                logging.warning(f"More than one URL provided for 'summary' mode. Only the first URL '{args.pages[0]}' will be used.")
                # Only use the first URL
                args.pages = [args.pages[0]]

        # Check if the mode is 'comparison' and validate the number of pages
        elif args.mode == 'comparison':
            if len(args.pages) != 2:
                logging.error("The 'comparison' mode requires exactly two URLs in the '--pages' argument.")
                return

        # Check if the mode is 'ranking' and validate the minimum number of pages
        elif args.mode == 'ranking':
            if len(args.pages) < 2:
                logging.error("The 'ranking' mode requires at least two URLs in the '--pages' argument.")
                return
            if len(args.ranking_fields) < 1:
                logging.warning("The 'ranking' mode requires ranking field in the '--ranking_fields' argument. All ranking fields will be used for the ranking")
                # Save ranking fields on which the ranking will be built, forcing all of them as no choice have been made
                self.posting_settings['ranking_fields'] = ["recent_conflict_levels", "recent_polemic_levels", "mean_conflict_level", "mean_polemic_level"]
            else:
                # Save ranking fields on which the ranking will be built
                self.posting_settings['ranking_fields'] = args.ranking_fields

        # Save extraction settings
        self.extraction_settings = {
            "number_of_words_that_matter_to_extract": args.number_of_words_that_matter_to_extract,
            "number_of_conflict_awards_to_extract": args.number_of_conflict_awards_to_extract,
            "number_of_polemic_awards_to_extract": args.number_of_polemic_awards_to_extract,
            "number_of_social_jumps_to_extract": args.number_of_social_jumps_to_extract,
        }

        logging.info(f"Handling negapedia module for Pages {args.pages}")
        self.process_pages(
            urls=args.pages,
            post_type=args.post_type,
            mode=args.mode,
            language=args.language,
            remove_suffix=args.remove_suffix,
            base_directory=args.base_directory,
            base_url=args.base_url,
            minimum_article_modified_date=args.minimum_article_modified_date,
            message=args.message
        )

    def process_pages(
        self,
        urls: List[str],
        post_type: List[str],
        mode: str,
        language: str,
        remove_suffix: Optional[bool] = None,
        base_directory: Optional[str] = None,
        base_url: Optional[str] = None,
        minimum_article_modified_date: Optional[str] = None,
        message: Optional[str] = None
    ) -> None:
        """
        Processes a list of URLs, extracts page information for each, and generates posts.

        Args:
            urls (List[str]): The list of URLs to process.
            post_type (List[str]): The types of posts to create (e.g., 'facebook', 'twitter', 'web').
            mode (str): The mode to analyze topics (e.g., 'summary', 'comparison', 'ranking').
            language (str): The language in which to generate the posts.
            remove_suffix (Optional[bool], optional): Flag indicating whether to remove .html or .htm suffixes from URLs.
            base_directory (Optional[str], optional): The base directory in the filesystem for local processing.
            base_url (Optional[str], optional): The base URL for mapping local files to web URLs.
            minimum_article_modified_date (Optional[str], optional): The minimum article modified date for filtering pages (YYYY-MM-DD).
            message (Optional[str], optional): A custom message to be used in the post, if provided.
        """
        web_urls = get_input_parameter_web_urls(urls, self.module, remove_suffix, base_directory, base_url)

        pages_info = self.extract_pages_info(web_urls, message, mode)

        self.generate_posts(pages_info, post_type, mode, language)

    def extract_pages_info(self, urls: List[str], message: Optional[str], mode: str) -> List[NegapediaPageInfo]:
        """
        Extracts relevant information from a list of URLs for the specified mode.

        Args:
            urls (List[str]): The list of URLs being processed.
            message (Optional[str]): The message to force into the post.
            mode (str): The mode to analyze topics (e.g., 'summary', 'comparison', 'ranking').

        Returns:
            List[NegapediaPageInfo]: A list of dictionaries containing extracted information.
        """
        if mode == 'summary':
            # As summary mode is meant to work only on one page, we take just the first URL passed
            negapedia_page_info = self.build_single_page_post_info(urls, message)
            negapedia_pages_info = [negapedia_page_info]
        elif mode == 'comparison':
            negapedia_pages_info = self.build_multiple_pages_post_info(urls, message)
        elif mode == 'ranking':
            negapedia_pages_info = self.build_multiple_pages_post_info(urls, message)
        else:
            logging.error(f"Unsupported mode '{mode}' provided. Accepted modes are 'summary', 'comparison' or 'ranking'.")
            sys.exit(1)

        return negapedia_pages_info

    def build_single_page_post_info(self, urls: List[str], message: Optional[str]) -> NegapediaPageInfo:
        """
        Builds the post information in summary mode for the given URL.

        Args:
            urls (List[str]): The list of URLs being processed.
            message (Optional[str]): The message to force into the post.

        Returns:
            NegapediaPageInfo: Negapedia page information.
        """
        env_data = load_from_env()
        number_of_words_that_matter_to_extract = self.extraction_settings.get('number_of_words_that_matter_to_extract') or env_data.get('modules').get(f'{self.module}').get('number_of_words_that_matter_to_extract')
        number_of_conflict_awards_to_extract = self.extraction_settings.get('number_of_conflict_awards_to_extract') or env_data.get('modules').get(f'{self.module}').get('number_of_conflict_awards_to_extract')
        number_of_polemic_awards_to_extract = self.extraction_settings.get('number_of_polemic_awards_to_extract') or env_data.get('modules').get(f'{self.module}').get('number_of_polemic_awards_to_extract')
        number_of_social_jumps_to_extract = self.extraction_settings.get('number_of_social_jumps_to_extract') or env_data.get('modules').get(f'{self.module}').get('number_of_social_jumps_to_extract')

        # extract the only url to process
        url = urls[0]

        # Initialize variables
        negapedia_page_info = {
            'title': None,
            'description': None,
            'message': None,
            'compact_message': None,
            'historical_conflict': [],
            'historical_polemic': [],
            'historical_conflict_comparison': [],
            'historical_polemic_comparison': [],
            'recent_conflict_levels': None,
            'recent_polemic_levels': None,
            'mean_conflict_level': None,
            'mean_polemic_level': None,
            'words_that_matter': [],
            'conflict_awards': {},
            'polemic_awards': {},
            'social_jumps': []
        }

        try:
            page_content = self.fetch_page_content(url)

            if not page_content:
                logging.error(f"Failed to fetch page content for URL: {url}")
                return negapedia_page_info

            soup = BeautifulSoup(page_content, 'html.parser')

            negaranks_list = self.extract_negaranks(soup)
            negaranks_dict = self.convert_negaranks_to_dict(negaranks_list)

            title = self.extract_page_title(soup, url)
            plot_color = self.color_manager.get_color_for_topic(title)
            historical_conflict_levels = self.extract_historical_plotted_data('conflict', negaranks_dict, plot_color, url, title)
            historical_polemic_levels = self.extract_historical_plotted_data('polemic', negaranks_dict, plot_color, url, title)
            recent_conflict_levels = self.extract_recent_data('conflict', negaranks_dict, url, title)
            recent_polemic_levels = self.extract_recent_data('polemic', negaranks_dict, url, title)
            mean_conflict_level = self.extract_mean_data_level('conflict', negaranks_dict, url, title)
            mean_polemic_level = self.extract_mean_data_level('polemic', negaranks_dict, url, title)
            words_that_matter = self.extract_words_that_matter(soup, url, title, number_of_words_that_matter_to_extract)
            conflict_awards = self.extract_data_awards('conflict', negaranks_dict, url, title, number_of_conflict_awards_to_extract)
            polemic_awards = self.extract_data_awards('polemic', negaranks_dict, url, title, number_of_polemic_awards_to_extract)
            social_jumps = self.extract_social_jumps(soup, url, title, number_of_social_jumps_to_extract)

            compact_message = self.build_compact_message(title, recent_conflict_levels, recent_polemic_levels, words_that_matter, conflict_awards, polemic_awards, social_jumps)

            negapedia_page_info = {
                'title': title,
                'description': None,
                'message': message,
                'compact_message': compact_message,
                'historical_conflict': historical_conflict_levels,
                'historical_polemic': historical_polemic_levels,
                'historical_conflict_comparison': [],
                'historical_polemic_comparison': [],
                'recent_conflict_levels': recent_conflict_levels,
                'recent_polemic_levels': recent_polemic_levels,
                'mean_conflict_level': mean_conflict_level,
                'mean_polemic_level': mean_polemic_level,
                'words_that_matter': words_that_matter,
                'conflict_awards': conflict_awards,
                'polemic_awards': polemic_awards,
                'social_jumps': social_jumps
            }

        except Exception as e:
            logging.error(f"Failed to process dynamic data extraction for URL={url}: {e}")
            return negapedia_page_info

        return negapedia_page_info

    def build_multiple_pages_post_info(self, urls: List[str], message: Optional[str]) -> List[NegapediaPageInfo]:
        """
        Builds the post information in comparison/ranking mode for the given URLs.

        Args:
            urls (List[str]): The list of URLs being processed.
            message (Optional[str]): The message to force into the post.

        Returns:
            List[NegapediaPageInfo]: Negapedia page information.
        """
        env_data = load_from_env()
        number_of_words_that_matter_to_extract = self.extraction_settings.get('number_of_words_that_matter_to_extract') or env_data.get('modules').get(f'{self.module}').get('number_of_words_that_matter_to_extract')
        number_of_conflict_awards_to_extract = self.extraction_settings.get('number_of_conflict_awards_to_extract') or env_data.get('modules').get(f'{self.module}').get('number_of_conflict_awards_to_extract')
        number_of_polemic_awards_to_extract = self.extraction_settings.get('number_of_polemic_awards_to_extract') or env_data.get('modules').get(f'{self.module}').get('number_of_polemic_awards_to_extract')
        number_of_social_jumps_to_extract = self.extraction_settings.get('number_of_social_jumps_to_extract') or env_data.get('modules').get(f'{self.module}').get('number_of_social_jumps_to_extract')

        # Initialize variables
        compact_message = None
        compact_messages = []  # List to accumulate compact messages
        negapedia_pages_info = []

        # Initialize arrays to hold data for comparison/ranking plotting
        negaranks_for_comparison = []
        urls_for_comparison = []
        titles_for_comparison = []
        plot_colors_for_comparison = []

        for url in urls:
            try:
                page_content = self.fetch_page_content(url)

                if not page_content:
                    logging.error(f"Failed to fetch page content for URL: {url}")
                    continue

                soup = BeautifulSoup(page_content, 'html.parser')

                negaranks_list = self.extract_negaranks(soup)
                negaranks_dict = self.convert_negaranks_to_dict(negaranks_list)

                title = self.extract_page_title(soup, url)
                plot_color = self.color_manager.get_color_for_topic(title)
                historical_conflict_levels = self.extract_historical_plotted_data('conflict', negaranks_dict, plot_color, url, title)
                historical_polemic_levels = self.extract_historical_plotted_data('polemic', negaranks_dict, plot_color, url, title)
                recent_conflict_levels = self.extract_recent_data('conflict', negaranks_dict, url, title)
                recent_polemic_levels = self.extract_recent_data('polemic', negaranks_dict, url, title)
                mean_conflict_level = self.extract_mean_data_level('conflict', negaranks_dict, url, title)
                mean_polemic_level = self.extract_mean_data_level('polemic', negaranks_dict, url, title)
                words_that_matter = self.extract_words_that_matter(soup, url, title, number_of_words_that_matter_to_extract)
                conflict_awards = self.extract_data_awards('conflict', negaranks_dict, url, title, number_of_conflict_awards_to_extract)
                polemic_awards = self.extract_data_awards('polemic', negaranks_dict, url, title, number_of_polemic_awards_to_extract)
                social_jumps = self.extract_social_jumps(soup, url, title, number_of_social_jumps_to_extract)

                negapedia_page_info = {
                    'title': title,
                    'description': None,
                    'message': message,
                    'compact_message': None,
                    'historical_conflict': historical_conflict_levels,
                    'historical_polemic': historical_polemic_levels,
                    'historical_conflict_comparison': [],
                    'historical_polemic_comparison': [],
                    'recent_conflict_levels': recent_conflict_levels,
                    'recent_polemic_levels': recent_polemic_levels,
                    'mean_conflict_level': mean_conflict_level,
                    'mean_polemic_level': mean_polemic_level,
                    'words_that_matter': words_that_matter,
                    'conflict_awards': conflict_awards,
                    'polemic_awards': polemic_awards,
                    'social_jumps': social_jumps
                }
                negapedia_pages_info.append(negapedia_page_info)

                # Build compact message for the current topic and add it to compact_messages
                topic_compact_message = self.build_compact_message(title, recent_conflict_levels, recent_polemic_levels, words_that_matter, conflict_awards, polemic_awards, social_jumps)
                compact_messages.append(topic_compact_message)

                # Append data to arrays for comparison
                negaranks_for_comparison.append(negaranks_dict)
                urls_for_comparison.append(url)
                titles_for_comparison.append(title)
                plot_colors_for_comparison.append(plot_color)

            except Exception as e:
                logging.error(f"Failed to process dynamic data extraction for URL={url}: {e}")
                continue

        historical_conflict_comparison = self.extract_comparison_of_historical_plotted_data('conflict', negaranks_for_comparison, plot_colors_for_comparison, urls_for_comparison, titles_for_comparison)
        historical_polemic_comparison = self.extract_comparison_of_historical_plotted_data('polemic', negaranks_for_comparison, plot_colors_for_comparison, urls_for_comparison, titles_for_comparison)

        # Combine all parts into a single compact_message
        if compact_messages:
            compact_message = "\n\n".join(compact_messages)

        for negapedia_page_info in negapedia_pages_info:
            negapedia_page_info['compact_message'] = compact_message
        for negapedia_page_info in negapedia_pages_info:
            negapedia_page_info['historical_conflict_comparison'] = historical_conflict_comparison
        for negapedia_page_info in negapedia_pages_info:
            negapedia_page_info['historical_polemic_comparison'] = historical_polemic_comparison

        return negapedia_pages_info

    @staticmethod
    def extract_negaranks(soup: BeautifulSoup) -> Optional[List[dict]]:
        """
        Extracts the NEGARANKS data from the page content.

        Args:
            soup (BeautifulSoup): Parsed HTML content of the page.

        Returns:
            Optional[List[dict]]: A list of dictionaries representing NEGARANKS data.
        """
        # Find the <script> tag that contains the NEGARANKS variable
        script_tag = soup.find('script', text=re.compile(r'var NEGARANKS = \['))

        if script_tag:
            # Extract the JavaScript content from the <script> tag
            script_content = script_tag.get_text()  # Use get_text() to ensure we capture all content

            # Use regex to find the NEGARANKS array, with re.DOTALL to match multiline content
            negaranks_match = re.search(r'var NEGARANKS = (\[.*\]);', script_content, re.DOTALL)

            if negaranks_match:
                # Extract the NEGARANKS array string
                negaranks_string = negaranks_match.group(1)

                # Remove any trailing commas before closing brackets to conform to JSON standards
                negaranks_string = re.sub(r',\s*]', ']', negaranks_string)

                # Convert the JavaScript array string to a Python list
                try:
                    negaranks_list = json.loads(negaranks_string)
                    return negaranks_list
                except json.JSONDecodeError as e:
                    logging.error(f"Error decoding NEGARANKS: {e}")
                    return None
            else:
                logging.error("NEGARANKS variable not found in the script content.")
                return None
        else:
            logging.error("No script tag containing NEGARANKS variable found.")
            return None

    @staticmethod
    def convert_negaranks_to_dict(negaranks_list: List[dict]) -> List[Dict[str, Union[int, str, float]]]:
        """
        Convert a list of negaranks into a list of dictionaries with descriptive keys.

        Args:
            negaranks_list (List[dict]): List of NEGARANKS data entries.

        Returns:
            List[Dict[str, Union[int, str, float]]]: Converted NEGARANKS data.
        """
        # Define the keys corresponding to the values in each negarank entry
        keys = ['ranking', 'percentile', 'normalized_value', 'type', 'category', 'period', 'absolute_value']

        # Define the desired type for each key
        type_mapping = {
            'ranking': int,
            'percentile': int,
            'normalized_value': int,
            'type': str,
            'category': str,
            'period': str,
            'absolute_value': float
        }

        # Convert each entry in the negaranks_list to a dictionary with correct types
        negaranks_dicts = []
        for entry in negaranks_list:
            # Cast each value to the desired type using the type mapping
            entry_dict = {key: type_mapping[key](value) for key, value in zip(keys, entry)}
            negaranks_dicts.append(entry_dict)

        return negaranks_dicts

    @staticmethod
    def extract_page_title(soup: BeautifulSoup, url: str) -> str:
        """
        Extracts the page title from a given BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML content of the page.
            url (str): The URL of the page.

        Returns:
            str: The extracted title of the page, or the URL if not found.
        """
        try:
            # Find the <title> element in the <head> section
            title_element = soup.find('title')
            if title_element:
                title = title_element.get_text(strip=True)

                # Strip the suffix " - Negapedia" if present
                if " - Negapedia" in title:
                    title = title.replace(" - Negapedia", "")

                return title
            else:
                logging.warning(f"No <title> element found for URL={url}")

        except Exception as e:
            logging.error(f"Error during page title extraction for URL={url}: {e}")

        # Return a default value if no title is found
        return url

    @staticmethod
    def extract_historical_plotted_data(type_check: str, negaranks_dict: List[Dict[str, Union[int, str, float]]], plot_color: str, url: str, title: str) -> List[dict]:
        """
        Extracts and plots historical conflict data from the NEGARANKS dictionary.

        Args:
            type_check (str): The type of data to extract ('conflict' or 'polemic').
            negaranks_dict (list): The list of NEGARANKS data entries.
            plot_color (str): The color assigned for plotting topic data.
            url (str): The URL of the page.
            title (str): The title of the topic being analyzed.

        Returns:
            List[dict]: A list containing information about the generated plot image.
        """
        env_data = load_from_env()
        posts_images_absolute_destination_path = env_data.get('posts_images_absolute_destination_path')

        # Define helper function to filter the NEGARANKS data
        def filter_data(negaranks_dict):
            return [entry for entry in negaranks_dict
                    if entry['type'] == type_check and
                    entry['category'] == 'all' and
                    entry['period'] != 'all' and
                    entry['period'] != str(datetime.now().year)]

        historical_data_levels = []
        # Filter the NEGARANKS data
        filtered_data = filter_data(negaranks_dict)

        years = [int(entry['period']) for entry in filtered_data]
        values = [entry['absolute_value'] for entry in filtered_data]

        # Create line plots
        plt.figure(figsize=(14, 8), dpi=100)

        years_to_plot = years
        values_to_plot = values
        plot_label = f"Historical {type_check.capitalize()} Levels for {title}"
        plt.plot(years_to_plot, values_to_plot, label=plot_label, color=plot_color, marker="o", linestyle='-')

        # Add labels and title
        plt.xlabel("Year", fontsize=14)
        plt.ylabel(f"{type_check.capitalize()} level", fontsize=14)
        plt.title(f"Historical {type_check.capitalize()} Levels for {title}", fontsize=16)
        plt.legend(fontsize=12)

        # Adjust x-axis and y-axis ticks
        plt.grid(True, linestyle='--', linewidth=0.5)
        max_x = max(years)
        min_x = min(years)
        max_y = max(values)
        min_y = min(values)

        x_tick_step = 1
        y_tick_step = max(1, round(max_y / 10))

        plt.xticks(range(min_x - 1, max_x + 1, x_tick_step), fontsize=12)
        plt.yticks(range(0, int(max_y) + 1, y_tick_step), fontsize=12)

        # Save the plot as a PNG file
        timestamp = datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")
        output_filename = f"{plot_label.replace(' ', '_').replace(',', '').replace('-', '')}_{timestamp}.png"
        output_path = os.path.join(posts_images_absolute_destination_path, output_filename)
        plt.tight_layout()
        plt.savefig(output_path)

        historical_data_levels.append({
            "image": output_path,
            'image_width': None,
            'image_height': None,
            'image_alt': f"Historical {type_check.capitalize()} Levels for {title}",
            'location': "local",
        })

        # Optionally show the plot
        # plt.show()

        logging.info(f"Historical {type_check.capitalize()} Levels plot for {url} saved at: {output_path}")
        return historical_data_levels

    @staticmethod
    def extract_recent_data(type_check: str, negaranks_dict: List[Dict[str, Union[int, str, float]]], url: str, title: str) -> Optional[str]:
        """
        Extracts recent data (conflict or polemic level) from the NEGARANKS dictionary.

        Args:
            type_check (str): The type of data to extract ('conflict' or 'polemic').
            negaranks_dict (list): The list of NEGARANKS data entries.
            url (str): The URL of the page.
            title (str): The title of the topic being analyzed.

        Returns:
            Optional[str]: The extracted data level or None if not found.
        """
        try:
            # Filter the NEGARANKS data for the current year and the specified type
            filtered_data = [
                entry for entry in negaranks_dict
                if entry['type'] == type_check and entry['category'] == 'all' and entry['period'] != 'all'
            ]

            # Find the entry with the highest numeric period
            recent_data = max(filtered_data, key=lambda x: int(x['period']))

            if recent_data:
                # Extract the 'normalized_value' from the recent data
                normalized_value = recent_data['normalized_value']
                logging.info(f"Extracted recent {type_check} level: {normalized_value} for {title} from {url}")
                return str(normalized_value)
            else:
                logging.warning(f"No recent {type_check} data found for {title} in year {str(datetime.now().year)} from {url}")
                return None

        except Exception as e:
            logging.error(f"Error during recent {type_check} extraction for {title} from {url}: {e}")
            return None

    @staticmethod
    def extract_mean_data_level(type_check: str, negaranks_dict: List[Dict[str, Union[int, str, float]]], url: str, title: str) -> Optional[str]:
        """
        Calculates the mean level (conflict or polemic) from the NEGARANKS dictionary using the 'absolute_value' field.

        Args:
            type_check (str): The type of data to calculate the mean for ('conflict' or 'polemic').
            negaranks_dict (list): The list of NEGARANKS data entries.
            url (str): The URL of the page.
            title (str): The title of the topic being analyzed.

        Returns:
            Optional[str]: The calculated mean level or None if not found.
        """
        try:
            # Filter the NEGARANKS data for all periods and the specified type
            filtered_data = [
                entry for entry in negaranks_dict
                if entry['type'] == type_check and entry['category'] == 'all' and entry['period'] != 'all'
            ]

            if not filtered_data:
                logging.warning(f"No {type_check} data found for {title} across any year from {url}")
                return None

            # Calculate the mean of 'absolute_value' for the filtered entries
            total_value = sum(float(entry['absolute_value']) for entry in filtered_data)
            mean_value = total_value / len(filtered_data)

            logging.info(f"Calculated mean {type_check} level: {mean_value:.2f} for {title} from {url}")
            return f"{mean_value:.2f}"  # Return as a string formatted to two decimal places

        except Exception as e:
            logging.error(f"Error during mean {type_check} extraction for {title} from {url}: {e}")
            return None

    @staticmethod
    def extract_words_that_matter(soup: BeautifulSoup, url: str, title: str, top_n: int) -> List[str]:
        """
        Extracts the N most important words from the 'Word2TFIDF' JavaScript variable.

        Args:
            soup (BeautifulSoup): Parsed HTML content of the page.
            url (str): The URL of the page.
            title (str): The title of the topic being analyzed.
            top_n (int): The number of top words to extract.

        Returns:
            List[str]: A list of the most important words.
        """
        words_that_matter = []

        try:
            # Find the <script> tag that contains the Word2TFIDF variable
            script_tag = soup.find('script', text=re.compile(r'var Word2TFIDF = new Map\(\[\['))

            if script_tag:
                # Extract the JavaScript content from the <script> tag
                script_content = script_tag.string

                # Use regex to find the Word2TFIDF map
                word2tfidf_match = re.search(r'var Word2TFIDF = new Map\((\[.*?\])\);', script_content, re.DOTALL)

                if word2tfidf_match:
                    # Extract the Word2TFIDF string
                    word2tfidf_string = word2tfidf_match.group(1)

                    # Convert the JavaScript array string to a Python list of tuples
                    try:
                        # Use eval to convert the list of tuples to a Python object safely
                        word2tfidf_list = eval(word2tfidf_string)

                        # Sort the words by their TF-IDF values (second element in each tuple) in descending order
                        # sorted_words = sorted(word2tfidf_list, key=lambda x: x[1], reverse=True)

                        # Extract the top N words
                        # words_that_matter = [word for word, _ in sorted_words[:top_n]]
                        words_that_matter = [word for word, _ in word2tfidf_list[:top_n]]

                        logging.info(f"Extracted top {top_n} important words for {title} from {url}: {words_that_matter}")
                    except Exception as e:
                        logging.error(f"Error decoding Word2TFIDF for {title} from {url}: {e}")
                else:
                    logging.warning(f"Word2TFIDF variable not found in the script content for {title} from {url}.")
            else:
                logging.warning(f"No script tag containing Word2TFIDF variable found for {title} from {url}.")

        except Exception as e:
            logging.error(f"Error during important words extraction for {title} from {url}: {e}")

        return words_that_matter

    @staticmethod
    def extract_data_awards(type_check: str, negaranks_dict: List[Dict[str, Union[int, str, float]]], url: str, title: str, top_n: int) -> Dict[str, List[str]]:
        """
        Extracts awards from the NEGARANKS data for the specified type (conflict or polemic).

        Args:
            type_check (str): The type of data to extract awards for ('conflict' or 'polemic').
            negaranks_dict (list): The list of NEGARANKS data entries.
            url (str): The URL of the page.
            title (str): The title of the topic being analyzed.
            top_n (int): The maximum number of awards to return per category.

        Returns:
            dict: A dictionary where the keys are categories and the values are lists of awards.
        """
        # Initialize awards as an empty dictionary
        awards = {}

        # Extract unique categories from the negaranks_dict
        categories = list({entry['category'] for entry in negaranks_dict})

        # Initialize an empty list for each category
        for category in categories:
            awards[category] = []

        for category in categories:
            try:
                # Filter NEGARANKS data by type and category
                filtered_data = [entry for entry in negaranks_dict if
                                 entry['type'] == type_check and entry['category'] == category]

                # Dictionary to group awards by type
                grouped_awards = {}

                # Award: Top 1000 of all time
                if any(entry['period'] == 'all' and entry['ranking'] <= 1000 for entry in filtered_data):
                    grouped_awards.setdefault("Top 1000 of all time", []).append("all time")

                # Award: Top 100 of all time
                if any(entry['period'] == 'all' and entry['ranking'] <= 100 for entry in filtered_data):
                    grouped_awards.setdefault("Top 100 of all time", []).append("all time")

                # Award: Top 1% of all time
                if any(entry['period'] == 'all' and entry['percentile'] == 100 for entry in filtered_data):
                    grouped_awards.setdefault("Top 1% of all time", []).append("all time")

                # Award: First place of the year
                first_place_years = [entry['period'] for entry in filtered_data if
                                     entry['ranking'] == 1 and entry['period'] != 'all']
                if first_place_years:
                    grouped_awards.setdefault("First place of the year", []).extend(first_place_years)

                # Award: Third place of the year
                third_place_years = [entry['period'] for entry in filtered_data if
                                     entry['ranking'] == 3 and entry['period'] != 'all']
                if third_place_years:
                    grouped_awards.setdefault("Third place of the year", []).extend(third_place_years)

                # Award: Top Ten of the year
                top_ten_years = [entry['period'] for entry in filtered_data if
                                 entry['ranking'] <= 10 and entry['period'] != 'all']
                if top_ten_years:
                    grouped_awards.setdefault("Top Ten of the year", []).extend(top_ten_years)

                # Award: Top 100 of the year
                top_hundred_years = [entry['period'] for entry in filtered_data if
                                     entry['ranking'] <= 100 and entry['period'] != 'all']
                if top_hundred_years:
                    grouped_awards.setdefault("Top 100 of the year", []).extend(top_hundred_years)

                # Award: Top 1000 of the year
                top_thousand_years = [entry['period'] for entry in filtered_data if
                                      entry['ranking'] <= 1000 and entry['period'] != 'all']
                if top_thousand_years:
                    grouped_awards.setdefault("Top 1000 of the year", []).extend(top_thousand_years)

                # Award: Top 1% of the year
                top_one_percent_years = [entry['period'] for entry in filtered_data if
                                         entry['percentile'] == 100 and entry['period'] != 'all']
                if top_one_percent_years:
                    grouped_awards.setdefault("Top 1% of the year", []).extend(top_one_percent_years)

                # Combine and format the grouped awards
                for award_type, years in grouped_awards.items():
                    if "all time" in years:
                        awards[category].append(award_type)
                    else:
                        unique_years = sorted(set(years))
                        awards[category].append(f"{award_type} ({', '.join(unique_years)})")

                # Limit the awards to the top N per category
                awards[category] = awards[category][:top_n]

                logging.info(f"Extracted awards for {title} from {url}: {awards}")
            except Exception as e:
                logging.error(f"Error during awards extraction for {title} from {url}: {e}")

        return awards

    @staticmethod
    def extract_social_jumps(soup: BeautifulSoup, url: str, title: str, top_n: int) -> List[dict]:
        """
        Extracts social jumps from the 'social-jumps' div and returns the top N entries.

        Args:
            soup (BeautifulSoup): Parsed HTML content of the page.
            url (str): The URL of the page.
            title (str): The title of the topic being analyzed.
            top_n (int): The maximum number of social jumps to return.

        Returns:
            List[dict]: A list of dictionaries containing social jump titles and links.
        """
        social_jumps = []

        try:
            # Load environment data to get the base URL
            env_data = load_from_env()
            base_url = env_data.get('modules').get(f'{NegapediaModule.module}').get('website_base_url')

            # Ensure the base_url is properly formatted
            if not base_url.endswith('/'):
                base_url += '/'

            # Locate the div containing the social jumps data
            social_jumps_div = soup.find('div', id='social-jumps')
            if social_jumps_div:
                # Find all 'dt' elements (titles) and their corresponding 'dd' elements (descriptions)
                social_jump_titles = social_jumps_div.find_all('dt')
                social_jump_descriptions = social_jumps_div.find_all('dd', class_='wikipedia-short')

                # Iterate over each pair of title and description to build the social jump data
                for title_element, description_element in zip(social_jump_titles, social_jump_descriptions):
                    # Extract title text from 'dt' element
                    title_text = title_element.get_text(strip=True)
                    # Extract the data-name attribute from 'dd' element to construct the link
                    data_name = description_element.get('data-name')

                    # Construct the full link using the base URL
                    link = urljoin(base_url, f"articles/{data_name}")

                    # Append the social jump to the list
                    social_jumps.append({'title': title_text, 'link': link})

                # Limit the extracted social jumps to the top N
                social_jumps = social_jumps[:top_n]

                logging.info(f"Extracted top {top_n} social jumps from {url}: {social_jumps}")
            else:
                logging.warning(f"No 'social-jumps' section found for URL={url}")
        except Exception as e:
            logging.error(f"Error during social jumps extraction for URL={url}: {e}")

        return social_jumps

    @staticmethod
    def extract_comparison_of_historical_plotted_data(type_check: str, negaranks_dicts: List[List[Dict[str, Union[int, str, float]]]], plot_colors: List[str], urls: List[str], titles: List[str]) -> List[dict]:
        """
        Extracts and plots comparative historical data for multiple NEGARANKS dictionaries.

        Args:
            type_check (str): The type of data to extract ('conflict' or 'polemic').
            negaranks_dicts (List[List[Dict[str, Union[int, str, float]]]]): A list of NEGARANKS data entries for each topic.
            plot_colors (List[str]): A list of color assigned for plotting topics data.
            urls (List[str]): A list of URLs for each page.
            titles (List[str]): A list of titles for each topic being analyzed.

        Returns:
            List[dict]: A list containing information about the generated plot image.
        """
        env_data = load_from_env()
        posts_images_absolute_destination_path = env_data.get('posts_images_absolute_destination_path')

        comparison_data_levels = []

        plt.figure(figsize=(14, 8), dpi=100)

        # Define helper function to filter the NEGARANKS data
        def filter_data(negaranks_dict):
            return [entry for entry in negaranks_dict
                    if entry['type'] == type_check and
                    entry['category'] == 'all' and
                    entry['period'] != 'all' and
                    entry['period'] != str(datetime.now().year)]

        # Loop through each set of NEGARANKS data to plot
        for i, negaranks_dict in enumerate(negaranks_dicts):
            filtered_data = filter_data(negaranks_dict)
            years = [int(entry['period']) for entry in filtered_data]
            values = [entry['absolute_value'] for entry in filtered_data]

            # Plot data for each topic
            plot_label = f"Historical {type_check.capitalize()} Levels for {titles[i]}"
            plot_color = plot_colors[i]
            plt.plot(years, values, label=plot_label, color=plot_color, marker="o", linestyle='-')

        # Add labels, title, and legend
        plt.xlabel("Year", fontsize=14)
        plt.ylabel(f"{type_check.capitalize()} level", fontsize=14)
        plt.title(f"Comparison of Historical {type_check.capitalize()} Levels", fontsize=16)
        plt.legend(fontsize=12)

        # Adjust x-axis and y-axis ticks
        plt.grid(True, linestyle='--', linewidth=0.5)
        min_year = min([int(entry['period']) for d in negaranks_dicts for entry in filter_data(d)])
        max_year = max([int(entry['period']) for d in negaranks_dicts for entry in filter_data(d)])
        max_value = max([entry['absolute_value'] for d in negaranks_dicts for entry in filter_data(d)])

        x_tick_step = 1
        y_tick_step = max(1, round(max_value / 10))

        plt.xticks(range(min_year - 1, max_year + 1, x_tick_step), fontsize=12)
        plt.yticks(range(0, int(max_value) + 1, y_tick_step), fontsize=12)

        # Save the plot as a PNG file
        timestamp = datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")
        output_filename = f"Comparison_Historical_{type_check.capitalize()}_Levels_{timestamp}.png"
        output_path = os.path.join(posts_images_absolute_destination_path, output_filename)
        plt.tight_layout()
        plt.savefig(output_path)

        comparison_data_levels.append({
            "image": output_path,
            'image_width': None,
            'image_height': None,
            'image_alt': f"Comparison of Historical {type_check.capitalize()} Levels for Multiple Topics",
            'location': "local",
        })

        logging.info(f"Comparison plot for {', '.join(urls)} saved at: {output_path}")
        return comparison_data_levels

    @staticmethod
    def build_compact_message(
            title: str,
            recent_conflict_levels: Optional[str],
            recent_polemic_levels: Optional[str],
            words_that_matter: List[str],
            conflict_awards: Dict[str, List[str]],
            polemic_awards: Dict[str, List[str]],
            social_jumps: List[dict]
    ) -> str:
        """
        Builds a textual compact message based on provided conflict and polemic levels, important words, awards, and social jumps.

        Args:
            title (str): The title of the topic being analyzed.
            recent_conflict_levels (Optional[str]): Recent conflict levels.
            recent_polemic_levels (Optional[str]): Recent polemic levels.
            words_that_matter (List[str]): List of important words.
            conflict_awards (Dict[str, List[str]]): Conflict awards categorized.
            polemic_awards (Dict[str, List[str]]): Polemic awards categorized.
            social_jumps (List[dict]): List of social jumps.

        Returns:
            str: A formatted compact message string.
        """
        # Initialize compact message string
        compact_message = ""

        # Add sections for recent conflict and polemic levels
        compact_message += "RECENT CONFLICT LEVELS:\n"
        compact_message += f" - Conflict Level at {title}: {recent_conflict_levels or 'N/A'}\n"
        compact_message += "\n"

        compact_message += "RECENT POLEMIC LEVELS:\n"
        compact_message += f" - Polemic Level at {title}: {recent_polemic_levels or 'N/A'}\n"
        compact_message += "\n"

        # Add a section for Important Words
        if words_that_matter:
            compact_message += "IMPORTANT WORDS (TOP 100):\n"
            compact_message += ", ".join(words_that_matter) + "...\n"
            compact_message += "\n"

        # Add sections for Conflict Awards
        if conflict_awards:
            compact_message += "CONFLICT AWARDS:\n"
            # Global awards (all categories)
            if 'all' in conflict_awards and conflict_awards['all']:
                compact_message += "GLOBAL (IN ALL WIKIPEDIA):\n"
                for award in conflict_awards['all']:
                    compact_message += f" - {award}\n"

            # Category-specific awards
            for category, awards in conflict_awards.items():
                if category != 'all' and awards:
                    compact_message += f"CATEGORY SPECIFIC ({category.upper()}):\n"
                    for award in awards:
                        compact_message += f" - {award}\n"
            compact_message += "\n"

        # Add sections for Polemic Awards
        if polemic_awards:
            compact_message += "POLEMIC AWARDS:\n"
            # Global awards (all categories)
            if 'all' in polemic_awards and polemic_awards['all']:
                compact_message += "GLOBAL (IN ALL WIKIPEDIA):\n"
                for award in polemic_awards['all']:
                    compact_message += f" - {award}\n"

            # Category-specific awards
            for category, awards in polemic_awards.items():
                if category != 'all' and awards:
                    compact_message += f"CATEGORY SPECIFIC ({category.upper()}):\n"
                    for award in awards:
                        compact_message += f" - {award}\n"
            compact_message += "\n"

        # Add a section for Social Jumps
        if social_jumps:
            compact_message += "SOCIAL JUMPS (TOP 100):\n"
            for jump in social_jumps:
                compact_message += f" - {jump['title']}: {jump['link']}\n"
            compact_message += "\n"

        return compact_message
