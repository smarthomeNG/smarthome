__author__ = 'pfischi'

import threading
from scapy.all import *
import logging
from lib.model.smartplugin import SmartPlugin
import time
from collections import namedtuple

DashBtnItem = namedtuple('DashBtnItem', 'item threshold')
start_time = time.time()


class Dashbutton(SmartPlugin):
    PLUGIN_VERSION = "1.3.0.1"
    ALLOW_MULTIINSTANCE = False

    def __init__(self, sh, *args, **kwargs):
        self._sh = sh
        self._dashbuttons = {}
        self._logger = logging.getLogger(__name__)
        self._scapy_thread = threading.Thread(target=self.listen)
        self._scapy_thread.daemon = True

    def run(self):
        self.alive = True
        self._scapy_thread.start()

    def listen(self):
        sniff(prn=self.dispatch, store=0, count=0, filter="udp", lfilter=lambda d: d.src in self._dashbuttons.keys())

    def stop(self):
        self._scapy_thread.join()
        self.alive = False

    def parse_item(self, item):
        if self.has_iattr(item.conf, 'dashbutton_mac'):

            mac_addresses = self.get_iattr_value(item.conf, 'dashbutton_mac')
            # if separated by |, mac_address is a list, otherwise a string (if only one mac address)

            if isinstance(mac_addresses, str):
                mac_addresses = mac_addresses.split('|')
            # lower all elements
            mac_addresses = [element.lower() for element in mac_addresses]
            # remove duplicates
            mac_addresses = list(set(mac_addresses))

            for mac_address in mac_addresses:
                # prevention from some strange miss behavior by sh.py if "mac1:mac2" as a string with ampersands was set
                mac_address = mac_address.strip().strip('\'').strip('\"')

                if not self.is_mac(mac_address):
                    self._logger.error('MAC address {mac} is not valid'.format(mac=mac_address))
                    return
                if mac_address not in self._dashbuttons:
                    item_list = [DashBtnItem(item, Dashbutton.elapsed_seconds())]
                    self._dashbuttons[mac_address] = item_list
                else:
                    self._dashbuttons[mac_address].append(DashBtnItem(item, Dashbutton.elapsed_seconds()))

    def parse_logic(self, logic):
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        pass

    def dispatch(self, pkt):
        options = pkt[DHCP].options
        for option in options:
            if isinstance(option, tuple) and 'requested_addr' in option:
                mac_address = pkt[Ether].src.lower()
                if not mac_address:
                    break
                if mac_address not in self._dashbuttons:
                    break

                for i in range(len(self._dashbuttons[mac_address])):
                    # sometimes the dashbutton triggers the push twice
                    # store last-push-timestamp to prevent the "double push"
                    delta = Dashbutton.elapsed_seconds() - self._dashbuttons[mac_address][i].threshold
                    self._logger.debug(self._dashbuttons[mac_address][i])
                    if delta < 1:
                        self._logger.debug("Threshold not reached, ignoring last push from {mac}".format(
                            mac=mac_address))
                        continue

                    # set the current timestamp
                    self._dashbuttons[mac_address][i] = \
                        self._dashbuttons[mac_address][i]._replace(threshold=Dashbutton.elapsed_seconds())
                    # check item for dash_button mode
                    item = self._dashbuttons[mac_address][i].item
                    if not self.has_iattr(item.conf, 'dashbutton_mode'):
                        self._logger.warning("{item}: Dashbutton mode missing!".format(item=item))
                        continue
                    mode = self.get_iattr_value(item.conf, 'dashbutton_mode').lower().strip()

                    # check for valid mode
                    if mode not in ['value', 'flip']:
                        self._logger.warning("{item}: unknown mode {mode}!".format(mode=mode, item=item))
                        continue

                    # check that 'flip' mode is only set for bool item
                    if mode == 'flip':
                        if item.type().lower() != 'bool':
                            self._logger.error("{item}: dashbutton mode 'flip' only valid for item type 'bool'!".
                                               format(item=item))
                            continue
                        item(not item(), 'dashbutton')
                        continue

                    if mode == 'value':
                        if not self.has_iattr(item.conf, 'dashbutton_value'):
                            self._logger.error("{item}: dashbutton attribute 'dashbutton_value' has to be set for mode "
                                               "'value'!".format(item=item))
                            continue
                        item(self.get_iattr_value(item.conf, 'dashbutton_value'))
                break

    # returns the elapsed seconds since the start of the program
    @staticmethod
    def elapsed_seconds():
        return time.time() - start_time