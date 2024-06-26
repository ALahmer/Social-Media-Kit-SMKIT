import argparse
import subprocess
from command_invoker import CommandInvoker
from facebook_poster import PostOnFacebook
from env_management import load_from_env
from twitter_poster import PostOnTwitter
from negapedia_connector import get_negapedia_url, get_negapedia_data_array, convert_negaranks_to_dicts
import matplotlib
from datetime import datetime


matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os


def check_access_token():
    env_data = load_from_env()
    return env_data and 'page_access_token' in env_data and env_data['page_access_token']


def start_flask_app():
    print("Starting Flask server for authentication...")
    subprocess.Popen(['python', 'app.py'])


def extract_data(topics_data_array, category):
    data_to_plot = dict()
    category_param = '"' + category + '"'
    for topic in topics_data_array:
        data_to_plot[topic] = dict()
        data_to_plot[topic]["years"] = [entry["year"] for entry in topics_data_array[topic] if
                                        entry['category'] != category_param]
        data_to_plot[topic]["values"] = [entry["value4"] for entry in topics_data_array[topic] if
                                         entry['category'] != category_param]
    return data_to_plot


def plot_negaraks_data_copilot(category, topics, topics_data_array, plots_path):
    # Extract data for plotting
    data_to_plot = extract_data(topics_data_array, category)

    # Define a color map for topics
    colors = ["brown", "black", "green", "red", "red", "blue"]
    topic_colors = dict()
    for topic in data_to_plot:
        color = colors.pop()
        topic_colors[topic] = color

    # Create line plots
    plt.figure(figsize=(10, 6))

    for topic in data_to_plot:
        years_to_plot = data_to_plot[topic]["years"]
        values_to_plot = data_to_plot[topic]["values"]
        plot_label = topic
        plot_color = topic_colors[topic]
        plt.plot(years_to_plot, values_to_plot, label=plot_label, color=plot_color, marker="o")

    # Add labels and title
    plt.xlabel("Year")
    y_label = category + " level"
    plt.ylabel(y_label)

    # Construct the title
    if len(topics) == 1:
        topics_str = topics[0]
    elif len(topics) == 2:
        topics_str = " and ".join(topics)
    else:
        topics_str = ", ".join(topics[:-1]) + ", and " + topics[-1]

    title_plot = "Comparison of " + category + " level between topics " + topics_str
    plt.title(title_plot)
    plt.legend()

    # Adjust x-axis and y-axis ticks
    plt.grid(True)
    max_x = max(max(data_to_plot[topic]["years"]) for topic in data_to_plot)
    min_x = min(min(data_to_plot[topic]["years"]) for topic in data_to_plot)
    max_y = max(max(data_to_plot[topic]["values"]) for topic in data_to_plot)
    min_y = min(min(data_to_plot[topic]["values"]) for topic in data_to_plot)

    x_tick_step = 1
    y_tick_step = round(max_y / 10)

    plt.xticks(range(min_x - 1, max_x + 1, x_tick_step))
    plt.yticks(range(0, int(max_y) + 1, y_tick_step))

    # Save the plot as a PNG file
    timestamp = datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")
    output_filename = title_plot.replace(" ", "_") + "_" + timestamp + ".png"
    output_path = os.path.join('images_to_post', output_filename)
    plt.savefig(output_path)

    plots_path.append( "images_to_post/" + output_filename )

    # Show the plot
    # plt.show()
    return None


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
            negapedia_url = get_negapedia_url(topic)
            topics_urls.append({topic: negapedia_url})
        except Exception as e:
            print(f"Failed to get Negapedia URL for topic={topic}: {e}")
            continue
        try:
            negapedia_string_data = get_negapedia_data_array(negapedia_url)
            negapedia_data = convert_negaranks_to_dicts(negapedia_string_data)
            negapedia_data_filtered = [entry for entry in negapedia_data if entry['type1'] == '"all"']
            topics_data_array[topic] = negapedia_data_filtered
        except Exception as e:
            print(f"Failed to process NEGARANKS data management for topic={topic}: {e}")
            continue

    # Plotting the data
    categories = ["conflict", "polemic"]
    plots_path = []
    for category in categories:
        plot_negaraks_data_copilot(category, args.topics, topics_data_array, plots_path)


    invoker = CommandInvoker()

    if args.command == 'facebook':
        if not check_access_token():
            start_flask_app()
            input("Press Enter after completing authentication in the browser...")
        command = PostOnFacebook(args.topics, args.image)
    elif args.command == 'twitter':
        command = PostOnTwitter(args.topics, plots_path)

    invoker.add_command(command)
    invoker.execute_commands()


if __name__ == "__main__":
    main()
