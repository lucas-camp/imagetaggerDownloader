from exporters.exporter import Exporter


class CSVExporter(Exporter):

    def __init__(self, imageset_id, imageset_infos, destination):
        super().__init__(imageset_id, imageset_infos, destination, 'CSVExporter')

    def setup(self, *arg, **kwargs):
        assert 'csvfile_path' in kwargs.keys()
        assert isinstance(kwargs['csvfile_path'], str)

        csvfile_path = kwargs['csvfile_path']
        self._csvfile = open(csvfile_path, 'w')

    def finish(self, *args, **kwargs):
        self._csvfile.close()

    def handle_annotation(self, image_data, image_name, annotations, *args, **kwargs):
        if annotations:
            for annotation in annotations:
                type, bounding_box = annotation

                if bounding_box is None:
                    self._csvfile.write('{}|{}|not in image\n'.format(image_name, type))
                else:
                    self._csvfile.write('{}|{}|{}|{}|{}|{}\n'.format(image_name, type,
                                                                     bounding_box['x1'], bounding_box['y1'],
                                                                     bounding_box['x2'], bounding_box['y2']))