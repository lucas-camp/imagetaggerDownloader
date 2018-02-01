import binascii
import struct


def read_label_chunk(image_path, in_memory=False):
    if in_memory:
        data = image_path.read()
    else:
        with open(image_path, 'rb') as f:
            data = f.read()

    total_length = len(data)
    end = 4

    while end + 8 < total_length:
        length = int.from_bytes(data[end + 4: end + 8], 'big')
        begin_chunk_type = end + 8
        begin_chunk_data = begin_chunk_type + 4
        end = begin_chunk_data + length

        type = data[begin_chunk_type:begin_chunk_data]
        chunk_data = data[begin_chunk_data:end]

        if type == b'laBl':
            return chunk_data


def write_label_chunk(image_path, image_data, encoded_protobuf, in_memory=False):
    if in_memory:
        image_data.seek(0)
        data = image_data.read()

        total_length = len(data)
        end = 8

        with open(image_path, 'wb') as f:

            # write header
            f.write(data[0:8])
            pointer = 8

            # iterate over chunks
            while end + 4 < total_length:
                length = int.from_bytes(data[end:end + 4], 'big')
                begin_chunk_type = end + 4
                begin_chunk_data = begin_chunk_type + 4
                end = begin_chunk_data + length + 4

                type = data[begin_chunk_type:begin_chunk_data]
                chunk_data = data[begin_chunk_data:end]

                if not type == b'laBl':
                    f.write(data[pointer:end])
                    pointer = end
                else:
                    length = len(encoded_protobuf)
                    type = b'laBl'
                    data_ = encoded_protobuf

                    # calculate crc
                    b = bytearray()
                    b.extend(type)
                    b.extend(data_)
                    crc = binascii.crc32(b)

                    f.write(bytearray(struct.pack('!i', length)))
                    f.write(type)
                    f.write(data_)
                    f.write(b'0000')
                    pointer += 4 + 4 + length + 4

            # write last  8 bytes
            #f.write(data[-8:])

    else:
        with open(image_path, 'rb') as f:
            data = f.read()
        raise NotImplementedError

