from imageLabelData_pb2 import ImageLabelData

from png import read_label_chunk


def decode_data(image_path, in_memory=False):
    encoded_data = read_label_chunk(image_path, in_memory)
    decoded_data = ImageLabelData()
    decoded_data.ParseFromString(encoded_data)

    return decoded_data


def encode_data(protobuf):
    return protobuf.SerializeToString()


def add_annotations(image_):
    pass