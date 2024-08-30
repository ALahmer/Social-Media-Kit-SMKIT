from .base_module import BaseModule
from schemas.negapedia_pageinfo import NegapediaPageInfo
from typing import Any, List, Optional
from utils.input_validation_management import get_input_parameter_web_urls
import time
from bs4 import BeautifulSoup
from utils.images_management import save_svg, convert_svg_to_png
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from utils.env_management import load_from_env
import matplotlib
from datetime import datetime
import logging


matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os
import seaborn as sns


class NegapediaModule(BaseModule):
    module = 'negapedia'

    def handle_module(self, args: Any) -> None:
        if not args.pages or not args.post_type or not args.mode or not args.language:
            raise ValueError("Pages, Post Type, Mode and Language are required for negapedia module posting.")

        # Check if the mode is 'summary' and warn if more than one page is provided
        if args.mode == 'summary':
            if len(args.pages) > 1:
                logging.warning(f"More than one URL provided for 'summary' mode. Only the first URL '{args.pages[0]}' will be used.")
                # Only use the first URL
                args.pages = [args.pages[0]]

        # Check if the mode is 'comparison' and validate the number of pages
        elif args.mode == 'comparison':
            if len(args.pages) != 2:
                raise ValueError("The 'comparison' mode requires exactly two URLs in the '--pages' argument.")

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
        web_urls = get_input_parameter_web_urls(urls, self.module, remove_suffix, base_directory, base_url)

        pages_info = self.extract_pages_info(web_urls, mode)
        # for page_info in pages_info:
        #     page_info['message']  # {{to_fix}} passiaggio parametro message da sistemare

        self.generate_posts(pages_info, post_type, mode, language)

    def extract_pages_info(self, urls: List[str], mode: str) -> List[NegapediaPageInfo]:
        # Initialize description with a default value
        description = None
        images = []

        if mode == 'summary':
            # As summary mode is meant to work only on one page, we take just the first URL passed
            description, images, negapedia_page_info = self.build_summary_mode_post_info(urls)
            negapedia_pages_info = [negapedia_page_info]
        elif mode == 'comparison':
            description, images, negapedia_pages_info = self.build_comparison_mode_post_info(urls)
        else:
            error_message = f"Unsupported mode '{mode}' provided. Accepted modes are 'summary' or 'comparison'."
            logging.error(error_message)
            raise ValueError(error_message)

        return negapedia_pages_info

    def build_summary_mode_post_info(self, urls: List[str]) -> (str, List[dict], NegapediaPageInfo):
        env_data = load_from_env()
        extract_original_charts_images = env_data.get('modules').get(f'{self.module}').get('extract_original_charts_images')

        # extract the only url to process
        url = urls[0]

        # Initialize variables
        images = []
        description = None
        negapedia_page_info = None

        if extract_original_charts_images:
            title = None
            historical_conflict_levels = []
            historical_polemic_levels = []
            recent_conflict_levels = []
            recent_polemic_levels = []
            words_that_matter = []
            conflict_awards = []
            polemic_awards = []
            social_jumps = []
            try:
                page_content = self.fetch_page_content(url)

                if not page_content:
                    logging.error(f"Failed to fetch page content for URL: {url}")
                    return description, images

                soup = BeautifulSoup(page_content, 'html.parser')

                title = self.extract_page_title(soup, url)
                self.extract_historical_conflict(soup, url, historical_conflict_levels)
                self.extract_historical_polemic(soup, url, historical_polemic_levels)
                self.extract_recent_conflict(soup, url, recent_conflict_levels)
                self.extract_recent_polemic(soup, url, recent_polemic_levels)
                self.extract_words_that_matter(soup, url, words_that_matter, 100)
                self.extract_conflict_awards(soup, url, conflict_awards, 100)
                self.extract_polemic_awards(soup, url, polemic_awards, 100)
                self.extract_social_jumps(soup, url, social_jumps, 100)

                description = self.build_description(recent_conflict_levels, recent_polemic_levels, words_that_matter, conflict_awards, polemic_awards, social_jumps)
                negapedia_page_info = {
                    'title': title,
                    'description': description,
                    'message': None,
                    'historical_conflict': historical_conflict_levels,
                    'historical_polemic': historical_polemic_levels,
                    'recent_conflict_levels': recent_conflict_levels,
                    'recent_polemic_levels': recent_polemic_levels,
                    'words_that_matter': words_that_matter,
                    'conflict_awards': conflict_awards,
                    'polemic_awards': polemic_awards,
                    'social_jumps': social_jumps
                }

            except Exception as e:
                logging.error(f"Failed to process dynamic data extraction for URL={url}: {e}")
                return description, images
        else:
            topics_data_array = dict()
            try:
                negapedia_string_data = self.get_negapedia_data_array(url)
                negapedia_data = self.convert_negaranks_to_dicts(negapedia_string_data)
                topics_data_array[url] = self.filter_useful_negaranks_data(negapedia_data)
            except Exception as e:
                print(f"Failed to process NEGARANKS data management for URL={url}: {e}")
                return description, images

            # Plotting the data
            categories = ["conflict", "polemic"]
            plots_paths = []
            for category in categories:
                self.plot_negaraks_data_copilot(category, [url], topics_data_array, plots_paths)

            for plot_path in plots_paths:
                image_info = {
                    'image': plot_path,
                    'image_width': None,
                    'image_height': None,
                    'image_alt': f"Plot for topic ... ",  # {{to_fix}}
                    'location': "local",
                }
                images.append(image_info)

        return description, images, negapedia_page_info

    def build_comparison_mode_post_info(self, urls: List[str]) -> (str, List[dict], List[NegapediaPageInfo]):
        env_data = load_from_env()
        extract_original_charts_images = env_data.get('modules').get(f'{self.module}').get('extract_original_charts_images')

        # Initialize variables
        images = []
        description = None
        description_parts = []  # List to accumulate descriptions
        negapedia_pages_info = []

        if extract_original_charts_images:
            for url in urls:
                title = None
                historical_conflict_levels = []
                historical_polemic_levels = []
                recent_conflict_levels = []
                recent_polemic_levels = []
                words_that_matter = []
                conflict_awards = []
                polemic_awards = []
                social_jumps = []
                try:
                    page_content = self.fetch_page_content(url)

                    if not page_content:
                        logging.error(f"Failed to fetch page content for URL: {url}")
                        continue

                    soup = BeautifulSoup(page_content, 'html.parser')

                    title = self.extract_page_title(soup, url)
                    self.extract_historical_conflict(soup, url, historical_conflict_levels)
                    self.extract_historical_polemic(soup, url, historical_polemic_levels)
                    self.extract_recent_conflict(soup, url, recent_conflict_levels)
                    self.extract_recent_polemic(soup, url, recent_polemic_levels)
                    self.extract_words_that_matter(soup, url, words_that_matter, 100)
                    self.extract_conflict_awards(soup, url, conflict_awards, 100)
                    self.extract_polemic_awards(soup, url, polemic_awards, 100)
                    self.extract_social_jumps(soup, url, social_jumps, 100)

                    # Build description for the current URL and add it to description_parts
                    url_description = self.build_description(recent_conflict_levels, recent_polemic_levels, words_that_matter, conflict_awards, polemic_awards, social_jumps)
                    description_parts.append(url_description)
                    negapedia_page_info = {
                        'title': title,
                        'description': description,
                        'message': None,
                        'historical_conflict': historical_conflict_levels,
                        'historical_polemic': historical_polemic_levels,
                        'recent_conflict_levels': recent_conflict_levels,
                        'recent_polemic_levels': recent_polemic_levels,
                        'words_that_matter': words_that_matter,
                        'conflict_awards': conflict_awards,
                        'polemic_awards': polemic_awards,
                        'social_jumps': social_jumps
                    }
                    negapedia_pages_info.append(negapedia_page_info)

                except Exception as e:
                    logging.error(f"Failed to process dynamic data extraction for URL={url}: {e}")
                    continue
        else:
            topics_data_array = dict()
            for url in urls:
                try:
                    negapedia_string_data = self.get_negapedia_data_array(url)
                    negapedia_data = self.convert_negaranks_to_dicts(negapedia_string_data)
                    topics_data_array[url] = self.filter_useful_negaranks_data(negapedia_data)
                except Exception as e:
                    print(f"Failed to process NEGARANKS data management for URL={url}: {e}")
                    continue

            # Plotting the data
            categories = ["conflict", "polemic"]
            plots_paths = []
            for category in categories:
                self.plot_negaraks_data_copilot(category, urls, topics_data_array, plots_paths)

            images = []
            for plot_path in plots_paths:
                image_info = {
                    'image': plot_path,
                    'image_width': None,
                    'image_height': None,
                    'image_alt': f"Plot for topic ... ",  # {{to_fix}}
                    'location': "local",
                }
                images.append(image_info)

        # Combine all parts into a single description
        if description_parts:
            description = "\n\n".join(description_parts)

        return description, images, negapedia_pages_info

    @staticmethod
    def extract_historical_conflict(soup, url: str, images: List[dict]) -> None:
        """
        Extracts historical conflict SVGs and appends them to the images list.
        """
        try:
            # Extract conflict diagram
            chart_time_conflict_image_path = NegapediaModule.extract_svg_from_div(soup, url, 'chart_time_conflict')
            if chart_time_conflict_image_path:
                images.append({
                    'image': chart_time_conflict_image_path,
                    'image_width': None,
                    'image_height': None,
                    'image_alt': f"Conflict diagram extracted from {url}",
                    'location': "local",
                })

        except Exception as e:
            logging.error(f"Error during historical conflict SVG extraction for URL={url}: {e}")

    @staticmethod
    def extract_page_title(soup, url: str) -> str:
        """
        Extracts the page title from a given BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML content of the page.
            url (str): The URL of the page.

        Returns:
            str: The extracted title of the page, or "No Title" if not found.
        """
        try:
            # Find the <h1> element that contains the title
            h1_element = soup.find('h1')
            if h1_element:
                # Find the first <span> element within the <h1> element
                title_element = h1_element.find('span')
                if title_element:
                    title = title_element.get_text(strip=True)
                    return title
                else:
                    logging.warning(f"No title found within <h1> for URL={url}")
            else:
                logging.warning(f"No <h1> element found for URL={url}")

        except Exception as e:
            logging.error(f"Error during page title extraction for URL={url}: {e}")

        return url

    @staticmethod
    def extract_historical_polemic(soup, url: str, images: List[dict]) -> None:
        """
        Extracts historical polemic SVGs and appends them to the images list.
        """
        try:
            # Extract polemic diagram
            chart_time_polemic_image_path = NegapediaModule.extract_svg_from_div(soup, url, 'chart_time_polemic')
            if chart_time_polemic_image_path:
                images.append({
                    'image': chart_time_polemic_image_path,
                    'image_width': None,
                    'image_height': None,
                    'image_alt': f"Polemic diagram extracted from {url}",
                    'location': "local",
                })

        except Exception as e:
            logging.error(f"Error during historical polemic SVG extraction for URL={url}: {e}")

    @staticmethod
    def extract_recent_conflict(soup, url: str, conflict_levels: List[dict]) -> None:
        """
        Extracts recent conflict level from the 'gauge_conflict_chart' div and appends it to the conflict_levels list.
        """
        try:
            # Locate the div containing the recent conflict data
            gauge_conflict_div = soup.find('div', id='gauge_conflict_chart')
            if gauge_conflict_div:
                # Find the nested <svg> element containing the conflict chart
                svg_element = gauge_conflict_div.find('svg')
                if svg_element:
                    # Find the first <g> element within the SVG
                    g_element = svg_element.find('g')
                    if g_element:
                        # Find the nested <g> element within the first <g> element
                        nested_g_element = g_element.find('g')
                        if nested_g_element:
                            # Extract the text element within the nested <g> element
                            text_element = nested_g_element.find('text')
                            if text_element:
                                conflict_value = text_element.get_text(strip=True)
                                conflict_levels.append({
                                    'url': url,
                                    'conflict_level': conflict_value
                                })
                                logging.info(f"Extracted recent conflict level: {conflict_value} from {url}")
                            else:
                                logging.warning(
                                    f"No <text> element found within nested <g> for recent conflict in URL={url}")
                        else:
                            logging.warning(f"No nested <g> element found in SVG for recent conflict in URL={url}")
                    else:
                        logging.warning(f"No <g> element found in SVG for recent conflict in URL={url}")
                else:
                    logging.warning(f"No SVG found within the div 'gauge_conflict_chart' for URL={url}")
            else:
                logging.warning(f"No div with id 'gauge_conflict_chart' found for URL={url}")
        except Exception as e:
            logging.error(f"Error during recent conflict extraction for URL={url}: {e}")

    @staticmethod
    def extract_recent_polemic(soup, url: str, polemic_levels: List[dict]) -> None:
        """
        Extracts recent polemic level from the 'gauge_polemic_chart' div and appends it to the polemic_levels list.
        """
        try:
            # Locate the div containing the recent polemic data
            gauge_polemic_div = soup.find('div', id='gauge_polemic_chart')
            if gauge_polemic_div:
                # Find the nested <svg> element containing the polemic chart
                svg_element = gauge_polemic_div.find('svg')
                if svg_element:
                    # Find the first <g> element within the SVG
                    g_element = svg_element.find('g')
                    if g_element:
                        # Find the nested <g> element within the first <g> element
                        nested_g_element = g_element.find('g')
                        if nested_g_element:
                            # Extract the text element within the nested <g> element
                            text_element = nested_g_element.find('text')
                            if text_element:
                                polemic_value = text_element.get_text(strip=True)
                                polemic_levels.append({
                                    'url': url,
                                    'polemic_level': polemic_value
                                })
                                logging.info(f"Extracted recent polemic level: {polemic_value} from {url}")
                            else:
                                logging.warning(
                                    f"No <text> element found within nested <g> for recent polemic in URL={url}")
                        else:
                            logging.warning(f"No nested <g> element found in SVG for recent polemic in URL={url}")
                    else:
                        logging.warning(f"No <g> element found in SVG for recent polemic in URL={url}")
                else:
                    logging.warning(f"No SVG found within the div 'gauge_polemic_chart' for URL={url}")
            else:
                logging.warning(f"No div with id 'gauge_polemic_chart' found for URL={url}")
        except Exception as e:
            logging.error(f"Error during recent polemic extraction for URL={url}: {e}")

    @staticmethod
    def extract_words_that_matter(soup, url: str, words_that_matter: List[dict], top_n: int) -> None:
        """
        Extracts the N most important words from the 'the_word_cloud' div and appends them to the important_words list.
        """
        try:
            # Locate the div containing the word cloud data
            word_cloud_div = soup.find('div', id='the_word_cloud')
            if word_cloud_div:
                # Find the nested <svg> element containing the word cloud
                svg_element = word_cloud_div.find('svg')
                if svg_element:
                    # Find all <text> elements within the SVG
                    text_elements = svg_element.find_all('text')

                    if text_elements:
                        # Extract the words from the text elements
                        words = [text_element.get_text(strip=True) for text_element in text_elements]

                        # Sort words by their font size (importance) if needed; here we take the first N words
                        words_that_matter.extend(words[:top_n])

                        logging.info(f"Extracted top {top_n} important words from {url}: {words_that_matter}")
                    else:
                        logging.warning(f"No <text> elements found in SVG for important words in URL={url}")
                else:
                    logging.warning(f"No SVG found within the div 'the_word_cloud' for URL={url}")
            else:
                logging.warning(f"No div with id 'the_word_cloud' found for URL={url}")
        except Exception as e:
            logging.error(f"Error during important words extraction for URL={url}: {e}")

    @staticmethod
    def extract_conflict_awards(soup, url: str, conflict_awards: List[dict], top_n: int) -> None:
        """
        Extracts the conflict awards from the 'infobox' div and appends them to the conflict_awards list.
        """
        try:
            # Locate the div containing the conflict awards data
            infobox_div = soup.find('div', class_='infobox', attrs={'data-type': 'conflict"'})  #{{to_check}} there's this " after conflict in the HTML, might be an error
            if infobox_div:
                # Find the div with the "GLOBAL" awards section
                global_awards_div = infobox_div.find('div', class_='box-awards')
                if global_awards_div:
                    # Extract awards under "GLOBAL (IN ALL WIKIPEDIA)"
                    award_headers = global_awards_div.find_all('strong')

                    if award_headers:
                        awards = []

                        # Extract the text from each award header element
                        for header in award_headers:
                            award_title = header.get_text(strip=True)
                            # Find all subsequent <img> elements and extract their 'title' attributes
                            year_parts = []
                            for sibling in header.find_next_siblings():
                                if sibling.name == 'img':
                                    img_title = sibling.get('title')
                                    if img_title and img_title.isdigit():  # Check if title is a year
                                        year_parts.append(img_title)
                                # Stop if a new <strong> or <hr> element is found (new award starts)
                                elif sibling.name == 'strong' or sibling.name == 'hr':
                                    break
                            # Append years to the award title if they exist
                            if year_parts:
                                award_title += f" ({', '.join(year_parts)})"
                            awards.append(award_title)

                        # Limit the extracted awards to the top N
                        conflict_awards.extend(awards[:top_n])

                        logging.info(f"Extracted top {top_n} conflict awards from {url}: {conflict_awards}")
                    else:
                        logging.warning(f"No <strong> elements found in 'GLOBAL' awards section for URL={url}")
                else:
                    logging.warning(f"No 'GLOBAL' awards section found in 'infobox' for URL={url}")
            else:
                logging.warning(f"No 'infobox' div with data-type 'conflict' found for URL={url}")
        except Exception as e:
            logging.error(f"Error during conflict awards extraction for URL={url}: {e}")

    @staticmethod
    def extract_polemic_awards(soup, url: str, polemic_awards: List[dict], top_n: int) -> None:
        """
        Extracts the polemic awards from the 'infobox' div and appends them to the polemic_awards list.
        """
        try:
            # Locate the div containing the polemic awards data
            infobox_div = soup.find('div', class_='infobox', attrs={'data-type': 'polemic"'})  #{{to_check}} there's this " after polemic in the HTML, might be an error
            if infobox_div:
                # Find the div with the "GLOBAL" awards section
                global_awards_div = infobox_div.find('div', class_='box-awards')
                if global_awards_div:
                    # Extract awards under "GLOBAL (IN ALL WIKIPEDIA)"
                    award_headers = global_awards_div.find_all('strong')

                    if award_headers:
                        awards = []

                        # Extract the text from each award header element
                        for header in award_headers:
                            award_title = header.get_text(strip=True)
                            # Find all subsequent <img> elements and extract their 'title' attributes
                            year_parts = []
                            for sibling in header.find_next_siblings():
                                if sibling.name == 'img':
                                    img_title = sibling.get('title')
                                    if img_title and img_title.isdigit():  # Check if title is a year
                                        year_parts.append(img_title)
                                # Stop if a new <strong> or <hr> element is found (new award starts)
                                elif sibling.name == 'strong' or sibling.name == 'hr':
                                    break
                            # Append years to the award title if they exist
                            if year_parts:
                                award_title += f" ({', '.join(year_parts)})"
                            awards.append(award_title)

                        # Limit the extracted awards to the top N
                        polemic_awards.extend(awards[:top_n])

                        logging.info(f"Extracted top {top_n} polemic awards from {url}: {polemic_awards}")
                    else:
                        logging.warning(f"No <strong> elements found in 'GLOBAL' awards section for URL={url}")
                else:
                    logging.warning(f"No 'GLOBAL' awards section found in 'infobox' for URL={url}")
            else:
                logging.warning(f"No 'infobox' div with data-type 'polemic' found for URL={url}")
        except Exception as e:
            logging.error(f"Error during polemic awards extraction for URL={url}: {e}")

    @staticmethod
    def extract_social_jumps(soup, url: str, social_jumps: List[dict], top_n: int) -> None:
        """
        Extracts the social jumps from the 'social-jumps' div and appends them to the social_jumps list.
        """
        try:
            env_data = load_from_env()
            base_url = env_data.get('modules').get(f'{NegapediaModule.module}').get('website_base_url')

            # Ensure the base_url is properly formatted
            if not base_url.endswith('/'):
                base_url += '/'

            # Locate the div containing the social jumps data
            social_jumps_div = soup.find('div', id='social-jumps')
            if social_jumps_div:
                # Find all the 'dt' elements which contain the social jump links
                social_jump_entries = social_jumps_div.find_all('dt')

                if social_jump_entries:
                    jumps = []

                    # Extract the title and link from each 'dt' element
                    for entry in social_jump_entries:
                        link_element = entry.find('a')
                        if link_element:
                            title = link_element.get_text(strip=True)
                            link = urljoin(base_url, link_element.get('href'))  # Use urljoin to handle URLs correctly
                            jumps.append({'title': title, 'link': link})

                    # Limit the extracted social jumps to the top N
                    social_jumps.extend(jumps[:top_n])

                    logging.info(f"Extracted top {top_n} social jumps from {url}: {social_jumps}")
                else:
                    logging.warning(f"No social jump entries found in 'social-jumps' section for URL={url}")
            else:
                logging.warning(f"No 'social-jumps' section found for URL={url}")
        except Exception as e:
            logging.error(f"Error during social jumps extraction for URL={url}: {e}")

    @staticmethod
    def build_description(
            recent_conflict_levels: List[dict],
            recent_polemic_levels: List[dict],
            words_that_matter: List[str],
            conflict_awards: List[str],
            polemic_awards: List[str],
            social_jumps: List[dict]
    ) -> str:
        # Initialize description string
        description = ""

        # Add a section for Recent Conflict Levels
        if recent_conflict_levels:
            description += "RECENT CONFLICT LEVELS:\n"
            for item in recent_conflict_levels:
                description += f" - Conflict Level at {item['url']}: {item['conflict_level']}\n"
            description += "\n"

        # Add a section for Recent Polemic Levels
        if recent_polemic_levels:
            description += "RECENT POLEMIC LEVELS:\n"
            for item in recent_polemic_levels:
                description += f" - Polemic Level at {item['url']}: {item['polemic_level']}\n"
            description += "\n"

        # Add a section for Important Words
        if words_that_matter:
            description += "IMPORTANT WORDS (TOP 100):\n"
            description += ", ".join(words_that_matter[:10]) + "...\n"  # Showing only top 10 for brevity
            description += "\n"

        # Add a section for Conflict Awards
        if conflict_awards:
            description += "CONFLICT AWARDS:\n"
            for award in conflict_awards:
                description += f" - {award}\n"
            description += "\n"

        # Add a section for Polemic Awards
        if polemic_awards:
            description += "POLEMIC AWARDS:\n"
            for award in polemic_awards:
                description += f" - {award}\n"
            description += "\n"

        # Add a section for Social Jumps
        if social_jumps:
            description += "SOCIAL JUMPS (TOP 100):\n"
            for jump in social_jumps[:10]:  # Showing only top 10 for brevity
                description += f" - {jump['title']}: {jump['link']}\n"
            description += "\n"

        return description

    @staticmethod
    def fetch_page_content(url: str) -> Optional[str]:
        """
        Uses Selenium to load the page fully, including dynamic content, and returns the page source.
        """
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        env_data = load_from_env()
        chromedriver_path = env_data['chromedriver_path']
        service = ChromeService(executable_path=chromedriver_path)  # Update with the path to your ChromeDriver

        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get(url)
            # Wait for both 'chart_time_conflict' and 'chart_time_polemic' divs to be present
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "chart_time_conflict")))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "chart_time_polemic")))

            # Allow an extra time for SVG rendering to be fully completed
            time.sleep(5)

            page_content = driver.page_source
            logging.info(f"Successfully fetched content from URL: {url}")
            return page_content

        except Exception as e:
            logging.error(f"Failed to fetch content from {url}: {e}")
            return None

        finally:
            driver.quit()

    @staticmethod
    def extract_svg_from_div(soup, url: str, div_name: str) -> Optional[str]:
        """
        Extracts an SVG from a specific div and converts it to PNG.
        """
        try:
            container_div = soup.find('div', id=div_name)
            if container_div:
                svg_element = container_div.find('svg')
                if svg_element:
                    svg_file_path = save_svg(svg_element, div_name)
                    png_file_path = convert_svg_to_png(svg_file_path)
                    logging.info(f"SVG extracted and converted to PNG: {png_file_path} from {url}")
                    return png_file_path
                else:
                    logging.warning(f"No SVG found within the div '{div_name}' for URL={url}")
            else:
                logging.warning(f"No div with id '{div_name}' found for URL={url}")
        except Exception as e:
            logging.error(f"Error during SVG extraction from div '{div_name}' for URL={url}: {e}")
        return None

    @staticmethod
    def get_negapedia_data_array(url):
        # Set up Selenium WebDriver
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        env_data = load_from_env()
        chromedriver_path = env_data['chromedriver_path']
        service = ChromeService(executable_path=chromedriver_path)  # Update with the path to your ChromeDriver

        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.get(url)

            # Wait for the dynamic content to load
            time.sleep(5)  # This can be adjusted based on your internet speed and the website's response time

            # Find the script containing NEGARANKS
            scripts = driver.find_elements(By.TAG_NAME, 'script')
            negaranks_script = None
            for script in scripts:
                if 'NEGARANKS' in script.get_attribute('innerHTML'):
                    negaranks_script = script.get_attribute('innerHTML')
                    break

            if not negaranks_script:
                raise Exception("NEGARANKS variable not found in script.")

            # Parse NEGARANKS value from script
            negaranks_start = negaranks_script.find('NEGARANKS')
            if negaranks_start != -1:
                negaranks_start += len('NEGARANKS')
                negaranks_end = negaranks_script.find(';', negaranks_start)
                if negaranks_end != -1:
                    negaranks_data = negaranks_script[negaranks_start:negaranks_end].strip().lstrip('=').strip()
                    return negaranks_data
                else:
                    raise Exception("Failed to parse NEGARANKS variable.")
            else:
                raise Exception("NEGARANKS variable not found in script.")

        except Exception as e:
            raise Exception(f"Failed to get Negapedia data array: {e}")

        finally:
            driver.quit()

    @staticmethod
    def convert_negaranks_to_dicts(negaranks_string):
        cleaned_negaranks_string = negaranks_string.strip().lstrip('[').rstrip(']').replace('\n', '').replace(' ', '').rstrip(',')
        negaranks_records = cleaned_negaranks_string.split('],')
        negaranks_list = []
        for negaranks_record in negaranks_records:
            negaranks_record = negaranks_record.lstrip('[')
            splitted_negaranks_record = negaranks_record.split(',')
            if splitted_negaranks_record[5] != '"all"':
                negaranks_dict = {
                    "rank": int(splitted_negaranks_record[0]),
                    "perc": int(splitted_negaranks_record[1]),
                    "dperc": int(splitted_negaranks_record[2]),
                    "type": str(splitted_negaranks_record[3]).replace("\"", ""),
                    "topic": str(splitted_negaranks_record[4]).replace("\"", ""),
                    "period": int(str(splitted_negaranks_record[5]).replace("\"", "")),
                    "measurement_value": float(str(splitted_negaranks_record[6]).replace("\"", "").replace("]", "").replace("[", ""))
                }
                negaranks_list.append(negaranks_dict)
        return negaranks_list

    @staticmethod
    def filter_useful_negaranks_data(negapedia_data):
        current_year = datetime.now().year
        return [entry for entry in negapedia_data if entry['topic'] == 'all' and entry['period'] != current_year]

    @staticmethod
    def extract_data(topics_data_array, category):
        data_to_plot = dict()
        for topic in topics_data_array:
            data_to_plot[topic] = dict()
            data_to_plot[topic]["years"] = [entry["period"] for entry in topics_data_array[topic] if
                                            entry['type'] == category]
            data_to_plot[topic]["values"] = [entry["measurement_value"] for entry in topics_data_array[topic] if
                                             entry['type'] == category]
        return data_to_plot

    @staticmethod
    def plot_negaraks_data_copilot(category, pages, topics_data_array, plots_path):
        # Extract data for plotting
        data_to_plot = NegapediaModule.extract_data(topics_data_array, category)

        # Define a color map for topics using seaborn color palette
        colors = sns.color_palette("husl", len(data_to_plot))
        topic_colors = {topic: colors[i] for i, topic in enumerate(data_to_plot)}

        # Create line plots
        plt.figure(figsize=(14, 8), dpi=100)

        for topic in data_to_plot:
            years_to_plot = data_to_plot[topic]["years"]
            values_to_plot = data_to_plot[topic]["values"]
            plot_label = topic
            plot_color = topic_colors[topic]
            plt.plot(years_to_plot, values_to_plot, label=plot_label, color=plot_color, marker="o", linestyle='-')

        # Add labels and title
        plt.xlabel("Year", fontsize=14)
        y_label = category + " level"
        plt.ylabel(y_label, fontsize=14)

        # Construct the title
        if len(pages) == 1:
            topics_str = pages[0]
        elif len(pages) == 2:
            topics_str = " and ".join(pages)
        else:
            topics_str = ", ".join(pages[:-1]) + ", and " + pages[-1]

        title_plot = "Comparison of " + category + " level between topics "
        plt.title(title_plot, fontsize=16)
        plt.legend(fontsize=12)

        # Adjust x-axis and y-axis ticks
        plt.grid(True, linestyle='--', linewidth=0.5)
        max_x = max(max(data_to_plot[topic]["years"]) for topic in data_to_plot)
        min_x = min(min(data_to_plot[topic]["years"]) for topic in data_to_plot)
        max_y = max(max(data_to_plot[topic]["values"]) for topic in data_to_plot)
        min_y = min(min(data_to_plot[topic]["values"]) for topic in data_to_plot)

        x_tick_step = 1
        y_tick_step = round(max_y / 10)

        plt.xticks(range(min_x - 1, max_x + 1, x_tick_step), fontsize=12)
        plt.yticks(range(0, int(max_y) + 1, y_tick_step), fontsize=12)

        # Save the plot as a PNG file
        timestamp = datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")
        output_filename = title_plot.replace(" ", "_").replace(",", "") + "_" + timestamp + ".png"
        output_path = os.path.join('images_to_post', output_filename)
        plt.tight_layout()
        plt.savefig(output_path)

        plots_path.append("images_to_post/" + output_filename)

        # Show the plot
        # plt.show()
        return None
