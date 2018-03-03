class Exporter:

    def __init__(self, imageset_id, imageset_infos, destination, format_name):
        assert isinstance(imageset_id, int)
        assert isinstance(imageset_infos, dict)
        assert all(key in imageset_infos.keys() for key in ('name', 'team', 'location', 'description'))
        assert all(isinstance(value, str) for value in imageset_infos.values())
        assert isinstance(destination, str)
        assert isinstance(format_name, str)

        self._imageset_id = imageset_id
        self._imageset_infos = imageset_infos
        self._destination = destination
        self._format_name = format_name

    def setup(self, *arg, **kwargs):
        """
        Is called before all annotations are processed. For example you can open a file in here.
        :param data_set_id the id of the processed data set
        :param data_set_name the name of the processed data set
        :param destination the destination directory
        :param arg: arbitrary arguments
        :param kwargs: arbitrary keyword arguments
        :return:
        """
        raise NotImplementedError

    def finish(self, *arg, **kwargs):
        """
        Is called after all annotations are processed. For example you can close a file in here.
        :param arg: arbitrary arguments
        :param kwargs: arbitrary keyword arguments
        :return:
        """
        raise NotImplementedError

    def handle_image(self, image_data, image_name, annotations, *arg, **kwargs):
        """
        A function to process an image and the corresponding annotations.
        :param image_data: the image to be processed
        :param annotations: the corresponding annotations
        :param arg: arbitrary arguments
        :param kwargs: arbitrary keyword arguments
        :return:
        """
        raise NotImplementedError

    def __repr__(self):
        return 'Exporter: {}'.format(self._format_name)