# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
import unittest

from wapiti.parsers import Decoder, Encoder

class TestJSONDecode(unittest.TestCase):

    def setUp(self):
        self.decoder = Decoder('json')

    def test_str(self):
        self.assertEqual(self.decoder.decode('"FOO"'), "FOO")
        self.assertRaises(TypeError, self.decoder.decode, ('FOO',))

    def test_list(self):
        self.assertEqual(self.decoder.decode('["FOO"]'), ["FOO"])
        
    def test_dict(self):
        self.assertEqual(self.decoder.decode('{"FOO":"BAR"}'), {"FOO": "BAR"})

    def test_nested(self):
        self.assertEqual(self.decoder.decode('{"FOO":["BAR"]}'), {"FOO": ["BAR"]})

class TestJSONEncode(unittest.TestCase):

    def setUp(self):
        self.encoder = Encoder('to_json')

    def test_str(self):
        self.assertEqual(self.encoder.encode("FOO"), '"FOO"')

    def test_list(self):
        self.assertEqual(self.encoder.encode(["FOO",]), '["FOO"]')
        
    def test_dict(self):
        self.assertEqual(self.encoder.encode({"FOO": "BAR"}), '{"FOO": "BAR"}')

    def test_nested(self):
        self.assertEqual(self.encoder.encode({"FOO":["BAR"]}), '{"FOO": ["BAR"]}')

if __name__ == '__main__':
    unittest.main()

