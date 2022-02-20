#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      Sebastian Helms             Morg @ knx-user-forum
#########################################################################
#  This file aims to become part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  MultiDevice plugin for handling arbitrary devices via network or serial
#  connection.
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
#
#########################################################################

import json

from lib.item import Items
from lib.model.smartplugin import SmartPluginWebIf
from ..MD_Globals import *
import cherrypy


#############################################################################################################################################################################################################################################
#
# class WebInterface
#
#############################################################################################################################################################################################################################################

class WebInterface(SmartPluginWebIf):

    def __init__(self, webif_dir, plugin):
        """
        Initialization of instance of class WebInterface

        :param webif_dir: directory where the webinterface of the plugin resides
        :param plugin: instance of the plugin
        :type webif_dir: str
        :type plugin: object
        """
        self.logger = plugin.logger
        self.webif_dir = webif_dir
        self.plugin = plugin
        self.items = Items.get_instance()

        self.tplenv = self.init_template_environment()

    @cherrypy.expose
    def index(self, reload=None):
        """
        Build index.html for cherrypy

        Render the template and return the html file to be delivered to the browser

        :return: contents of the template after beeing rendered
        """
        tmpl = self.tplenv.get_template('index.html')
        # add values to be passed to the Jinja2 template eg: tmpl.render(p=self.plugin, interface=interface, ...)

        plgitems = []
        for item in self.items.return_items():
            if any(elem in item.property.attributes for elem in ITEM_ATTRS):
                plgitems.append(item)

        return tmpl.render(p=self.plugin,
                           items=sorted(self.items.return_items(), key=lambda k: str.lower(k['_path'])),
                           item_count=0,
                           plgitems=plgitems,
                           running={dev: self.plugin._devices[dev]['device'].alive for dev in self.plugin._devices},
                           devices=self.plugin._devices,
                           lookups={dev: self.plugin._devices[dev]['device']._commands._lookups for dev in self.plugin._devices})

    @cherrypy.expose
    def submit(self, button=None, param=None):
        """
        Submit handler for Ajax
        """
        if button is not None:

            notify = None

            if '#' in button:

                # run/stop command
                cmd, __, dev = button.partition('#')
                device = self.plugin.get_device(dev)
                if device:
                    if cmd == 'run':
                        self.logger.info(f'Webinterface starting device {dev}')
                        device.start()
                    elif cmd == 'stop':
                        self.logger.info(f'Webinterface stopping device {dev}')
                        device.stop()
            elif '.' in button:

                # set device arg - but only when stopped
                dev, __, arg = button.partition('.')
                if param is not None:
                    param = sanitize_param(param)
                    try:
                        self.logger.info(f'Webinterface setting param {arg} of device {dev} to {param}')
                        self.plugin._devices[dev]['params'][arg] = param
                        self.plugin._update_device_params(dev)
                        notify = dev + '-' + arg + '-notify'
                    except Exception as e:
                        self.logger.info(f'Webinterface failed to set param {arg} of device {dev} to {param} with error {e}')

            # # possibly prepare data for returning
            # read_cmd = self.plugin._commandname_by_commandcode(button)
            # if read_cmd is not None:
            #     self._last_read[button] = {'addr': button, 'cmd': read_cmd, 'val': read_val}
            #     self._last_read['last'] = self._last_read[button]

            data = {'running': {dev: self.plugin._devices[dev]['device'].alive for dev in self.plugin._devices}, 'notify': notify}

        # # possibly return data to WebIf
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(data).encode('utf-8')

    @cherrypy.expose
    def get_data_html(self, dataSet=None):
        """
        Return data to update the webpage

        For the standard update mechanism of the web interface, the dataSet to return the data for is None

        :param dataSet: Dataset for which the data should be returned (standard: None)
        :return: dict with the data needed to update the web page.
        """
        if dataSet is None:
            # get the new data
            # data = {}
            pass

            # data['item'] = {}
            # for i in self.plugin.items:
            #     data['item'][i]['value'] = self.plugin.getitemvalue(i)
            #
            # return it as json the the web page
            # try:
            #     return json.dumps(data)
            # except Exception as e:
            #     self.logger.error('get_data_html exception: {}'.format(e))
        return {}
