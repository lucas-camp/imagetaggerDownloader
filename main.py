import argparse
import getpass
import os
import sys

from http_requests import RequestHandler, ImageSetNotFoundError, ImageSetPermissionError
from utils import parse_image_id_from_url
from png import read_label_chunk, write_label_chunk
from protobuf import decode_data, encode_data


def main():
    # parse arguments
    parser = argparse.ArgumentParser(prog='imagesetDownloader',
                                     description='Download an immageset and write label data in protobuf chunk')
    parser.add_argument('-d', '--destination', type=str, help='specify the output directory (absolute path)')
    parser.add_argument('-n', '--no-label-data', dest='label_data', action='store_false',
                        default=True, help='do not write the label data in protobuf chunk')
    parser.add_argument('imageset_id', type=int, help='the id of the imageset that is downloaded')

    args = parser.parse_args()

    imageset_id = args.imageset_id
    destination = args.destination if args.destination else '.'
    label_data = args.label_data

    # request handler
    requestHandler = RequestHandler()

    # get login data
    username = input('Username: ')
    password = getpass.getpass('Password: ')

    # try to log in
    if not (requestHandler.login(username, password)):
       print("Invalid username or password. Could not login.")
       sys.exit()

    requestHandler.login(username, password)

    # try to get the image links from imageset with id imageset_id
    try:
        image_links = requestHandler.get_image_links(imageset_id)
    except (ImageSetNotFoundError, ImageSetPermissionError) as e:
        print(e)
        sys.exit()

    for i, link in enumerate(sorted(image_links)):
        # some debug messages
        print('Downloading image {} of {}'.format(i+1, len(image_links)))

        # get the id of the image
        id = parse_image_id_from_url(link)

        # ugly
        name = os.path.basename(link)[1:]

        # concatenate file path
        file_path = os.path.join(destination, name)

        # do not write the labels data in protobuf chunk
        if not label_data:
            requestHandler.download_image(link, file_path, False)
        # write the labels in protobuf chunk
        else:
            # download image in file like object
            image_data = requestHandler.download_image(link, file_path, True)

            # decode protobuf
            protobuf = decode_data(image_data, True)

            # get annotations
            annotations = requestHandler.get_annotations(id)

            # add annotations if there are any
            if annotations:
                for type, bounding_box in annotations:
                    if type == 'ball':
                        type_ = protobuf.balls.add()
                    elif type == 'robot':
                        type_ = protobuf.robots.add()
                    elif type == 'obstacle':
                        continue
                    else:
                        raise NotImplementedError

                    # per convention, if the type does not exist in the image
                    # all coordinates are set to -1
                    if bounding_box is None:
                        type_.label.boundingBox.upperLeft.x = -1
                        type_.label.boundingBox.upperLeft.y = -1
                        type_.label.boundingBox.lowerRight.x = -1
                        type_.label.boundingBox.lowerRight.y = -1
                    else:
                        type_.label.boundingBox.upperLeft.x = bounding_box['x1']
                        type_.label.boundingBox.upperLeft.y = bounding_box['y1']
                        type_.label.boundingBox.lowerRight.x = bounding_box['x2']
                        type_.label.boundingBox.lowerRight.y = bounding_box['y2']

            # encode protobuf
            encoded_protobuf = encode_data(protobuf)

            # write out the image incl protobuf
            write_label_chunk(file_path, image_data, encoded_protobuf, True)


if __name__ == '__main__':
    main()
