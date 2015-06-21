import io
import os
import sys
import unittest
import collections


sys.path.append(os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])
import cross_correlate

Chunk = collections.namedtuple('Chunk', ['chunk', 'subset_slices'])
FileData = collections.namedtuple('FileData', ['name', 'type', 'frequencies', 'chunks'])
HashSlice = collections.namedtuple('SubHash', ['hash', 'start', 'end'])
SubSlice = collections.namedtuple('SubSlice', ['start', 'end'])
HashTable = collections.namedtuple('HashTable', ['values_table', 'frequency_table'])

class TestCrossCorrelate(unittest.TestCase):
    def test_process_file(self):
        in_value = io.BytesIO(b'abc')
        out_value = [[b'a', b'b', b'ab'], [b'c']]
        cc = cross_correlate.CrossCorrelate()
        result = list(cc.process_file(in_value, 2))
        self.assertEqual(out_value, result)

class TestBayesChunkPredictor(unittest.TestCase):
    def test_prior_homogenity(self):
        msg = (
            "Test basic functionality of returning the entropy of two files"
            "which have the same contents.")
        cc = cross_correlate.CrossCorrelate()
        chunk = b"abc"
        subsets = tuple(cc.gen_slices(chunk))
        chunk_struct = (Chunk(chunk, subsets),)
        frequency_table = HashTable(None, 
                                    [(24929, 1), (25186, 1), (25443, 1),
                                     (9667, 1), (9924, 1), (10437, 1)])
        data = FileData('test1', 'binary', frequency_table, chunk_struct)
        testdata = cross_correlate.BayesChunkPredictor.prior_homogenity(
            cross_correlate.BayesChunkPredictor, 
            data, 
            data)
        self.assertEqual(testdata[0], testdata[1], msg)
        msg = "Test that prior_homogenity outputs the right values for inputs."
        entropy = 2.584962500721156
        self.assertEqual(testdata[0], entropy, msg)

unittest.main()
