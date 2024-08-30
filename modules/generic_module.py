from .base_module import BaseModule
from schemas.pageinfo import PageInfo
from typing import Any, List, Optional
from utils.input_validation_management import get_input_parameter_web_urls
from bs4 import BeautifulSoup
from datetime import datetime


class GenericModule(BaseModule):
    module = 'generic'

    def handle_module(self, args: Any) -> None:
        if not args.pages or not args.post_type or not args.mode or not args.language:
            raise ValueError("Pages, Post Type, Mode and Language are required for generic module posting.")
        print(f"Handling generic module for Pages {args.pages}")
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

        minimum_date = datetime.strptime(minimum_article_modified_date, '%Y-%m-%d') if minimum_article_modified_date else None

        page_info = self.extract_pages_info(web_urls, mode)
        page_info['message'] = message

        if minimum_date:
            article_modified_time_str = page_info.get('article_modified_time', None)
            if article_modified_time_str:
                try:
                    article_modified_time = datetime.strptime(article_modified_time_str, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None)
                except ValueError:
                    article_modified_time = datetime.strptime(article_modified_time_str, '%Y-%m-%dT%H:%M:%S')

                if minimum_date and article_modified_time < minimum_date:
                    raise ValueError(f"URL: {web_urls[0]} - Article modified date is too old.")
            else:
                raise ValueError(f"URL: {web_urls[0]} - Article modified date is not filled.")

        self.generate_posts(page_info, post_type, mode, language)

    def extract_pages_info(self, urls: List[str], mode: str) -> PageInfo:
        # as generic module is thinked to be working only on one page, we take just the first url passed
        url = urls[0]

        page_content = self.fetch_page_content(url)

        if not page_content:
            return {
                'title': None,
                'description': None,
                'message': None,
                'images': [],
                'audio': None,
                'video': None,
                'urls': [],
                'updated_time': None,
                'article_published_time': None,
                'article_modified_time': None,
                'article_tag': None,
                'keywords': None,
            }

        soup = BeautifulSoup(page_content, 'html.parser')

        def get_meta_content(name):
            tag = soup.find('meta', attrs={'name': name})
            return tag.get('content', None) if tag else None

        info = {
            'title': (soup.find('meta', property='og:title').get('content', None)
                      if soup.find('meta', property='og:title')
                      else (soup.title.string if soup.title else "No Title")),  # {{to_check}} what to put if title can not be retrieved
            'description': (soup.find('meta', property='og:description')['content']
                            if soup.find('meta', property='og:description')
                            else get_meta_content('description')),
            'message': None,
            'images': [{
                'image': soup.find('meta', property='og:image')['content']
                if soup.find('meta', property='og:image') else None,
                'image_width': soup.find('meta', property='og:image:width').get('content', None)
                if soup.find('meta', property='og:image:width') else None,
                'image_height': soup.find('meta', property='og:image:height').get('content', None)
                if soup.find('meta', property='og:image:height') else None,
                'image_alt': soup.find('meta', property='og:image:alt').get('content', None)
                if soup.find('meta', property='og:image:alt') else None,
                'location': "web",
            }],
            'audio': soup.find('meta', property='og:audio').get('content', None)
            if soup.find('meta', property='og:audio') else None,
            'video': soup.find('meta', property='og:video').get('content', None)
            if soup.find('meta', property='og:video') else None,
            'urls': [(soup.find('meta', property='og:url').get('content', None)
                      if soup.find('meta', property='og:url')
                      else url)],
            'updated_time': soup.find('meta', property='og:updated_time').get('content', None)
            if soup.find('meta', property='og:updated_time') else None,
            'article_published_time': soup.find('meta', property='article:published_time').get('content', None)
            if soup.find('meta', property='article:published_time') else None,
            'article_modified_time': soup.find('meta', property='article:modified_time').get('content', None)
            if soup.find('meta', property='article:modified_time') else None,
            'article_tag': soup.find('meta', property='article:tag').get('content', None)
            if soup.find('meta', property='article:tag') else None,
            'keywords': get_meta_content('Keywords'),
        }

        return info
