# Copyright (c) Ecometrica. All rights reserved.
# Distributed under the BSD license. See LICENSE for details.
import unittest

from datetime import date

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

    def test_date(self):
        self.assertEqual(self.decoder.decode('1945-09-02'), date(1945, 9, 2))
        self.assertEqual(self.decoder.decode('1820-09-16'), date(1820, 9, 16))


class TestJSONEncode(unittest.TestCase):

    def setUp(self):
        self.encoder = Encoder('to_json')

    def test_str(self):
        self.assertEqual(self.encoder.encode("FOO"), '"FOO"')

    def test_list(self):
        self.assertEqual(self.encoder.encode(["FOO"]), '["FOO"]')

    def test_dict(self):
        self.assertEqual(self.encoder.encode({"FOO": "BAR"}), '{"FOO": "BAR"}')

    def test_nested(self):
        self.assertEqual(self.encoder.encode({"FOO": ["BAR"]}), '{"FOO": ["BAR"]}')

    def test_date(self):
        self.assertEqual(self.encoder.encode(date(1945, 8, 2)), '"1945-08-02"')
        self.assertEqual(self.encoder.encode(date(1820, 9, 16)), '"1820-09-16"')

if __name__ == '__main__':
    unittest.main()
