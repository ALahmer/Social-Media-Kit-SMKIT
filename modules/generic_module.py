from connectors.facebook_connector import post_on_facebook
from connectors.twitter_connector import post_on_twitter
from connectors.web_connector import post_on_web
import requests
from bs4 import BeautifulSoup


def handle_generic_module(args):
    if not args.urls or not args.post_type or not args.mode:
        print("Url, Date, Language and Post Type are required for generic module posting.")
        return
    else:
        print(f"Handling generic module for URLs {args.urls}")
        generate_generic_post(args.urls, args.post_type)


def generate_generic_post(urls, post_type):
    for url in urls:
        print(f"Processing URL: {url}")
        page_content = fetch_page_content(url)
        extracted_info = extract_page_info(page_content)

        message = extracted_info.get('description') if extracted_info.get('description') else f"Check out this topic at {url}"
        title = extracted_info.get('title') if extracted_info.get('title') else f"Check out this topic at {url}"
        print(f"Posting on {post_type} about with message: {message}")

        images_urls = []
        image = {
            'location': "web",
            'src': extracted_info.get('image')
        }
        images_urls.append(image)

        for posting_channel in post_type:
            if posting_channel == 'facebook':
                post_on_facebook(message, images_urls)
            elif posting_channel == 'twitter':
                post_on_twitter(message, images_urls)
            elif posting_channel == 'web':
                post_on_web(title, message, images_urls, 'summary')


def fetch_page_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch the page content from {url}")
        return None


def extract_page_info(content):
    if not content:
        return {}

    soup = BeautifulSoup(content, 'html.parser')
    info = {
        'title': soup.find('meta', property='og:title')['content'] if soup.find('meta', property='og:title') else (soup.title.string if soup.title else "No Title"),
        'description': soup.find('meta', property='og:description')['content'] if soup.find('meta', property='og:description') else (soup.find('meta', name='description')['content'] if soup.find('meta', name='description') else "No Description"),
        'image': soup.find('meta', property='og:image')['content'] if soup.find('meta', property='og:image') else None,
        'url': soup.find('meta', property='og:url')['content'] if soup.find('meta', property='og:url') else None,
    }

    return info
