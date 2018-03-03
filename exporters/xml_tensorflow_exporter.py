import os
from lxml import etree

from exporters.exporter import Exporter
from protobuf.protobuf import decode_data


class XMLTensorFlowExporter(Exporter):

    def __init__(self, imageset_id, imageset_infos, destination):
        super().__init__(imageset_id, imageset_infos, destination, 'XMLTensorFlowExporter')

    def setup(self, *arg, **kwargs):
        self._xml_directory = os.path.join(self._destination, 'annotations')
        if not os.path.exists(self._xml_directory):
            os.makedirs(self._xml_directory)

    def finish(self, *args, **kwargs):
        pass

    def handle_annotation(self, image_data, image_name, annotations, *args, **kwargs):
        file_path = '{}.{}'.format(image_name[:-4], 'xml')

        decoded_protobuf = decode_data(image_data)
        width = decoded_protobuf.cameraInformation.resolution.width
        height = decoded_protobuf.cameraInformation.resolution.height

        root = etree.Element("annotation")

        etree.SubElement(root, "filename").text = image_name

        size = etree.SubElement(root, "size")
        etree.SubElement(size, "width").text = str(width)
        etree.SubElement(size, "height").text = str(height)
        etree.SubElement(size, "depth").text = "3"

        if annotations:
            for annotation in annotations:
                type, bounding_box = annotation

                if bounding_box is not None:
                    x_min = bounding_box['x1']
                    x_max = bounding_box['x2']
                    y_min = bounding_box['y1']
                    y_max = bounding_box['y2']

                    object = etree.SubElement(root, "object")
                    etree.SubElement(object, type)
                    bounding_box_element = etree.SubElement(object, "bndbox")
                    etree.SubElement(bounding_box_element, "xmin").text = str(x_min)
                    etree.SubElement(bounding_box_element, "xmax").text = str(x_max)
                    etree.SubElement(bounding_box_element, "ymin").text = str(y_min)
                    etree.SubElement(bounding_box_element, "ymax").text = str(y_max)

            tree = etree.ElementTree(root)
            tree.write('{}/{}'.format(self._xml_directory, file_path))
