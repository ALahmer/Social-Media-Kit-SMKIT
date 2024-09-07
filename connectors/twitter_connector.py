import tweepy
from utils.env_management import load_from_env
from utils.images_management import fetch_image_as_stream
from utils.translations_management import get_translation
import re
import logging


class TwitterConnector:
    def __init__(self, post_info, template, module, posting_settings):
        self.post_info = post_info
        self.template = template
        self.module = module
        self.posting_settings = posting_settings
        self.env_data = load_from_env()
        self.language = posting_settings['language']

    def post_on_twitter(self):
        if not self.env_data or not all(k in self.env_data for k in ('twitter_api_key', 'twitter_api_secret_key', 'twitter_access_token', 'twitter_access_token_secret')):
            logging.error("Twitter credentials not found. Please add them to env.json.")
            return

        auth = tweepy.OAuth1UserHandler(
            self.env_data['twitter_api_key'],
            self.env_data['twitter_api_secret_key'],
            self.env_data['twitter_access_token'],
            self.env_data['twitter_access_token_secret']
        )
        api = tweepy.API(auth)

        client = tweepy.Client(
            consumer_key=self.env_data['twitter_api_key'],
            consumer_secret=self.env_data['twitter_api_secret_key'],
            access_token=self.env_data['twitter_access_token'],
            access_token_secret=self.env_data['twitter_access_token_secret']
        )

        # Load the template
        template_content = self.load_template()
        if not template_content:
            logging.error("Template could not be loaded.")
            return

        images = []
        # Fill the template based on the type of post_info
        filled_content = template_content

        if self.module == 'negapedia':

            if self.template == 'summary':
                filled_content = self.convert_negapediapageinfo_to_summary_filled_content(filled_content)
                images = (self.post_info[0].get('historical_conflict', []) or []) + (self.post_info[0].get('historical_polemic', []) or [])
            elif self.template == 'comparison':
                filled_content = self.convert_negapediapageinfo_to_comparison_filled_content(filled_content)
                images = (self.post_info[0].get('historical_conflict_comparison', []) or []) + (self.post_info[0].get('historical_polemic_comparison', []) or [])
            elif self.template == 'ranking':
                filled_content = self.convert_negapediapageinfo_to_ranking_filled_content(filled_content)
                images = (self.post_info[0].get('historical_conflict_comparison', []) or []) + (self.post_info[0].get('historical_polemic_comparison', []) or [])
        else:
            filled_content = self.convert_pageinfo_to_filled_content(filled_content)
            images = self.post_info.get('images', []) or []

        # Post the message to your page
        self.post_to_twitter(api, client, filled_content, images)

    @staticmethod
    def post_to_twitter(api, client, message, images):
        if images:
            media_ids = []
            for image_info in images:
                try:
                    media = None
                    src = image_info.get('image')
                    width = image_info.get('image_width')
                    height = image_info.get('image_height')
                    alt = image_info.get('image_alt') or "Image"
                    location = image_info.get('location')

                    if location == "web":
                        image_stream = fetch_image_as_stream(src)   # {{to_test}}
                        if image_stream:
                            media = api.media_upload(filename="image.jpg", file=image_stream)
                    else:
                        media = api.media_upload(src)
                    if media:
                        media_ids.append(media.media_id_string)
                except tweepy.TweepyException as e:
                    logging.error(f"An error occurred while uploading image {image_info}: {e}")

            if media_ids:
                try:
                    client.create_tweet(text=message, media_ids=media_ids)
                    logging.info("Successfully posted the tweet with image.")
                except tweepy.TweepyException as e:
                    logging.error(f"An error occurred while creating the tweet: {e}")
            else:
                logging.error("No images were uploaded. Post was not created.")
        else:
            try:
                client.create_tweet(text=message)
                logging.info("Successfully posted the tweet.")
            except tweepy.TweepyException as e:
                logging.error(f"An error occurred: {e}")

    def load_template(self):
        """
        Loads the Facebook post template content.
        """
        try:
            file_path = f'templates/{self.language}/{self.module}/twitter_post_{self.template}_template.txt'
            with open(file_path, 'r', encoding='utf-8') as template_file:
                return template_file.read()
        except FileNotFoundError:
            logging.error(f"Template file {file_path} not found.")
            return None

    def convert_pageinfo_to_filled_content(self, filled_content):
        filled_content = self.replace_title(filled_content, self.post_info, '{{title}}')
        filled_content = self.replace_description(filled_content, self.post_info, '{{description}}')
        filled_content = self.replace_images_alt(
            filled_content,
            (self.post_info.get('images', []) or []),
            '{{images_alt}}'
        )
        filled_content = self.replace_optional_fields(filled_content, self.post_info)
        filled_content = self.replace_urls(filled_content, self.post_info)
        return filled_content

    def convert_negapediapageinfo_to_summary_filled_content(self, filled_content):
        filled_content = self.replace_negapedia_template_title(filled_content, '{{title}}')
        filled_content = self.replace_description(filled_content, self.post_info[0], '{{description}}')
        filled_content = self.replace_recent_conflict_levels(filled_content, self.post_info[0], '{{recent_conflict_levels}}')
        filled_content = self.replace_recent_polemic_levels(filled_content, self.post_info[0], '{{recent_polemic_levels}}')
        filled_content = self.replace_important_words(filled_content, self.post_info[0], '{{important_words}}')
        filled_content = self.replace_conflict_awards(filled_content, self.post_info[0], '{{conflict_awards}}')
        filled_content = self.replace_polemic_awards(filled_content, self.post_info[0], '{{polemic_awards}}')
        filled_content = self.replace_social_jumps(filled_content, self.post_info[0], '{{social_jumps}}')
        filled_content = self.replace_images_alt(
            filled_content,
            (self.post_info[0].get('historical_conflict', []) or []) + (self.post_info[0].get('historical_polemic', []) or []),
            '{{images_alt}}'
        )
        return filled_content

    def convert_negapediapageinfo_to_comparison_filled_content(self, filled_content):
        # Replace the titles
        filled_content = self.replace_negapedia_template_title(filled_content, '{{title}}')
        filled_content = self.replace_topics_titles(filled_content, self.post_info[0], '{{topic1_title}}')
        filled_content = self.replace_topics_titles(filled_content, self.post_info[1], '{{topic2_title}}')

        # Replace descriptions for both topics
        filled_content = self.replace_description(filled_content, self.post_info[0], '{{description_topic1}}')
        filled_content = self.replace_description(filled_content, self.post_info[1], '{{description_topic2}}')

        # Replace recent conflict and polemic levels for both topics
        filled_content = self.replace_recent_conflict_levels(filled_content, self.post_info[0], '{{recent_conflict_levels_topic1}}')
        filled_content = self.replace_recent_conflict_levels(filled_content, self.post_info[1], '{{recent_conflict_levels_topic2}}')
        filled_content = self.replace_recent_polemic_levels(filled_content, self.post_info[0], '{{recent_polemic_levels_topic1}}')
        filled_content = self.replace_recent_polemic_levels(filled_content, self.post_info[1], '{{recent_polemic_levels_topic2}}')

        # Replace important words for both topics
        filled_content = self.replace_important_words(filled_content, self.post_info[0], '{{important_words_topic1}}')
        filled_content = self.replace_important_words(filled_content, self.post_info[1], '{{important_words_topic2}}')

        # Replace conflict and polemic awards for both topics
        filled_content = self.replace_conflict_awards(filled_content, self.post_info[0], '{{conflict_awards_topic1}}')
        filled_content = self.replace_conflict_awards(filled_content, self.post_info[1], '{{conflict_awards_topic2}}')
        filled_content = self.replace_polemic_awards(filled_content, self.post_info[0], '{{polemic_awards_topic1}}')
        filled_content = self.replace_polemic_awards(filled_content, self.post_info[1], '{{polemic_awards_topic2}}')

        # Replace social jumps for both topics
        filled_content = self.replace_social_jumps(filled_content, self.post_info[0], '{{social_jumps_topic1}}')
        filled_content = self.replace_social_jumps(filled_content, self.post_info[1], '{{social_jumps_topic2}}')

        # Replace images alt for both topics
        filled_content = self.replace_images_alt(
            filled_content,
            (self.post_info[0].get('historical_conflict_comparison', []) or []) +
            (self.post_info[0].get('historical_polemic_comparison', []) or []),
            '{{images_alt}}'
        )

        return filled_content

    def convert_negapediapageinfo_to_ranking_filled_content(self, filled_content):
        filled_content = self.replace_negapedia_template_title(filled_content, '{{title}}')
        filled_content = self.replace_description(filled_content, self.post_info[0], '{{description}}')
        filled_content = self.replace_ranking_field(filled_content, '{{ranking_field}}')
        filled_content = self.replace_recent_conflict_levels_ranking(filled_content, '{{recent_conflict_levels_ranking}}')
        filled_content = self.replace_recent_polemic_levels_ranking(filled_content, '{{recent_polemic_levels_ranking}}')
        filled_content = self.replace_mean_conflict_level_ranking(filled_content, '{{mean_conflict_level_ranking}}')
        filled_content = self.replace_mean_polemic_level_ranking(filled_content, '{{mean_polemic_level_ranking}}')

        # Replace images alt for both topics
        filled_content = self.replace_images_alt(
            filled_content,
            (self.post_info[0].get('historical_conflict_comparison', []) or []) + (self.post_info[0].get('historical_polemic_comparison', []) or []),
            '{{images_alt}}'
        )

        return filled_content

    @staticmethod
    def replace_title(filled_content, post_info, template_variable_to_fill):
        title = post_info.get('title') or (post_info.get('urls', [None])[0]) or None

        if title:
            return filled_content.replace(template_variable_to_fill, str(title))
        else:
            # Remove the line if there is no title
            return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)

    def replace_negapedia_template_title(self, filled_content, template_variable_to_fill):
        if self.template == 'summary':
            summary_for_negapedia_page = get_translation("summary_for_negapedia_page", self.language, title=self.post_info[0].get('title', 'Topic 1'))
            title = f"\n{summary_for_negapedia_page}"
        elif self.template == 'comparison':
            comparison_between_negapedia_pages = get_translation("comparison_between_negapedia_pages", self.language, title1=self.post_info[0].get('title', 'Topic 1'), title2=self.post_info[1].get('title', 'Topic 2'))
            title = f"\n{comparison_between_negapedia_pages}"
        elif self.template == 'ranking':
            ranking_comparison_between_negapedia_pages = get_translation("ranking_comparison_between_negapedia_pages", self.language)
            topic_titles = [topic.get('title', f'Topic {i + 1}') for i, topic in enumerate(self.post_info)]
            title = f"{ranking_comparison_between_negapedia_pages}: {', '.join(topic_titles)}"
        else:
            negapedia_page_analysis = get_translation("negapedia_page_analysis", self.language)
            title = f"{negapedia_page_analysis}"

        if title:
            return filled_content.replace(template_variable_to_fill, str(title))
        else:
            # Remove the line if there is no title
            return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)

    @staticmethod
    def replace_topics_titles(filled_content, post_info, template_variable_to_fill):
        title = post_info.get('title', 'No Title')
        return filled_content.replace(template_variable_to_fill, str(title))

    @staticmethod
    def replace_description(filled_content, post_info, template_variable_to_fill):
        description = post_info.get('message') or post_info.get('description') or ""

        if description:
            return filled_content.replace(template_variable_to_fill, str(description))
        else:
            # Remove the line if there is no description
            return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)

    @staticmethod
    def replace_images_alt(filled_content, images, template_variable_to_fill):
        images_alt = ''
        for image_info in images:
            src = image_info.get('image')
            width = image_info.get('image_width')
            height = image_info.get('image_height')
            alt = image_info.get('image_alt', '')
            location = image_info.get('location')
            if alt:
                images_alt += f'\n- {alt}'

        if images_alt.strip():  # Check if any alt text is found
            return filled_content.replace(template_variable_to_fill, str(images_alt))
        else:
            # Remove the line if there is no alt text
            return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)

    @staticmethod
    def replace_optional_fields(filled_content, post_info):
        # Replacing various metadata fields
        optional_fields = {
            '{{article_tag}}': post_info.get('article_tag', ''),
            '{{keywords}}': post_info.get('keywords', ''),
            '{{updated_time}}': post_info.get('updated_time', ''),
            '{{article_published_time}}': post_info.get('article_published_time', ''),
            '{{article_modified_time}}': post_info.get('article_modified_time', ''),
        }

        for placeholder, value in optional_fields.items():
            if value:
                filled_content = filled_content.replace(placeholder, str(value))
            else:
                # Remove the line if there is no value
                filled_content = re.sub(rf'^.*{re.escape(placeholder)}.*\n?', '', filled_content, flags=re.MULTILINE)

        return filled_content

    @staticmethod
    def replace_urls(filled_content, post_info):
        urls = ''
        for url in post_info.get('urls', []):
            if url:
                urls += f'\n- {url}'

        if urls.strip():  # Check if any URL is found
            return filled_content.replace('{{urls}}', str(urls))
        else:
            # Remove the line if there is no URL
            return re.sub(r'^.*{{urls}}.*\n?', '', filled_content, flags=re.MULTILINE)

    @staticmethod
    def replace_recent_conflict_levels(filled_content, post_info, template_variable_to_fill):
        # Handle recent_conflict_levels as a string
        recent_conflict_levels = post_info.get('recent_conflict_levels', '')

        if recent_conflict_levels:
            return filled_content.replace(template_variable_to_fill, recent_conflict_levels)
        else:
            return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)

    @staticmethod
    def replace_recent_polemic_levels(filled_content, post_info, template_variable_to_fill):
        # Handle recent_polemic_levels as a string
        recent_polemic_levels = post_info.get('recent_polemic_levels', '')

        if recent_polemic_levels:
            return filled_content.replace(template_variable_to_fill, recent_polemic_levels)
        else:
            # Remove the line if there are no recent polemic levels
            return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)

    @staticmethod
    def replace_important_words(filled_content, post_info, template_variable_to_fill):
        important_words = ''
        for important_word in post_info.get('words_that_matter', []):
            if important_word:
                important_words += f'\n- {important_word}'

        if important_words.strip():
            return filled_content.replace(template_variable_to_fill, str(important_words))
        else:
            # Remove the line if there are no important words
            return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)

    def replace_conflict_awards(self, filled_content, post_info, template_variable_to_fill):
        conflict_awards = self.construct_awards_text(post_info.get('conflict_awards', {}))

        if conflict_awards.strip():
            return filled_content.replace(template_variable_to_fill, str(conflict_awards))
        else:
            # Remove the line if there are no conflict awards
            return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)

    def replace_polemic_awards(self, filled_content, post_info, template_variable_to_fill):
        polemic_awards = self.construct_awards_text(post_info.get('polemic_awards', {}))

        if polemic_awards.strip():
            return filled_content.replace(template_variable_to_fill, str(polemic_awards))
        else:
            # Remove the line if there are no polemic awards
            return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)

    def construct_awards_text(self, awards_dict):
        awards_text = ""
        if 'all' in awards_dict and awards_dict['all']:
            global_in_all_wikipedia = get_translation("global_in_all_wikipedia", self.language)
            awards_text += f"\n{global_in_all_wikipedia}:\n"
            awards_text += "\n".join([f"- {award}" for award in awards_dict['all']])
            awards_text += "\n"

        for category, awards in awards_dict.items():
            if category != 'all' and awards:
                category_specific = get_translation("category_specific", self.language)
                awards_text += f"{category_specific} ({category.upper()}):\n"
                awards_text += "\n".join([f"- {award}" for award in awards])
                awards_text += "\n"

        return awards_text

    @staticmethod
    def replace_social_jumps(filled_content, post_info, template_variable_to_fill):
        social_jumps = ''
        for social_jump in post_info.get('social_jumps', []):
            if social_jump:
                social_jumps += f"\n* {social_jump['title']}: {social_jump['link']}"

        if social_jumps.strip():
            return filled_content.replace(template_variable_to_fill, str(social_jumps))
        else:
            # Remove the line if there are no social jumps
            return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)

    def replace_ranking_field(self, filled_content, template_variable_to_fill):
        field_names = {
            'recent_conflict_levels': get_translation("recent_conflict_levels", self.language),
            'recent_polemic_levels': get_translation("recent_polemic_levels", self.language),
            'mean_conflict_level': get_translation("mean_conflict_level", self.language),
            'mean_polemic_level': get_translation("mean_polemic_level", self.language),
        }

        ranking_field_names = ', '.join([field_names.get(field, field) for field in self.posting_settings['ranking_fields']])

        if ranking_field_names.strip():
            return filled_content.replace(template_variable_to_fill, str(ranking_field_names))
        else:
            # Remove the line if there are no conflict levels
            return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)

    def replace_recent_conflict_levels_ranking(self, filled_content, template_variable_to_fill):
        conflict_levels_ranking = ''

        # Sort topics by their recent conflict levels (descending)
        sorted_by_conflict = sorted(self.post_info, key=lambda post_info_topic: int(post_info_topic.get('recent_conflict_levels', 0)), reverse=True)

        for rank, topic in enumerate(sorted_by_conflict, start=1):
            conflict_levels_ranking += f'\n{rank}. {topic.get("title", "Unknown Topic")}: {topic.get("recent_conflict_levels", "N/A")}'

        if conflict_levels_ranking.strip() and 'recent_conflict_levels' in self.posting_settings['ranking_fields']:
            return filled_content.replace(template_variable_to_fill, str(conflict_levels_ranking))
        else:
            # Remove the line if there are no conflict levels
            return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)

    def replace_recent_polemic_levels_ranking(self, filled_content, template_variable_to_fill):
        polemic_levels_ranking = ''

        # Sort topics by their recent polemic levels (descending)
        sorted_by_polemic = sorted(self.post_info, key=lambda post_info_topic: int(post_info_topic.get('recent_polemic_levels', 0)), reverse=True)

        for rank, topic in enumerate(sorted_by_polemic, start=1):
            polemic_levels_ranking += f'\n{rank}. {topic.get("title", "Unknown Topic")}: {topic.get("recent_polemic_levels", "N/A")}'

        if polemic_levels_ranking.strip() and 'recent_polemic_levels' in self.posting_settings['ranking_fields']:
            return filled_content.replace(template_variable_to_fill, str(polemic_levels_ranking))
        else:
            # Remove the line if there are no polemic levels
            return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)

    def replace_mean_conflict_level_ranking(self, filled_content, template_variable_to_fill):
        mean_conflict_levels_ranking = ''

        # Sort topics by their recent conflict levels (descending)
        sorted_by_mean_conflict = sorted(self.post_info, key=lambda post_info_topic: float(post_info_topic.get('mean_conflict_level', 0)), reverse=True)

        for rank, topic in enumerate(sorted_by_mean_conflict, start=1):
            mean_conflict_levels_ranking += f'\n{rank}. {topic.get("title", "Unknown Topic")}: {topic.get("mean_conflict_level", "N/A")}'

        if mean_conflict_levels_ranking.strip() and 'mean_conflict_level' in self.posting_settings['ranking_fields']:
            return filled_content.replace(template_variable_to_fill, str(mean_conflict_levels_ranking))
        else:
            # Remove the line if there are no mean conflict levels
            return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)

    def replace_mean_polemic_level_ranking(self, filled_content, template_variable_to_fill):
        mean_polemic_levels_ranking = ''

        # Sort topics by their recent polemic levels (descending)
        sorted_by_polemic = sorted(self.post_info, key=lambda post_info_topic: int(post_info_topic.get('recent_polemic_levels', 0)), reverse=True)

        for rank, topic in enumerate(sorted_by_polemic, start=1):
            mean_polemic_levels_ranking += f'\n{rank}. {topic.get("title", "Unknown Topic")}: {topic.get("recent_polemic_levels", "N/A")}'

        if mean_polemic_levels_ranking.strip() and 'mean_polemic_level' in self.posting_settings['ranking_fields']:
            return filled_content.replace(template_variable_to_fill, str(mean_polemic_levels_ranking))
        else:
            # Remove the line if there are no mean conflict levels
            return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)
