#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
# Copyright 2013 KNX-User-Forum e.V.            http://knx-user-forum.de/
#
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
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#

import logging
import json
import http.client
import time
import threading

logger = logging.getLogger('')


class HUE():

    def __init__(self, smarthome, hue_ip='Philips-hue', hue_user=None, hue_port=80, cycle=10):
        self._sh = smarthome
        self._hue_ip = hue_ip
        self._hue_user = hue_user
        self._lamps = {}
        self._lampslock = threading.Lock()
        self._sh.scheduler.add('hue-update', self._update_lamps, cycle=cycle)
        self._sh.trigger('hue-update', self._update_lamps)

    def run(self):
        self.alive = True
        # if you want to create child threads, do not make them daemon = True!
        # They will not shutdown properly. (It's a python bug)

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if 'hue_id' in item.conf:
            logger.debug("parse item: {0}".format(item))
            item.hue_id = int(item.conf['hue_id'])
            if 'hue_transitiontime' in item.conf:
                item.hue_transitiontime = int(item.conf['hue_transitiontime'])
            else:
                item.hue_transitiontime = 5
            if 'hue_feature' in item.conf:
                item.hue_feature = item.conf['hue_feature']
            else:
                if item.type() == 'bool':
                    item.hue_feature = 'on'
                elif item.type() == 'num':
                    item.hue_feature = 'bri'
                elif item.type() == 'dict':
                    item.hue_feature = 'all'
                else:
                    logger.error(
                        "Can't decide for hue feature based on item type. Item {0}".format(item))
            itemkey = item.hue_feature + 'items'
            self._lampslock.acquire()
            try:
                if not item.hue_id in self._lamps:
                    self._lamps[item.hue_id] = {
                        itemkey: [item], 'state': None, 'lastupdate': 0}
                else:
                    if itemkey in self._lamps[item.hue_id]:
                        logger.debug("Add Lamp {0}".format(item.hue_id))
                        self._lamps[item.hue_id][itemkey].append(item)
                    else:
                        self._lamps[item.hue_id][itemkey] = [item]
                # if a state is already available, set it
                currentstate = self._lamps[item.hue_id].get('state', None)
                if currentstate is not None:
                    if item.hue_feature == 'all':
                        item(self._lamps[item.hue_id]['state'], caller='HUE')
                    else:
                        item(self._lamps[item.hue_id]['state']
                             [item.hue_feature], caller='HUE')
            finally:
                self._lampslock.release()
            return self.update_item
        else:
            return None

    def update_item(self, item, caller=None, source=None, dest=None):
        logging.debug("Update: caller {0}".format(caller))
        if caller != 'HUE':
            logger.info("update item: {0}".format(item.id()))
            if item.hue_feature == 'all':
                self._set_state(item.hue_id, item())
            elif item.hue_feature == 'on':
                bri = 254 * item()
                self._set_state(
                    item.hue_id, {"on": item(), "bri": bri, "transitiontime": item.hue_transitiontime})
                for item in self._lamps[item.hue_id]['briitems']:
                    item(bri, caller='HUE')
            elif item.hue_feature == 'bri':
                value = item()
                if isinstance(value, float):
                    value = int(value + 0.5)
                on = value > 0
                self._set_state(
                    item.hue_id, {"on": on, "bri": value, "transitiontime": item.hue_transitiontime})
                for item in self._lamps[item.hue_id]['onitems']:
                    item(on, caller='HUE')
            else:
                value = item()
                if isinstance(value, float):
                    value = int(value + 0.5)
                self._set_state(
                    item.hue_id, {item.hue_feature: value, "transitiontime": item.hue_transitiontime})

    def _request(self, path="", method="GET", data=None):
        con = http.client.HTTPConnection(self._hue_ip)
        con.request(method, "/api/%s%s" % (self._hue_user, path), data)
        resp = con.getresponse()
        con.close()

        if resp.status != 200:
            logger.error("Request failed")
            return None

        resp = resp.read().decode("utf-8")
        # logger.debug(resp)

        resp = json.loads(resp)

        # logger.debug(resp)

        if isinstance(resp, list) and resp[0].get("error", None):
            error = resp[0]["error"]
            if error["type"] == 1:
                description = error["description"]
                logger.error(
                    "Error: {0} (Need to specify correct hue user?)".format(description))
                raise Exception("Hue error: {0}".format(description))
        else:
            return resp

    def _set_state(self, light_id, state):
        try:
            values = self._request("/lights/%s/state" % light_id,
                                   "PUT", json.dumps(state))
            # update information database
            for part in values:
                for status, info in part.items():
                    if status == 'success':
                        for path, val in info.items():
                            parm = path.split('/')[4]
                            logger.debug(
                                "{0} {2}  => {1}".format(path, val, parm))
                            if parm in self._lamps[light_id]['state']:
                                self._lamps[light_id]['state'][parm] = val
                    else:
                        logger.error("hue: {0}: {1}".format(status, info))
                        raise Exception(
                            "Hue error: {0}: {1}".format(status, info))
            self._lamps[light_id]['lastupdate'] = time.time()
        except Exception:
            self._lamps[light_id]['state'] = None  # to get an update
        return self

    def _update_lamps(self):
        try:
            values = self._request()
            for lamp_id, lamp_info in values['lights'].items():
                lamp_id = int(lamp_id)
                state = lamp_info['state']
                logger.debug("Lamp {0}, State {1}".format(lamp_id, state))
                self._lampslock.acquire()
                try:
                    lamp = self._lamps.get(lamp_id, None)
                    if lamp is not None:
                        tick = time.time()
                        if (tick - lamp['lastupdate'] > 2):
                            # determine difference
                            oldstate = lamp['state']
                            if oldstate is None:
                                diff = list(state.keys())
                            else:
                                diff = set(
                                    o for o in state if oldstate[o] != state[o])
                            # Update the differences
                            for up in diff:
                                newval = state[up]
                                logger.info(
                                    "New value for {0}: {1}".format(up, newval))
                                for item in lamp.get(up + 'items', []):
                                    item(newval, caller='HUE')
                            if len(diff) > 0:
                                for item in lamp.get('allitems', []):
                                        item(state, caller='HUE')
                        lamp['state'] = state
                        lamp['lastupdate'] = tick
                    else:
                        # lamp not used, add it to databse
                        logger.debug("Add lamp {0}".format(lamp_id))
                        self._lamps[lamp_id] = {'state':
                                                state, 'lastupdate': time.time()}
                finally:
                    self._lampslock.release()
        except:
            # communication failed
            pass

    def authorizeuser(self):
        data = json.dumps(
            {"devicetype": "smarthome", "username": self._hue_user})

        con = http.client.HTTPConnection(self._hue_ip)
        con.request("POST", "/api", data)
        resp = con.getresponse()
        con.close()

        if resp.status != 200:
            logger.error("Authenticate request failed")
            return "Authenticate request failed"

        resp = resp.read()
        logger.debug(resp)

        resp = json.loads(resp)

        logger.debug(resp)
        return resp

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    myplugin = HUE('smarthome-dummy')
    myplugin.run()
