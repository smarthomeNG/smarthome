#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016 Christian Strassburg  c.strassburg@gmx.de
#########################################################################
# Personal and non-commercial use only, redistribution is prohibited.
#########################################################################

import logging
from lib.utils import Utils

logger = logging.getLogger(__name__)


class SmartObject():

    def __init__(self, **kwargs):
       pass
    def __new__(cls, *args, **kargs):
        if not hasattr(cls,'PLUGIN_VERSION'):
            raise NotImplementedError("'Plugin' subclasses should have a 'PLUGIN_VERSION' attribute")
        return object.__new__(cls)


