from abc import ABC, abstractmethod
from typing import Any, List, Optional
from schemas.pageinfo import PageInfo
from schemas.negapedia_pageinfo import NegapediaPageInfo
from connectors.facebook_connector import post_on_facebook
from connectors.twitter_connector import post_on_twitter
from connectors.web_connector import post_on_web
import requests


class BaseModule(ABC):
    module = None

    @abstractmethod
    def handle_module(self, args: Any) -> None:
        """
        Handle the main logic for the module, based on the input arguments.
        This method must be implemented by any subclass.
        """
        pass

    @abstractmethod
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
            mode (str): The mode to analise topics.
            language (str): The language in which to generate the posts.
            remove_suffix (Optional[bool]): Flag indicating whether to remove .html or .htm suffixes from URLs.
            base_directory (Optional[str]): The base directory in the filesystem for local processing.
            base_url (Optional[str]): The base URL for mapping local files to web URLs.
            minimum_article_modified_date (Optional[str]): The minimum article modified date for filtering pages (YYYY-MM-DD).
            message (Optional[str]): A custom message to be used in the post, if provided.
        """
        pass

    @abstractmethod
    def extract_pages_info(self, urls: List[str], mode: str) -> PageInfo | List[NegapediaPageInfo]:
        """
        Extracts relevant information from a web page's content.

        Args:
            urls (List[str]): The list of URLs being processed.
            mode (str): The mode to analise topics.

        Returns:
            PageInfo | List[NegapediaPageInfo]: A dictionary containing extracted information like title, description, images, etc.
        """
        pass

    @staticmethod
    def fetch_page_content(url: str) -> Optional[str]:
        """
        Fetches the HTML content of the given web page.

        Args:
            url (str): The URL of the web page to fetch.

        Returns:
            Optional[str]: The HTML content of the page if successfully fetched, otherwise None.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Failed to fetch the page content from {url}: {e}")
            return None

    def generate_posts(self, post_info: PageInfo | List[NegapediaPageInfo], post_type: List[str], mode: str, language: str) -> None:
        """
        Generates posts on different platforms based on the extracted information.

        Args:
            post_info (PageInfo | List[NegapediaPageInfo]): The extracted page information to be posted.
            post_type (List[str]): The types of posts to be created (e.g., 'facebook', 'twitter', 'web').
            mode (str): The mode to analise topics which will governate the template to use in the different channels.
            language (str): The language in which to generate the posts.
        """
        for channel in post_type:
            if channel == 'facebook':
                # if not check_access_token():  # {{to_check}} if needed or not, it was only on negapedia module
                #     start_flask_app()
                #     input("Press Enter after completing authentication in the browser...")
                post_on_facebook(post_info, language)
            elif channel == 'twitter':
                post_on_twitter(post_info, language)
            elif channel == 'web':
                post_on_web(post_info, mode, language, self.module)
            else:
                print(f"Post type '{channel}' is not supported.")
