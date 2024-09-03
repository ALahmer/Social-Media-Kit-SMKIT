import os
import re
from datetime import datetime


def post_on_web(post_info, template, language, module):
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
        filled_content = convert_negapediapageinfo_to_filled_content(post_info, filled_content, template)
    else:
        filled_content = convert_pageinfo_to_filled_content(post_info, filled_content, template)

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


def convert_negapediapageinfo_to_filled_content(post_info, filled_content, template):
    # Handle NegapediaPageInfo
    topic1 = post_info[0]
    topic2 = post_info[1] if len(post_info) > 1 else None

    # Process first topic
    filled_content = replace_topic_content(filled_content, topic1, '1')

    # Process second topic if it exists
    if topic2:
        filled_content = replace_topic_content(filled_content, topic2, '2')
    else:
        filled_content = clear_second_topic_placeholders(filled_content)    # {{to_check}} do we really need it?

    # Replace placeholders for the general title
    filled_content = replace_main_title(filled_content, topic1, topic2, template)

    # Replace placeholders for the page description
    filled_content = replace_description(filled_content, topic1)

    return filled_content


def convert_pageinfo_to_filled_content(post_info, filled_content, template):
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


def replace_recent_conflict_levels(filled_content, topic, topic_number):
    conflict_levels = ', '.join([topic.get('recent_conflict_levels', [])])

    return filled_content.replace(f'{{{{conflict_levels_{topic_number}}}}}', str(conflict_levels))


def replace_recent_polemic_levels(filled_content, topic, topic_number):
    polemic_levels = ', '.join([topic.get('recent_polemic_levels', [])])

    return filled_content.replace(f'{{{{polemic_levels_{topic_number}}}}}', str(polemic_levels))


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


def replace_main_title(filled_content, topic1, topic2, template):
    if template == 'comparison':
        title = f"Comparison between {topic1.get('title', 'Topic 1')} and {topic2.get('title', 'Topic 2')} Negapedia pages"
    else:
        title = f"Summary for {topic1.get('title', 'Topic 1')} Negapedia page"

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
