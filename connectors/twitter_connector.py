import tweepy
from utils.env_management import load_from_env


def post_on_twitter(topic, images_paths=None):
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

    # Prepare tweet
    if len(topic) == 1:
        topics_str = topic[0]
    elif len(topic) == 2:
        topics_str = " and ".join(topic)
    else:
        topics_str = ", ".join(topic[:-1]) + ", and " + topic[-1]
    message = f"Comparison of conflict and polemic levels between topics {topics_str}"

    if images_paths:
        media_ids = []
        for image_path in images_paths:
            try:
                media = api.media_upload(image_path)
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
