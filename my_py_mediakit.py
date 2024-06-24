import argparse
import subprocess
from command_invoker import CommandInvoker
from facebook_poster import PostOnFacebook
from env_management import load_from_env
from twitter_poster import PostOnTwitter
from negapedia_connector import get_negapedia_url


def check_access_token():
    env_data = load_from_env()
    return env_data and 'page_access_token' in env_data and env_data['page_access_token']


def start_flask_app():
    print("Starting Flask server for authentication...")
    subprocess.Popen(['python', 'app.py'])


def main():
    parser = argparse.ArgumentParser(description='Command-line interface example')
    parser.add_argument('command', choices=['facebook', 'twitter'], help='Where to post')
    parser.add_argument('topic', help='Topic to post about')
    parser.add_argument('--image', help='Path to image to post', default=None)
    args = parser.parse_args()

    # Get the Negapedia URL
    try:
        negapedia_url = get_negapedia_url(args.topic)
        print(f"Negapedia URL for {args.topic}: {negapedia_url}")
    except Exception as e:
        print(f"Failed to get Negapedia URL: {e}")
        return

    invoker = CommandInvoker()

    if args.command == 'facebook':
        if not check_access_token():
            start_flask_app()
            input("Press Enter after completing authentication in the browser...")
        command = PostOnFacebook(args.topic, args.image)
    elif args.command == 'twitter':
        command = PostOnTwitter(args.topic, args.image)

    invoker.add_command(command)
    invoker.execute_commands()


if __name__ == "__main__":
    main()
