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

class TestWeightedRandomVariable(unittest.TestCase):
    def test_add(self):
        msg = "Test that initial additions to the pool work properly."
        WRV = cross_correlate.WeightedRandomVariable()
        WRV.add("a")
        self.assertEqual(WRV.pool, {"a":1}, msg)
        WRV.add("a", 2)
        msg = "Test that repeated additions to the pool work properly."
        self.assertEqual(WRV.pool, {"a":3}, msg)

    def test_probability_mass(self):
        msg = "Test whether the probability mass function gives the proper values."
        WRV = cross_correlate.WeightedRandomVariable()
        WRV.add("a", 2)
        self.assertEqual(WRV.probability_mass("a"), 1)

    def test_draw(self):
        msg = "Test whether two draws from the same seed give the same results."
        WRV = cross_correlate.WeightedRandomVariable()
        WRV.rangen = random()
        WRV.add("a", 2)
        WRV.add("b", 5)
        draw1 = (WRV.draw(), WRV.draw(), WRV.draw())
        draw2 = (WRV.draw(), WRV.draw(), WRV.draw())
        self.assertEqual(draw1, draw2, msg)
        msg = "Test that draw completes properly. (I.E, does not return None.)"
        self.assertTrue(draw1[0] is not None) 

class random():
    """Fake random class to give reproducible results for TestWeightedRandomVariable."""
    def randrange(self, _range):
        """Fake randrange function to stand in for the real one. Just returns 
        seven."""
        return 7

unittest.main()
