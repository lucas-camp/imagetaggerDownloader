import json
import requests
import shutil

from io import BytesIO

from constants import BASE_URL, IMAGE_LIST_BASE_URL, LOAD_ANNOTATION_URL, LOGIN_URL


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

    def get_image_links(self, imageset_id):
        url = IMAGE_LIST_BASE_URL + str(imageset_id)
        response = self._get(url)

        if response.status_code == 404:
            raise ImageSetNotFoundError('The imageset with id {} does not exist on the server.'.format(imageset_id))

        if response.status_code == 403:
            raise ImageSetPermissionError('You do not have permission to download the imageset with id {}.'
                                         .format(imageset_id))

        links = [BASE_URL + link[:-1] for link in response.text.split()]

        return links

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

    def download_image(self, image_link, file_path, in_memory):
        response = self._session.get(image_link, stream=True)
        response.raw.decode_content = True
        if not in_memory:
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
                return
        else:
            return BytesIO(response.raw.data)


class ImageSetNotFoundError(Exception):

    def __init__(self, message):
        super().__init__(message)


class ImageSetPermissionError(Exception):

    def __init__(self, message):
        super().__init__(message)
