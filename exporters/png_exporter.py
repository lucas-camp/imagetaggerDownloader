import shutil

from exporters.exporter import Exporter


class PNGExporter(Exporter):

    def __init__(self, imageset_id, imageset_infos, destination):
        super().__init__(imageset_id, imageset_infos, destination, 'PNGExporter')

    def setup(self, *arg, **kwargs):
        pass

    def finish(self, *args, **kwargs):
        pass

    def handle_annotation(self, image_data, image_name, annotations, *args, **kwargs):
        file_path = '{}/{}'.format(self._destination, image_name)

        with open(file_path, 'wb') as f:
            shutil.copyfileobj(image_data, f)