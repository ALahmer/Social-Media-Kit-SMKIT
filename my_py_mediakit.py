import argparse
import subprocess
from command_invoker import CommandInvoker
from facebook_poster import PostOnFacebook
from env_management import load_from_env
from twitter_poster import PostOnTwitter
import negapedia_connector


def check_access_token():
    env_data = load_from_env()
    return env_data and 'page_access_token' in env_data and env_data['page_access_token']


def start_flask_app():
    print("Starting Flask server for authentication...")
    subprocess.Popen(['python', 'app.py'])


def main():
    parser = argparse.ArgumentParser(description='Command-line interface example')
    parser.add_argument('command', choices=['facebook', 'twitter'], help='Where to post')
    parser.add_argument('topics', nargs='+', help='List of topics to post about')
    parser.add_argument('--image', help='Path to image to post', default=None)
    args = parser.parse_args()

    topics_urls = []
    topics_data_array = dict()
    for topic in args.topics:
        try:
            negapedia_url = negapedia_connector.get_negapedia_url(topic)
            topics_urls.append({topic: negapedia_url})
        except Exception as e:
            print(f"Failed to get Negapedia URL for topic={topic}: {e}")
            continue
        try:
            negapedia_string_data = negapedia_connector.get_negapedia_data_array(negapedia_url)
            negapedia_data = negapedia_connector.convert_negaranks_to_dicts(negapedia_string_data)
            topics_data_array[topic] = negapedia_connector.filter_useful_negaranks_data(negapedia_data)
        except Exception as e:
            print(f"Failed to process NEGARANKS data management for topic={topic}: {e}")
            continue

    # Plotting the data
    categories = ["conflict", "polemic"]
    plots_paths = []
    for category in categories:
        negapedia_connector.plot_negaraks_data_copilot(category, args.topics, topics_data_array, plots_paths)


    invoker = CommandInvoker()

    if args.command == 'facebook':
        if not check_access_token():
            start_flask_app()
            input("Press Enter after completing authentication in the browser...")
        command = PostOnFacebook(args.topics, plots_paths)
    elif args.command == 'twitter':
        command = PostOnTwitter(args.topics, plots_paths)

    invoker.add_command(command)
    invoker.execute_commands()


if __name__ == "__main__":
    main()
