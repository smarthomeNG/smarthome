#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2020-      <AUTHOR>                                  <EMAIL>
#########################################################################
#  This file is part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  Sample plugin for new plugins to run with SmartHomeNG version 1.10
#  and up.
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

import asyncio

from lib.model.smartplugin import SmartPlugin
from lib.item import Items

from .webif import WebInterface


# If a needed package is imported, which might be not installed in the Python environment,
# add it to a requirements.txt file within the plugin's directory


class SamplePlugin(SmartPlugin):
    """
    Main class of the Plugin. Does all plugin specific stuff and provides
    the update functions for the items

    HINT: Please have a look at the SmartPlugin class to see which
    class properties and methods (class variables and class functions)
    are already available!
    """

    PLUGIN_VERSION = '1.0.0'  # must match the version in plugin.yaml; use '1.0.0' for initial release
    ALLOW_MULTIINSTANCE = False  # set to True if the plugin can run as multiple instances simultaneously

    def __init__(self, sh=None, **kwargs):
        """
        Initalizes the plugin.

        If you need the sh object at all, use the method self.get_sh() to get it. There should be almost no need for
        a reference to the sh object any more.

        Plugins have to use the new way of getting parameter values:
        use the SmartPlugin method get_parameter_value(parameter_name). Anywhere within the Plugin you can get
        the configured (and checked) value for a parameter by calling self.get_parameter_value(parameter_name). It
        returns the value in the datatype that is defined in the metadata.
        """

        # Call init code of parent class (SmartPlugin)
        super().__init__()

        # cycle time in seconds, only needed, if hardware/interface needs to be
        # polled for value changes by adding a scheduler entry in the run method of this plugin
        # (maybe you want to make it a plugin parameter?)
        #
        # self._cycle = 60

        # if you want to use an item to toggle plugin execution, enable the
        # definition in plugin.yaml and uncomment the following line
        #
        # self._pause_item_path = self.get_parameter_value('pause_item')

        # Initialization code goes here

        # On initialization error use:
        #
        # self._init_complete = False
        # return

        self.init_webinterface(WebInterface)
        # if plugin should not start without web interface
        #
        # if not self.init_webinterface():
        #     self._init_complete = False

    def run(self):
        """
        Run method for the plugin
        """
        self.logger.dbghigh(self.translate("Methode '{method}' aufgerufen", {'method': 'run()'}))

        # connect to network / web / serial device
        # (enable the following lines if you want to open a connection
        #  don't forget to implement a connect (and disconnect) method.. :) )
        #
        # self.connect()

        # setup scheduler for device poll loop
        # (enable the following line, if you need to poll the device.
        #  Rember to un-comment the self._cycle statement in __init__ as well)
        #
        # self.scheduler_add(self.get_fullname() + '_poll', self.poll_device, cycle=self._cycle)

        # Start the asyncio eventloop in it's own thread
        # and set self.alive to True when the eventloop is running
        # (enable the following line, if you need to use asyncio in the plugin)
        #
        # self.start_asyncio(self.plugin_coro())

        self.alive = True  # if using asyncio, do not set self.alive here. Set it in the session coroutine

        # let the plugin change the state of pause_item
        if self._pause_item:
            self._pause_item(False, self.get_fullname())

        # if you need to create child threads, do not make them daemon = True!
        # They will not shutdown properly. (It's a python bug)
        # Also, don't create the thread in __init__() and start them here, but
        # create and start them here. Threads can not be restarted after they
        # have been stopped...

    def stop(self):
        """
        Stop method for the plugin
        """
        self.logger.dbghigh(self.translate("Methode '{method}' aufgerufen", {'method': 'stop()'}))
        self.alive = False  # if using asyncio, do not set self.alive here. Set it in the session coroutine

        # let the plugin change the state of pause_item
        if self._pause_item:
            self._pause_item(True, self.get_fullname())

        # this stops all schedulers the plugin has started.
        # you can disable/delete the line if you don't use schedulers
        self.scheduler_remove_all()

        # stop the asyncio eventloop and it's thread
        # If you use asyncio, enable the following line
        #
        # self.stop_asyncio()

        # If you called connect() on run(), disconnect here
        # (remember to write a disconnect() method!)
        #
        # self.disconnect()

        # also, clean up anything you set up in run(), so the plugin can be
        # cleanly stopped and started again

    def parse_item(self, item):
        """
        Default plugin parse_item method. Is called when the plugin is initialized.
        The plugin can, corresponding to its attribute keywords, decide what to do with
        the item in future, like adding it to an internal array for future reference
        :param item:    The item to process.
        :return:        If the plugin needs to be informed of an items change you should return a call back function
                        like the function update_item down below. An example when this is needed is the knx plugin
                        where parse_item returns the update_item function when the attribute knx_send is found.
                        This means that when the items value is about to be updated, the call back function is called
                        with the item, caller, source and dest as arguments and in case of the knx plugin the value
                        can be sent to the knx with a knx write function within the knx plugin.
        """
        # the pause item is registered by SmartPlugin
        if item.property.path == self._pause_item_path:
            return super().parse_item(item)

        if self.has_iattr(item.conf, 'foo_itemtag'):
            self.logger.debug(f'parse item: {item}')
            # Register the item so update_item() is called when the item changes.
            # updating=True means the item is also tracked in get_trigger_items().
            self.add_item(item, updating=True)
            return self.update_item

    def parse_logic(self, logic):
        """
        Default plugin parse_logic method
        """
        if 'xxx' in logic.conf:
            # self.function(logic['name'])
            pass

    def update_item(self, item, caller=None, source=None, dest=None):
        """
        Item has been updated

        This method is called, if the value of an item has been updated by SmartHomeNG.
        It should write the changed value out to the device (hardware/interface) that
        is managed by this plugin.

        To prevent a loop, the changed value should only be written to the device, if the plugin is running and
        the value was changed outside of this plugin(-instance). That is checked by comparing the caller parameter
        with the fullname (plugin name & instance) of the plugin.

        :param item: item to be updated towards the plugin
        :param caller: if given it represents the callers name
        :param source: if given it represents the source
        :param dest: if given it represents the dest
        """
        # pause item changes call on_pause_item_change(), which stops/runs the plugin unless overwritten
        if self._handle_pause_item(item, caller):
            return

        if self.alive and caller != self.get_fullname():
            # code to execute if the plugin is not stopped
            # and only, if the item has not been changed by this plugin:
            self.logger.info(
                f"update_item: '{item.property.path}' has been changed outside this plugin "
                f"by caller '{self.callerinfo(caller, source)}'"
            )

            # OPTIONAL (asyncio): bridge the synchronous update_item call into
            # the plugin's async event loop.  run_asyncio_coro() blocks until
            # the coroutine returns, so update_item stays synchronous to shNG.
            # result = self.run_asyncio_coro(self._async_send('some_command', item()))

            pass

    def poll_device(self):
        """
        Polls for updates of the device

        This method is only needed, if the device (hardware/interface) does not propagate
        changes on it's own, but has to be polled to get the actual status.
        It is called by the scheduler which is set within run() method.
        """
        # # get the value from the device
        # device_value = ...
        #
        # # find the item(s) to update:
        # for item in self.sh.find_items('...'):
        #
        #     # update the item by calling item(value, caller, source=None, dest=None)
        #     # - value and caller must be specified, source and dest are optional
        #     #
        #     # The simple case:
        #     item(device_value, self.get_fullname())
        #     # if the plugin is a gateway plugin which may receive updates from several external sources,
        #     # the source should be included when updating the value:
        #     item(device_value, self.get_fullname(), source=device_source_id)
        pass

    # ==========================================================================
    # OPTIONAL: asyncio support
    # ==========================================================================
    # Use this block if your plugin relies on an asyncio-based device library.
    # SmartPlugin runs the plugin coroutine in a dedicated per-plugin event loop
    # inside its own thread, separate from the main shNG event loop.
    #
    # Enable by uncommenting the corresponding lines in run() and stop():
    #   run()  → self.start_asyncio(self.plugin_coro())
    #   stop() → self.stop_asyncio()
    # When using asyncio, do NOT set self.alive in run()/stop() — plugin_coro
    # manages self.alive so that the timing matches the event loop's lifecycle.
    # ==========================================================================

    async def plugin_coro(self):
        """
        Async entry point for the plugin (only needed when using asyncio).

        SmartPlugin.start_asyncio() launches this coroutine inside a dedicated
        event loop thread.  The coroutine is responsible for managing self.alive
        so the rest of shNG knows when the plugin is actually running.

        Lifecycle
        ---------
        1. One-time async setup (e.g. open a client connection).
        2. Set self.alive = True and notify the pause item.
        3. Await wait_for_asyncio_termination() — this blocks until stop()
           calls stop_asyncio(), which puts 'STOP' on the internal run-queue.
        4. Async teardown, then self.alive = False.
        """
        self.logger.debug('plugin_coro: started')

        # --- one-time async setup (open connection, subscribe to events, …) ---
        # await self._async_connect()

        self.alive = True
        if self._pause_item:
            self._pause_item(False, self.get_fullname())

        # Keep running until stop_asyncio() signals termination.
        await self.wait_for_asyncio_termination()

        # --- async teardown ---
        # await self._async_disconnect()

        self.alive = False
        if self._pause_item:
            self._pause_item(True, self.get_fullname())

        self.logger.debug('plugin_coro: finished')

    async def _async_send(self, command: str, value) -> bool:
        """
        Example async helper: send a command/value to the device.

        Call this from synchronous code (e.g. update_item) via the bridge::

            result = self.run_asyncio_coro(self._async_send('power', True))

        run_asyncio_coro() submits the coroutine to the plugin event loop and
        blocks the calling thread until the coroutine returns.

        :param command: device command name
        :param value:   value to send
        :return:        True on success, False on error
        """
        self.logger.debug(f'_async_send: {command!r} = {value!r}')
        # Replace with your actual async device call, e.g.:
        #   await self._client.write(command, value)
        return True
