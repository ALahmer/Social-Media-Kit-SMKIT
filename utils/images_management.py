import requests
from io import BytesIO
from PIL import Image
from datetime import datetime
import os
import cairosvg
from utils.env_management import load_from_env


def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        print(f"Failed to download image from {url}")
        return None


def get_downloaded_image_path(image_path_src):
    env_data = load_from_env()
    posts_images_absolute_destination_path = env_data.get('posts_images_absolute_destination_path')

    image_data = download_image(image_path_src)
    with Image.open(image_data) as img:
        original_format = img.format.lower()
        timestamp = datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")
        image_path_src = f"{posts_images_absolute_destination_path}temp_image_{timestamp}.{original_format}"
        img.save(image_path_src)
    return image_path_src


def save_svg(svg_element, div_container_name):
    """
    Save the SVG content to a file.
    """
    env_data = load_from_env()
    posts_images_absolute_destination_path = env_data.get('posts_images_absolute_destination_path')

    svg_content = str(svg_element)
    timestamp = datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")
    svg_filename = f"{div_container_name}_extracted_svg_file_{timestamp}.svg"
    svg_file_path = os.path.join(posts_images_absolute_destination_path, svg_filename)
    with open(svg_file_path, 'w') as f:
        f.write(svg_content)
    print(f"SVG saved at: {svg_file_path}")
    return svg_file_path


def convert_svg_to_png(svg_file_path):
    """
    Convert the saved SVG file to a PNG image.
    """
    png_file_path = svg_file_path.replace('.svg', '.png')
    cairosvg.svg2png(url=svg_file_path, write_to=png_file_path)
    print(f"SVG file {svg_file_path} converted to PNG: {png_file_path}")
    return png_file_path
