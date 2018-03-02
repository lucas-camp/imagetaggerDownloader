import xml.etree.cElementTree as ET
import os

from protobuf.protobuf import decode_data


def save_annotations_to_xml(file_path, file_name):
    label_data = decode_data(os.path.join(file_path, file_name))

    xml_root = ET.Element("annotation")
    ET.SubElement(xml_root, "filename").text = file_name

    xml_size = ET.SubElement(xml_root, "size")
    ET.SubElement(xml_size, "width").text = str(label_data.cameraInformation.resolution.width)
    ET.SubElement(xml_size, "height").text = str(label_data.cameraInformation.resolution.height)
    # TODO check for grayscale
    ET.SubElement(xml_size, "depth").text = "3"

    isRobotInImage = None
    isBallInImage = None

    # read all robots
    for robot in label_data.robots:
        xmin = str(robot.label.boundingBox.upperLeft.x)
        ymin = str(robot.label.boundingBox.upperLeft.y)
        xmax = str(robot.label.boundingBox.lowerRight.x)
        ymax = str(robot.label.boundingBox.lowerRight.y)
        if robot.label.boundingBox.upperLeft.x >= 0 and \
                        robot.label.boundingBox.upperLeft.y >= 0 and \
                        robot.label.boundingBox.lowerRight.x >= 0 and \
                        robot.label.boundingBox.lowerRight.y >= 0:
            isRobotInImage = True
            xml_object = ET.SubElement(xml_root, "object")
            ET.SubElement(xml_object, "name").text = "robot"
            _create_xml_bndbox(xml_object, xmin, ymin, xmax, ymax)
        else:
            isRobotInImage = False

    # read all balls
    for ball in label_data.balls:
        xmin = str(ball.label.boundingBox.upperLeft.x)
        ymin = str(ball.label.boundingBox.upperLeft.y)
        xmax = str(ball.label.boundingBox.lowerRight.x)
        ymax = str(ball.label.boundingBox.lowerRight.y)
        if ball.label.boundingBox.upperLeft.x >= 0 and \
                        ball.label.boundingBox.upperLeft.y >= 0 and \
                        ball.label.boundingBox.lowerRight.x >= 0 and \
                        ball.label.boundingBox.lowerRight.y >= 0:
            isBallInImage = True
            xml_object = ET.SubElement(xml_root, "object")
            ET.SubElement(xml_object, "name").text = "ball"
            _create_xml_bndbox(xml_object, xmin, ymin, xmax, ymax)
        else:
            isBallInImage = False

    if (isRobotInImage == True and isBallInImage == False) or \
            (isRobotInImage == False and isBallInImage == True) or \
            (isRobotInImage == True and isBallInImage == True):
        tree = ET.ElementTree(xml_root)
        if not os.path.exists(os.path.join(file_path, "annotations")):
            os.makedirs(os.path.join(file_path, "annotations"))
        xml_file_name = os.path.join(file_path, "annotations", file_name[:-4] + ".xml")
        tree.write(xml_file_name)
    else:
        print("Skipped " + file_name[:-4] + ".xml, because of Robot:" + str(isRobotInImage) + " | Ball:" + str(isBallInImage))


def _create_xml_bndbox(xml_object, xmin, ymin, xmax, ymax):
    # create bounding boxes
    xml_bndbox = ET.SubElement(xml_object, "bndbox")
    ET.SubElement(xml_bndbox, "xmin").text = xmin
    ET.SubElement(xml_bndbox, "ymin").text = ymin
    ET.SubElement(xml_bndbox, "xmax").text = xmax
    ET.SubElement(xml_bndbox, "ymax").text = ymax