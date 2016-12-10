#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2012-2013 Marcus Popp                         marcus@popp.mx
#            2016      Thomas Ernst
#########################################################################
#  This file is part of SmartHome.py.
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

import logging
import threading
import lib.connection
from lib.model.smartplugin import SmartPlugin
from lib.utils import Utils


class CLIHandler(lib.connection.Stream):
    terminator = '\n'.encode()

    def __init__(self, smarthome, sock, source, updates, hashed_password, commands):
        """
        Constructor
        :param smarthome: SmartHomeNG instance
        :param sock: Socket
        :param source: Source
        :param updates: Flag: Updates allowed
        :param hashed_password: Hashed password that is required to logon
        :param commands: CLICommands instance containing available commands
        """
        lib.connection.Stream.__init__(self, sock, source)
        self.logger = logging.getLogger(__name__)
        self.source = source
        self.updates_allowed = updates
        self.sh = smarthome
        self.hashed_password = hashed_password
        self.commands = commands
        self.__prompt_type = ''
        self.push("SmartHomeNG v{0}\n".format(self.sh.version))

        if hashed_password is None:
            self.__push_helpmessage()
            self.__push_command_prompt()
        else:
            self.__push_password_prompt()

    def push(self, data):
        """
        Send data to client
        :param data: String to send
        """
        self.send(data.encode())

    def found_terminator(self, data):
        """
        Received data and found terminator (newline) in data
        :param data: Received data up to terminator
        """
        # Call process methods based on prompt type
        cmd = data.decode().strip()
        if self.__prompt_type == 'password':
            self.__process_password(cmd)
        elif self.__prompt_type == 'command':
            self.__process_command(cmd)

    def __process_password(self, cmd):
        """
        Process entered password
        :param cmd: entered password
        """
        self.__push_password_finished()
        if Utils.check_hashed_password(cmd, self.hashed_password):
            self.logger.debug("CLI: {0} Authorization succeeded".format(self.source))
            self.__push_helpmessage()
            self.__push_command_prompt()
            return
        else:
            self.logger.debug("CLI: {0} Authorization failed".format(self.source))
            self.push("Authorization failed. Bye\n")
            self.close()
            return

    def __process_command(self, cmd):
        """
        Process entered command
        :param cmd: entered command
        """
        if cmd in ('quit', 'q', 'exit', 'x'):
            self.push('bye\n')
            self.close()
            return
        else:
            if not self.commands.execute(self, cmd, self.source):
                self.push("Unknown command.\n")
                self.__push_helpmessage()
            self.__push_command_prompt()

    def __push_helpmessage(self):
        """Push help message to client"""
        self.push("Enter 'help' for a list of available commands.\n")

    def __push_password_prompt(self):
        """
        Push 'echo off' and password prompt to client.
        """
        self.__echo_off()
        self.push("Password: ")
        self.__prompt_type = 'password'

    def __push_password_finished(self):
        """
        Push 'echo on' and newline to client
        :return:
        """
        self.__echo_on()
        self.push("\n")

    def __echo_off(self):
        """
        Send 'IAC WILL ECHO' to client, telling the client that we will echo.
        Check that reply is 'IAC DO ECHO', meaning that the client has understood.
        As we are not echoing entered text will be invisible
        """
        try:
            self.socket.settimeout(2)
            self.send(bytearray([0xFF, 0xFB, 0x01]))  # IAC WILL ECHO
            data = self.socket.recv(3)
            self.socket.setblocking(0)
            if data != bytearray([0xFF, 0xFD, 0x01]):  # IAC DO ECHO
                logger.error("Error at 'echo off': Sent b'\\xff\\xfb\\x01 , Expected reply b'\\xff\\xfd\\x01, received {0}".format(data))
                self.push("'echo off' failed. Bye")
                self.close()
        except Exception as e:
            self.push("\nException at 'echo off'. See log for details.")
            self.logger.exception(e)
            self.close()

    def __echo_on(self):
        """
        Send 'IAC WONT ECHO' to client, telling the client that we wont echo.
        Check that reply is 'IAC DONT ECHO', meaning that the client has understood.
        Now the client should be echoing and we do not have to care about this
        """
        try:
            self.socket.settimeout(2)
            self.send(bytearray([0xFF, 0xFC, 0x01]))  # IAC WONT ECHO
            data = self.socket.recv(3)
            self.socket.setblocking(0)
            if data != bytearray([0xFF, 0xFE, 0x01]):  # IAC DONT ECHO
                logger.error("Error at 'echo on': Sent b'\\xff\\xfc\\x01 , Expected reply b'\\xff\\xfe\\x01, received {0}".format(data))
                self.push("'echo off' failed. Bye")
                self.close()
        except Exception as e:
            self.push("\nException at 'echo on'. See log for details.")
            self.logger.exception(e)
            self.close()

    def __push_command_prompt(self):
        """Push command prompt to client"""
        self.push("> ")
        self.__prompt_type = 'command'


class CLI(lib.connection.Server, SmartPlugin):
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION = '1.1.0'

    def __init__(self, smarthome, update='False', ip='127.0.0.1', port=2323, hashed_password=''):
        """
        Constructor
        :param smarthome: smarthomeNG instance
        :param update: Flag: Updates allowed
        :param ip: IP to bind on
        :param port: Port to bind on
        :param hashed_password: Hashed password that is required to logon
        """
        self.logger = logging.getLogger(__name__)

        if hashed_password is None or hashed_password == '':
            self.logger.warning("CLI: You should set a password for this plugin.")
            hashed_password = None
        elif hashed_password.lower() == 'none':
            hashed_password = None
        elif not Utils.is_hash(hashed_password):
            self.logger.error("CLI: Value given for 'hashed_password' is not a valid hash value. Login will not be possible")

        lib.connection.Server.__init__(self, ip, port)
        self.sh = smarthome
        self.updates_allowed = Utils.to_bool(update)
        self.hashed_password = hashed_password
        self.commands = CLICommands(self.sh, self.updates_allowed)
        self.alive = False

    def handle_connection(self):
        """
        Handle incoming connection
        """
        sock, address = self.accept()
        if sock is None:
            return
        self.logger.debug("{}: incoming connection from {} to {}".format(self._name, address, self.address))
        CLIHandler(self.sh, sock, address, self.updates_allowed, self.hashed_password, self.commands)

    def run(self):
        """
        Called by SmartHomeNG to start plugin
        """
        self.alive = True

    def stop(self):
        """
        Called by SmarthomeNG to stop plugin
        """
        self.alive = False
        self.close()

    def add_command(self, command, function, usage):
        """
        Add command to list of available commands
        :param command: Command to add
        :param function: Function to execute for command
        :param usage: Usage string for help-command
        """
        self.commands.add_command(command, function, usage)

    def remove_command(self, command):
        """
        Remove a command from the list of available commands
        :param command: Command to remove
        :return: True: command found and removed, False: command not found
        """
        return self.commands.remove_command(command)


class CLICommands:
    """
    Class containing handling for CLI commands as well as a basic set of commands
    """

    def __init__(self, smarthome, updates_allowed=False):
        """
        Constructor
        :param smarthome: sh.py instance
        :param updates_allowed: bool True: basic commands may do updates, False: basic commands may not do updates
        """
        self.sh = smarthome
        self.logger = logging.getLogger(__name__)
        self.updates_allowed = updates_allowed
        self._commands = {}

        # Add basic commands
        self.add_command('cl', self._cli_cl, 'cl [log]: clean (memory) log')
        self.add_command('la', self._cli_la, 'la: list all items (with values)')
        self.add_command('update', self._cli_update, 'update [item] = [value]: update the specified item with the specified value')
        self.add_command('up', self._cli_update, 'up: alias for update')
        self.add_command('ls', self._cli_ls, 'ls: list the first level items\nls [item]: list item and every child item (with values)')
        self.add_command('lo', self._cli_lo, 'lo: list all logics and next execution time')
        self.add_command('lt', self._cli_lt, 'lt: list current thread names')
        self.add_command('tr', self._cli_tr, 'tr [logic]: trigger logic')
        self.add_command('rl', self._cli_rl, 'rl [logic]: reload logic')
        self.add_command('rr', self._cli_rr, 'rr [logic]: reload and run logic')
        self.add_command('rt', self._cli_rt, 'rt: return runtime')
        self.add_command('dump', self._cli_dump, 'dump [item]: dump details about given item')
        self.add_command('help', self._cli_help, None)
        self.add_command('h', self._cli_help, None)
        self.add_command('sl', self._cli_sl, 'sl: list all scheduler tasks by name')
        self.add_command('st', self._cli_sl, 'st: list all scheduler tasks by execution time')
        self.add_command('si', self._cli_si, 'si [task]: show details for given task')
        self.add_command('ld', self._cli_ld, 'ld [log]: log dump of (memory) log')

    def add_command(self, command, function, usage):
        """
        Add command to list
        :param command: Command to add
        :param function: Function to execute for command
        :param usage: Usage string for help-command
        """
        self._commands[command] = {'function': function, 'usage': usage}

    def remove_command(self, command):
        """
        Remove a command from the list
        :param command: Command to remove
        :return: True: command found and removed, False: command not found
        """
        if command in self._commands:
            del self._commands[command]
            return True
        else:
            return False

    def execute(self, handler, cmd, source):
        """
        Execute an arbitrary command
        :param handler: CLIHandler to use for reply
        :param cmd: Received command
        :param source: Call source
        :return: TRUE: Command found and handled, FALSE: Unknown command, nothing done
        """
        for command, data in self._commands.items():
            if cmd == command or cmd.startswith(command + " "):
                try:
                    data['function'](handler, cmd.lstrip(command).strip(), source)
                except Exception as e:
                    self.logger.exception(e)
                    handler.push("Exception \"{0}\" occured when executing command \"{1}\".\n".format(e, command))
                    handler.push("See smarthomeNG log for details\n")
                return True
        return False

    # noinspection PyUnusedLocal
    def _cli_tr(self, handler, parameter, source):
        """
        CLI command "tr" - Trigger logic
        :param handler: CLIHandler instance
        :param parameter: Parameters used to call the command
        :param source: Source
        """
        if not self.updates_allowed:
            handler.push("Logic triggering is not allowed.\n")
            return
        if parameter is None or parameter == "":
            handler.push("Please name logic to trigger\n")
        elif parameter in self.sh.return_logics():
            self.sh.trigger(parameter, by='CLI')
            handler.push("Logic '{0}' triggered.\n".format(parameter))
        else:
            handler.push("Logic '{0}' not found.\n".format(parameter))

    # noinspection PyUnusedLocal
    def _cli_rl(self, handler, parameter, source):
        """
        CLI command "rl" - Reload logic
        :param handler: CLIHandler instance
        :param parameter: Parameters used to call the command
        :param source: Source
        """
        if not self.updates_allowed:
            handler.push("Logic triggering is not allowed.\n")
            return
        if parameter is None or parameter == "":
            handler.push("Please name logic to reload\n")
        elif parameter in self.sh.return_logics():
            logic = self.sh.return_logic(parameter)
            logic.generate_bytecode()
            handler.push("Logic '{0}' reloaded.\n".format(parameter))
        else:
            handler.push("Logic '{0}' not found.\n".format(parameter))

    # noinspection PyUnusedLocal
    def _cli_rr(self, handler, parameter, source):
        """
        CLI command "rr" - Reload and trigger logic
        :param handler: CLIHandler instance
        :param parameter: Parameters used to call the command
        :param source: Source
        """
        if not self.updates_allowed:
            handler.push("Logic triggering is not allowed.\n")
            return
        if parameter is None or parameter == "":
            handler.push("Please name logic to reload and trigger")
        elif parameter in self.sh.return_logics():
            logic = self.sh.return_logic(parameter)
            logic.generate_bytecode()
            logic.trigger(by='CLI')
            handler.push("Logic '{0}' reloaded and triggered.\n".format(parameter))
        else:
            handler.push("Logic '{0}' not found.\n".format(name))

    # noinspection PyUnusedLocal
    def _cli_lo(self, handler, parameter, source):
        """
        CLI command "lo" - List logics
        :param handler: CLIHandler instance
        :param parameter: Parameters used to call the command
        :param source: Source
        """
        handler.push("Logics:\n")
        for logic in sorted(self.sh.return_logics()):
            nt = self.sh.scheduler.return_next(logic)
            if nt is not None:
                handler.push("{0} (scheduled for {1})\n".format(logic, nt.strftime('%Y-%m-%d %H:%M:%S%z')))
            else:
                handler.push("{0}\n".format(logic))

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def _cli_lt(self, handler, parameter, source):
        """
        CLI command "lt" - list all threads with names
        :param handler: CLIHandler instance
        :param parameter: Parameters used to call the command
        :param source: Source
        """
        handler.push("{0} Threads:\n".format(threading.activeCount()))
        for t in threading.enumerate():
            handler.push("{0}\n".format(t.name))

    # noinspection PyUnusedLocal
    def _cli_rt(self, handler, parameter, source):
        """
        CLI command "rt" - show runtime
        :param handler: CLIHandler instance
        :param parameter: Parameters used to call the command
        :param source: Source
        """
        handler.push("Runtime: {}\n".format(self.sh.runtime()))

    # noinspection PyUnusedLocal
    def _cli_ls(self, handler, parameter, source):
        """
        CLI command "ls" - list first level items
        :param handler: CLIHandler instance
        :param parameter: Parameters used to call the command
        :param source: Source
        """
        handler.push("Items:\n======\n")
        self._cli_ls_int(handler, parameter, '*' in parameter or ':' in parameter)

    def _cli_ls_int(self, handler, parameter, match=True):
        """
        Internal processing for command "ls"
        :param handler: CLIHandler instance
        :param parameter: Parameters used to call the command
        :param match: True: use match_items to select items, False: single item given
        """
        if not parameter:
            for item in self.sh:
                handler.push("{0}\n".format(item.id()))
        else:
            if match:
                items = self.sh.match_items(parameter)
                childs = False
            else:
                items = [self.sh.return_item(parameter)]
                childs = True
            if len(items):
                for item in items:
                    if hasattr(item, 'id'):
                        if item.type():
                            handler.push("{0} = {1}\n".format(item.id(), item()))
                        else:
                            handler.push("{}\n".format(item.id()))
                        if childs:
                            for child in item:
                                self._cli_ls_int(handler, child.id())
            else:
                handler.push("Could not find path: {}\n".format(parameter))

    # noinspection PyUnusedLocal
    def _cli_dump(self, handler, parameter, source):
        """
        CLI command "dump" - dump item(s)
        :param handler: CLIHandler instance
        :param parameter: Parameters used to call the command
        :param source: Source
        """
        if '*' in parameter or ':' in parameter:
            items = self.sh.match_items(parameter)
        else:
            items = [self.sh.return_item(parameter)]
        if len(items):
            for item in items:
                # noinspection PyProtectedMember
                if hasattr(item, 'id') and item._type:
                    handler.push("Item {} ".format(item.id()))
                    handler.push("{\n")
                    handler.push("  type = {}\n".format(item.type()))
                    handler.push("  value = {}\n".format(item()))
                    handler.push("  age = {}\n".format(item.age()))
                    handler.push("  last_change = {}\n".format(item.last_change()))
                    handler.push("  changed_by = {}\n".format(item.changed_by()))
                    handler.push("  previous_value = {}\n".format(item.prev_value()))
                    handler.push("  previous_age = {}\n".format(item.prev_age()))
                    handler.push("  previous_change = {}\n".format(item.prev_change()))
                    if hasattr(item, 'conf'):
                        handler.push("  config = {\n")
                        for name in item.conf:
                            handler.push("    {} = {}\n".format(name, item.conf[name]))
                        handler.push("  }\n")
                    handler.push("  logics = [\n")
                    for trigger in item.get_logic_triggers():
                        handler.push("    {}\n".format(trigger))
                    handler.push("  ]\n")
                    handler.push("  triggers = [\n")
                    for trigger in item.get_method_triggers():
                        handler.push("    {}\n".format(trigger))
                    handler.push("  ]\n")
                    handler.push("}\n")
        else:
            handler.push("Nothing found\n")

    # noinspection PyUnusedLocal
    def _cli_help(self, handler, parameter, source):
        """
        CLI command "help" - show available commands
        :param handler: CLIHandler instance
        :param parameter: Parameters used to call the command
        :param source: Source
        """
        for command, data in sorted(self._commands.items()):
            if data['usage'] is not None:
                handler.push(data['usage'] + '\n')
        handler.push('quit: quit the session\n')
        handler.push('q: alias for quit\n')

    # noinspection PyUnusedLocal
    def _cli_cl(self, handler, parameter, source):
        """
        CLI command "cl" - clear (memory) log
        :param handler: CLIHandler instance
        :param parameter: Parameters used to call the command
        :param source: Source
        """
        if parameter is None or parameter == "":
            log = self.sh.log
        else:
            logs = self.sh.return_logs()
            if parameter not in logs:
                handler.push("Log '{0}' does not exist\n".format(parameter))
                log = None
            else:
                log = logs[parameter]

        if log is not None:
            log.clean(self.sh.now())

    # noinspection PyUnusedLocal
    def _cli_la(self, handler, parameter, source):
        """
        CLI command "la" - list all items
        :param handler: CLIHandler instance
        :param parameter: Parameters used to call the command
        :param source: Source
        """
        handler.push("Items:\n======\n")
        for item in self.sh.return_items():
            if item.type():
                handler.push("{0} = {1}\n".format(item.id(), item()))
            else:
                handler.push("{0}\n".format(item.id()))

    def _cli_update(self, handler, parameter, source):
        """
        CLI command "update" - update item value
        :param handler: CLIHandler instance
        :param parameter: Parameters used to call the command
        :param source: Source
        """
        if not self.updates_allowed:
            handler.push("Updating items is not allowed.\n")
            return
        path, sep, value = parameter.partition('=')
        path = path.strip()
        value = value.strip()
        if not value:
            handler.push("You have to specify an item value. Syntax: up item = value\n")
            return
        items = self.sh.match_items(path)
        if len(items):
            for item in items:
                if not item.type():
                    handler.push("Could not find item with a valid type specified: '{0}'\n".format(path))
                    return
                item(value, 'CLI', source)
        else:
            handler.push("Could not find any item with given pattern: '{0}'\n".format(path))

    # noinspection PyUnusedLocal
    def _cli_sl(self, handler, parameter, source):
        logics = sorted(self.sh.return_logics())
        tasks = []
        for name in sorted(self.sh.scheduler):
            nt = self.sh.scheduler.return_next(name)
            if name not in logics and nt is not None:
                task = {'nt': nt, 'name': name}
                tasks.append(task)

        handler.push("{} scheduler tasks:\n".format(len(tasks)))
        for task in tasks:
            handler.push("{0} (scheduled for {1})\n".format(task['name'], task['nt'].strftime('%Y-%m-%d %H:%M:%S%z')))

    # noinspection PyUnusedLocal
    def _cli_st(self, handler, parameter, source):
        logics = sorted(self.sh.return_logics())
        tasks = []
        for name in sorted(self.sh.scheduler):
            nt = self.sh.scheduler.return_next(name)
            if name not in logics and nt is not None:
                task = {'nt': nt, 'name': name}
                p = len(tasks)
                for i in range(0, len(tasks)):
                    if nt < tasks[i]['nt']:
                        p = i
                        break
                tasks.insert(p, task)

        handler.push("{} scheduler tasks by time:\n".format(len(tasks)))
        for task in tasks:
            handler.push("{0} {1}\n".format(task['nt'].strftime('%Y-%m-%d %H:%M:%S%z'), task['name']))

    # noinspection PyUnusedLocal
    def _cli_si(self, handler, parameter, source):
        if parameter not in self.sh.scheduler._scheduler:
            handler.push("Scheduler task '{}' not found\n".format(parameter))
        else:
            task = self.sh.scheduler._scheduler[parameter]
            handler.push("Task {}".format(parameter))
            handler.push("{\n")
            for key in task:
                handler.push("  {} = {}\n".format(key, task[key]))
            handler.push("}\n")

    # noinspection PyUnusedLocal
    def _cli_ld(self, handler, parameter, source):
        if parameter is None or parameter == "":
            log = self.sh.log
        else:
            logs = self.sh.return_logs()
            if parameter not in logs:
                handler.push("Log '{0}' does not exist\n".format(parameter))
                log = None
            else:
                log = logs[parameter]

        if log is not None:
            handler.push("Log dump of '{0}':\n".format(log._name))
            for entry in log.last(10):
                values = [str(value) for value in entry]
                handler.push(str(values))
                handler.push("\n")
