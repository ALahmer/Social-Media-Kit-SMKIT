import tweepy
from utils.env_management import load_from_env
from utils.images_management import get_downloaded_image_path
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

    # Fill the template based on the type of post_info
    filled_content = template_content

    if module == 'negapedia':
        filled_content = convert_negapediapageinfo_to_filled_content(post_info, filled_content)
    else:
        filled_content = convert_pageinfo_to_filled_content(post_info, filled_content)

    # Post the message to your page
    post_to_twitter(api, client, post_info, filled_content)


def post_to_twitter(api, client, post_info, message):
    if post_info.get('images'):
        media_ids = []
        for image_info in post_info.get('images', []):
            try:
                src = image_info.get('image')
                width = image_info.get('image_width')
                height = image_info.get('image_height')
                alt = image_info.get('image_alt') or "Image"
                location = image_info.get('location')

                if location == "web":
                    src = get_downloaded_image_path(src)
                media = api.media_upload(src)
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
    filled_content = replace_description(filled_content, post_info)
    filled_content = replace_images_alt(filled_content, (post_info.get('images', []) or []), '{{images_alt}}')
    filled_content = replace_optional_fields(filled_content, post_info)
    filled_content = replace_urls(filled_content, post_info)
    return filled_content


def convert_negapediapageinfo_to_filled_content(post_info, filled_content):
    # {{to_do}}
    return filled_content


def replace_title(filled_content, post_info, template_variable_to_fill):
    title = post_info.get('title') or (post_info.get('urls', [None])[0]) or None

    if title:
        return filled_content.replace(template_variable_to_fill, str(title))
    else:
        # Remove the line if there is no title
        return re.sub(rf'^.*{re.escape(template_variable_to_fill)}.*\n?', '', filled_content, flags=re.MULTILINE)


def replace_description(filled_content, post_info):
    description = post_info.get('message') or post_info.get('description') or ""

    if description:
        return filled_content.replace('{{description}}', str(description))
    else:
        # Remove the line if there is no description
        return re.sub(r'^.*{{description}}.*\n?', '', filled_content, flags=re.MULTILINE)


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
