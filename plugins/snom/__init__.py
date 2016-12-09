#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2012-2013 Marcus Popp                         marcus@popp.mx
#########################################################################
#  This file is part of SmartHomeNG.    https://github.com/smarthomeNG//
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
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree

logger = logging.getLogger('')


class Snom():

    def __init__(self, smarthome, username=None, password=None, phonebook=None):
        self._sh = smarthome
        self._phonebook = phonebook
        self._username = username
        self._password = password

    def run(self):
        self.alive = True
        # if you want to create child threads, do not make them daemon = True!
        # They will not shutdown properly. (It's a python bug)

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if 'snom_key' in item.conf:
            logger.debug("parse item: {0}".format(item))
            if 'snom_host' in item.conf:
                return self.update_item
            else:
                parent = item.return_parent()
                if hasattr(parent, 'conf'):
                    if 'snom_host' in parent.conf:
                        item.conf['snom_host'] = parent.conf['snom_host']
                        return self.update_item
            logger.warning("No 'snom_host' specified for {0}".format(item.id()))

    def parse_logic(self, logic):
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'HTTP':
            uri = "https://{0}/dummy.htm".format(item.conf['snom_host'])
            req = "{0}?settings=save&store_settings=save&{1}={2}".format(uri, item.conf['snom_key'], urllib.parse.quote(str(item())))
            try:
                self._sh.tools.fetch_url(req, self._username, self._password)
            except Exception as e:
                logger.exception("Error updating Snom Phone ({0}): {1}".format(item.conf['snom_host'], e))

    def phonebook_add(self, name, number):
        if self._phonebook is None:
            logger.warning("Snom: No Phonebook specified")
            return
        root = xml.etree.ElementTree.Element('SnomIPPhoneDirectory')
        root.text = "\n"
        tree = xml.etree.ElementTree.ElementTree(root)
        try:
            root = tree.parse(self._phonebook)
        except IOError as e:
            logger.warning("Could not read {0}: {1}".format(self._phonebook, e))
        except Exception as e:
            logger.warning("Problem reading {0}: {1}".format(self._phonebook, e))
            return
        found = False
        for entry in tree.findall('DirectoryEntry'):
            ename = entry.findtext('Name')
            if ename == name:
                # update number
                entry.find('Telephone').text = number
                found = True
        if not found:
            # add new element
            new = xml.etree.ElementTree.SubElement(tree.getroot(), 'DirectoryEntry')
            new.tail = "\n"
            xml.etree.ElementTree.SubElement(new, 'Name').text = name
            xml.etree.ElementTree.SubElement(new, 'Telephone').text = number
            # sort
            data = []
            for entry in tree.findall('DirectoryEntry'):
                key = entry.findtext("Name")
                data.append((key, entry))
            data.sort()
            root[:] = [item[-1] for item in data]
        try:
            tree.write(self._phonebook, encoding="UTF-8", xml_declaration=True)
        except Exception as e:
            logger.warning("Problem writing {0}: {1}".format(self._phonebook, e))
