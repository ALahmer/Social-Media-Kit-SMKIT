import os
import re
from datetime import datetime


def post_on_web(post_info, template, language, module):
    # Ensure the 'pages_to_post' directory exists
    output_dir = 'pages_to_post'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load the HTML template
    if template == 'comparison':
        with open(f'templates/{language}/{module}/web_post_comparison_template.html', 'r') as template_file:
            template_content = template_file.read()
    elif template == 'summary':
        with open(f'templates/{language}/{module}/web_post_summary_template.html', 'r') as template_file:
            template_content = template_file.read()
    else:
        print("Passed template is not accepted.")
        return

    filled_content = template_content

    if module == 'generic':     # {{to_fix}} mettere in else senza 'generic'
        title = post_info.get('title') or "No Title"
        description = post_info.get('message') or post_info.get('description') or "No Description"

        images_html = ''
        for image_info in post_info.get('images', []):
            src = image_info.get('image')
            width = image_info.get('image_width')
            height = image_info.get('image_height')
            alt = image_info.get('image_alt') or "Image"
            location = image_info.get('location')

            src_prefix = "" if location == "web" else "../"

            if width and height:
                image_tag = f'<img src="{src_prefix}{src}" alt="{alt}" width="{width}" height="{height}">'
            else:
                image_tag = f'<img src="{src_prefix}{src}" alt="{alt}">'

            images_html += image_tag

        urls_html = ''
        for url in post_info.get('urls', []):
            url_tag = f'<li><a href="{url}">{url}</a></li>'
            urls_html += url_tag

        # Replace placeholders with dynamic content and ensure all values are strings
        filled_content = template_content
        filled_content = filled_content.replace('{{title}}', str(title))
        filled_content = filled_content.replace('{{description}}', str(description))
        filled_content = filled_content.replace('{{images}}', str(images_html))
        filled_content = filled_content.replace('{{urls}}', str(urls_html))

        # Manually insert video and audio if they exist
        video_html = ''
        if post_info.get('video'):
            video_html = f'''
                <video controls>
                    <source src="{str(post_info.get('video'))}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            '''
        filled_content = filled_content.replace('{{video}}', video_html)

        audio_html = ''
        if post_info.get('audio'):
            audio_html = f'''
                <audio controls>
                    <source src="{str(post_info.get('audio'))}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
            '''
        filled_content = filled_content.replace('{{audio}}', audio_html)

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
    elif module == 'negapedia':
        # Handle NegapediaPageInfo for comparison
        topic1 = post_info[0]
        topic2 = post_info[1] if len(post_info) > 1 else None

        # Process first topic
        topic1_title = topic1.get('title', 'Topic 1')
        # conflict_levels_1 = ', '.join([f"{level['url']}: {level['conflict_level']}" for level in topic1.get('recent_conflict_levels', [])])
        # polemic_levels_1 = ', '.join([f"{level['url']}: {level['polemic_level']}" for level in topic1.get('recent_polemic_levels', [])])
        conflict_levels_1 = ', '.join([f"{level['conflict_level']}" for level in topic1.get('recent_conflict_levels', [])])
        polemic_levels_1 = ', '.join([f"{level['polemic_level']}" for level in topic1.get('recent_polemic_levels', [])])
        important_words_1 = ', '.join(topic1.get('words_that_matter', []))
        conflict_awards_1 = ', '.join(topic1.get('conflict_awards', []))
        polemic_awards_1 = ', '.join(topic1.get('polemic_awards', []))
        social_jumps_1 = ', '.join([f"<a href='{jump['link']}'>{jump['title']}</a>" for jump in topic1.get('social_jumps', [])])

        images_html_1 = ''
        for image_info in topic1.get('historical_conflict', []) + topic1.get('historical_polemic', []):
            src = image_info.get('image')
            width = image_info.get('image_width')
            height = image_info.get('image_height')
            alt = image_info.get('image_alt') or "Image"
            location = image_info.get('location')

            src_prefix = "" if location == "web" else "../"

            if width and height:
                image_tag = f'<img src="{src_prefix}{src}" alt="{alt}" width="{width}" height="{height}">'
            else:
                image_tag = f'<img src="{src_prefix}{src}" alt="{alt}">'

            images_html_1 += image_tag

        # Replace placeholders for the first topic
        filled_content = filled_content.replace('{{topic1_title}}', str(topic1_title))
        filled_content = filled_content.replace('{{conflict_levels_1}}', str(conflict_levels_1))
        filled_content = filled_content.replace('{{polemic_levels_1}}', str(polemic_levels_1))
        filled_content = filled_content.replace('{{important_words_1}}', str(important_words_1))
        filled_content = filled_content.replace('{{conflict_awards_1}}', str(conflict_awards_1))
        filled_content = filled_content.replace('{{polemic_awards_1}}', str(polemic_awards_1))
        filled_content = filled_content.replace('{{social_jumps_1}}', str(social_jumps_1))
        filled_content = filled_content.replace('{{images_1}}', str(images_html_1))

        # Process second topic if it exists
        if topic2:
            topic2_title = topic2.get('title', 'Topic 2')
            # conflict_levels_2 = ', '.join([f"{level['url']}: {level['conflict_level']}" for level in topic2.get('recent_conflict_levels', [])])
            # polemic_levels_2 = ', '.join([f"{level['url']}: {level['polemic_level']}" for level in topic2.get('recent_polemic_levels', [])])
            conflict_levels_2 = ', '.join([f"{level['conflict_level']}" for level in topic2.get('recent_conflict_levels', [])])
            polemic_levels_2 = ', '.join([f"{level['polemic_level']}" for level in topic2.get('recent_polemic_levels', [])])
            important_words_2 = ', '.join(topic2.get('words_that_matter', []))
            conflict_awards_2 = ', '.join(topic2.get('conflict_awards', []))
            polemic_awards_2 = ', '.join(topic2.get('polemic_awards', []))
            social_jumps_2 = ', '.join([f"<a href='{jump['link']}'>{jump['title']}</a>" for jump in topic2.get('social_jumps', [])])

            images_html_2 = ''
            for image_info in topic2.get('historical_conflict', []) + topic2.get('historical_polemic', []):
                src = image_info.get('image')
                width = image_info.get('image_width')
                height = image_info.get('image_height')
                alt = image_info.get('image_alt') or "Image"
                location = image_info.get('location')

                src_prefix = "" if location == "web" else "../"

                if width and height:
                    image_tag = f'<img src="{src_prefix}{src}" alt="{alt}" width="{width}" height="{height}">'
                else:
                    image_tag = f'<img src="{src_prefix}{src}" alt="{alt}">'

                images_html_2 += image_tag

            # Replace placeholders for the second topic
            filled_content = filled_content.replace('{{topic2_title}}', str(topic2_title))
            filled_content = filled_content.replace('{{conflict_levels_2}}', str(conflict_levels_2))
            filled_content = filled_content.replace('{{polemic_levels_2}}', str(polemic_levels_2))
            filled_content = filled_content.replace('{{important_words_2}}', str(important_words_2))
            filled_content = filled_content.replace('{{conflict_awards_2}}', str(conflict_awards_2))
            filled_content = filled_content.replace('{{polemic_awards_2}}', str(polemic_awards_2))
            filled_content = filled_content.replace('{{social_jumps_2}}', str(social_jumps_2))
            filled_content = filled_content.replace('{{images_2}}', str(images_html_2))
        else:
            # If no second topic is provided, clear the placeholders for topic 2
            filled_content = re.sub(r'{{topic2_title}}.*\n?', '', filled_content)
            filled_content = re.sub(r'{{conflict_levels_2}}.*\n?', '', filled_content)
            filled_content = re.sub(r'{{polemic_levels_2}}.*\n?', '', filled_content)
            filled_content = re.sub(r'{{important_words_2}}.*\n?', '', filled_content)
            filled_content = re.sub(r'{{conflict_awards_2}}.*\n?', '', filled_content)
            filled_content = re.sub(r'{{polemic_awards_2}}.*\n?', '', filled_content)
            filled_content = re.sub(r'{{social_jumps_2}}.*\n?', '', filled_content)
            filled_content = re.sub(r'{{images_2}}.*\n?', '', filled_content)

        # Replace placeholders for the general title
        if template == 'comparison':
            title = f"Comparison between {topic1_title} and {topic2_title} Negapedia pages"
        else:
            title = f"Summary for {topic1_title} Negapedia page"
        filled_content = filled_content.replace('{{title}}', str(title))


    # Create a unique filename based on the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"post_{timestamp}.html"
    file_path = os.path.join(output_dir, filename)

    # Write the filled content to the output HTML file
    with open(file_path, 'w') as output_file:
        output_file.write(filled_content)

    print(f"Web page created successfully: {file_path}")
    return file_path
