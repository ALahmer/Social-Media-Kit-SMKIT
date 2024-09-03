import facebook
from datetime import datetime
import requests
from utils.env_management import load_from_env, save_to_env
from utils.images_management import get_downloaded_image_path
import re


def check_access_token():
    env_data = load_from_env()
    return env_data and 'page_access_token' in env_data and env_data['page_access_token']


def is_token_expired(access_token):
    debug_token_url = (
        f"https://graph.facebook.com/debug_token?input_token={access_token}&access_token={access_token}"
    )
    response = requests.get(debug_token_url)
    token_info = response.json()

    if 'data' in token_info and 'expires_at' in token_info['data']:
        expiry_timestamp = token_info['data']['expires_at']
        expiry_datetime = datetime.fromtimestamp(expiry_timestamp)
        return datetime.utcnow() > expiry_datetime
    return True


def refresh_access_token(facebook_app_id, facebook_app_secret, short_lived_token):
    refresh_url = (
        f"https://graph.facebook.com/v12.0/oauth/access_token?"
        f"grant_type=fb_exchange_token&client_id={facebook_app_id}&client_secret={facebook_app_secret}&fb_exchange_token={short_lived_token}"
    )
    response = requests.get(refresh_url)
    new_token_info = response.json()
    if 'access_token' in new_token_info:
        return new_token_info['access_token']
    else:
        print("Error refreshing access token")
        return None


def post_on_facebook(post_info, template, language, module):
    env_data = load_from_env()
    if not env_data or 'page_access_token' not in env_data:
        print("Access token not found. Please authenticate first.")
        return

    access_token = env_data['page_access_token']

    if is_token_expired(access_token):
        print("Access token expired. Refreshing...")
        access_token = refresh_access_token(env_data['facebook_app_id'], env_data['facebook_app_secret'], access_token)
        if access_token:
            env_data['page_access_token'] = access_token
            save_to_env(env_data)
        else:
            print("Failed to refresh access token.")
            return

    # Initialize the Graph API with your access token
    graph = facebook.GraphAPI(access_token)

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
    post_to_facebook(graph, post_info, filled_content)


def post_to_facebook(graph, post_info, message):
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
                with open(src, 'rb') as image:
                    media = graph.put_photo(image=image, published=False)
                    media_ids.append(media['id'])
            except facebook.GraphAPIError as e:
                print(f"An error occurred while uploading image {image_info}: {e}")

        if media_ids:
            try:
                args = {"message": message}
                for idx, media_id in enumerate(media_ids):
                    args[f"attached_media[{idx}]"] = f'{{"media_fbid":"{media_id}"}}'

                post = graph.request(path='/me/feed', args=args, method='POST')
                print(f"Successfully posted with post ID: {post['id']}")
            except facebook.GraphAPIError as e:
                print(f"An error occurred while creating the post: {e}")
        else:
            print("No images were uploaded. Post was not created.")
    else:
        try:
            post = graph.put_object(parent_object='me', connection_name='feed', message=message)
            # Print the post ID
            print(f"Successfully posted with post ID: {post['id']}")
        except facebook.GraphAPIError as e:
            print(f"An error occurred: {e}")


def load_template(template, language, module):
    """
    Loads the Facebook post template content.
    """
    try:
        file_path = f'templates/{language}/{module}/facebook_post_{template}_template.txt'
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
