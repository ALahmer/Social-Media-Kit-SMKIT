import facebook
from datetime import datetime
import requests
from utils.env_management import load_from_env, save_to_env
from utils.images_management import get_downloaded_image_path


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


def post_on_facebook(post_info):
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

    title = post_info.get('title') or "No Title"
    description = post_info.get('description') or "No Description"
    tags = post_info.get('article_tag')
    keywords = post_info.get('keywords')

    if tags:
        tags = " ".join(f"#{tag.strip().replace(' ', '')}" for tag in tags.split(','))
    else:
        tags = ""
    if keywords:
        keywords = " ".join(f"#{keyword.strip().replace(' ', '')}" for keyword in keywords.split(','))
    else:
        keywords = ""

    with open('templates/facebook_post_template.txt', 'r') as template_file:
        template_content = template_file.read()
    message = template_content.replace('{{title}}', title)
    message = message.replace('{{description}}', description)
    message = message.replace('{{tags}}', tags)
    message = message.replace('{{keywords}}', keywords)

    # Post the message to your page
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
