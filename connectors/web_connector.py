import os
import re
from datetime import datetime
from utils.env_management import load_from_env
from bs4 import BeautifulSoup


def post_on_web(post_info, template, language, module, posting_settings):
    # Ensure the 'pages_to_post' directory exists
    output_dir = 'pages_to_post'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load the HTML template
    template_content = load_template(template, language, module)
    if not template_content:
        print("Template could not be loaded.")
        return

    filled_content = template_content

    if module == 'negapedia':
        filled_content = convert_negapediapageinfo_to_filled_content(post_info, filled_content, template, language, posting_settings)
    else:
        filled_content = convert_pageinfo_to_filled_content(post_info, filled_content, template, posting_settings)

    # Create a unique filename based on the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"post_{timestamp}.html"
    file_path = os.path.join(output_dir, filename)

    # Write the filled content to the output HTML file using UTF-8 encoding
    with open(file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(filled_content)

    print(f"Web page created successfully: {file_path}")

    return file_path


def load_template(template, language, module):
    """
    Loads the HTML template content.
    """
    try:
        file_path = f'templates/{language}/{module}/web_post_{template}_template.html'
        with open(file_path, 'r', encoding='utf-8') as template_file:
            return template_file.read()
    except FileNotFoundError:
        print(f"Template file {file_path} not found.")
        return None


def convert_negapediapageinfo_to_filled_content(post_info, filled_content, template, language, posting_settings):
    # Handle NegapediaPageInfo

    # Determine the mode based on the template
    if template == 'summary':
        # Process first topic for summary mode
        topic1 = post_info[0]
        filled_content = replace_topic_content(filled_content, topic1, '1')

    elif template == 'comparison':
        topic1 = post_info[0]
        topic2 = post_info[1]

        # Process both topics for comparison mode
        filled_content = replace_topic_content(filled_content, topic1, '1')
        filled_content = replace_topic_content(filled_content, topic2, '2')

    elif template == 'ranking':
        # Handle ranking mode, where multiple topics are ranked and listed
        filled_content = replace_ranking_content(filled_content, post_info, language, posting_settings)

    # Replace placeholders for the general title
    filled_content = replace_main_title(filled_content, post_info, template)

    # Replace placeholders for the page description
    filled_content = replace_description(filled_content, post_info[0])

    return filled_content


def convert_pageinfo_to_filled_content(post_info, filled_content, template, posting_settings):
    filled_content = replace_title(filled_content, post_info, '{{title}}')
    filled_content = replace_description(filled_content, post_info)
    filled_content = replace_images(filled_content, (post_info.get('images', []) or []), '{{images}}')
    filled_content = replace_urls(filled_content, post_info)
    filled_content = replace_video(filled_content, post_info)
    filled_content = replace_audio(filled_content, post_info)
    filled_content = replace_optional_fields(filled_content, post_info)

    return filled_content


def replace_title(filled_content, post_info, template_variable_to_fill):
    title = post_info.get('title', 'No Title')

    return filled_content.replace(template_variable_to_fill, str(title))


def replace_description(filled_content, post_info):
    description = post_info.get('message') or post_info.get('description') or ""

    return filled_content.replace('{{description}}', str(description))


def replace_images(filled_content, images, template_variable_to_fill):
    images_html = ''
    for image_info in images:
        src = image_info.get('image')
        width = image_info.get('image_width')
        height = image_info.get('image_height')
        alt = image_info.get('image_alt') or "Image"
        location = image_info.get('location')

        if width and height:
            image_tag = f'<img src="{src}" alt="{alt}" width="{width}" height="{height}">'
        else:
            image_tag = f'<img src="{src}" alt="{alt}">'

        images_html += image_tag

    return filled_content.replace(template_variable_to_fill, str(images_html))


def replace_urls(filled_content, post_info):
    urls_html = ''
    for url in post_info.get('urls', []):
        urls_html += f'<li><a href="{url}">{url}</a></li>'

    return filled_content.replace('{{urls}}', str(urls_html))


def replace_video(filled_content, post_info):
    video_html = ''
    if post_info.get('video'):
        video_html = f'''
            <video controls>
                <source src="{str(post_info.get('video'))}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        '''

    return filled_content.replace('{{video}}', video_html)


def replace_audio(filled_content, post_info):
    audio_html = ''
    if post_info.get('audio'):
        audio_html = f'''
            <audio controls>
                <source src="{str(post_info.get('audio'))}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
        '''

    return filled_content.replace('{{audio}}', audio_html)


def replace_optional_fields(filled_content, post_info):
    optional_fields = {
        '{{updated_time}}': post_info.get('updated_time', ''),
        '{{article_published_time}}': post_info.get('article_published_time', ''),
        '{{article_modified_time}}': post_info.get('article_modified_time', ''),
        '{{article_tag}}': post_info.get('article_tag', ''),
        '{{keywords}}': post_info.get('keywords', ''),
    }

    for placeholder, value in optional_fields.items():
        if value:
            filled_content = filled_content.replace(placeholder, str(value))
        else:
            filled_content = re.sub(rf'.*{re.escape(placeholder)}.*\n?', '', filled_content)

    return filled_content


def replace_topic_content(filled_content, topic, topic_number):
    filled_content = replace_title(filled_content, topic, f'{{{{topic{topic_number}_title}}}}')
    filled_content = replace_recent_conflict_levels(filled_content, topic, topic_number)
    filled_content = replace_recent_polemic_levels(filled_content, topic, topic_number)
    filled_content = replace_words_that_matter(filled_content, topic, topic_number)
    filled_content = replace_conflict_awards(filled_content, topic, topic_number)
    filled_content = replace_polemic_awards(filled_content, topic, topic_number)
    filled_content = replace_social_jumps(filled_content, topic, topic_number)
    filled_content = replace_images(filled_content, (topic.get('historical_conflict', []) or []) + (topic.get('historical_polemic', []) or []), f'{{{{images_{topic_number}}}}}')
    filled_content = replace_images(filled_content, (topic.get('historical_conflict_comparison', []) or []) + (topic.get('historical_polemic_comparison', []) or []), '{{comparison_images}}')

    return filled_content


def replace_ranking_content(filled_content, post_info, language, posting_settings):
    filled_content = replace_ranking_field(filled_content, language, posting_settings)

    if 'recent_conflict_levels' in posting_settings['ranking_fields']:
        filled_content = replace_recent_conflict_levels_ranking(filled_content, post_info)
    else:
        filled_content = delete_div(filled_content, 'recent_conflict_levels_ranking')

    if 'recent_polemic_levels' in posting_settings['ranking_fields']:
        filled_content = replace_recent_polemic_levels_ranking(filled_content, post_info)
    else:
        filled_content = delete_div(filled_content, 'recent_polemic_levels_ranking')

    if 'mean_conflict_level' in posting_settings['ranking_fields']:
        filled_content = replace_mean_conflict_levels_ranking(filled_content, post_info)
    else:
        filled_content = delete_div(filled_content, 'mean_conflict_level_ranking')

    if 'mean_polemic_level' in posting_settings['ranking_fields']:
        filled_content = replace_mean_polemic_levels_ranking(filled_content, post_info)
    else:
        filled_content = delete_div(filled_content, 'mean_polemic_level_ranking')

    filled_content = replace_images(filled_content, (post_info[0].get('historical_conflict_comparison', []) or []) + (post_info[0].get('historical_polemic_comparison', []) or []), '{{comparison_images}}')

    return filled_content


def replace_ranking_field(filled_content, language, posting_settings):
    env_data = load_from_env()
    translations_dictionary = env_data.get('translations_dictionary')

    field_names = {
        'recent_conflict_levels': translations_dictionary.get(language).get('recent_conflict_levels'),
        'recent_polemic_levels': translations_dictionary.get(language).get('recent_polemic_levels'),
        'mean_conflict_level': translations_dictionary.get(language).get('mean_conflict_level'),
        'mean_polemic_level': translations_dictionary.get(language).get('mean_polemic_level'),
    }

    ranking_field_names = ', '.join([field_names.get(field, field) for field in posting_settings['ranking_fields']])

    return filled_content.replace('{{ranking_field}}', str(ranking_field_names))


def replace_recent_conflict_levels(filled_content, topic, topic_number):
    conflict_levels = ', '.join([topic.get('recent_conflict_levels', '')])

    return filled_content.replace(f'{{{{conflict_levels_{topic_number}}}}}', str(conflict_levels))


def replace_recent_conflict_levels_ranking(filled_content, post_info):
    conflict_levels_html = ''

    # Sort topics by their recent conflict levels (descending)
    sorted_by_conflict = sorted(post_info, key=lambda post_info_topic: int(post_info_topic.get('recent_conflict_levels', 0)), reverse=True)

    for rank, topic in enumerate(sorted_by_conflict, start=1):
        conflict_levels_html += f'<p>{rank}. {topic.get("title", "Unknown Topic")}: {topic.get("recent_conflict_levels", "N/A")}</p>'

    return filled_content.replace('{{recent_conflict_levels_ranking}}', str(conflict_levels_html))


def replace_mean_conflict_levels_ranking(filled_content, post_info):
    mean_conflict_levels_html = ''

    # Sort topics by their recent conflict levels (descending)
    sorted_by_mean_conflict = sorted(post_info, key=lambda post_info_topic: float(post_info_topic.get('mean_conflict_level', 0)), reverse=True)

    for rank, topic in enumerate(sorted_by_mean_conflict, start=1):
        mean_conflict_levels_html += f'<p>{rank}. {topic.get("title", "Unknown Topic")}: {topic.get("mean_conflict_level", "N/A")}</p>'

    return filled_content.replace('{{mean_conflict_level_ranking}}', str(mean_conflict_levels_html))


def replace_recent_polemic_levels(filled_content, topic, topic_number):
    polemic_levels = ', '.join([topic.get('recent_polemic_levels', '')])

    return filled_content.replace(f'{{{{polemic_levels_{topic_number}}}}}', str(polemic_levels))


def replace_recent_polemic_levels_ranking(filled_content, post_info):
    polemic_levels_html = ''

    # Sort topics by their recent polemic levels (descending)
    sorted_by_polemic = sorted(post_info, key=lambda post_info_topic: int(post_info_topic.get('recent_polemic_levels', 0)), reverse=True)

    for rank, topic in enumerate(sorted_by_polemic, start=1):
        polemic_levels_html += f'<p>{rank}. {topic.get("title", "Unknown Topic")}: {topic.get("recent_polemic_levels", "N/A")}</p>'

    return filled_content.replace('{{recent_polemic_levels_ranking}}', str(polemic_levels_html))


def replace_mean_polemic_levels_ranking(filled_content, post_info):
    mean_polemic_levels_html = ''

    # Sort topics by their recent polemic levels (descending)
    sorted_by_mean_polemic = sorted(post_info, key=lambda post_info_topic: float(post_info_topic.get('mean_polemic_level', 0)), reverse=True)

    for rank, topic in enumerate(sorted_by_mean_polemic, start=1):
        mean_polemic_levels_html += f'<p>{rank}. {topic.get("title", "Unknown Topic")}: {topic.get("mean_polemic_level", "N/A")}</p>'

    return filled_content.replace('{{mean_polemic_level_ranking}}', str(mean_polemic_levels_html))


def delete_div(filled_content, div_id):
    # Initialize BeautifulSoup with the filled content
    soup = BeautifulSoup(filled_content, 'html.parser')

    # Find the div with the specific ID
    mean_polemic_div = soup.find(id=div_id)

    if mean_polemic_div:
        # If the div is found, delete it
        mean_polemic_div.decompose()

    return str(soup)


def replace_words_that_matter(filled_content, topic, topic_number):
    important_words = ', '.join(topic.get('words_that_matter', []))

    return filled_content.replace(f'{{{{important_words_{topic_number}}}}}', str(important_words))


def replace_conflict_awards(filled_content, topic, topic_number):
    conflict_awards = construct_awards_html(topic.get('conflict_awards', {}))

    return filled_content.replace(f'{{{{conflict_awards_{topic_number}}}}}', str(conflict_awards))


def replace_polemic_awards(filled_content, topic, topic_number):
    polemic_awards = construct_awards_html(topic.get('polemic_awards', {}))

    return filled_content.replace(f'{{{{polemic_awards_{topic_number}}}}}', str(polemic_awards))


def replace_social_jumps(filled_content, topic, topic_number):
    social_jumps = ', '.join([f"<a href='{jump['link']}'>{jump['title']}</a>" for jump in topic.get('social_jumps', [])])

    return filled_content.replace(f'{{{{social_jumps_{topic_number}}}}}', str(social_jumps))


def clear_second_topic_placeholders(filled_content):
    placeholders = [
        '{{topic2_title}}',
        '{{conflict_levels_2}}',
        '{{polemic_levels_2}}',
        '{{important_words_2}}',
        '{{conflict_awards_2}}',
        '{{polemic_awards_2}}',
        '{{social_jumps_2}}',
        '{{images_2}}'
    ]

    for placeholder in placeholders:
        filled_content = re.sub(rf'{placeholder}.*\n?', '', filled_content)

    return filled_content


def replace_main_title(filled_content, topics, template):
    if template == 'summary':
        title = f"Summary for {topics[0].get('title', 'Topic 1')} Negapedia page"
    elif template == 'comparison':
        title = f"Comparison between {topics[0].get('title', 'Topic 1')} and {topics[1].get('title', 'Topic 2')} Negapedia pages"
    elif template == 'ranking':
        topic_titles = [topic.get('title', f'Topic {i + 1}') for i, topic in enumerate(topics)]
        title = f"Ranking comparison between Negapedia topics pages: {', '.join(topic_titles)}"
    else:
        title = "Negapedia Page Analysis"

    return filled_content.replace('{{title}}', str(title))


# Constructing awards sections dynamically
def construct_awards_html(awards_dict):
    awards_html = ""
    # Global awards
    if 'all' in awards_dict and awards_dict['all']:
        awards_html += "<strong>GLOBAL (IN ALL WIKIPEDIA):</strong><br>"
        awards_html += "<br>".join([f"- {award}" for award in awards_dict['all']])
        awards_html += "<br>"

    # Category-specific awards
    for category, awards in awards_dict.items():
        if category != 'all' and awards:
            awards_html += f"<strong>CATEGORY SPECIFIC ({category.upper()}):</strong><br>"
            awards_html += "<br>".join([f"- {award}" for award in awards])
            awards_html += "<br>"

    return awards_html
