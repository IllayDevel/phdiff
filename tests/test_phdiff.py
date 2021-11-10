import logging
import unittest
import hashlib
import os

import phdiff

class DetoolsTest(unittest.TestCase):

    def getSize(self, filename):
        fileobject = open(filename, 'rb')
        fileobject.seek(0, 2)
        size = fileobject.tell()
        fileobject.close()
        return size

    def md5(self, fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def assert_create_patch(self,
                            from_filename,
                            to_filename,
                            patch_filename,
                            **kwargs):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        phdiff.create_patch(dir_path+from_filename, dir_path+to_filename, dir_path+patch_filename, **kwargs)
        self.assertGreater(self.getSize(dir_path+patch_filename), 0)

    def assert_apply_patch(self,
                           from_filename,
                           to_filename,
                           patch_filename,
                           patched_filename,
                           **kwargs):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        phdiff.apply_patch(dir_path+from_filename, dir_path+patch_filename, dir_path+to_filename)
        self.assertEqual(self.md5(dir_path+patched_filename), self.md5(dir_path+to_filename))

    def assert_create_and_apply_patch(self,
                                      from_filename,
                                      to_filename,
                                      patch_filename,
                                      **kwargs):
        self.assert_create_patch(from_filename,
                                 to_filename,
                                 patch_filename,
                                 **kwargs)
        self.assert_apply_patch(from_filename,
                                from_filename+".patched",
                                patch_filename,
                                to_filename,
                                **kwargs)

  

    def test_create_and_apply_patch_foo_match_blocks_sequential_none(self):
        self.assert_create_and_apply_patch(
            '/files/old.bin',
            '/files/new.bin',
            '/files/match-blocks-sequential-none.patch',
            compression='none',
            match_block_size=8)

    def test_create_and_apply_patch_random_match_blocks_sequential_none(self):
        self.assert_create_and_apply_patch(
            '/files/from.bin',
            '/files/to.bin',
            '/files/match-blocks-sequential-none.patch',
            compression='none',
            match_block_size=64)

    def test_create_and_apply_patch_random_match_blocks_hdiffpatch(self):
        self.assert_create_and_apply_patch(
            '/files/from.bin',
            '/files/to.bin',
            '/files/match-blocks-hdiffpatch.patch',
            compression='none',
            match_block_size=64)

    def test_create_and_apply_patch_random_match_blocks_hdiffpatch_lzma(self):
        self.assert_create_and_apply_patch(
            '/files/from.bin',
            '/files/to.bin',
            '/files/match-blocks-hdiffpatch.patch.lzma',
            compression='lzma',
            match_block_size=64)
    
    def test_create_and_apply_patch_random_match_blocks_hdiffpatch_crle(self):
        self.assert_create_and_apply_patch(
            '/files/from.bin',
            '/files/to.bin',
            '/files/match-blocks-hdiffpatch.patch.crle',
            compression='crle',
            match_block_size=64) 

    def test_create_and_apply_patch_random_match_blocks_hdiffpatch_bz2(self):
        self.assert_create_and_apply_patch(
            '/files/from.bin',
            '/files/to.bin',
            '/files/match-blocks-hdiffpatch.patch.bz2',
            compression='bz2',
            match_block_size=64)            
                  
    def test_create_and_apply_patch_random_match_blocks_hdiffpatch_heatshrink(self):
        self.assert_create_and_apply_patch(
            '/files/from.bin',
            '/files/to.bin',
            '/files/match-blocks-hdiffpatch.patch.heatshrink',
            compression='heatshrink',
            match_block_size=64)   
    
    def test_create_and_apply_patch_random_match_blocks_hdiffpatch_zstd(self):
        self.assert_create_and_apply_patch(
            '/files/from.bin',
            '/files/to.bin',
            '/files/match-blocks-hdiffpatch.patch.zstd',
            compression='zstd',
            match_block_size=64)   

    def test_create_and_apply_patch_random_match_blocks_hdiffpatch_lz4(self):
        self.assert_create_and_apply_patch(
            '/files/from.bin',
            '/files/to.bin',
            '/files/match-blocks-hdiffpatch.patch.lz4',
            compression='lz4',
            match_block_size=64)                                     



logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    unittest.main()
