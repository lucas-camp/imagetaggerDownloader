import os


def parse_image_id_from_url(url):
    return int(url.split('/')[6])


def parse_filename_from_url(url):
    return os.path.basename(url)[1:]