import tweepy
from utils.env_management import load_from_env
from utils.images_management import get_downloaded_image_path


def post_on_twitter(post_info):
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

    url = post_info.get('url')
    title = post_info.get('title', f"Check out this topic at {url}")
    description = post_info.get('description', f"Check out this topic at {url}")
    message = title + "\n" + description

    images_paths = []
    image = {
        'location': "web",  # {{to_fix}} for negapedia and multiple plots
        'src': post_info.get('image')   # {{to_fix}} for negapedia and multiple plots
    }
    images_paths.append(image)

    if images_paths:
        media_ids = []
        for image_path in images_paths:
            try:
                image_path_src = image_path['src']
                if image_path['location'] == "web":
                    image_path_src = get_downloaded_image_path(image_path_src)
                media = api.media_upload(image_path_src)
                media_ids.append(media.media_id_string)
            except tweepy.TweepyException as e:
                print(f"An error occurred while uploading image {image_path}: {e}")

        if media_ids:
            try:
                client.create_tweet(text=message, media_ids=media_ids)
                print("Successfully posted the tweet with image.")
            except tweepy.TweepyException as e:
                print(f"An error occurred while creating the tweet: {e}")
        else:
            print("No images were uploaded. Post was not created.")
    else:
        try:
            client.create_tweet(text=message)
            print("Successfully posted the tweet.")
        except tweepy.TweepyException as e:
            print(f"An error occurred: {e}")
