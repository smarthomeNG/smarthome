#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2016-2020   Martin Sinn                         m.sinn@gmx.de
# Copyright 2016        Christian Straßburg           c.strassburg@gmx.de
# Copyright 2012-2013   Marcus Popp                        marcus@popp.mx
#########################################################################
#  This file is part of SmartHomeNG.
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


"""
This library implements items in SmartHomeNG.

The main class ``Items`` implements the handling for all items. This class has a  static method to get a handle to the
instance of the Items class, that is created during initialization of SmartHomeNG. This method implements a way to
access the API for handling items without having to juggle through the object hierarchy of the running SmartHomeNG.

This API enables plugins and logics to access the details of the items initialized in SmartHomeNG.

Each item is represented by an instance of the class ``Item``.

The methods of the class Items implement the API for items.
They can be used the following way: To call eg. **get_toplevel_items()**, use the following syntax:

.. code-block:: python

    from lib.item import Items

    sh_items = Items.get_instance()

    # to access a method (eg. get_toplevel_items()):
    tl_items = sh_items.get_toplevel_items()


:Note: Do not use the functions or variables of the main smarthome object any more. They are deprecated. Use the methods of the class **Items** instead.

:Note: This library is part of the core of SmartHomeNG. Regular plugins should not need to use this API.  It is manily implemented for plugins near to the core like **backend** and the core itself!

"""

import copy
import logging
import os
import re

import lib.config
import lib.utils
import lib.shyaml as shyaml

from lib.constants import ITEM_DEFAULTS, PLUGIN_PARSE_ITEM, PLUGIN_REMOVE_ITEM
from lib.item._internal._lifecycle import _detach_from_other_items_triggers, _remove_scheduler_jobs, _stop_fading

from .item import Item
from .structs import Structs


_items_instance = None  # Pointer to the initialized instance of the Items class (for use by static methods)


def _flatten_with_children(item):
    """
    Yield *item* followed by all of its descendants, depth-first.

    Used by ``Items.create_item()`` to find every item that was newly
    created together with the requested one (nested config dicts create
    child items automatically, via Item's own recursive construction).
    """
    yield item
    for child in item.return_children():
        yield from _flatten_with_children(child)


class Items:
    """
    Items loader class. (Item-methods from bin/smarthome.py are moved here.)

    - An instance is created during initialization by bin/smarthome.py
    - There should be only one instance of this class. So: Don't create another instance

    :param smarthome: Instance of the smarthome master-object
    :type smarthome: object
    """

    __items = []  # list with the paths of all items that are defined
    __item_dict = {}  # dict with all the items that are defined in the form: {"<item-path>": "<item-object>", ...}

    _children = []  # List of top level items

    plugin_attributes = {}  # dict with all item attributes, that are defined by plugins
    plugin_attribute_prefixes = {}  # dict with all item attribute-prefixes, that are defined by plugins
    plugin_prefixes_tuple = None  # tuple for finding if an attribute name starts with one of the prefixes

    structs = None

    _item_methods = [name for name in dir(Item) if name[0] != '_']

    def __init__(self, smarthome):
        self._sh = smarthome
        self.logger = logging.getLogger(__name__)

        global _items_instance
        if _items_instance is not None:
            import inspect

            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 4)
            self.logger.critical(
                "A second 'items' object has been created. There should only be ONE instance of class 'Items'!!! Called from: {} ({})".format(
                    calframe[1][1], calframe[1][3]
                )
            )

        _items_instance = self
        self.structs = Structs(self._sh)

        self._sh._ignore_item_collision = getattr(self._sh, '_ignore_item_collision', 'False') == 'True'

    # -----------------------------------------------------------------------------------------
    #   Following (static) method of the class Items implement the API for Items in SmartHomeNG
    # -----------------------------------------------------------------------------------------

    @staticmethod
    def get_instance():
        """
        Returns the instance of the Items class, to be used to access the items-api

        Use it the following way to access the api:

        .. code-block:: python

            from lib.item import Items

            items = Items.get_instance()

            # to access a method (eg. return_items()):
            items.return_items()


        :return: items instance
        :rtype: object
        """
        return _items_instance

    # -----------------------------------------------------------------------------------------
    #   Following methods handle structs
    # -----------------------------------------------------------------------------------------

    def add_struct_definition(self, plugin_name, struct_name, struct, from_dir='plugins', optional=False):
        self.structs.add_struct_definition(plugin_name, struct_name, struct, from_dir, optional)

    def return_struct_definitions(self, all=True):
        """
        Return all loaded structure template definitions

        :return:
        :rtype: dict
        """
        return self.structs.return_struct_definitions(all)

    def load_itemdefinitions(self, env_dir, items_dir, etc_dir, plugins_dir):
        """
        Load item definitions

        This method is called during initialization of SmartHomeNG to initialize the item tree.
        For that, it loads the item definitions from **../items** directory through calling the function **parse_itemsdir()**
        from **lib.config**

        :param env_dir: path to the directory containing the core's environment item definition files
        :param items_dir: path to the directory containing the user's item definition files
        :param etc_dir: path to the directory containing the user's configuration files (only used for 'struct' support)
        :param plugins_dir: path to the directory containing the plugins (only used for 'struct' support)
        :type env_dir: str
        :type items_dir: str
        :type etc_dir: str
        :type plugins_dir: str
        """

        # --------------------------------------------------------------------
        # Read in all struct definitions before reading item definitions
        #
        # structs are merged into the item tree in lib.config
        #
        # structs are read in from metadata file of plugins while loading plugins
        # and from ../etc/struct.yaml
        #
        # Read in item structs from ../etc/struct.yaml
        self._sh.shng_status['details'] = 'Structs'
        self.structs.load_struct_definitions()

        # --------------------------------------------------------------------
        # Read in item definitions
        #
        self._sh.shng_status['details'] = 'Items'
        item_conf = None
        item_conf = lib.config.parse_itemsdir(env_dir, item_conf)
        item_conf = lib.config.parse_itemsdir(
            items_dir, item_conf, addfilenames=True, struct_dict=self.structs._struct_definitions
        )

        for attr, value in item_conf.items():
            if isinstance(value, dict):
                try:
                    self._construct_and_link(attr, value)
                except Exception as e:
                    self.logger.error('load_itemdefinitions: Item {}: problem creating: {}'.format(attr, e))
        del item_conf  # clean up

        # Test if all used attributes are defined in configuread plugins
        # feature moved to lib.metadata
        # for item in self.return_items():
        #    item._test_attribute_existance()

        # --------------------------------------------------------------------
        # prepare loaded items for run phase of SmartHomeNG
        #
        self._sh.shng_status = {'code': 14, 'text': 'Starting: Preparing loaded items', 'details': 'prerun'}

        # Build eval expressions from special functions and triggers before first run
        for item in self.return_items():
            item._init_prerun()

        self._sh.shng_status = {'code': 14, 'text': 'Starting: Preparing loaded items', 'details': 'start scheduler'}
        # Start schedulers of the items which have a crontab or a cycle attribute
        for item in self.return_items():
            item._init_start_scheduler()
        self._sh.shng_status = {'code': 14, 'text': 'Starting: Preparing loaded items', 'details': 'eval-run'}
        # Run initial eval to set an initial value for the item
        # import time
        # gstart = time.time()
        # gduration = 0.0
        # gcount = 0
        for item in self.return_items():
            item._init_run()
            # start = time.time()
            # calculated = item._init_run()
            # end = time.time()
            # if calculated:
            #    duration = end - start
            #    self.logger.warning(f"_init_run: {item._path}, execution time = {duration}")
            #    gduration += duration
            #    gcount += 1
        # gend = time.time()
        # self.logger.warning(f"_init_run: Totals: duration {gend-gstart}, eval execution time = {gduration} for {gcount} items")

        self._sh.shng_status = {'code': 14, 'text': 'Starting: Preparing loaded items'}

    #        self.item_count = len(self.__items)
    #        self._sh.item_count = self.item_count()

    # here goes debug output (if needed) after the initialization of all items
    # import lib.metadata as metadata
    # self.logger.notice(f"metadata.all_itemprefixdefinitions: {metadata.all_itemprefixdefinitions.keys()}")

    def _construct_and_link(self, path, config, parent=None):
        """
        Construct a single item and link it into the tree, without running
        any of the post-construction init phases (_init_prerun/
        _init_start_scheduler/_init_run).

        This is the shared construction path used both by
        load_itemdefinitions() (which batches the init phases across the
        whole tree afterward, to support forward references between items)
        and by create_item() (which runs the init phases immediately, for
        just the newly created subtree).

        :param path: Full path of the item to create
        :param config: Attribute configuration dict for the item (may
                        contain nested dicts for child items, handled by
                        Item's own recursive construction)
        :param parent: Item under which to create this item; None for a
                        top-level item (parent becomes this Items instance)
        :type path: str
        :type config: dict

        :return: The newly created Item
        :rtype: Item
        """
        parent_obj = self if parent is None else parent
        leaf_attr = path.rsplit('.', 1)[-1]

        child = Item(self._sh, parent_obj, path, config, items_instance=self)

        setattr(parent_obj, leaf_attr, child)
        if parent is None:
            setattr(self._sh, leaf_attr, child)
        self.add_item(path, child)
        parent_obj._append_child(child)

        return child

    def create_item(self, path, config, parent=None, persist=True, filename=None):
        """
        Create a single item at runtime and fully initialize it (and any
        nested child items declared in *config*).

        Unlike load_itemdefinitions(), which batches the init phases across
        the whole tree (to support forward references between items being
        loaded together), this runs the init phases immediately, scoped to
        only the newly created item and its descendants. A pre-existing
        item with a wildcard ``trigger:`` pattern that would now match this
        new item is *not* retroactively rewired — that would require
        re-running _init_prerun() across the whole tree on every creation.

        :param path: Full path of the item to create
        :param config: Attribute configuration dict for the item
        :param parent: Item under which to create this item; None for a
                        top-level item
        :param persist: If True (default), also write *config* to a yaml
                         file in items_dir, so the item survives a restart.
                         If False, the item is runtime-only, same as before
                         this parameter existed.
        :param filename: Basename (without extension) of the yaml file to
                          persist to. Only used when persist is True; falls
                          back to ``sh._created_items_file`` if not given.
        :type path: str
        :type config: dict
        :type persist: bool
        :type filename: str

        :return: The newly created Item
        :rtype: Item
        """
        item_config = config
        if persist:
            filename = filename or getattr(self._sh, '_created_items_file', 'created')
            item_config = copy.deepcopy(config)
            # _add_filenames_to_config() sets '_filename' on dict *values* of
            # its argument, recursively - wrap item_config so it (and every
            # nested child config) gets the key too, not just grandchildren.
            lib.config._add_filenames_to_config({'_': item_config}, filename)
            self._write_to_yaml_file(filename, path, config)

        item = self._construct_and_link(path, item_config, parent=parent)

        new_items = list(_flatten_with_children(item))
        for new_item in new_items:
            new_item._init_prerun()
        for new_item in new_items:
            new_item._init_start_scheduler()
        for new_item in new_items:
            new_item._init_run()

        return item

    def _write_to_yaml_file(self, filename, path, config):
        """
        Write *config* (the original, caller-supplied dict — no internal
        bookkeeping keys like ``_filename``) into ``items_dir/<filename>.yaml``
        at the given dotted *path*, creating intermediate branches as
        needed. Preserves comments/formatting already in the file via
        ruamel.yaml's round-trip loader/dumper.

        :param filename: Basename (without extension) of the target file
        :param path: Full dotted path at which to insert *config*
        :param config: Attribute configuration dict to persist
        """
        target = os.path.join(self._sh._items_dir, filename)
        yf = shyaml.yamlfile(target)
        if os.path.isfile(target + shyaml.YAML_FILE):
            yf.load()
        yf.setvalue(path, config)
        yf.save()

    def _preserve_existing_children(self, filename, path, config):
        """
        Return a copy of *config* with any child-item entries (dict-valued
        keys) from the EXISTING persisted file at *path* merged in.

        edit_item() never touches an item's children (see its docstring) —
        persisting its new attribute config must not either. setvalue()
        replaces the whole dict at *path* wholesale, so without this, an
        edit would silently wipe out any child item's own YAML block.

        :param filename: Basename (without extension) of the target file
        :param path: Full dotted path *config* is about to be written to
        :param config: New attribute configuration dict (no children)
        :type filename: str
        :type path: str
        :type config: dict

        :return: config, with existing child entries merged in
        :rtype: dict
        """
        target = os.path.join(self._sh._items_dir, filename)
        if not os.path.isfile(target + shyaml.YAML_FILE):
            return config
        yf = shyaml.yamlfile(target)
        yf.load()
        existing = yf.getnode(path)
        if not isinstance(existing, dict):
            return config
        merged = dict(config)
        for key, value in existing.items():
            if isinstance(value, dict) and key not in merged:
                merged[key] = value
        return merged

    def add_item(self, path, item):
        """
        Function to to add an item to the dictionary of items.
        If the path does not exist, it is created

        :param path: Path of the item
        :param item: The item itself
        :type path: str
        :type item: object
        """

        if path not in self.__items:
            self.__items.append(path)
        self.__item_dict[path] = item

    # aus bin/smarthome.py
    #    def __iter__(self):
    #        for child in self.__children:
    #            yield child

    def edit_item(self, item, config):
        """
        Edit an existing item's attributes at runtime, in place — preserves
        Python object identity (unlike create_item()/remove_item()), so
        other items' incoming trigger/hysteresis_input registrations onto
        *item*, and this item's own value/history/children, all survive
        automatically without any rewiring step. See
        ~/.claude/handoff/shng-edit-item-attributes.md for the full design
        rationale.

        *config* is the COMPLETE new attribute set, same convention as
        create_item() — omitting a key resets it to its default, there is
        no separate partial-patch/delete-sentinel scheme.

        Other items' incoming trigger/hysteresis_input registrations onto
        *item* live on THIS item's own _items_to_trigger list, which an
        edit never resets — they survive an edit untouched, with no
        special-case code needed here.

        :param item: The item to edit
        :param config: Complete new attribute configuration dict
        :type item: object
        :type config: dict

        :return: The same item, mutated
        :rtype: Item
        """
        # Undo this item's own OUTGOING trigger/hysteresis_input wiring
        # (based on the OLD config) before re-parsing — otherwise a moved
        # trigger leaves a stale registration on the old target. Incoming
        # references (other items pointing AT this one) live on THIS
        # item's own _items_to_trigger list, untouched here — that's the
        # whole point of editing in place instead of remove+recreate.
        _detach_from_other_items_triggers(item)
        _remove_scheduler_jobs(item)
        _stop_fading(item)

        # Undo old plugin bindings before re-parsing — without this, a
        # plugin that appends to its own internal state in parse_item()
        # (e.g. the database plugin) would double-register the same item
        # object when parse_item() runs again below.
        for plugin in item.plugins.return_plugins():
            if hasattr(plugin, PLUGIN_REMOVE_ITEM):
                plugin.remove_item(item)

        item._apply_config(config)

        # Re-wire based on the NEW config (eval/trigger/hysteresis_input
        # expansion, registers this item onto its new trigger targets).
        item._init_prerun()
        item._init_start_scheduler()
        item._init_run()

        # Rebind to plugins per the NEW config — mirrors the same loop
        # Item.__init__ runs inline for a freshly constructed item.
        for plugin in item.plugins.return_plugins():
            if hasattr(plugin, PLUGIN_PARSE_ITEM):
                update = plugin.parse_item(item)
                if update:
                    try:
                        plugin.add_item(item, updating=True)
                    except Exception:
                        pass
                    item.add_method_trigger(update)

        # Preserved value may not be valid for a new type (e.g. num -> str
        # always works, str -> num doesn't if the string isn't numeric).
        # Same try-cast-with-fallback pattern as the existing cache-restore
        # path (Item.__init__'s "Cache" section) — not new logic.
        try:
            item._value = item.cast(item._value)
        except Exception:
            self.logger.warning(
                f'Item {item.property.path}: value {item._value!r} does not match new type '
                f'{item._type} after edit — resetting to default.'
            )
            item._value = ITEM_DEFAULTS[item._type]

        if item._filename:
            merged_config = self._preserve_existing_children(item._filename, item.property.path, config)
            self._write_to_yaml_file(item._filename, item.property.path, merged_config)

        return item

    def remove_item(self, item, persist=True):
        """
        Function to remove an item from the dictionary of items
        and delete the item object.

        :param item: The item to delete
        :param persist: If True (default), also remove the item's entry
                         from the yaml file it was defined in (``item.
                         property.defined_in``/``item._filename``), if any.
                         Works for any item with a known source file, not
                         only ones created via create_item(persist=True) —
                         deliberately generic. No-op if the item has no
                         known source file.
        :type item: object
        :type persist: bool
        """

        if item.property.path not in self.__items:
            return

        path = item.property.path
        source_filename = item._filename

        # remove item from Items data
        try:
            del self.__item_dict[path]
            self.__items.remove(path)
        except Exception as e:
            self.logger.warning(f'Error occured while trying to remove item {path}: {e}')

        # remove item bindings in plugins
        if item.remove():
            # delete item
            del item
        else:
            self.logger.warning(f'Item {path} could not be removed due to incompatible plugins.')

        if persist and source_filename:
            self._remove_from_yaml_file(source_filename, path)

    def _remove_from_yaml_file(self, filename, path):
        """
        Remove the entry at dotted *path* from ``items_dir/<filename>.yaml``,
        if that file exists. Cleans up now-empty parent branches. Preserves
        comments/formatting of everything else in the file (round-trip
        load/save).

        :param filename: Basename (without extension) of the file to edit
        :param path: Full dotted path of the entry to remove
        """
        target = os.path.join(self._sh._items_dir, filename)
        if not os.path.isfile(target + shyaml.YAML_FILE):
            return
        yf = shyaml.yamlfile(target)
        yf.load()
        yf.setvalue(path, None)
        yf.save()

    def find_references(self, path):
        """
        Best-effort search for textual references to item *path* inside
        other items' ``eval``, ``on_change``, ``on_update``, ``trigger``
        and ``hysteresis_input`` attributes.

        This is a review aid, not a safety mechanism: a reference embedded
        in free-form ``eval`` text cannot be tracked structurally (unlike
        ``trigger``/``hysteresis_input``, which already are, via
        ``_items_to_trigger``/``_hysteresis_items_to_trigger`` — those are
        included here too, for a complete picture in one place). There is
        no guarantee of completeness (e.g. a computed/concatenated
        reference won't be found) and no guarantee against false positives
        beyond a word-boundary match. Intended to be called interactively
        before deleting an item, so a human can review the result — it is
        deliberately not wired into remove_item() itself.

        :param path: Path of the item to search for
        :type path: str

        :return: List of (item, attribute_name, attribute_value, unambiguous)
                 tuples, one per match. ``unambiguous`` is True if *path* is
                 the only item the matched text depends on (see
                 _is_unambiguous_reference()) — a hint for which matches
                 might be safe to auto-clean later, not a guarantee.
        :rtype: list
        """
        target = self.return_item(path)
        pattern = re.compile(r'\b' + re.escape(path) + r'\b')

        results = []
        for other in self.return_items():
            if other is target:
                continue
            for attr_name, text in self._reference_candidates(other):
                if text and pattern.search(text):
                    unambiguous = self._is_unambiguous_reference(attr_name, text, path)
                    results.append((other, attr_name, text, unambiguous))
        return results

    # Item paths only ever contain ASCII letters, digits and underscores
    # (lib/config.py's valid_item_chars) — deliberately not \w, which is
    # Unicode-aware and would also match e.g. German umlauts.
    _SH_REF_RE = re.compile(r'sh\.([A-Za-z0-9_.]+)')

    def _resolve_references(self, text):
        """
        Return the set of distinct item paths referenced via ``sh.<path>``
        in *text*. Resolves against the live item tree (longest valid
        prefix wins), not a hardcoded property-name list — so
        ``sh.a.b.last_change`` correctly resolves to item ``a.b``
        (``last_change`` being the property), not ``a.b.last_change``,
        unless the latter also happens to be a real item path (longest
        match wins regardless — same best-effort character as the rest of
        find_references()).

        :param text: eval/on_change/on_update text to scan
        :type text: str

        :return: set of item paths found
        :rtype: set
        """
        found = set()
        for m in self._SH_REF_RE.finditer(text):
            parts = m.group(1).split('.')
            for end in range(len(parts), 0, -1):
                candidate = '.'.join(parts[:end])
                if self.return_item(candidate) is not None:
                    found.add(candidate)
                    break
        return found

    def _is_unambiguous_reference(self, attr_name, text, target_path):
        """
        True if *target_path* is the only item *text* depends on.

        ``trigger``/``hysteresis_input`` entries are always a single bare
        absolute item path (see _reference_candidates()) — never
        ``sh.``-prefixed eval text, that syntax is only valid inside eval
        expressions — so they are unambiguous by construction whenever
        they matched at all (the word-boundary match in find_references()
        already guarantees there's nothing else in the string).
        ``eval``/``on_change``/``on_update`` are free-form Python and need
        the ``sh.<path>`` resolution in _resolve_references().

        :param attr_name: Attribute the text came from
        :param text: The matched attribute text
        :param target_path: Path being checked for exclusivity
        :type attr_name: str
        :type text: str
        :type target_path: str

        :return: True if target_path is the only dependency
        :rtype: bool
        """
        if attr_name in ('trigger', 'hysteresis_input'):
            return True
        return self._resolve_references(text) == {target_path}

    @staticmethod
    def _reference_candidates(item):
        """
        Yield (attribute_name, text) pairs for *item*'s reference-bearing
        attributes, for use by find_references(). Single-value attributes
        are skipped when unset; list attributes contribute one pair per
        entry.
        """
        if item._eval:
            yield ('eval', item._eval)
        for text in item._on_change or []:
            yield ('on_change', text)
        for text in item._on_update or []:
            yield ('on_update', text)
        for text in item._trigger or []:
            yield ('trigger', text)
        if item._hysteresis_input:
            yield ('hysteresis_input', item._hysteresis_input)

    def get_toplevel_items(self):
        """
        Returns a list with all items defined at the top level

        :return: items defined at the top level
        :rtype: list
        """
        for child in self._children:
            yield child

    def _remove_child(self, item) -> None:
        """Remove item from _children — used by _lifecycle.py when a top-level item is deleted."""
        try:
            self._children.remove(item)
        except ValueError:
            pass

    def _append_child(self, item) -> None:
        """Append item to _children — used by _construct_and_link() when a top-level item is created."""
        self._children.append(item)

    # aus lib.logic.py
    #    def __iter__(self):
    #        for logic in self._logics:
    #            yield logic

    def return_item(self, string):
        """
        Function to return the item for a given path

        :param string: Path of the item to return
        :type string: str

        :return: Item
        :rtype: object
        """

        if string in self.__items:
            return self.__item_dict[string]

    def return_items(self, ordered=False):
        """
        Function to return a list with all defined items

        :param ordered: return list sorted alphabetically, defaults to False
        :type ordered: bool

        :return: List of all items
        :rtype: list
        """

        if ordered:
            for item in sorted(self.__items):
                yield self.__item_dict[item]
        else:
            for item in self.__items:
                yield self.__item_dict[item]

    def match_items(self, regex):
        """
        Function to match items against a regular expression

        :param regex: Regular expression to match items against
        :type regex: str

        :return: List of matching items
        :rtype: list
        """

        regex, __, attr = regex.partition(':')
        # regex = regex.replace('.', '\.').replace('*', '.*') + '$'
        regex = regex.replace('.', r'\.').replace('*', '.*') + '$'
        regex = re.compile(regex)
        attr, __, val = attr.partition('[')
        val = val.rstrip(']')
        if attr != '' and val != '':
            return [
                self.__item_dict[item]
                for item in self.__items
                if regex.match(item)
                and attr in self.__item_dict[item].conf
                and (
                    (
                        type(self.__item_dict[item].conf[attr]) in [list, dict]
                        and val in self.__item_dict[item].conf[attr]
                    )
                    or (val == self.__item_dict[item].conf[attr])
                )
            ]
        elif attr != '':
            return [
                self.__item_dict[item]
                for item in self.__items
                if regex.match(item) and attr in self.__item_dict[item].conf
            ]
        else:
            return [self.__item_dict[item] for item in self.__items if regex.match(item)]

    def _attribute_find(self, attr, attr_list):
        """
        Find an attribute in an attribute list

        :param attr:
        :param attr_list:
        :return:

        examples:
            attr_list = ['avm_identifier' , 'avm_data_type@willy_tel', 'avm_wlan_index', 'visu_acl']

            attr                          result
            ---_                          ------
            'willy_tel'                -> False
            '@willy_tel'               -> True
            '@fritz_wz'                -> False

            'avm_data_type@willy_tel'  -> True
            'avm_data_type@fritz_wz'   -> False
            'avm_data_type'            -> False
            'avm_data_type@'           -> True

            'avm_wlan_index'           -> True
            'avm_wlan_index@'          -> True

            'visu_acl'                 -> True
            '@visu_acl'                -> False

        """
        result = False
        if attr.endswith('@'):
            result = any(s for s in attr_list if s.startswith(attr))
            if not result:
                result = attr[:-1] in attr_list
        elif attr.startswith('@'):
            result = any(s for s in attr_list if s.endswith(attr))
        else:
            result = attr in attr_list
        return result

    def find_items(self, conf):
        """
        Function to find items that match the specified configuration

        :param conf: Configuration to look for
        :type conf: str

        :return: list of matching items
        :rtype: list
        """

        for item in self.__items:
            # if conf in self.__item_dict[item].conf:
            #     yield self.__item_dict[item]
            if self._attribute_find(conf, self.return_item(item).property.attributes):
                yield self.__item_dict[item]

    def find_children(self, parent, conf):
        """
        Function to find children with the specified configuration

        :param parent: parent item on which to start the search
        :param conf: Configuration to look for
        :type parent: str
        :type conf: str

        :return: list or matching child-items
        :rtype: list
        """

        children = []
        for item in parent:
            # if conf in item.conf:
            #     children.append(item)
            if self._attribute_find(conf, item.property.attributes):
                children.append(item)
            children += self.find_children(item, conf)
        return children

    def item_count(self):
        """
        Return the number of defined items

        :return: number of items
        :rtype: int
        """
        return len(self.__items)

    def stop(self, signum=None, frame=None):
        """
        Stop what all items are doing

        At the moment, it stops fading of all items
        """
        for item in self.__items:
            self.__item_dict[item]._fading = False
            with self.__item_dict[item]._lock:
                self.__item_dict[item]._lock.notify_all()

    def add_plugin_attribute(self, plugin_name, attribute_name, attribute):
        """
        Add an attribute definition to the dict of plugin specific item-attributes

        :param plugin_name:    Name of the plugin that defines the attribute
        :param attribute_name: Name of the attribute
        :param attribute:      Metadata that defines the attribute
        :return:
        """
        attribute_name = attribute_name.lower()
        if self.plugin_attributes.get(attribute_name, None) is None:
            self.plugin_attributes[attribute_name] = {}
            self.plugin_attributes[attribute_name]['plugin'] = plugin_name
            self.plugin_attributes[attribute_name]['meta'] = dict(attribute)
            self.logger.info('add_plugin_attribute: {} ({}) -> {}'.format(attribute_name, plugin_name, dict(attribute)))
        else:
            if plugin_name != self.plugin_attributes[attribute_name]['plugin']:
                if self.plugin_attributes[attribute_name]['meta']['type'] != attribute['type']:
                    self.logger.error(
                        f"Plugins '{self.plugin_attributes[attribute_name]['plugin']}' and '{plugin_name}' define the same item-attribute '{attribute_name}' with different type definitions {self.plugin_attributes[attribute_name]['meta']['type']}/{attribute['type']}"
                    )
                elif not self.plugin_attributes[attribute_name]['meta'].get('duplicate_use', False):
                    self.logger.warning(
                        f"Plugins '{self.plugin_attributes[attribute_name]['plugin']}' and '{plugin_name}' define the same item-attribute '{attribute_name}'"
                    )
                else:
                    self.logger.info(
                        f"Plugins '{self.plugin_attributes[attribute_name]['plugin']}' and '{plugin_name}' define the same item-attribute '{attribute_name}'"
                    )

    def add_plugin_attribute_prefix(self, plugin_name, prefix_name, prefix):
        """
        Add an attribute-prefix definition to the dict of plugin specific item-attribute prefixes

        :param plugin_name: Name of the plugin that defines the attribute
        :param prefix_name: Name of the attribute-prefix
        :param prefix:      Metadata that defines the attribute-prefix
        :return:
        """
        prefix_name = prefix_name.lower()
        if self.plugin_attribute_prefixes.get(prefix_name, None) is None:
            self.plugin_attribute_prefixes[prefix_name] = {}
            self.plugin_attribute_prefixes[prefix_name]['plugin'] = plugin_name
            self.plugin_attribute_prefixes[prefix_name]['meta'] = dict(prefix)
            self.logger.info(
                'add_plugin_attribute_prefix: {} ({}) -> {}'.format(prefix_name, plugin_name, dict(prefix))
            )
        else:
            if plugin_name != self.plugin_attribute_prefixes[prefix_name]['plugin']:
                self.logger.error(
                    "Plugins '{}' and '{}' define the same item-attribute-prefix '{}'".format(
                        self.plugin_attribute_prefixes[prefix_name]['plugin'], plugin_name, prefix_name
                    )
                )

    def plugin_attribute_exists(self, attribute_name):
        """
        Returns the type of the attribute's value

        :param attribute_name: Name of the attribute
        :return:               Type of the attribute's value or None
        """
        meta = self.plugin_attributes.get(attribute_name.lower(), None)
        if meta is not None:
            return True

        if self.plugin_prefixes_tuple is None:
            # Generate tuple on first call to this method
            self.plugin_prefixes_tuple = tuple(self.plugin_attribute_prefixes.keys())
        if attribute_name.startswith(self.plugin_prefixes_tuple):
            return True

        return False

    def get_plugin_attribute_type(self, attribute_name):
        """
        Returns the type of the attribute's value

        :param attribute_name: Name of the attribute
        :return:               Type of the attribute's value or None
        """
        meta = self.plugin_attributes.get(attribute_name.lower, None)
        if meta is None:
            return None
        else:
            return meta['type']
