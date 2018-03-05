import argparse
import os
import sys
import getpass

from exporters.csv_exporter import CSVExporter
from exporters.png_exporter import PNGExporter
from exporters.protobuf_exporter import ProtobufExporter
from exporters.xml_tensorflow_exporter import XMLTensorFlowExporter
from http_util.http_requests import RequestHandler, ImageSetNotFoundError, ImageSetPermissionError
from utils import parse_image_id_from_url, parse_filename_from_url


def main():
    # parse arguments
    parser = argparse.ArgumentParser(prog='imagesetDownloader',
                                     description='Download an immageset and write label data in protobuf chunk')

    parser.add_argument('-d', '--destination', type=str, help='specify the output directory (absolute path)')
    parser.add_argument('-p', '--protobuf-label-data', dest='protobuf_labels', action='store_true', default=False,
                        help='Save annotations in label chunk of the png file.')
    parser.add_argument('-x', '--xml-tensorflow-label-data', dest='xml_tensorflow_labels', action='store_true',
                        default=True, help='Save annotations in XML files')
    parser.add_argument('-c', '--csv-label-data', dest='csv_labels', action='store_true', default=False,
                        help='Save annotations in CSV files.')
    parser.add_argument('-n', '--no-images', dest='no_images', action='store_true', default=False,
                        help='Do not download the images.')
    parser.add_argument('imageset_id', type=int, help='the id of the imageset that is downloaded')

    args = parser.parse_args()

    imageset_id = args.imageset_id
    destination = args.destination if args.destination else '.'
    protobuf_labels = args.protobuf_labels
    xml_tensorflow_labels = args.xml_tensorflow_labels
    csv_labels = args.csv_labels
    no_images = args.no_images

    if protobuf_labels and no_images:
        print("Invalid options, -n nad -p are not compatible")
        sys.exit()

    # request handler
    request_handler = RequestHandler()

    # get login data
    username = input('Username: ')
    password = getpass.getpass('Password: ')

    # try to log in
    if not (request_handler.login(username, password)):
        print("Invalid username or password. Could not login.")
        sys.exit()

    # try to get the infos and image links from imageset with id imageset_id
    try:
        imageset_infos = request_handler.get_dataset_infos(imageset_id)
        image_links = request_handler.get_image_links(imageset_id)
    except (ImageSetNotFoundError, ImageSetPermissionError) as e:
        print(e)
        sys.exit()

    exporters = []

    if not protobuf_labels and not no_images:
        png_exporter = PNGExporter(imageset_id, imageset_infos, destination)
        png_exporter.setup()
        exporters.append(png_exporter)
    if csv_labels:
        csv_exporter = CSVExporter(imageset_id, imageset_infos, destination)
        csv_exporter.setup(csvfile_path=destination + '/annotations.csv')
        exporters.append(csv_exporter)
    if protobuf_labels:
        protobuf_exporter = ProtobufExporter(imageset_id, imageset_infos, destination)
        protobuf_exporter.setup()
        exporters.append(protobuf_exporter)
    if xml_tensorflow_labels:
        xml_tensorflow_exporter = XMLTensorFlowExporter(imageset_id, imageset_infos, destination)
        xml_tensorflow_exporter.setup()
        exporters.append(xml_tensorflow_exporter)

    # if csv_labels:
    #     csv_file = open('{}/annotations.csv'.format(destination), 'w')

    for i, image_link in enumerate(image_links):
        # some debug messages
        print('Downloading image {} of {} in image set {}'.format(i + 1, len(image_links), imageset_infos['name']))

        # get the id of the image
        image_id = parse_image_id_from_url(image_link)

        # get the name of the image
        image_name = parse_filename_from_url(image_link)

        # concatenate file path
        file_path = os.path.join(destination, image_name)

        # download image in file like object
        if not no_images or xml_tensorflow_labels:
            image_data = request_handler.download_image(image_link)
        else:
            image_data = None

        # get annotations
        annotations = request_handler.get_annotations(image_id)

        # call all exporters
        for exporter in exporters:
            exporter.handle_annotation(image_data, image_name, annotations, file_path=file_path)

    for exporter in exporters:
        exporter.finish()


if __name__ == '__main__':
    main()
    sys.exit()