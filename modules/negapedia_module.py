from .base_module import BaseModule
from schemas.pageinfo import PageInfo
from typing import Any, List, Optional
from utils.input_validation_management import get_input_parameter_web_urls
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from utils.env_management import load_from_env
import matplotlib
from datetime import datetime


matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os
import seaborn as sns


class NegapediaModule(BaseModule):
    module = 'negapedia'

    def handle_module(self, args: Any) -> None:
        if not args.pages or not args.post_type or not args.mode or not args.language:
            raise ValueError("Pages, Post Type, Mode and Language are required for negapedia module posting.")
        print(f"Handling negapedia module for Pages {args.pages}")
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

        page_info = self.extract_pages_info(web_urls)
        page_info['message'] = message

        self.generate_posts(page_info, post_type, mode, language)

    def extract_pages_info(self, urls: List[str]) -> PageInfo:
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

        # Prepare post
        if len(urls) == 1:
            topics_str = urls[0]
        elif len(urls) == 2:
            topics_str = " and ".join(urls)
        else:
            topics_str = ", ".join(urls[:-1]) + ", and " + urls[-1]

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

        info = {
            'title': "Conflict and polemic levels",
            'description': f"Topic: {topics_str}",
            'message': None,
            'images': images,
            'audio': None,
            'video': None,
            'urls': urls,
            'updated_time': None,
            'article_published_time': None,
            'article_modified_time': None,
            'article_tag': None,
            'keywords': None,
        }

        return info

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
                                            entry['type'] != category]
            data_to_plot[topic]["values"] = [entry["measurement_value"] for entry in topics_data_array[topic] if
                                             entry['type'] != category]
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
