from lzma import LZMADecompressor
from bz2 import BZ2Decompressor
from .errors import Error
from .compression.crle import CrleDecompressor
from .compression.none import NoneDecompressor
from .compression.heatshrink import HeatshrinkDecompressor
from .compression.zstd import ZstdDecompressor
from .compression.lz4 import Lz4Decompressor
from .common import COMPRESSION_NONE
from .common import COMPRESSION_LZMA
from .common import COMPRESSION_CRLE
from .common import COMPRESSION_BZ2
from .common import COMPRESSION_HEATSHRINK
from .common import COMPRESSION_ZSTD
from .common import COMPRESSION_LZ4
from .common import format_bad_compression_string
from .common import format_bad_compression_number
from .common import file_size
from .common import file_read
from .common import unpack_size
from .common import unpack_header
from . import phdiffpatch


class PatchReader(object):

    def __init__(self, fpatch, compression):
        if compression == 'lzma':
            self.decompressor = LZMADecompressor()
        elif compression == 'bz2':
            self.decompressor = BZ2Decompressor()
        elif compression == 'crle':
            self.decompressor = CrleDecompressor(patch_data_length(fpatch))
        elif compression == 'none':
            self.decompressor = NoneDecompressor(patch_data_length(fpatch))
        elif compression == 'heatshrink':
            self.decompressor = HeatshrinkDecompressor(patch_data_length(fpatch))
        elif compression == 'zstd':
            self.decompressor = ZstdDecompressor(patch_data_length(fpatch))
        elif compression == 'lz4':
            self.decompressor = Lz4Decompressor()
        else:
            raise Error(format_bad_compression_string(compression))

        self._fpatch = fpatch

    def read(self, size):
        return self.decompress(size)

    def decompress(self, size):
        """Decompress `size` bytes.

        """

        buf = b''

        while len(buf) < size:
            if self.decompressor.eof:
                raise Error('Early end of patch data.')

            if self.decompressor.needs_input:
                data = self._fpatch.read(4096)

                if not data:
                    raise Error('Out of patch data.')
            else:
                data = b''

            try:
                buf += self.decompressor.decompress(data, size - len(buf))
            except Exception:
                raise Error('Patch decompression failed.')

        return buf

    @property
    def eof(self):
        return self.decompressor.eof

def patch_data_length(fpatch):
    return file_size(fpatch) - fpatch.tell()

def convert_compression(compression):
    if compression == COMPRESSION_NONE:
        compression = 'none'
    elif compression == COMPRESSION_LZMA:
        compression = 'lzma'
    elif compression == COMPRESSION_CRLE:
        compression = 'crle'
    elif compression == COMPRESSION_BZ2:
        compression = 'bz2'
    elif compression == COMPRESSION_HEATSHRINK:
        compression = 'heatshrink'
    elif compression == COMPRESSION_ZSTD:
        compression = 'zstd'
    elif compression == COMPRESSION_LZ4:
        compression = 'lz4'
    else:
        raise Error(format_bad_compression_number(compression))

    return compression

def read_header_hdiffpatch(fpatch):
    header = fpatch.read(1)

    if len(header) != 1:
        raise Error('Failed to read the patch header.')

    patch_type, compression  = unpack_header(header)

    compression = convert_compression(compression)
    to_size = unpack_size(fpatch)
    patch_size = unpack_size(fpatch)

    return compression, to_size, patch_size

def apply_patch_hdiffpatch(ffrom, fpatch, fto):

    compression, to_size, patch_size = read_header_hdiffpatch(fpatch)
    if to_size == 0:
        return to_size

    patch_reader = PatchReader(fpatch, compression)
    to_data = phdiffpatch.apply_patch(file_read(ffrom),
                                     patch_reader.read(patch_size))
    return fto.write(to_data)

def apply_patch(fromfile, patchfile, tofile):
    with open(fromfile, 'rb') as ffrom:
            with open(patchfile, 'rb') as fpatch:
                with open(tofile, 'wb') as fto:
                    apply_patch_hdiffpatch(ffrom, fpatch, fto)
