import os
from datetime import datetime


def post_on_web(title, message, image_paths, template):
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

    # Replace placeholders with dynamic content
    images_html = ''.join([(f'<img src="../{image_path["src"]}" alt="Image">' if image_path['location'] == 'local' else f'<img src="{image_path["src"]}" alt="Image">') for image_path in image_paths])
    filled_content = template_content.replace('{{title}}', title)
    filled_content = filled_content.replace('{{message}}', message)
    filled_content = filled_content.replace('{{images}}', images_html)

    # Create a unique filename based on the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"post_{timestamp}.html"
    file_path = os.path.join(output_dir, filename)

    # Write the filled content to the output HTML file
    with open(file_path, 'w') as output_file:
        output_file.write(filled_content)

    print(f"Web page created successfully: {file_path}")
    return file_path
