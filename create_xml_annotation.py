from protobuf import decode_data
import xml.etree.cElementTree as ET
from os import walk
import xml.dom.minidom


def create_xml_bndbox(xml_object, xmin, ymin, xmax, ymax):
    # create bounding boxes
    xml_bndbox = ET.SubElement(xml_object, "bndbox")
    ET.SubElement(xml_bndbox, "xmin").text = xmin
    ET.SubElement(xml_bndbox, "ymin").text = ymin
    ET.SubElement(xml_bndbox, "xmax").text = xmax
    ET.SubElement(xml_bndbox, "ymax").text = ymax


def create_xml_annotation(file_name_list: list, input_dir, output_dir):

    for file_name in file_name_list:

        label_data = decode_data(input_dir + file_name, False)

        xml_root = ET.Element("annotation")
        ET.SubElement(xml_root, "filename").text = file_name

        xml_size = ET.SubElement(xml_root, "size")
        ET.SubElement(xml_size, "width").text = str(label_data.cameraInformation.resolution.width)
        ET.SubElement(xml_size, "height").text = str(label_data.cameraInformation.resolution.height)
        # TODO check for grayscale
        ET.SubElement(xml_size, "depth").text = "3"

        # todo create object list

        # read all robots
        for robot in label_data.robots:
            xml_object = ET.SubElement(xml_root, "object")

            ET.SubElement(xml_object, "name").text = "robot"

            xmin = str(robot.label.boundingBox.upperLeft.x)
            ymin = str(robot.label.boundingBox.upperLeft.y)
            xmax = str(robot.label.boundingBox.lowerRight.x)
            ymax = str(robot.label.boundingBox.lowerRight.y)
            create_xml_bndbox(xml_object, xmin, ymin, xmax, ymax)

        # read all balls
        for ball in label_data.balls:
            xml_object = ET.SubElement(xml_root, "object")

            ET.SubElement(xml_object, "name").text = "ball"

            xmin = str(ball.label.boundingBox.upperLeft.x)
            ymin = str(ball.label.boundingBox.upperLeft.y)
            xmax = str(ball.label.boundingBox.lowerRight.x)
            ymax = str(ball.label.boundingBox.lowerRight.y)
            create_xml_bndbox(xml_object, xmin, ymin, xmax, ymax)

        tree = ET.ElementTree(xml_root)

        xml_file_name = input_dir + file_name[:-4] + ".xml"

        tree.write(output_dir)

        xml_file = xml.dom.minidom.parse(xml_file_name)
        pretty_xml_as_string = xml_file.toprettyxml()


def create_file_name_list(input_dir):
    file_name_list = []
    for (dirpath, dirnames, filenames) in walk(input_dir):
        file_name_list.extend(filenames)
        break

    return file_name_list


if __name__ == '__main__':
    input_dir = "/media/max/DATA/dev/data/test/images/"

    output_dir = "/media/max/DATA/dev/data/test/annotations/"

    file_name_list = create_file_name_list(input_dir)

    create_xml_annotation(file_name_list, input_dir, output_dir)

