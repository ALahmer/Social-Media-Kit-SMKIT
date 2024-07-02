import tweepy
from datetime import datetime
from env_management import load_from_env


class PostOnTwitter:
    def __init__(self, topic, images_paths=None):
        self.topic = topic
        self.images_paths = images_paths

    def execute(self):
        print(f"Post to be posted on Twitter about {self.topic}")
        self.post()

    def post(self):
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

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        # Prepare tweet
        if len(self.topic) == 1:
            topics_str = self.topic[0]
        elif len(self.topic) == 2:
            topics_str = " and ".join(self.topic)
        else:
            topics_str = ", ".join(self.topic[:-1]) + ", and " + self.topic[-1]
        message = f"Comparison of conflict and polemic levels between topics {topics_str}"

        if self.images_paths:
            media_ids = []
            for image_path in self.images_paths:
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
