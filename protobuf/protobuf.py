from protobuf.imageLabelData_pb2 import ImageLabelData

from png_io.png_io import read_label_chunk


def decode_data(image_path):
    encoded_data = read_label_chunk(image_path)
    decoded_data = ImageLabelData()
    decoded_data.ParseFromString(encoded_data)

    return decoded_data


def encode_data(protobuf):
    return protobuf.SerializeToString()