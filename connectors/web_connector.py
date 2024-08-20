import os
import re
from datetime import datetime


def post_on_web(post_info, template):
    # Ensure the 'pages_to_post' directory exists
    output_dir = 'pages_to_post'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load the HTML template
    if template == 'comparison':
        with open('templates/web_post_comparison_template.html', 'r') as template_file:
            template_content = template_file.read()
    elif template == 'summary':
        with open('templates/web_post_summary_template.html', 'r') as template_file:
            template_content = template_file.read()
    else:
        print("Passed template is not accepted.")
        return

    title = post_info.get('title') or "No Title"
    description = post_info.get('description') or "No Description"

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

    # Create a unique filename based on the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"post_{timestamp}.html"
    file_path = os.path.join(output_dir, filename)

    # Write the filled content to the output HTML file
    with open(file_path, 'w') as output_file:
        output_file.write(filled_content)

    print(f"Web page created successfully: {file_path}")
    return file_path
