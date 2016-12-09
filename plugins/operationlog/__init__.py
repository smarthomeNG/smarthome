#!/usr/bin/env python3
#########################################################################
# Copyright 2016 Jan Troelsen                             jan@troelsen.de
#########################################################################
#  operationlogger
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
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import threading
import datetime
import lib.log
import os
import pickle

from .AutoBlindLoggerOLog import AbLogger

logger = logging.getLogger('')


class OperationLog(AbLogger):
    _log = None
    _items = {}

    def __init__(self, smarthome, name, cache=True, logtofile=True, filepattern="{year:04}-{month:02}-{day:02}-{name}.log",
                 mapping=['time', 'thread', 'level', 'message'], items=[], maxlen=50):
        log_directory = "var/log/operationlog/"
        self._sh = smarthome
        self.name = name
        if log_directory[0] != "/":
            base = self._sh.base_dir
            if base[-1] != "/":
                base += "/"
            self.log_directory = base + log_directory
        else:
            self.log_directory = log_directory
        if not os.path.exists(self.log_directory):
            os.makedirs(log_directory)
        AbLogger.set_logdirectory(self.log_directory)
        AbLogger.set_loglevel(2)
        AbLogger.set_logmaxage(0)
        AbLogger.__init__(self, name)
        self._filepattern = filepattern
        self._log = lib.log.Log(smarthome, name, mapping, int(maxlen))
        self._path = name
        self._cachefile = None
        self._cache = True
        self.__myLogger = None
        self._logcache = None
        self._maxlen = int(maxlen)
        self._items = items
        self._item_conf = {}
        self.__date = None
        self.__fname = None
        info_txt_cache = ", caching active"
        if isinstance(cache, str) and cache in ['False', 'false', 'No', 'no']:
            self._cache = False
            info_txt_cache = ""
        self._logtofile = True
        info_txt_log = "OperationLog {}: logging to file {}{}, keeping {} entries in memory".format(self.name, self.log_directory,
                                                                                                    self._filepattern, int(self._maxlen))
        if isinstance(logtofile, str) and logtofile in ['False', 'false', 'No', 'no']:
            self._logtofile = False
        logger.info(info_txt_log + info_txt_cache)

        #############################################################
        # Cache
        #############################################################
        if self._cache is True:
            self._cachefile = self._sh._cache_dir + self._path
            try:
                self.__last_change, self._logcache = _cache_read(self._cachefile, self._sh._tzinfo)
                self.load(self._logcache)
                logger.debug("OperationLog {}: read cache: {}".format(self.name, self._logcache))
            except Exception:
                try:
                    _cache_write(self._cachefile, self._log.export(int(self._maxlen)))
                    _cache_read(self._cachefile, self._sh._tzinfo)
                    logger.info("OperationLog {}: generated cache file".format(self.name))
                except Exception as e:
                    logger.warning("OperationLog {}: problem reading cache: {}".format(self._path, e))

    def update_logfilename(self):
        if self.__date == datetime.datetime.today() and self.__fname is not None:
            return
        now = self._sh.now()
        self.__fname = self._filepattern.format(**{'name': self.name, 'year': now.year, 'month': now.month, 'day': now.day})
        self.__myLogger.update_logfile(self.__fname)

    def run(self):
        if self._logtofile is True:
            self.__myLogger = self.create(self.name)
        sh = self._sh
        for item_id in self._item_conf:
            if 'olog_eval' in self._item_conf[item_id]:
                for (ind, eval_str) in enumerate(self._item_conf[item_id]['olog_eval']):
                    try:
                        eval(eval_str)
                    except Exception as e:
                        logger.warning('olog: could not evaluate {} for item: {}, {}'.format(eval_str, item_id, e))
                        self._item_conf[item_id]['olog_eval'][ind] = "'--'"
        self.alive = True

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if 'olog' in item.conf and item.conf['olog'] == self.name:
            self._item_conf[item.id()] = {}
            if 'olog_txt' in item.conf or 'olog_rules' in item.conf:
                self._item_conf[item.id()]['olog_rules'] = {}
                self._item_conf[item.id()]['olog_rules']['lowlim'] = None
                self._item_conf[item.id()]['olog_rules']['highlim'] = None
                self._item_conf[item.id()]['olog_rules']['*'] = None
            if 'olog_txt' in item.conf:
                olog_txt = item.conf['olog_txt']
                self._item_conf[item.id()]['olog_eval'] = []
                pos = -1
                while True:
                    pos = olog_txt.find('{eval=', pos + 1)
                    if pos == -1:
                        break
                    start = pos + 5
                    pos = olog_txt.find('}', pos + 1)
                    if pos == -1:
                        logger.warning('olog: did not find ending } for eval in item.conf, item {}'.format(item.id()))
                        break
                    eval_str = olog_txt[start + 1:pos]
                    self._item_conf[item.id()]['olog_eval'].append(eval_str)
                    olog_txt = olog_txt[:start - 4] + olog_txt[pos:]
                    pos = start
                self._item_conf[item.id()]['olog_txt'] = olog_txt
                if len(self._item_conf[item.id()]['olog_eval']) != 0:
                    logger.info('Item: {}, olog evaluating: {}'.format(item.id(), self._item_conf[item.id()]['olog_eval']))
            if 'olog_rules' in item.conf:
                olog_rules = item.conf['olog_rules']
                if isinstance(olog_rules, str):
                    olog_rules = [olog_rules, ]
                for txt in olog_rules:
                    key_txt, value = txt.split(':')
                    if key_txt == 'True':
                        key = True
                    elif key_txt == 'False':
                        key = False
                    else:
                        try:
                            if float(key_txt) == int(key_txt):
                                key = int(key_txt)
                            else:
                                key = float(key_txt)
                        except:
                            key = key_txt
                            if key_txt in ['lowlim', 'highlim']:
                                self._item_conf[item.id()]['olog_rules']["*"] = 'value'
                    self._item_conf[item.id()]['olog_rules'][key] = value
                if len(self._item_conf[item.id()]['olog_rules']) != 0:
                    logger.info('Item: {}, olog rules: {}'.format(item.id(), self._item_conf[item.id()]['olog_rules']))
            return self.update_item
        else:
            return None

    def parse_logic(self, logic):
        pass

    def __call__(self, param1=None, param2=None):
        if isinstance(param1, list) and isinstance(param2, type(None)):
            self.log(param1)
        elif isinstance(param1, str) and isinstance(param2, type(None)):
            self.log([param1])
        elif isinstance(param1, str) and isinstance(param2, str):
            self.log([param2], param1)
        elif isinstance(param1, type(None)) and isinstance(param2, type(None)):
            return self._log

    def load(self, logentries):
        if len(logentries) != 0:
            for logentry in reversed(logentries):
                log = []
                for name in self._log.mapping:
                    if name == 'time':
                        log.append(logentry['time'])
                    elif name == 'thread':
                        log.append(logentry['thread'])
                    elif name == 'level':
                        log.append(logentry['level'])
                    elif name == 'message':
                        log.append(logentry['message'])
                self._log.add(log)

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'OperationLog':
            if item.conf['olog'] == self.name:
                if len(self._items) == 0:
                    if item.id() in self._item_conf and 'olog_txt' in self._item_conf[item.id()]:
                        mvalue = item()
                        if 'olog_rules' in self._item_conf[item.id()]:
                            if 'lowlim' in self._item_conf[item.id()]['olog_rules']:
                                if item.type() == 'num':
                                    if self._item_conf[item.id()]['olog_rules']['lowlim'] is not None and item() < float(self._item_conf[item.id()]['olog_rules']['lowlim']):
                                        return
                                elif item.type() == 'str':
                                    if self._item_conf[item.id()]['olog_rules']['lowlim'] is not None and item() < str(self._item_conf[item.id()]['olog_rules']['lowlim']):
                                        return
                            if 'highlim' in self._item_conf[item.id()]['olog_rules']:
                                if item.type() == 'num':
                                    if self._item_conf[item.id()]['olog_rules']['highlim'] is not None and item() >= float(self._item_conf[item.id()]['olog_rules']['highlim']):
                                        return
                                elif item.type() == 'str':
                                    if self._item_conf[item.id()]['olog_rules']['highlim'] is not None and item() >= str(self._item_conf[item.id()]['olog_rules']['highlim']):
                                        return
                            try:
                                mvalue = self._item_conf[item.id()]['olog_rules'][item()]
                            except KeyError:
                                mvalue = item()
                                if self._item_conf[item.id()]['olog_rules']["*"] is None:
                                    return
                        sh = self._sh
                        self._item_conf[item.id()]['olog_eval_res'] = []
                        for expr in self._item_conf[item.id()]['olog_eval']:
                            self._item_conf[item.id()]['olog_eval_res'].append(eval(expr))
                        logtxt = self._item_conf[item.id()]['olog_txt'].format(*self._item_conf[item.id()]['olog_eval_res'],
                                                                               **{'value': item(),
                                                                                  'mvalue': mvalue,
                                                                                  'name': str(item),
                                                                                  'age': round(item.prev_age(), 2),
                                                                                  'pname': str(item.return_parent()),
                                                                                  'id': item.id(),
                                                                                  'pid': item.return_parent().id(),
                                                                                  'lowlim': self._item_conf[item.id()]['olog_rules']['lowlim'],
                                                                                  'highlim': self._item_conf[item.id()]['olog_rules']['highlim']})
                        logvalues = [logtxt]
                    else:
                        logvalues = [item.id(), '=', item()]
                else:
                    logvalues = []
                    for it in self._items:
                        logvalues.append('{} = {} '.format(str(it), self._sh.return_item(it)()))
                self.log(logvalues, 'INFO' if 'olog_level' not in item.conf else item.conf['olog_level'])

    def log(self, logvalues, level='INFO'):
        if len(logvalues):
            log = []
            for name in self._log.mapping:
                if name == 'time':
                    log.append(self._sh.now())
                elif name == 'thread':
                    log.append(threading.current_thread().name)
                elif name == 'level':
                    log.append(level)
                else:
                    values_txt = map(str, logvalues)
                    log.append(' '.join(values_txt))
            self._log.add(log)
            if self._logtofile is True:
                self.update_logfilename()
                self.__myLogger.info('{}: {}', log[2], ''.join(log[3:]))

            if self._cache is True:
                try:
                    _cache_write(self._cachefile, self._log.export(int(self._maxlen)))
                except Exception as e:
                    logger.warning("OperationLog {}: could not update cache {}".format(self._path, e))


#####################################################################
# Cache Methods
#####################################################################
def _cache_read(filename, tz):
    ts = os.path.getmtime(filename)
    dt = datetime.datetime.fromtimestamp(ts, tz)
    value = None
    with open(filename, 'rb') as f:
        value = pickle.load(f)
    return (dt, value)


def _cache_write(filename, value):
    try:
        with open(filename, 'wb') as f:
            pickle.dump(value, f)
    except IOError:
        logger.warning("Could not write to {}".format(filename))