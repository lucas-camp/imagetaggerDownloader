import png


def read_label_chunk(image_path):
    image_path.seek(0)
    p = png.Reader(image_path)
    for chunk_name, chunk_data in p.chunks():
        if chunk_name == 'laBl':
            return chunk_data


def write_label_chunk(image_path, image_data, encoded_protobuf):
    image_data.seek(0)
    p = png.Reader(image_data)

    chunk_list = []

    index = None

    for i, (chunk_name, chunk_data) in enumerate(p.chunks()):
        chunk_list.append([chunk_name, chunk_data])
        if chunk_name == 'laBl':
            index = i

    if index is not None:
        chunk_list[index][1] = encoded_protobuf
    else:
        chunk_list.insert(-1, ['laBl', encoded_protobuf])

    with open(image_path, 'wb') as f:
        png.write_chunks(f, chunk_list)