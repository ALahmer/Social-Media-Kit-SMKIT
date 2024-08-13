import requests
from io import BytesIO
from PIL import Image
from datetime import datetime


def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        print(f"Failed to download image from {url}")
        return None


def get_downloaded_image_path(image_path_src):
    image_data = download_image(image_path_src)
    with Image.open(image_data) as img:
        timestamp = datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S")
        image_path_src = "images_to_post/temp_image_" + timestamp + ".jpg"
        img.save(image_path_src)
