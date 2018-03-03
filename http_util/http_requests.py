import json
from io import BytesIO

import requests
from lxml import html

from constants import IMAGE_LINK_URL, IMAGE_LIST_URL, IMAGE_SET_URL, LOAD_ANNOTATION_URL, LOGIN_URL, \
    IMAGE_SET_NAME_XPATH, IMAGE_SET_TEAM_XPATH, IMAGE_SET_LOCATION_XPATH, IMAGE_SET_DESCRIPTION_XPATH


class RequestHandler:

    def __init__(self):
        # get the csrf token
        session = requests.session()
        response = session.get(LOGIN_URL)

        self._session = session
        self._crsf_token = session.cookies['csrftoken']

    def login(self, username, password):
        post_data = {'username': username, 'password': password, 'csrfmiddlewaretoken': self._crsf_token}
        headers = {'Referer': LOGIN_URL}
        response = self._session.post(LOGIN_URL, data=post_data, headers=headers)

        # bad test, slow
        if 'Login' in response.text:
            success = False
        else:
            success = True

        return success

    def _get(self, url, params=None):
        headers = {'Referer': url}
        response = self._session.get(url, headers=headers, cookies=self._session.cookies, params=params)

        return response

    def get_dataset_infos(self, imageset_id):
        url = IMAGE_SET_URL.format(imageset_id=imageset_id)
        response = self._get(url)

        if response.status_code == 404:
            raise ImageSetNotFoundError('The imageset with id {} does not exist on the server.'.format(imageset_id))

        if response.status_code == 403:
            raise ImageSetPermissionError('You do not have permission to download the imageset with id {}.'
                                         .format(imageset_id))

        tree = html.fromstring(response.content)

        name = tree.xpath(IMAGE_SET_NAME_XPATH)[0].text
        team = tree.xpath(IMAGE_SET_TEAM_XPATH)[0].text
        location = tree.xpath(IMAGE_SET_LOCATION_XPATH)[0].text
        description = tree.xpath(IMAGE_SET_DESCRIPTION_XPATH)[0].text

        return {'name': name, 'team': team, 'location': location, 'description': description}

    def get_image_links(self, imageset_id):
        url = IMAGE_LIST_URL.format(imageset_id=imageset_id)
        response = self._get(url)

        if response.status_code == 404:
            raise ImageSetNotFoundError('The imageset with id {} does not exist on the server.'.format(imageset_id))

        if response.status_code == 403:
            raise ImageSetPermissionError('You do not have permission to download the imageset with id {}.'
                                         .format(imageset_id))

        links = [IMAGE_LINK_URL.format(image_link=link.strip()) for link in response.text.split(',') if link.strip()]

        return sorted(links)

    def get_annotations(self, image_id):
        params = {'image_id': image_id}
        response = self._get(LOAD_ANNOTATION_URL, params)

        encoded_json = json.loads(response.text)['annotations']

        # no annotations found
        if not encoded_json:
            return None

        annotations = []

        for annotation in encoded_json:
            type = annotation['annotation_type']['name']
            content = annotation['content']
            if content == 'Not in image':
                bounding_box = None
            else:
                bounding_box = content

            annotations.append((type, bounding_box))

        return annotations

    def download_image(self, image_link):
        response = self._session.get(image_link, stream=True)
        response.raw.decode_content = True

        return BytesIO(response.raw.data)


class ImageSetNotFoundError(Exception):

    def __init__(self, message):
        super().__init__(message)


class ImageSetPermissionError(Exception):

    def __init__(self, message):
        super().__init__(message)
