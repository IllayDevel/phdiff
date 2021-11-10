import os
import bitstruct
from .errors import Error
from .phdiffpatch import pack_size

COMPRESSION_NONE        = 0
COMPRESSION_LZMA        = 1
COMPRESSION_CRLE        = 2
COMPRESSION_BZ2         = 3
COMPRESSION_HEATSHRINK  = 4
COMPRESSION_ZSTD        = 5
COMPRESSION_LZ4         = 6

COMPRESSIONS = {
    'none': COMPRESSION_NONE,
    'lzma': COMPRESSION_LZMA,
    'crle': COMPRESSION_CRLE,
    'bz2': COMPRESSION_BZ2,
    'heatshrink': COMPRESSION_HEATSHRINK,
    'zstd': COMPRESSION_ZSTD,
    'lz4': COMPRESSION_LZ4
}

DATA_FORMAT_ARM_CORTEX_M4 = 0
DATA_FORMAT_AARCH64       = 1
DATA_FORMAT_XTENSA_LX106  = 2

def format_or(items):
    items = [str(item) for item in items]

    if len(items) == 1:
        return items[0]
    else:
        return '{} or {}'.format(', '.join(items[:-1]),
                                 items[-1])


def format_bad_compression_string(compression):
    return "Expected compression {}, but got {}.".format(
        format_or(sorted(COMPRESSIONS)),
        compression)

def format_bad_compression_number(compression):
    items = sorted([(n, '{}({})'.format(s, n)) for s, n in COMPRESSIONS.items()])

    return "Expected compression {}, but got {}.".format(
        format_or([v for _, v in items]),
        compression)

def compression_string_to_number(compression):
    try:
        return COMPRESSIONS[compression]
    except KeyError:
        raise Error(format_bad_compression_string(compression))

def div_ceil(a, b):
    return (a + b - 1) // b


def file_size(f):
    position = f.tell()
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(position, os.SEEK_SET)

    return size


def file_read(f):
    f.seek(0, os.SEEK_SET)
    return f.read()

def unpack_size_with_length(fin):
    try:
        byte = fin.read(1)[0]
    except IndexError:
        raise Error('Failed to read first size byte.')

    is_signed = (byte & 0x40)
    value = (byte & 0x3f)
    offset = 6

    while byte & 0x80:
        try:
            byte = fin.read(1)[0]
        except IndexError:
            raise Error('Failed to read consecutive size byte.')

        value |= ((byte & 0x7f) << offset)
        offset += 7

    if is_signed:
        value *= -1

    return value, ((offset - 6) / 7 + 1)

def unpack_size(fin):
    return unpack_size_with_length(fin)[0]

class DataSegment(object):

    def __init__(self,
                 from_data_offset_begin,
                 from_data_offset_end,
                 from_data_begin,
                 from_data_end,
                 from_code_begin,
                 from_code_end,
                 to_data_offset_begin,
                 to_data_offset_end,
                 to_data_begin,
                 to_data_end,
                 to_code_begin,
                 to_code_end):
        self.from_data_offset_begin = from_data_offset_begin
        self.from_data_offset_end = from_data_offset_end
        self.from_data_begin = from_data_begin
        self.from_data_end = from_data_end
        self.from_code_begin = from_code_begin
        self.from_code_end = from_code_end
        self.to_data_offset_begin = to_data_offset_begin
        self.to_data_offset_end = to_data_offset_end
        self.to_data_begin = to_data_begin
        self.to_data_end = to_data_end
        self.to_code_begin = to_code_begin
        self.to_code_end = to_code_end


def unpack_header(data):
    return bitstruct.unpack('p1u3u4', data)
