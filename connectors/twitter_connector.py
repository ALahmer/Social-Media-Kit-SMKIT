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
