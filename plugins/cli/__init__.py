#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2012-2013 Marcus Popp                         marcus@popp.mx
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



class CLIHandler(lib.connection.Stream):
    terminator = '\n'.encode()

    def __init__(self, smarthome, sock, source, updates):
        lib.connection.Stream.__init__(self, sock, source)
        self.source = source
        self.updates_allowed = updates
        self.sh = smarthome
        self.push("SmartHome.py v{0}\n".format(self.sh.version))
        self.push("Enter 'help' for a list of available commands.\n")
        self.push("> ")

    def push(self, data):
        self.send(data.encode())

    def found_terminator(self, data):
        cmd = data.decode().strip()
        if cmd.startswith('ls'):
            self.push("Items:\n======\n")
            self.ls(cmd.lstrip('ls').strip(), '*' in cmd or ':' in cmd)
        elif cmd == 'la':
            self.la()
        elif cmd == 'lo':
            self.lo()
        elif cmd == 'll':
            self.lo()
        elif cmd == 'lt':
            self.lt()
        elif cmd == 'cl':
            self.cl()
        elif cmd.startswith('update ') or cmd.startswith('up '):
            self.update(cmd.lstrip('update').strip())
        elif cmd.startswith('dump'):
            self.dump(cmd.lstrip('dump').strip(), '*' in cmd or ':' in cmd)
        elif cmd.startswith('tr'):
            self.tr(cmd.lstrip('tr').strip())
        elif cmd.startswith('rl'):
            self.rl(cmd.lstrip('rl').strip())
        elif cmd.startswith('rr'):
            self.rr(cmd.lstrip('rr').strip())
        elif cmd == 'rt' or cmd == 'runtime':
            self.rt()
        elif cmd == 'help' or cmd == 'h':
            self.usage()
        elif cmd in ('quit', 'q', 'exit', 'x'):
            self.push('bye\n')
            self.close()
            return
        self.push("> ")

    def cl(self):
        self.sh.log.clean(self.sh.now())

    def ls(self, path, match=True):
        if not path:
            for item in self.sh:
                self.push("{0}\n".format(item.id()))
        else:
            if match:
               items = self.sh.match_items(path)
               childs = False
            else:
               items = [self.sh.return_item(path)]
               childs = True
            if len(items):
                for item in items:
                    if hasattr(item, 'id'):
                        if item.type():
                            self.push("{0} = {1}\n".format(item.id(), item()))
                        else:
                            self.push("{}\n".format(item.id()))
                        if childs:
                            for child in item:
                                self.ls(child.id(), False)
            else:
                self.push("Could not find path: {}\n".format(path))

    def la(self):
        self.push("Items:\n======\n")
        for item in self.sh.return_items():
            if item.type():
                self.push("{0} = {1}\n".format(item.id(), item()))
            else:
                self.push("{0}\n".format(item.id()))

    def update(self, data):
        if not self.updates_allowed:
            self.push("Updating items is not allowed.\n")
            return
        path, sep, value = data.partition('=')
        path = path.strip()
        value = value.strip()
        if not value:
            self.push("You have to specify an item value. Syntax: up item = value\n")
            return
        items = self.sh.match_items(path)
        if len(items):
            for item in items:
                if not item.type():
                    self.push("Could not find item with a valid type specified: '{0}'\n".format(path))
                    return
                item(value, 'CLI', self.source)
        else:
            self.push("Could not find any item with given pattern: '{0}'\n".format(path))

    def dump(self, path, match=True):
        if match:
            items = self.sh.match_items(path)
        else:
            items = [self.sh.return_item(path)]
        if len(items):
            for item in items:
                if hasattr(item, 'id') and item._type:
                    self.push("Item {} ".format(item.id()))
                    self.push("{\n")
                    self.push("  type = {}\n".format(item.type()))
                    self.push("  value = {}\n".format(item()))
                    self.push("  age = {}\n".format(item.age()))
                    self.push("  last_change = {}\n".format(item.last_change()))
                    self.push("  changed_by = {}\n".format(item.changed_by()))
                    self.push("  previous_value = {}\n".format(item.prev_value()))
                    self.push("  previous_age = {}\n".format(item.prev_age()))
                    self.push("  previous_change = {}\n".format(item.prev_change()))
                    if hasattr(item, 'conf'):
                        self.push("  config = {\n")
                        for name in item.conf:
                            self.push("    {} = {}\n".format(name, item.conf[name]))
                        self.push("  }\n")
                    self.push("  logics = [\n")
                    for trigger in item.get_logic_triggers():
                        self.push("    {}\n".format(trigger))
                    self.push("  ]\n")
                    self.push("  triggers = [\n")
                    for trigger in item.get_method_triggers():
                        self.push("    {}\n".format(trigger))
                    self.push("  ]\n")
                    self.push("}\n")
        else:
            self.push("Nothing found\n")

    def tr(self, logic):
        if not self.updates_allowed:
            self.push("Logic triggering is not allowed.\n")
            return
        if logic in self.sh.return_logics():
            self.sh.trigger(logic, by='CLI')
        else:
            self.push("Logic '{0}' not found.\n".format(logic))

    def rl(self, name):
        if not self.updates_allowed:
            self.push("Logic triggering is not allowed.\n")
            return
        if name in self.sh.return_logics():
            logic = self.sh.return_logic(name)
            logic.generate_bytecode()
        else:
            self.push("Logic '{0}' not found.\n".format(name))

    def rr(self, name):
        if not self.updates_allowed:
            self.push("Logic triggering is not allowed.\n")
            return
        if name in self.sh.return_logics():
            logic = self.sh.return_logic(name)
            logic.generate_bytecode()
            logic.trigger(by='CLI')
        else:
            self.push("Logic '{0}' not found.\n".format(name))

    def lo(self):
        self.push("Logics:\n")
        for logic in sorted(self.sh.return_logics()):
            nt = self.sh.scheduler.return_next(logic)
            if nt is not None:
                self.push("{0} (scheduled for {1})\n".format(logic, nt.strftime('%Y-%m-%d %H:%M:%S%z')))
            else:
                self.push("{0}\n".format(logic))

    def lt(self):
        # list all threads with names
        self.push("{0} Threads:\n".format(threading.activeCount()))
        for t in threading.enumerate():
            self.push("{0}\n".format(t.name))

    def rt(self):
        # return SH.py runtime
        self.push("Runtime: {}\n".format(self.sh.runtime()))

    def usage(self):
        self.push('cl: clean (memory) log\n')
        self.push('ls: list the first level items\n')
        self.push('ls item: list item and every child item (with values)\n')
        self.push('la: list all items (with values)\n')
        self.push('lo: list all logics and next execution time\n')
        self.push('lt: list current thread names\n')
        self.push('update item = value: update the specified item with the specified value\n')
        self.push('up: alias for update\n')
        self.push('dump item: dump details about given item\n')
        self.push('tr logic: trigger logic\n')
        self.push('rl logic: reload logic\n')
        self.push('rr logic: reload and run logic\n')
        self.push('rt: return runtime\n')
        self.push('quit: quit the session\n')
        self.push('q: alias for quit\n')


class CLI(lib.connection.Server):

    def __init__(self, smarthome, update='False', ip='127.0.0.1', port=2323):
        self.logger = logging.getLogger(__name__)
        lib.connection.Server.__init__(self, ip, port)
        self.sh = smarthome
        self.updates_allowed = smarthome.string2bool(update)

    def handle_connection(self):
        sock, address = self.accept()
        if sock is None:
            return
        self.logger.debug("{}: incoming connection from {} to {}".format(self._name, address, self.address))
        CLIHandler(self.sh, sock, address, self.updates_allowed)

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False
        self.close()
