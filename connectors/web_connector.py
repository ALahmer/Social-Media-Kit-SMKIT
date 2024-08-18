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
        with open('templates/comparison_template.html', 'r') as template_file:
            template_content = template_file.read()
    elif template == 'summary':
        with open('templates/summary_template.html', 'r') as template_file:
            template_content = template_file.read()
    else:
        print("Passed template is not accepted.")
        return

    url = post_info.get('url')
    title = post_info.get('title', f"Check out this topic at {url}")
    description = post_info.get('description', f"Check out this topic at {url}")

    images_paths = []
    image = {
        'location': "web",
        'src': post_info.get('image')
    }
    images_paths.append(image)

    images_html = ''.join([
        (f'<img src="../{image_path["src"]}" alt="Image">' if image_path['location'] == 'local'
        else f'<img src="{image_path["src"]}" alt="Image">')
        for image_path in images_paths
    ])  # {{to_test}} for negapedia and multiple plots

    # Replace placeholders with dynamic content and ensure all values are strings
    filled_content = template_content
    filled_content = filled_content.replace('{{title}}', str(title))
    filled_content = filled_content.replace('{{description}}', str(description))
    filled_content = filled_content.replace('{{images}}', str(images_html))
    filled_content = filled_content.replace('{{url}}', str(post_info.get('url', url)))

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
