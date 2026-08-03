#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for DT_bytes/DT_bytearray.get_send_data(). The naive bytes(data)/
bytearray(data) conversion has type-dependent surprises: str input raises
TypeError (no encoding given), and int input produces a zero-filled buffer
of that many bytes rather than any encoding of the value. The base class's
own typed-cast helper for 'bytes' already does this correctly
(bytes(str(data), 'utf-8')) a few lines above in this same file - DT_bytes
and DT_bytearray should behave the same way.
"""

import unittest

from lib.model.sdp.datatypes import DT_bytes, DT_bytearray


class TestDTBytesSendData(unittest.TestCase):
    def test_str_input_does_not_raise(self):
        result = DT_bytes().get_send_data('hello')
        self.assertEqual(result, b'hello')

    def test_int_input_encodes_value_not_zero_buffer(self):
        result = DT_bytes().get_send_data(5)
        self.assertEqual(result, b'5')  # not b'\x00\x00\x00\x00\x00'


class TestDTBytearraySendData(unittest.TestCase):
    def test_str_input_does_not_raise(self):
        result = DT_bytearray().get_send_data('hello')
        self.assertEqual(result, bytearray(b'hello'))

    def test_int_input_encodes_value_not_zero_buffer(self):
        result = DT_bytearray().get_send_data(5)
        self.assertEqual(result, bytearray(b'5'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
