import os


def parse_image_id_from_url(url):
    parts = url.split('/')
    index = parts.index('image') + 1
    return int(parts[index])


def parse_filename_from_url(url):
    return os.path.basename(url)[1:]