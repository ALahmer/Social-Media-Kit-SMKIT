import tweepy
from utils.env_management import load_from_env
from utils.images_management import fetch_image_as_stream
import re


def post_on_twitter(post_info, template, language, module):
    env_data = load_from_env()
    if not env_data or not all(k in env_data for k in ('twitter_api_key', 'twitter_api_secret_key', 'twitter_access_token', 'twitter_access_token_secret')):
        print("Twitter credentials not found. Please add them to env.json.")
        return

    auth = tweepy.OAuth1UserHandler(
        env_data['twitter_api_key'],
        env_data['twitter_api_secret_key'],
        env_data['twitter_access_token'],
        env_data['twitter_access_token_secret']
    )
    api = tweepy.API(auth)

    client = tweepy.Client(
        consumer_key=env_data['twitter_api_key'],
        consumer_secret=env_data['twitter_api_secret_key'],
        access_token=env_data['twitter_access_token'],
        access_token_secret=env_data['twitter_access_token_secret']
    )

    # Load the template
    template_content = load_template(template, language, module)
    if not template_content:
        print("Template could not be loaded.")
        return

    images = []
    # Fill the template based on the type of post_info
    filled_content = template_content

    if module == 'negapedia':
        topic1 = post_info[0]
        topic2 = post_info[1] if len(post_info) > 1 else None

        if template == 'summary':
            filled_content = convert_negapediapageinfo_to_summary_filled_content(topic1, filled_content, template)
            images = (topic1.get('historical_conflict', []) or []) + (topic1.get('historical_polemic', []) or [])
        elif template == 'comparison':
            filled_content = convert_negapediapageinfo_to_comparison_filled_content(topic1, topic2, filled_content, template)
            images = (topic1.get('historical_conflict_comparison', []) or []) + (topic1.get('historical_polemic_comparison', []) or [])
    else:
        filled_content = convert_pageinfo_to_filled_content(post_info, filled_content)
        images = post_info.get('images', []) or []

    # Post the message to your page
    post_to_twitter(api, client, filled_content, images)


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
                print(f"An error occurred while uploading image {image_info}: {e}")

        if media_ids:
            try:
                client.create_tweet(text=message, media_ids=media_ids)   # {{to_check}} if tweet has certain hashtag the posting will go on 403 error (try to print verbose logs, example problematic link: https://www.w3schools.com/tags/tag_meta.asp)
                print("Successfully posted the tweet with image.")
            except tweepy.TweepyException as e:
                print(f"An error occurred while creating the tweet: {e}")
        else:
            print("No images were uploaded. Post was not created.")
    else:
        try:
            client.create_tweet(text=message)   # {{to_check}} if tweet has certain hashtag the posting will go on 403 error (try to print verbose logs, example problematic link: https://www.w3schools.com/tags/tag_meta.asp)
            print("Successfully posted the tweet.")
        except tweepy.TweepyException as e:
            print(f"An error occurred: {e}")


def load_template(template, language, module):
    """
    Loads the Facebook post template content.
    """
    try:
        file_path = f'templates/{language}/{module}/twitter_post_{template}_template.txt'
        with open(file_path, 'r', encoding='utf-8') as template_file:
            return template_file.read()
    except FileNotFoundError:
        print(f"Template file {file_path} not found.")
        return None


def convert_pageinfo_to_filled_content(post_info, filled_content):
    filled_content = replace_title(filled_content, post_info, '{{title}}')
    filled_content = replace_description(filled_content, post_info, '{{description}}')
    filled_content = replace_images_alt(
        filled_content,
        (post_info.get('images', []) or []),
        '{{images_alt}}'
    )
    filled_content = replace_optional_fields(filled_content, post_info)
    filled_content = replace_urls(filled_content, post_info)
    return filled_content


def convert_negapediapageinfo_to_summary_filled_content(post_info, filled_content, template):
    filled_content = replace_negapedia_template_title(filled_content, post_info, None, template, '{{title}}')
    filled_content = replace_description(filled_content, post_info, '{{description}}')
    filled_content = replace_recent_conflict_levels(filled_content, post_info, '{{recent_conflict_levels}}')
    filled_content = replace_recent_polemic_levels(filled_content, post_info, '{{recent_polemic_levels}}')
    filled_content = replace_important_words(filled_content, post_info, '{{important_words}}')
    filled_content = replace_conflict_awards(filled_content, post_info, '{{conflict_awards}}')
    filled_content = replace_polemic_awards(filled_content, post_info, '{{polemic_awards}}')
    filled_content = replace_social_jumps(filled_content, post_info, '{{social_jumps}}')
    filled_content = replace_images_alt(
        filled_content,
        (post_info.get('historical_conflict', []) or []) + (post_info.get('historical_polemic', []) or []),
        '{{images_alt}}'
    )
    return filled_content


def convert_negapediapageinfo_to_comparison_filled_content(topic1_post_info, topic2_post_info, filled_content, template):
    # Replace the titles
    filled_content = replace_negapedia_template_title(filled_content, topic1_post_info, topic2_post_info, template, '{{title}}')
    filled_content = replace_topics_titles(filled_content, topic1_post_info, '{{topic1_title}}')
    filled_content = replace_topics_titles(filled_content, topic2_post_info, '{{topic2_title}}')

    # Replace descriptions for both topics
    filled_content = replace_description(filled_content, topic1_post_info, '{{description_topic1}}')
    filled_content = replace_description(filled_content, topic2_post_info, '{{description_topic2}}')

    # Replace recent conflict and polemic levels for both topics
    filled_content = replace_recent_conflict_levels(filled_content, topic1_post_info, '{{recent_conflict_levels_topic1}}')
    filled_content = replace_recent_conflict_levels(filled_content, topic2_post_info, '{{recent_conflict_levels_topic2}}')
    filled_content = replace_recent_polemic_levels(filled_content, topic1_post_info, '{{recent_polemic_levels_topic1}}')
    filled_content = replace_recent_polemic_levels(filled_content, topic2_post_info, '{{recent_polemic_levels_topic2}}')

    # Replace important words for both topics
    filled_content = replace_important_words(filled_content, topic1_post_info, '{{important_words_topic1}}')
    filled_content = replace_important_words(filled_content, topic2_post_info, '{{important_words_topic2}}')

    # Replace conflict and polemic awards for both topics
    filled_content = replace_conflict_awards(filled_content, topic1_post_info, '{{conflict_awards_topic1}}')
    filled_content = replace_conflict_awards(filled_content, topic2_post_info, '{{conflict_awards_topic2}}')
    filled_content = replace_polemic_awards(filled_content, topic1_post_info, '{{polemic_awards_topic1}}')
    filled_content = replace_polemic_awards(filled_content, topic2_post_info, '{{polemic_awards_topic2}}')

    # Replace social jumps for both topics
    filled_content = replace_social_jumps(filled_content, topic1_post_info, '{{social_jumps_topic1}}')
    filled_content = replace_social_jumps(filled_content, topic2_post_info, '{{social_jumps_topic2}}')

    # Replace images alt for both topics
    filled_content = replace_images_alt(
        filled_content,
        (topic1_post_info.get('historical_conflict_comparison', []) or []) +
        (topic1_post_info.get('historical_polemic_comparison', []) or []),
        '{{images_alt}}'
    )

    return filled_content


def replace_title(filled_content, post_info, template_variable_to_fill):
    title = post_info.get('title') or (post_info.get('urls', [None])[0]) or None

    if title:
        return filled_content.replace(template_variable_to_fill, str(title))
    else:
        # Remove the line if there is no title
        return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)


def replace_negapedia_template_title(filled_content, topic1, topic2, template, template_variable_to_fill):
    if template == 'comparison':
        title = f"Comparison between {topic1.get('title', 'Topic 1')} and {topic2.get('title', 'Topic 2')} Negapedia pages"
    else:
        title = f"Summary for {topic1.get('title', 'Topic 1')} Negapedia page"

    if title:
        return filled_content.replace(template_variable_to_fill, str(title))
    else:
        # Remove the line if there is no title
        return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)


def replace_topics_titles(filled_content, post_info, template_variable_to_fill):
    title = post_info.get('title', 'No Title')
    return filled_content.replace(template_variable_to_fill, str(title))


def replace_description(filled_content, post_info, template_variable_to_fill):
    description = post_info.get('message') or post_info.get('description') or ""

    if description:
        return filled_content.replace(template_variable_to_fill, str(description))
    else:
        # Remove the line if there is no description
        return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)


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


def replace_recent_conflict_levels(filled_content, post_info, template_variable_to_fill):
    # Handle recent_conflict_levels as a string
    recent_conflict_levels = post_info.get('recent_conflict_levels', '')

    if recent_conflict_levels:
        return filled_content.replace(template_variable_to_fill, recent_conflict_levels)
    else:
        return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)


def replace_recent_polemic_levels(filled_content, post_info, template_variable_to_fill):
    # Handle recent_polemic_levels as a string
    recent_polemic_levels = post_info.get('recent_polemic_levels', '')

    if recent_polemic_levels:
        return filled_content.replace(template_variable_to_fill, recent_polemic_levels)
    else:
        # Remove the line if there are no recent polemic levels
        return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)


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


def replace_conflict_awards(filled_content, post_info, template_variable_to_fill):
    conflict_awards = construct_awards_text(post_info.get('conflict_awards', {}))

    if conflict_awards.strip():
        return filled_content.replace(template_variable_to_fill, str(conflict_awards))
    else:
        # Remove the line if there are no conflict awards
        return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)


def replace_polemic_awards(filled_content, post_info, template_variable_to_fill):
    polemic_awards = construct_awards_text(post_info.get('polemic_awards', {}))

    if polemic_awards.strip():
        return filled_content.replace(template_variable_to_fill, str(polemic_awards))
    else:
        # Remove the line if there are no polemic awards
        return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)


def construct_awards_text(awards_dict):
    awards_text = ""
    if 'all' in awards_dict and awards_dict['all']:
        awards_text += "\nGLOBAL (IN ALL WIKIPEDIA):\n"
        awards_text += "\n".join([f"- {award}" for award in awards_dict['all']])
        awards_text += "\n"

    for category, awards in awards_dict.items():
        if category != 'all' and awards:
            awards_text += f"CATEGORY SPECIFIC ({category.upper()}):\n"
            awards_text += "\n".join([f"- {award}" for award in awards])
            awards_text += "\n"

    return awards_text


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
