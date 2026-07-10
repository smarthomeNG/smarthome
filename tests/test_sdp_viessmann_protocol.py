#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Tests for SDPProtocolViessmann: static utilities, packet building/parsing,
protocol initialisation sequences, and _send() error paths.

All tests use a minimal protocol instance created without __init__ so that
no serial hardware or connection setup is required.
"""

import builtins

builtins.SDP_standalone = False

import logging
import threading
import unittest
from unittest.mock import MagicMock, call, patch

from lib.model.sdp.globals import SDPConnectionError, SDPProtocolError
from plugins.viessmann.protocol import SDPProtocolViessmann


# ---------------------------------------------------------------------------
# Control-set constants (copied from SDPProtocolViessmann.__init__)
# ---------------------------------------------------------------------------

P300_CS = {
    'baudrate': 4800,
    'bytesize': 8,
    'parity': 'E',
    'stopbits': 2,
    'timeout': 0.5,
    'startbyte': 0x41,
    'request': 0x00,
    'response': 0x01,
    'error': 0x03,
    'read': 0x01,
    'write': 0x02,
    'functioncall': 0x07,
    'acknowledge': 0x06,
    'not_initiated': 0x05,
    'init_error': 0x15,
    'reset_command': 0x04,
    'reset_command_response': 0x05,
    'sync_command': 0x160000,
    'sync_command_response': 0x06,
    'command_bytes_read': 5,
    'command_bytes_write': 5,
}

KW_CS = {
    'baudrate': 4800,
    'bytesize': 8,
    'parity': 'E',
    'stopbits': 2,
    'timeout': 1,
    'startbyte': 0x01,
    'read': 0xF7,
    'write': 0xF4,
    'acknowledge': 0x01,
    'reset_command': 0x04,
    'not_initiated': 0x05,
    'write_ack': 0x00,
}


# ---------------------------------------------------------------------------
# Helper — build a minimal protocol instance
# ---------------------------------------------------------------------------


def _make_proto(viess_proto='P300'):
    p = object.__new__(SDPProtocolViessmann)
    p.logger = logging.getLogger('test.viessmann')
    p._viess_proto = viess_proto
    p._controlsets = {'P300': P300_CS, 'KW': KW_CS}
    p._controlset = P300_CS if viess_proto == 'P300' else KW_CS
    p._is_initialized = False
    p._is_connected = True
    p._lock = threading.Lock()
    p._send_bytes = MagicMock()
    p._read_bytes = MagicMock(return_value=b'')
    p._close = MagicMock()
    p._open = MagicMock()
    p._connection = MagicMock()  # needed by KW reset_input_buffer
    return p


# ---------------------------------------------------------------------------
# Static utility methods
# ---------------------------------------------------------------------------


class TestStaticUtilities(unittest.TestCase):
    def test_int2bytes_single_byte(self):
        result = SDPProtocolViessmann._int2bytes(0x06, 1)
        self.assertEqual(result, b'\x06')

    def test_int2bytes_three_bytes_big_endian(self):
        result = SDPProtocolViessmann._int2bytes(0x160000, 3)
        self.assertEqual(result, b'\x16\x00\x00')

    def test_int2bytes_truncates_to_length(self):
        # 0x0104 in 1 byte → 0x04
        result = SDPProtocolViessmann._int2bytes(0x0104, 1)
        self.assertEqual(result, b'\x04')

    def test_bytes2int_unsigned(self):
        result = SDPProtocolViessmann._bytes2int(b'\x95\x00', signed=False)
        self.assertEqual(result, 149)  # 0x0095 little-endian

    def test_bytes2int_signed_negative(self):
        result = SDPProtocolViessmann._bytes2int(b'\xd8\xff', signed=True)
        self.assertEqual(result, -40)  # -40 in 16-bit signed little-endian

    def test_bytes2hexstring(self):
        result = SDPProtocolViessmann._bytes2hexstring(b'\x41\x06\x0a')
        self.assertEqual(result, '41060a')

    def test_calc_checksum_p300_packet(self):
        # packet starting with startbyte 0x41: checksum over bytes after 0x41
        # bytes: 0x05 0x00 0x01 0x01 0x01 0x02  → sum = 10 = 0x0A
        packet = bytearray([0x41, 0x05, 0x00, 0x01, 0x01, 0x01, 0x02])
        result = SDPProtocolViessmann._calc_checksum(packet)
        self.assertEqual(result, 0x0A)

    def test_calc_checksum_packet_not_starting_with_startbyte(self):
        # _calc_checksum only computes when packet starts with 0x41;
        # otherwise the if-block is not entered and checksum stays 0.
        packet = bytearray([0x05, 0x00, 0x01])
        result = SDPProtocolViessmann._calc_checksum(packet)
        self.assertEqual(result, 0)

    def test_calc_checksum_empty_packet(self):
        self.assertEqual(SDPProtocolViessmann._calc_checksum(bytearray()), 0)


# ---------------------------------------------------------------------------
# _build_payload()
# ---------------------------------------------------------------------------


class TestBuildPayload(unittest.TestCase):
    def setUp(self):
        self.p = _make_proto('P300')

    def test_p300_read_command_structure(self):
        data_dict = {'payload': '0101', 'data': {'len': 2, 'value': None, 'kwseq': False}}
        packet, responselen = self.p._build_payload(data_dict)
        # Expected: [0x41, 0x05, 0x00, 0x01, 0x01, 0x01, 0x02, 0x0A]
        self.assertEqual(packet[0:1], b'\x41')  # startbyte
        self.assertEqual(packet[1:2], b'\x05')  # command_bytes_read
        self.assertEqual(packet[2:3], b'\x00')  # request
        self.assertEqual(packet[3:4], b'\x01')  # read opcode
        self.assertEqual(packet[4:6], bytes.fromhex('0101'))  # addr
        self.assertEqual(packet[6:7], b'\x02')  # cmdlen
        # checksum is last byte; verify it matches _calc_checksum of rest
        expected_cs = SDPProtocolViessmann._calc_checksum(packet[:-1])
        self.assertEqual(packet[-1], expected_cs)

    def test_p300_read_response_length(self):
        data_dict = {'payload': '0101', 'data': {'len': 2, 'value': None, 'kwseq': False}}
        packet, responselen = self.p._build_payload(data_dict)
        # command_bytes_read(5) + 4 + cmdlen(2) = 11
        self.assertEqual(responselen, 11)

    def test_p300_write_command_structure(self):
        valuebytes = b'\x3c'  # write value 60 (°C setpoint)
        data_dict = {'payload': '6000', 'data': {'len': 1, 'value': valuebytes, 'kwseq': False}}
        packet, responselen = self.p._build_payload(data_dict)
        self.assertEqual(packet[3:4], b'\x02')  # write opcode
        self.assertEqual(packet[4:6], bytes.fromhex('6000'))  # addr
        self.assertIn(valuebytes, bytes(packet))  # value embedded

    def test_p300_write_response_length(self):
        valuebytes = b'\x3c'
        data_dict = {'payload': '6000', 'data': {'len': 1, 'value': valuebytes, 'kwseq': False}}
        packet, responselen = self.p._build_payload(data_dict)
        # write response: command_bytes_read + 4 + 0 = 9
        self.assertEqual(responselen, 9)

    def test_bad_data_dict_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.p._build_payload({'payload': '0101', 'data': {}})


# ---------------------------------------------------------------------------
# _parse_response()
# ---------------------------------------------------------------------------

# Valid P300 read response:
#   ACK(06) startbyte(41) datalen(07) resptype(01) datacode(01)
#   addr(01 01) valuebytecount(02) value(00 95) checksum(A2)
# checksum = sum([07,01,01,01,01,02,00,95]) % 256 = 162 = 0xA2
P300_VALID_READ = bytearray([0x06, 0x41, 0x07, 0x01, 0x01, 0x01, 0x01, 0x02, 0x00, 0x95, 0xA2])

# Valid P300 write response:
#   ACK(06) startbyte(41) datalen(05) resptype(01) datacode(02)
#   addr(60 00) byteswritten(01) checksum(69)
# checksum = sum([05,01,02,60,00,01]) % 256 = 105 = 0x69
P300_VALID_WRITE = bytearray([0x06, 0x41, 0x05, 0x01, 0x02, 0x60, 0x00, 0x01, 0x69])

# P300 device error response (10 bytes):
#   ACK(06) startbyte(41) datalen(06) typecode(03=error) datacode(02=write)
#   addr(60 00) errlen(01) errcode(21) checksum(8d)
# checksum: sum([06,03,02,60,00,01,21]) % 256 = 141 = 0x8D
P300_DEVICE_ERROR_WRITE = bytearray([0x06, 0x41, 0x06, 0x03, 0x02, 0x60, 0x00, 0x01, 0x21, 0x8D])

# Same as valid read but with wrong checksum
P300_BAD_CHECKSUM = bytearray(P300_VALID_READ)
P300_BAD_CHECKSUM[-1] = 0xFF


def _sequential_read(data: bytes):
    """Return a side_effect that serves data in sequential chunks by requested size."""
    pos = [0]

    def reader(n):
        chunk = data[pos[0] : pos[0] + n]
        pos[0] += n
        return bytes(chunk)

    return reader


class TestParseResponse(unittest.TestCase):
    def setUp(self):
        self.p = _make_proto('P300')

    def test_p300_valid_read_returns_value_bytes(self):
        result = self.p._parse_response(P300_VALID_READ)
        self.assertEqual(result, bytearray([0x00, 0x95]))

    def test_p300_valid_write_returns_none(self):
        result = self.p._parse_response(P300_VALID_WRITE)
        self.assertIsNone(result)

    def test_p300_checksum_mismatch_raises_sdp_protocol_error(self):
        with self.assertRaises(SDPProtocolError) as ctx:
            self.p._parse_response(P300_BAD_CHECKSUM)
        self.assertIn('checksum', str(ctx.exception).lower())

    def test_p300_checksum_mismatch_does_not_call_close(self):
        """_parse_response must NOT call _close itself; that's _send()'s job."""
        try:
            self.p._parse_response(P300_BAD_CHECKSUM)
        except SDPProtocolError:
            pass
        self.p._close.assert_not_called()


# ---------------------------------------------------------------------------
# _send_init_on_send() — P300
# ---------------------------------------------------------------------------


class TestSendInitP300(unittest.TestCase):
    def setUp(self):
        self.p = _make_proto('P300')

    def test_already_initialized_returns_true_immediately(self):
        self.p._is_initialized = True
        result = self.p._send_init_on_send()
        self.assertTrue(result)
        self.p._send_bytes.assert_not_called()

    def test_success_sequence_reset_notinit_sync_ack(self):
        """Simulate: RESET sent → NOTINIT received → SYNC sent → ACK received."""
        NOTINIT = SDPProtocolViessmann._int2bytes(P300_CS['not_initiated'], 1)
        ACK = SDPProtocolViessmann._int2bytes(P300_CS['acknowledge'], 1)
        self.p._read_bytes.side_effect = [NOTINIT, ACK]

        result = self.p._send_init_on_send()

        self.assertTrue(result)
        self.assertTrue(self.p._is_initialized)

    def test_success_sends_reset_then_sync(self):
        NOTINIT = SDPProtocolViessmann._int2bytes(P300_CS['not_initiated'], 1)
        ACK = SDPProtocolViessmann._int2bytes(P300_CS['acknowledge'], 1)
        self.p._read_bytes.side_effect = [NOTINIT, ACK]
        RESET = SDPProtocolViessmann._int2bytes(P300_CS['reset_command'], 1)
        SYNC = SDPProtocolViessmann._int2bytes(P300_CS['sync_command'], 3)

        self.p._send_init_on_send()

        calls = self.p._send_bytes.call_args_list
        self.assertEqual(calls[0], call(RESET))
        self.assertEqual(calls[1], call(SYNC))

    def test_all_retries_exhausted_raises_sdp_protocol_error(self):
        """10 consecutive empty reads → SDPProtocolError."""
        self.p._read_bytes.return_value = b''
        with self.assertRaises(SDPProtocolError):
            self.p._send_init_on_send()
        self.assertFalse(self.p._is_initialized)

    def test_error_byte_triggers_reset_and_continues(self):
        """ERR byte causes a RESET; loop continues rather than aborting."""
        ERR = SDPProtocolViessmann._int2bytes(P300_CS['init_error'], 1)
        NOTINIT = SDPProtocolViessmann._int2bytes(P300_CS['not_initiated'], 1)
        ACK = SDPProtocolViessmann._int2bytes(P300_CS['acknowledge'], 1)
        # ERR on first read → RESET resent; then normal success sequence
        self.p._read_bytes.side_effect = [ERR, NOTINIT, ACK]

        result = self.p._send_init_on_send()
        self.assertTrue(result)


# ---------------------------------------------------------------------------
# _send_init_on_send() — KW
# ---------------------------------------------------------------------------


class TestSendInitKW(unittest.TestCase):
    def setUp(self):
        self.p = _make_proto('KW')

    @patch('plugins.viessmann.protocol.sleep')
    def test_kw_sync_success(self, mock_sleep):
        NOINIT = SDPProtocolViessmann._int2bytes(KW_CS['not_initiated'], 1, signed=False)
        self.p._read_bytes.return_value = NOINIT
        result = self.p._send_init_on_send()
        self.assertTrue(result)
        self.assertTrue(self.p._is_initialized)

    @patch('plugins.viessmann.protocol.sleep')
    def test_kw_sync_failure_raises_sdp_protocol_error(self, mock_sleep):
        """5 failed sync attempts → SDPProtocolError (not return False)."""
        self.p._read_bytes.return_value = b'\xff'  # never matches NOINIT
        with self.assertRaises(SDPProtocolError):
            self.p._send_init_on_send()

    @patch('plugins.viessmann.protocol.sleep')
    def test_kw_sync_failure_does_not_return_false(self, mock_sleep):
        """Ensure we raise rather than return False (old broken behaviour)."""
        self.p._read_bytes.return_value = b'\xff'
        raised = False
        try:
            self.p._send_init_on_send()
        except SDPProtocolError:
            raised = True
        self.assertTrue(raised, '_send_init_on_send() must raise, not return False')


# ---------------------------------------------------------------------------
# _send() — P300 error paths
# ---------------------------------------------------------------------------


class TestSendP300ErrorPaths(unittest.TestCase):
    def setUp(self):
        self.p = _make_proto('P300')
        # pre-build a minimal data_dict that _build_payload accepts
        self.data_dict = {'payload': '0101', 'data': {'len': 2, 'value': None, 'kwseq': False}}

    def test_no_response_raises_sdp_connection_error(self):
        self.p._read_bytes.return_value = b''
        with self.assertRaises(SDPConnectionError):
            self.p._send(self.data_dict)

    def test_error_byte_raises_sdp_protocol_error(self):
        ERROR = SDPProtocolViessmann._int2bytes(P300_CS['error'], 1)
        # Pad to expected response length so the first byte check fires
        response = ERROR + b'\x00' * 10
        self.p._read_bytes.return_value = response
        with self.assertRaises(SDPProtocolError):
            self.p._send(self.data_dict)

    def test_not_initiated_raises_sdp_protocol_error_and_clears_flag(self):
        NOTINIT = SDPProtocolViessmann._int2bytes(P300_CS['not_initiated'], 1)
        self.p._read_bytes.return_value = NOTINIT
        self.p._is_initialized = True  # was initialized; device reset
        with self.assertRaises(SDPProtocolError):
            self.p._send(self.data_dict)
        self.assertFalse(self.p._is_initialized)

    def test_wrong_ack_raises_sdp_protocol_error(self):
        WRONG = b'\xab' + b'\x00' * 10  # not ACK (0x06)
        self.p._read_bytes.return_value = WRONG
        with self.assertRaises(SDPProtocolError):
            self.p._send(self.data_dict)

    def test_close_called_on_connection_error(self):
        self.p._send_bytes.side_effect = SDPConnectionError('port gone')
        with self.assertRaises(SDPConnectionError):
            self.p._send(self.data_dict)
        self.p._close.assert_called_once()

    def test_close_not_called_on_protocol_error(self):
        # Device returning an error byte (0x15) is a protocol-level rejection —
        # the serial link is intact, so _close() must NOT be called.
        ERROR = SDPProtocolViessmann._int2bytes(P300_CS['error'], 1)
        self.p._read_bytes.return_value = ERROR + b'\x00' * 10
        with self.assertRaises(SDPProtocolError):
            self.p._send(self.data_dict)
        self.p._close.assert_not_called()

    def test_is_initialized_cleared_on_any_error(self):
        self.p._is_initialized = True
        self.p._send_bytes.side_effect = SDPConnectionError('broken')
        try:
            self.p._send(self.data_dict)
        except SDPConnectionError:
            pass
        self.assertFalse(self.p._is_initialized)

    def test_unexpected_exception_wrapped_as_sdp_connection_error(self):
        """A bare Exception from _send_bytes becomes SDPConnectionError."""
        self.p._send_bytes.side_effect = Exception('something weird')
        with self.assertRaises(SDPConnectionError):
            self.p._send(self.data_dict)

    def test_successful_read_returns_value_bytes(self):
        self.p._read_bytes.side_effect = _sequential_read(bytes(P300_VALID_READ))
        result = self.p._send(self.data_dict)
        self.assertEqual(result, bytearray([0x00, 0x95]))

    def test_successful_write_returns_none(self):
        write_dict = {'payload': '6000', 'data': {'len': 1, 'value': b'\x3c', 'kwseq': False}}
        self.p._read_bytes.side_effect = _sequential_read(bytes(P300_VALID_WRITE))
        result = self.p._send(write_dict)
        self.assertIsNone(result)

    def test_device_error_response_raises_sdp_protocol_error(self):
        """10-byte P300 device error response must raise SDPProtocolError, not checksum mismatch."""
        write_dict = {'payload': '6000', 'data': {'len': 1, 'value': b'\x3c', 'kwseq': False}}
        self.p._read_bytes.side_effect = _sequential_read(bytes(P300_DEVICE_ERROR_WRITE))
        with self.assertRaises(SDPProtocolError) as ctx:
            self.p._send(write_dict)
        self.assertNotIn('checksum', str(ctx.exception).lower())


# ---------------------------------------------------------------------------
# _send() — KW error paths
# ---------------------------------------------------------------------------


class TestSendKWErrorPaths(unittest.TestCase):
    def setUp(self):
        self.p = _make_proto('KW')
        self.data_dict = {'payload': '0101', 'data': {'len': 2, 'value': None, 'kwseq': False}}

    def test_kw_no_response_raises_sdp_connection_error(self):
        self.p._read_bytes.return_value = b''
        with self.assertRaises(SDPConnectionError):
            self.p._send(self.data_dict)


if __name__ == '__main__':
    unittest.main(verbosity=2)
