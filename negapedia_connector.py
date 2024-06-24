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
