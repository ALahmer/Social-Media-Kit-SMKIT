from connectors.facebook_connector import post_on_facebook
from connectors.twitter_connector import post_on_twitter
from connectors.web_connector import post_on_web
from utils.input_validation_management import get_input_parameter_web_urls
import requests
from bs4 import BeautifulSoup


def handle_generic_module(args):
    if not args.pages or not args.post_type or not args.mode:
        print("Pages, Post Type and Mode are required for generic module posting.")
        return
    else:
        web_urls = get_input_parameter_web_urls(args.pages, 'generic', args.remove_suffix, args.base_directory, args.base_url)
        print(f"Handling generic module for Pages {args.pages}")
        generate_generic_post(web_urls, args.post_type)


def generate_generic_post(pages, post_type):
    for url in pages:
        print(f"Processing URL: {url}")
        page_content = fetch_page_content(url)
        post_info = extract_page_info(page_content, url)

        for posting_channel in post_type:
            if posting_channel == 'facebook':
                post_on_facebook(post_info)
            elif posting_channel == 'twitter':
                post_on_twitter(post_info)
            elif posting_channel == 'web':
                post_on_web(post_info, 'summary')


def fetch_page_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch the page content from {url}")
        return None


def extract_page_info(content, input_url=None):
    if not content:
        return {}

    soup = BeautifulSoup(content, 'html.parser')

    def get_meta_content(name):
        tag = soup.find('meta', attrs={'name': name})
        if tag:
            return tag.get('content', None)
        return None

    info = {
        'title': (soup.find('meta', property='og:title')['content']
                  if soup.find('meta', property='og:title')
                  else (soup.title.string if soup.title else "No Title")),
        'description': (soup.find('meta', property='og:description')['content']
                        if soup.find('meta', property='og:description')
                        else get_meta_content('description')),
        'images': [{
            'image': soup.find('meta', property='og:image')['content']
                    if soup.find('meta', property='og:image') else None,
            'image_width': soup.find('meta', property='og:image:width')['content']
                        if soup.find('meta', property='og:image:width') else None,
            'image_height': soup.find('meta', property='og:image:height')['content']
                            if soup.find('meta', property='og:image:height') else None,
            'image_alt': soup.find('meta', property='og:image:alt')['content']
                        if soup.find('meta', property='og:image:alt') else None,
            'location': "web",
        }],
        'audio': soup.find('meta', property='og:audio')['content']
                 if soup.find('meta', property='og:audio') else None,
        'video': soup.find('meta', property='og:video')['content']
                 if soup.find('meta', property='og:video') else None,
        'urls': [(soup.find('meta', property='og:url')['content']
                if soup.find('meta', property='og:url')
                else input_url)],
        'updated_time': soup.find('meta', property='og:updated_time')['content']
                        if soup.find('meta', property='og:updated_time') else None,
        'article_published_time': soup.find('meta', property='article:published_time')['content']
                                  if soup.find('meta', property='article:published_time') else None,
        'article_modified_time': soup.find('meta', property='article:modified_time')['content']
                                 if soup.find('meta', property='article:modified_time') else None,
        'article_tag': soup.find('meta', property='article:tag')['content']
                       if soup.find('meta', property='article:tag') else None,
        'keywords': get_meta_content('Keywords'),
    }

    return info
