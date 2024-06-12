import tweepy
from datetime import datetime
from env_management import load_encrypted_env


class PostOnTwitter:
    def __init__(self, topic):
        self.topic = topic

    def execute(self):
        print(f"Post to be posted on Twitter about {self.topic}")
        self.post()

    def post(self):
        env_data = load_encrypted_env()
        if not env_data or not all(k in env_data for k in ('twitter_api_key', 'twitter_api_secret_key', 'twitter_access_token', 'twitter_access_token_secret')):
            print("Twitter credentials not found. Please add them to env.json.")
            return

        client = tweepy.Client(
            consumer_key=env_data['twitter_api_key'],
            consumer_secret=env_data['twitter_api_secret_key'],
            access_token=env_data['twitter_access_token'],
            access_token_secret=env_data['twitter_access_token_secret']
        )

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Hello, world! This is a tweet about {self.topic}.\n[{timestamp}]"

        try:
            client.create_tweet(text=message)
            print("Successfully posted the tweet.")
        except tweepy.TweepyException as e:
            print(f"An error occurred: {e}")
