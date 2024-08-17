from connectors.facebook_connector import check_access_token, post_on_facebook
from connectors.twitter_connector import post_on_twitter
from connectors.web_connector import post_on_web
from utils.app_management import start_flask_app
from utils.input_validation_management import get_input_parameter_web_urls
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from utils.env_management import load_from_env
import matplotlib
from datetime import datetime


matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os
import seaborn as sns


def handle_negapedia_module(args):
    if not args.pages or not args.post_type or not args.mode:
        print("Pages, Post Type and Mode are required for negapedia module posting.")
        return
    else:
        web_urls = get_input_parameter_web_urls(args.pages)
        if args.mode == "comparison":
            print(f"Handling Negapedia module for Pages {web_urls} and mode {args.mode}")
            generate_comparison_negapedia_post(web_urls, args.post_type, args.mode)
        elif args.mode == "summary":
            print(f"Handling Negapedia module for Pages {web_urls} and mode {args.mode}")
            generate_summary_negapedia_post(web_urls, args.post_type, args.mode)


def generate_comparison_negapedia_post(pages, post_type, mode):
    # Implement the logic to generate and post content specific to Negapedia
    print(f"Generating Negapedia comparison post for Pages: {pages}, post_type: {post_type}, mode: {mode}")

    topics_data_array = dict()
    for topic_url in pages:
        try:
            negapedia_string_data = get_negapedia_data_array(topic_url)
            negapedia_data = convert_negaranks_to_dicts(negapedia_string_data)
            topics_data_array[topic_url] = filter_useful_negaranks_data(negapedia_data)
        except Exception as e:
            print(f"Failed to process NEGARANKS data management for URL={topic_url}: {e}")
            continue

    # Plotting the data
    categories = ["conflict", "polemic"]
    plots_paths = []
    for category in categories:
        plot_negaraks_data_copilot(category, pages, topics_data_array, plots_paths)

    # Prepare post
    if len(pages) == 1:
        topics_str = pages[0]
    elif len(pages) == 2:
        topics_str = " and ".join(pages)
    else:
        topics_str = ", ".join(pages[:-1]) + ", and " + pages[-1]
    message = f"Comparison of conflict and polemic levels between topics {topics_str}"
    title = message

    for posting_channel in post_type:
        if posting_channel == 'facebook':
            if not check_access_token():
                start_flask_app()
                input("Press Enter after completing authentication in the browser...")
            post_on_facebook(message, plots_paths)
        elif posting_channel == 'twitter':
            post_on_twitter(message, plots_paths)
        elif posting_channel == 'web':
            post_on_web(title, message, plots_paths, 'comparison')


def generate_summary_negapedia_post(pages, post_type, mode):
    print(f"Generating Negapedia summary post for Pages: {pages}, post_type: {post_type}, mode: {mode}")

    topics_data_array = dict()
    for topic_url in pages:
        try:
            negapedia_string_data = get_negapedia_data_array(topic_url)
            negapedia_data = convert_negaranks_to_dicts(negapedia_string_data)
            topics_data_array[topic_url] = filter_useful_negaranks_data(negapedia_data)
        except Exception as e:
            print(f"Failed to process NEGARANKS data management for URL={topic_url}: {e}")
            continue

    # Plotting the data
    categories = ["conflict", "polemic"]
    plots_paths = []
    for category in categories:
        plot_negaraks_data_copilot(category, pages, topics_data_array, plots_paths)

    # Prepare post
    if len(pages) == 1:
        topics_str = pages[0]
    elif len(pages) == 2:
        topics_str = " and ".join(pages)
    else:
        topics_str = ", ".join(pages[:-1]) + ", and " + pages[-1]
    message = f"Conflict and polemic levels for topic {topics_str}"
    title = message

    for posting_channel in post_type:
        if posting_channel == 'facebook':
            if not check_access_token():
                start_flask_app()
                input("Press Enter after completing authentication in the browser...")
            post_on_facebook(message, plots_paths)
        elif posting_channel == 'twitter':
            post_on_twitter(message, plots_paths)
        elif posting_channel == 'web':
            post_on_web(title, message, plots_paths, 'summary')


def get_negapedia_url(topic):
    base_url = "http://it.negapedia.org"
    search_url = f"{base_url}/search/?&o=0&c=&q={topic.replace(' ', '%20')}"

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
        driver.get(search_url)

        # Wait for the dynamic content to load
        time.sleep(5)  # This can be adjusted based on your internet speed and the website's response time

        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Navigate through the HTML structure
        content_div = soup.find('div', id='content')
        if not content_div:
            raise Exception("Failed to find the content div in the search results.")

        results_div = content_div.find('div', id='results')
        if not results_div:
            raise Exception("Failed to find the results div in the search results.")

        list_entries_dl = results_div.find('dl', class_='list-entries')
        if not list_entries_dl:
            raise Exception("Failed to find the list-entries dl in the search results.")

        first_result_dt = list_entries_dl.find('dt')
        if not first_result_dt:
            raise Exception("Failed to find the first result dt in the search results.")

        first_result_a = first_result_dt.find('a')
        if not first_result_a or 'href' not in first_result_a.attrs:
            raise Exception("Failed to find the result link in the search results.")

        relative_url = first_result_a['href']
        full_url = f"{base_url}{relative_url[2:]}"  # Remove the first two characters `..` from relative URL
        return full_url

    except Exception as e:
        raise Exception(f"Failed to get Negapedia URL: {e}")

    finally:
        driver.quit()


def get_negapedia_data_array(topic_url):
    base_url = "http://it.negapedia.org"

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
        driver.get(topic_url)

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


def filter_useful_negaranks_data(negapedia_data):
    current_year = datetime.now().year
    return [entry for entry in negapedia_data if entry['topic'] == 'all' and entry['period'] != current_year]


def extract_data(topics_data_array, category):
    data_to_plot = dict()
    for topic in topics_data_array:
        data_to_plot[topic] = dict()
        data_to_plot[topic]["years"] = [entry["period"] for entry in topics_data_array[topic] if
                                        entry['type'] != category]
        data_to_plot[topic]["values"] = [entry["measurement_value"] for entry in topics_data_array[topic] if
                                         entry['type'] != category]
    return data_to_plot


def plot_negaraks_data_copilot(category, pages, topics_data_array, plots_path):
    # Extract data for plotting
    data_to_plot = extract_data(topics_data_array, category)

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

    image = {
        'location': "local",
        'src': "images_to_post/" + output_filename
    }
    plots_path.append(image)

    # Show the plot
    # plt.show()
    return None
