import facebook
from datetime import datetime
import requests
from env_management import load_encrypted_env, save_to_env


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
    def __init__(self, topic):
        self.topic = topic

    def execute(self):
        print(f"Post to be posted on Facebook about {self.topic}")
        self.post()

    def post(self):
        env_data = load_encrypted_env()
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
        # Prepare your post
        message = f"Hello, world! This is a post about {self.topic}.\n[{timestamp}]"

        # Post the message to your page
        try:
            post = graph.put_object(parent_object='me', connection_name='feed', message=message)
            # Print the post ID
            print(f"Successfully posted with post ID: {post['id']}")
        except facebook.GraphAPIError as e:
            print(f"An error occurred: {e}")
