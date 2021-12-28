#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Based on aioudp by bashkirtsevich: https://github.com/bashkirtsevich-llc/aioudp
#  Copyright 2020- Sebastian Helms
#########################################################################
#  This file is part of SmartHomeNG
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG  If not, see <http://www.gnu.org/licenses/>.
#########################################################################


import asyncio
import socket
from collections import deque


class aioUDPServer():
    def __init__(self):
        self._recv_max_size = 4096

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setblocking(False)

        self._send_event = asyncio.Event()
        self._send_queue = deque()

        self._subscribers = {}
        self._task = None

    # region Interface
    def run(self, host, port, loop):
        self.loop = loop
        self._sock.bind((host, port))
        self._run_future(self._recv_periodically())

    def stop(self):
        self._sock.close()
        self._subscribers = {}

    def subscribe(self, fut):
        self._subscribers[id(fut)] = fut

    def unsubscribe(self, fut):
        self._subscribers.pop(id(fut), None)

    # endregion

    def _run_future(self, *args):
        for fut in args:
            asyncio.ensure_future(fut, loop=self.loop)

    def _sock_recv(self, fut=None, registered=False):
        fd = self._sock.fileno()

        if fut is None:
            fut = self.loop.create_future()

        if registered:
            self.loop.remove_reader(fd)

        try:
            data, addr = self._sock.recvfrom(self._recv_max_size)
        except (BlockingIOError, InterruptedError):
            self.loop.add_reader(fd, self._sock_recv, fut, True)
        except Exception as e:
            fut.set_result(0)
            self._socket_error(e)
        else:
            fut.set_result((data, addr))

        return fut

    async def _recv_periodically(self):
        while True:
            data, addr = await self._sock_recv()
            self._notify_subscribers(*self._datagram_received(data, addr))

    def _socket_error(self, e):
        pass

    def _datagram_received(self, data, addr):
        return data, addr

    def _notify_subscribers(self, data, addr):
        self._run_future(*(fut(data, addr) for fut in self._subscribers.values()))