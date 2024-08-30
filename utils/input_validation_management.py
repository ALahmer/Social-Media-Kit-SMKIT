import os
import filetype
from utils.env_management import load_from_env

env_data = load_from_env()


def get_input_parameter_web_urls(input_paths, module, args_remove_suffix, args_base_directory=None, args_base_url=None):
    web_urls = []
    for input_path in input_paths:
        web_url = process_input(input_path, module, args_remove_suffix, args_base_directory, args_base_url)
        web_urls.extend(web_url)
    return web_urls


def process_input(input_path, module, args_remove_suffix, args_base_directory=None, args_base_url=None):
    """
    Processes a given input path, handling URLs, files, and directories.
    Maps local paths to web URLs if base_dir and base_url are provided.
    """
    if args_base_directory and args_base_url:
        base_dir = args_base_directory
        base_url = args_base_url
    else:
        base_dir = env_data.get('modules').get(f'{module}').get('filesystem_website_base_directory')
        base_url = env_data.get('modules').get(f'{module}').get('website_base_url')

    if not base_dir or not base_url:
        raise ValueError("Base directory or base URL is not defined in the environment data.")

    if is_url(input_path):
        return [input_path]

    if os.path.isfile(input_path):
        return process_file(input_path, args_remove_suffix, base_dir, base_url)

    if os.path.isdir(input_path):
        print(f"Processing directory: {input_path}")
        return process_directory(input_path, args_remove_suffix, base_dir, base_url)

    raise ValueError(f"Invalid input path provided: {input_path}")


def is_url(path):
    return path.startswith(('http://', 'https://'))


def process_file(input_path, args_remove_suffix, base_dir, base_url):
    """
    Processes a single file, checks if it is compressed, and maps to the corresponding web URL.
    """
    print(f"Processing local file: {input_path}")

    if is_compressed_file(input_path):
        input_path = remove_compression_suffix(input_path)

    if args_remove_suffix:
        if has_extension_suffix(input_path):
            input_path = remove_extension_suffix(input_path)

    web_url = map_local_path_to_url(input_path, base_dir, base_url)
    print(f"Mapped local file to web URL: {web_url}")
    return [web_url]


def process_directory(directory_path, args_remove_suffix, base_dir, base_url):
    """
    Processes all files in a directory, mapping them to their corresponding web URLs.
    """
    web_urls = []
    for root, _, files in os.walk(directory_path):  # {{to_check}} if other directories and files are in the scanned path, those will be processed...what to do? Exclude all files except html htm and compressed file?
        for filename in files:
            filepath = os.path.join(root, filename)
            web_urls.extend(process_file(filepath, args_remove_suffix, base_dir, base_url))
    return web_urls


def map_local_path_to_url(local_path, base_dir, base_url):
    """
    Maps a local file path to a corresponding web URL.
    """
    if not local_path.startswith(base_dir):
        raise ValueError(f"Local path {local_path} does not match the base directory {base_dir}.")

    # Strip the base directory from the local path
    relative_path = os.path.relpath(local_path, base_dir)

    # Replace backslashes with forward slashes (for Windows paths)
    relative_path = relative_path.replace(os.path.sep, '/')

    # Construct the URL by combining the base URL and relative path
    web_url = f"{base_url}/{relative_path}"

    return web_url


def is_compressed_file(filepath):
    """
    Determines if a file is compressed based on its MIME type.
    """
    kind = filetype.guess(filepath)
    if kind:
        return kind.mime.startswith(('application/x-', 'application/')) and kind.extension in ['gz', 'bz2', 'xz', 'zip', '7z', 'tar']
    return False


def has_extension_suffix(filepath):
    """
    Determines if a file has a .html or .htm suffix (extension).
    """
    return filepath.endswith(('.html', '.htm'))


def remove_compression_suffix(filepath):
    """
    Removes the compression-related suffix from a filepath.
    """
    if filepath.endswith(('.html.gz', '.html.xz', '.html.7z')):
        return filepath[:-8]
    elif filepath.endswith(('.html.bz2', '.html.zip', '.html.tar')):
        return filepath[:-9]
    return filepath


def remove_extension_suffix(filepath):
    """
    Removes the .html or .htm suffix from a filepath.
    """
    if filepath.endswith('.html'):
        return filepath[:-5]
    elif filepath.endswith('.htm'):
        return filepath[:-4]
    return filepath
