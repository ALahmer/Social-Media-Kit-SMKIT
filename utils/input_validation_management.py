import os
import filetype
from utils.env_management import load_from_env


env_data = load_from_env()


def get_input_parameter_web_urls(input_paths):
    web_urls = []
    for input_path in input_paths:
        web_url = process_input(input_path)
        web_urls = web_urls + web_url
    return web_urls


def process_input(input_path):
    """
    Processes a given input path, handling URLs, files, and directories.
    Maps local paths to web URLs if base_dir and base_url are provided.
    """
    base_dir = env_data['filesystem_website_base_directory']
    base_url = env_data['website_base_url']
    if is_url(input_path):
        web_url = input_path
        return [web_url]

    elif os.path.isfile(input_path):
        print(f"Processing local file: {input_path}")

        is_compressed = is_compressed_file(input_path)
        if is_compressed:
            # Remove unnecessary suffixes (e.g., .html.gz)
            if input_path.endswith('.html.gz') or input_path.endswith('.html.xz') or input_path.endswith('.html.7z'):
                input_path = input_path[:-8]
            elif input_path.endswith('.html.bz2') or input_path.endswith('.html.zip') or input_path.endswith('.html.tar'):
                input_path = input_path[:-9]

        if base_dir and base_url:
            web_url = map_local_path_to_url(input_path, base_dir, base_url)
            print(f"Mapped local file to web URL: {web_url}")
            return [web_url]

    elif os.path.isdir(input_path):
        print(f"Processing directory: {input_path}")
        web_urls = []
        for root, _, files in os.walk(input_path):
            for filename in files:
                filepath = os.path.join(root, filename)
                response = process_input(filepath)
                web_urls = web_urls + response
        return web_urls
    else:
        raise ValueError("Invalid input path provided.")

    return []


def is_url(path):
    return path.startswith('http://') or path.startswith('https://')


def map_local_path_to_url(local_path, base_dir, base_url):
    """
    Maps a local file path to a corresponding web URL.
    """
    if not local_path.startswith(base_dir):
        raise ValueError("Local path does not match the base directory.")

    # Strip the base directory from the local path
    relative_path = os.path.relpath(local_path, base_dir)

    # Replace backslashes with forward slashes (for Windows paths)
    relative_path = relative_path.replace(os.path.sep, '/')

    # Construct the URL by combining the base URL and relative path
    web_url = f"{base_url}/{relative_path}"

    return web_url


def is_compressed_file(filepath):
    kind = filetype.guess(filepath)
    compressed_types = ['gz', 'bz2', 'xz', 'zip', '7z', 'tar']
    if kind:
        return kind.extension in compressed_types
    return False
