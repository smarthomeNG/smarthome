#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2012-2013 Marcus Popp                         marcus@popp.mx
#########################################################################
#  This file is part of SmartHome.py.    http://mknx.github.io/smarthome/
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py.  If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import datetime
import functools
import logging
import os

import rrdtool

logger = logging.getLogger('')


class RRD():

    def __init__(self, smarthome, step=300, rrd_dir=None):
        self._sh = smarthome
        if rrd_dir is None:
            rrd_dir = smarthome.base_dir + '/var/rrd/'
        self._rrd_dir = rrd_dir
        self._rrds = {}
        self.step = int(step)

    def run(self):
        self.alive = True
        # create rrds
        for itempath in self._rrds:
            rrd = self._rrds[itempath]
            if not os.path.isfile(rrd['rrdb']):
                self._create(rrd)
        offset = 100  # wait 100 seconds for 1-Wire to update values
        self._sh.scheduler.add('RRDtool', self._update_cycle, cycle=self.step, offset=offset, prio=5)

    def stop(self):
        self.alive = False

    def _update_cycle(self):
        for itempath in self._rrds:
            rrd = self._rrds[itempath]
            if rrd['type'] == 'GAUGE':
                value = 'N:' + str(float(rrd['item']()))
            else:  # 'COUNTER'
                value = 'N:' + str(int(rrd['step'] * rrd['item']()))
            try:
                rrdtool.update(
                    rrd['rrdb'],
                    value
                )
            except Exception as e:
                logger.warning("RRD: error updating {}: {}".format(itempath, e))
                continue

    def parse_item(self, item):
        if 'rrd' not in item.conf:
            return
        rrdb = self._rrd_dir + item.id() + '.rrd'
        rrd_min = False
        rrd_max = False
        rrd_type = 'GAUGE'
        rrd_step = self.step
        if 'rrd_min' in item.conf:
            rrd_min = self._sh.string2bool(item.conf['rrd_min'])
        if 'rrd_max' in item.conf:
            rrd_max = self._sh.string2bool(item.conf['rrd_max'])
        if 'rrd_type' in item.conf:
            if item.conf['rrd_type'].lower() == 'counter':
                rrd_type = 'COUNTER'
        if 'rrd_step' in item.conf:
            rrd_step = int(item.conf['rrd_step'])
        item.series = functools.partial(self._series, item=item.id())
        item.db = functools.partial(self._single, item=item.id())
        self._rrds[item.id()] = {'item': item, 'id': item.id(), 'rrdb': rrdb, 'max': rrd_max, 'min': rrd_min, 'step': rrd_step, 'type': rrd_type}

        if item.conf['rrd'] == 'init':
            last = self._single('last', '5d', item=item.id())
            if last is not None:
                item.set(last, 'RRDtool')

    def parse_logic(self, logic):
        pass

    def _series(self, func, start='1d', end='now', count=100, ratio=1, update=False, step=None, sid=None, item=None):
        if item in self._rrds:
            rrd = self._rrds[item]
        else:
            logger.warning("RRDtool: not enabled for {}".format(item))
            return
        query = ["{}".format(rrd['rrdb'])]
        if func == 'avg':
            query.append('AVERAGE')
        elif func == 'max':
            if not rrd['max']:
                logger.warning("RRDtool: unsupported consolidation function {} for {}".format(func, item))
                return
            query.append('MAX')
        elif func == 'min':
            if not rrd['min']:
                logger.warning("RRDtool: unsupported consolidation function {} for {}".format(func, item))
                return
            query.append('MIN')
        else:
            logger.warning("RRDtool: unsupported consolidation function {} for {}".format(func, item))
            return
        if start.isdigit():
            query.extend(['--start', "{}".format(start)])
        else:
            query.extend(['--start', "now-{}".format(start)])
        if end != 'now':
            if end.isdigit():
                query.extend(['--end', "{}".format(end)])
            else:
                query.extend(['--end', "now-{}".format(end)])
        if step is not None:
            query.extend(['--resolution', step])
        try:
            meta, name, data = rrdtool.fetch(*query)
        except Exception as e:
            logger.warning("error reading {0} data: {1}".format(item, e))
            return None
        if sid is None:
            sid = item + '|' + func + '|' + start + '|' + end
        reply = {'cmd': 'series', 'series': None, 'sid': sid}
        istart, iend, istep = meta
        mstart = istart * 1000
        mstep = istep * 1000
        tuples = [(mstart + i * mstep, v[0]) for i, v in enumerate(data)]
        reply['series'] = sorted(tuples)
        reply['params'] = {'update': True, 'item': item, 'func': func, 'start': str(iend), 'end': str(iend + istep), 'step': str(istep), 'sid': sid}
        reply['update'] = self._sh.now() + datetime.timedelta(seconds=istep)
        return reply

    def _single(self, func, start='1d', end='now', item=None):
        if item in self._rrds:
            rrd = self._rrds[item]
        else:
            logger.warning("RRDtool: not enabled for {}".format(item))
            return
        query = ["{}".format(rrd['rrdb'])]
        if func == 'avg':
            query.append('AVERAGE')
        elif func == 'max':
            if rrd['max']:
                query.append('MAX')
            else:
                query.append('AVERAGE')
        elif func == 'min':
            if rrd['min']:
                query.append('MIN')
            else:
                query.append('AVERAGE')
        elif func == 'last':
            query.append('AVERAGE')
        else:
            logger.warning("RRDtool: unsupported consolidation function {} for {}".format(func, item))
            return
        if start.isdigit():
            query.extend(['--start', "{}".format(start)])
        else:
            query.extend(['--start', "now-{}".format(start)])
        if end != 'now':
            if end.isdigit():
                query.extend(['--end', "{}".format(end)])
            else:
                query.extend(['--end', "now-{}".format(end)])
        try:
            meta, name, data = rrdtool.fetch(*query)
        except Exception as e:
            logger.warning("error reading {0} data: {1}".format(item, e))
            return None
        values = [v[0] for v in data if v[0] is not None]
        if func == 'avg':
            if len(values) > 0:
                return sum(values) / len(values)
        elif func == 'min':
            if len(values) > 0:
                return min(values)
        elif func == 'max':
            if len(values) > 0:
                return max(values)
        elif func == 'last':
            if len(values) > 0:
                return values[-1]

    def _create(self, rrd):
        args = [rrd['rrdb']]
        item_id = rrd['id'].rpartition('.')[2][:19]
        args.append("DS:{}:{}:{}:U:U".format(item_id, rrd['type'], str(2 * rrd['step'])))
        if rrd['min']:
            args.append('RRA:MIN:0.5:{}:1825'.format(int(86400 / rrd['step'])))  # 24h/5y
        if rrd['max']:
            args.append('RRA:MAX:0.5:{}:1825'.format(int(86400 / rrd['step'])))  # 24h/5y
        args.extend(['--step', str(rrd['step'])])
        if rrd['type'] == 'GAUGE':
            args.append('RRA:AVERAGE:0.5:1:{}'.format(int(86400 / rrd['step']) * 7 + 8))  # 7 days
            args.append('RRA:AVERAGE:0.5:{}:1536'.format(int(1800 / rrd['step'])))  # 0.5h/32 days
            args.append('RRA:AVERAGE:0.5:{}:1600'.format(int(21600 / rrd['step'])))  # 6h/400 days
            args.append('RRA:AVERAGE:0.5:{}:1826'.format(int(86400 / rrd['step'])))  # 24h/5y
            args.append('RRA:AVERAGE:0.5:{}:1300'.format(int(604800 / rrd['step'])))  # 7d/25y
        elif rrd['type'] == 'COUNTER':
            args.append('RRA:AVERAGE:0.5:{}:1826'.format(int(86400 / rrd['step'])))  # 24h/5y
            args.append('RRA:AVERAGE:0.5:{}:1300'.format(int(604800 / rrd['step'])))  # 7d/25y
        try:
            rrdtool.create(*args)
            logger.debug("Creating rrd ({0}) for {1}.".format(rrd['rrdb'], rrd['item']))
        except Exception as e:
            logger.warning("Error creating rrd ({0}) for {1}: {2}".format(rrd['rrdb'], rrd['item'], e))
