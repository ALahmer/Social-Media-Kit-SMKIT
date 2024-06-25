import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from env_management import load_from_env


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
        negaranks_dict = {
            "value1": splitted_negaranks_record[0],
            "value2": splitted_negaranks_record[1],
            "value3": splitted_negaranks_record[2],
            "category": splitted_negaranks_record[3],
            "type1": splitted_negaranks_record[4],
            "year": splitted_negaranks_record[5],
            "value4": splitted_negaranks_record[6]
        }
        negaranks_list.append(negaranks_dict)
    return negaranks_list
