#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""Datatypes of the MPD tutorial example."""

import lib.model.sdp.datatypes as DT


class DT_mpdflag(DT.Datatype):
    """MPD flag: ``1``/``0`` on the wire, bool in shng."""

    def get_send_data(self, data, **kwargs):
        return 1 if data else 0

    def get_shng_data(self, data, type=None, **kwargs):
        if type is None:
            return data == '1'
        return super().get_shng_data(data, type)
