import io
import os
import sys
import unittest

sys.path.append(os.path.split(os.path.split(os.path.abspath(__file__))[0])[0])
import cross_correlate

class TestCrossCorrelate(unittest.TestCase):
    def test_process_file(self):
        in_value = io.BytesIO(b'abc')
        out_value = [[b'a', b'b', b'ab'], [b'c']]
        cc = cross_correlate.CrossCorrelate()
        result = list(cc.process_file(in_value, 2))
        self.assertEqual(out_value, result)

unittest.main()
