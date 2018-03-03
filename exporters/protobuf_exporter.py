from exporters.exporter import Exporter
from png_io.png_io import write_label_chunk
from protobuf.protobuf import decode_data, encode_data


class ProtobufExporter(Exporter):

    def __init__(self, imageset_id, imageset_infos, destination):
        super().__init__(imageset_id, imageset_infos, destination, 'ProtobufExporter')

    def setup(self, *arg, **kwargs):
        pass

    def finish(self, *args, **kwargs):
        pass

    def handle_annotation(self, image_data, image_name, annotations, *args, **kwargs):
        file_path = '{}/{}'.format(self._destination, image_name)
        decoded_protobuf = decode_data(image_data)
        if annotations:
            for annotation in annotations:
                type, bounding_box = annotation

                if type == 'ball':
                    entity = decoded_protobuf.balls.add()
                elif type == 'robot':
                    entity = decoded_protobuf.robots.add()
                else:
                    continue

                if bounding_box is None:
                    entity.label.boundingBox.upperLeft.x = -1
                    entity.label.boundingBox.upperLeft.y = -1
                    entity.label.boundingBox.lowerRight.x = -1
                    entity.label.boundingBox.lowerRight.y = -1
                else:
                    entity.label.boundingBox.upperLeft.x = bounding_box['x1']
                    entity.label.boundingBox.upperLeft.y = bounding_box['x2']
                    entity.label.boundingBox.lowerRight.x = bounding_box['y1']
                    entity.label.boundingBox.lowerRight.y = bounding_box['y2']

        encoded_protobuf = encode_data(decoded_protobuf)

        write_label_chunk(file_path, image_data, encoded_protobuf)