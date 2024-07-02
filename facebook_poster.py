import facebook
from datetime import datetime
import requests
from env_management import load_from_env, save_to_env


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


class PostOnFacebook:
    def __init__(self, topic, images_paths=None):
        self.topic = topic
        self.images_paths = images_paths

    def execute(self):
        print(f"Post to be posted on Facebook about {self.topic}")
        self.post()

    def post(self):
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

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        # Prepare post
        if len(self.topic) == 1:
            topics_str = self.topic[0]
        elif len(self.topic) == 2:
            topics_str = " and ".join(self.topic)
        else:
            topics_str = ", ".join(self.topic[:-1]) + ", and " + self.topic[-1]
        message = f"This is a post about {topics_str}.\n[{timestamp}]"

        # Post the message to your page
        if self.images_paths:
            media_ids = []
            for image_path in self.images_paths:
                try:
                    with open(image_path, 'rb') as image:
                        media = graph.put_photo(image=image, published=False)
                        media_ids.append(media['id'])
                except facebook.GraphAPIError as e:
                    print(f"An error occurred while uploading image {image_path}: {e}")

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
