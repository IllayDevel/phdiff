from .apply import read_header_hdiffpatch
from .apply import PatchReader
from .common import file_size
from .compression.heatshrink import HeatshrinkDecompressor


def _compression_info(patch_reader):
    info = None

    if patch_reader:
        decompressor = patch_reader.decompressor

        if isinstance(decompressor, HeatshrinkDecompressor):
            info = {
                'window-sz2': decompressor.window_sz2,
                'lookahead-sz2': decompressor.lookahead_sz2
            }

    return info


def patch_info_hdiffpatch(fpatch):
    patch_size = file_size(fpatch)
    compression, to_size, _ = read_header_hdiffpatch(fpatch)
    patch_reader = None

    if to_size > 0:
        patch_reader = PatchReader(fpatch, compression)

    return (patch_size,
            compression,
            _compression_info(patch_reader),
            to_size)


def patch_info(fpatch):
    return 'hdiffpatch', patch_info_hdiffpatch(fpatch)



def patch_info_filename(patchfile, fsize=None):
    with open(patchfile, 'rb') as fpatch:
        return patch_info(fpatch, fsize)
