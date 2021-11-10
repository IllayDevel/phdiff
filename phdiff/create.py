import time
import logging
import mmap
import lzma
from bz2 import BZ2Compressor
import bitstruct
from humanfriendly import format_timespan
from .errors import Error
from .compression.crle import CrleCompressor
from .compression.none import NoneCompressor
from .compression.heatshrink import HeatshrinkCompressor
from .compression.zstd import ZstdCompressor
from .compression.lz4 import Lz4Compressor
from .common import format_bad_compression_string
from .common import compression_string_to_number
from .common import div_ceil
from .common import file_size
from .common import file_read
from .common import pack_size
from . import phdiffpatch


LOGGER = logging.getLogger(__name__)


def pack_header(patch_type, compression):
    return bitstruct.pack('p1u3u4', patch_type, compression)


def create_compressor(compression,
                      heatshrink_window_sz2,
                      heatshrink_lookahead_sz2):
    if compression == 'lzma':
        compressor = lzma.LZMACompressor(format=lzma.FORMAT_ALONE)
    elif compression == 'bz2':
        compressor = BZ2Compressor()
    elif compression == 'none':
        compressor = NoneCompressor()
    elif compression == 'crle':
        compressor = CrleCompressor()
    elif compression == 'heatshrink':
        compressor = HeatshrinkCompressor(heatshrink_window_sz2,
                                          heatshrink_lookahead_sz2)
    elif compression == 'zstd':
        compressor = ZstdCompressor()
    elif compression == 'lz4':
        compressor = Lz4Compressor()
    else:
        raise Error(format_bad_compression_string(compression))

    return compressor


def mmap_read_only(fin):
    return mmap.mmap(fin.fileno(), 0, access=mmap.ACCESS_READ)


def calc_shift(memory_size, segment_size, minimum_shift_size, from_size):
    memory_segments = div_ceil(memory_size, segment_size)
    from_segments = div_ceil(from_size, segment_size)

    shift_segments = (memory_segments - from_segments)
    shift_size = (shift_segments * segment_size)

    if shift_size < minimum_shift_size:
        shift_size = minimum_shift_size

    return shift_size


def create_patch_hdiffpatch_generic(ffrom,
                                    fto,
                                    match_score,
                                    match_block_size,
                                    use_mmap):
    if use_mmap:
        with mmap_read_only(ffrom) as from_mmap:
            with mmap_read_only(fto) as to_mmap:
                return phdiffpatch.create_patch(from_mmap,
                                               to_mmap,
                                               match_score,
                                               match_block_size,
                                               2)
    else:
        return phdiffpatch.create_patch(file_read(ffrom),
                                       file_read(fto),
                                       match_score,
                                       match_block_size,
                                       2)


def create_patch_hdiffpatch(ffrom,
                            fto,
                            fpatch,
                            compression,
                            match_score=6,
                            use_mmap=True,
                            heatshrink_window_sz2=8,
                            heatshrink_lookahead_sz2=7):
    start_time = time.time()
    patch = create_patch_hdiffpatch_generic(ffrom,
                                            fto,
                                            match_score,
                                            0,
                                            2,
                                            use_mmap)

    LOGGER.info('Hdiffpatch algorithm completed in %s.',
                format_timespan(time.time() - start_time))

    start_time = time.time()
    compressor = create_compressor(compression,
                                   heatshrink_window_sz2,
                                   heatshrink_lookahead_sz2)

    fpatch.write(pack_header(2, compression_string_to_number(compression)))
    fpatch.write(pack_size(file_size(fto)))
    fpatch.write(pack_size(len(patch)))
    fpatch.write(compressor.compress(patch))
    fpatch.write(compressor.flush())

    LOGGER.info('Compression completed in %s.',
                format_timespan(time.time() - start_time))


def create_patch_match_blocks(ffrom,
                fto,
                fpatch,
                compression,
                match_block_size,
                use_mmap,
                heatshrink_window_sz2,
                heatshrink_lookahead_sz2):
    start_time = time.time()
    patch = create_patch_hdiffpatch_generic(ffrom,
                                            fto,
                                            0,
                                            match_block_size,
                                            use_mmap)

    LOGGER.info('Match blocks algorithm completed in %s.',
                format_timespan(time.time() - start_time))

    start_time = time.time()
    compressor = create_compressor(compression,
                                   heatshrink_window_sz2,
                                   heatshrink_lookahead_sz2)

    fpatch.write(pack_header(2, compression_string_to_number(compression)))
    fpatch.write(pack_size(file_size(fto)))
    fpatch.write(pack_size(len(patch)))

    fpatch.write(compressor.compress(patch))
    fpatch.write(compressor.flush())

    LOGGER.info('Compression completed in %s.',
                format_timespan(time.time() - start_time))

def create_patch(fromfile,
                 tofile,
                 patchfile,
                 compression,
                 match_block_size,
                 use_mmap=False,
                 heatshrink_window_sz2=8,
                 heatshrink_lookahead_sz2=7):
        with open(fromfile, 'rb') as ffrom:
            with open(tofile, 'rb') as fto:
                with open(patchfile, 'wb') as fpatch:
                    create_patch_match_blocks(ffrom,
                                 fto,
                                 fpatch,
                                 compression,
                                 match_block_size,
                                 use_mmap,
                                 heatshrink_window_sz2,
                                 heatshrink_lookahead_sz2)
