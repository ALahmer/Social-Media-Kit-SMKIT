import argparse
import subprocess
from command_invoker import CommandInvoker
from facebook_poster import PostOnFacebook, load_from_env
from twitter_poster import PostOnTwitter


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
    args = parser.parse_args()

    invoker = CommandInvoker()

    if args.command == 'facebook':
        if not check_access_token():
            start_flask_app()
            input("Press Enter after completing authentication in the browser...")
        command = PostOnFacebook(args.topic)
    elif args.command == 'twitter':
        command = PostOnTwitter(args.topic)

    invoker.add_command(command)
    invoker.execute_commands()


if __name__ == "__main__":
    main()
