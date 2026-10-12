#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Loads real plugins in tests via the real plugin loader on MockSmartHome.

Scheduler and (for SDP plugins) device connection are replaced by recording
stand-ins: RecordingScheduler and RecordingConnection.
"""

from __future__ import annotations

import builtins
import logging
import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

builtins.SDP_standalone = False

import tests.common as common  # noqa: E402

common.register_shng_log_levels()

import lib.item.item  # noqa: E402
import lib.item.items  # noqa: E402
from lib.item.item import Item  # noqa: E402
from lib.item.items import Items  # noqa: E402
from lib.model.sdp.connection import SDPConnection  # noqa: E402
from lib.model.sdp.carriers import ConnectionHooks, DeviceConfig  # noqa: E402
from lib.model.sdp.protocol import SDPProtocol  # noqa: E402
from lib.model.smartdeviceplugin import SmartDevicePlugin  # noqa: E402
from lib.model.smartplugin import SmartPlugin  # noqa: E402
from tests.mock.core import MockScheduler, MockSmartHome  # noqa: E402


@dataclass
class ScheduledJob:
    """One scheduler entry as passed to ``scheduler.add()``."""

    name: str
    obj: Callable[..., Any]
    prio: int | None = None
    cycle: Any = None
    offset: Any = None
    next: Any = None

    def fire(self) -> None:
        """Run the job once, as the scheduler would when it is due."""
        self.obj()


class RecordingScheduler(MockScheduler):
    """Scheduler stand-in that keeps added jobs by full scheduler name instead of running them."""

    def __init__(self) -> None:
        super().__init__()
        self.jobs: dict[str, ScheduledJob] = {}

    def add(
        self,
        name,
        obj,
        prio=3,
        cron=None,
        cycle=None,
        value=None,
        offset=None,
        next=None,
        from_smartplugin=False,
        items=None,
    ):
        self.jobs[name] = ScheduledJob(name=name, obj=obj, prio=prio, cycle=cycle, offset=offset, next=next)

    def remove(self, name, from_smartplugin=False):
        self.jobs.pop(name, None)

    def get(self, name, from_smartplugin=False):
        job = self.jobs.get(name)
        return {'name': job.name, 'cycle': job.cycle} if job else {}

    def change(self, name, **kwargs):
        job = self.jobs.get(name)
        if job:
            for key, val in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, val)


class RecordingConnection(SDPConnection):
    """
    Records sent data_dicts; replies from ``responder``, else ``replies`` by payload.

    Opening and closing fire the connect/disconnect callbacks.
    """

    def _setup(self) -> None:
        self.sent: list[dict] = []
        self.replies: dict[Any, Any] = {}
        self.responder: Callable[[dict], Any] | None = None

    def _open(self) -> bool:
        self._is_connected = True
        if self._hooks.on_connect:
            self._hooks.on_connect(self.__class__.__name__)
        return True

    def _close(self) -> None:
        if self._hooks.on_disconnect:
            self._hooks.on_disconnect(self.__class__.__name__)

    def _send(self, data_dict: dict, **kwargs) -> Any:
        self.sent.append(data_dict)
        if self.responder:
            return self.responder(data_dict)
        return self.replies.get(data_dict.get('payload'))

    @property
    def payloads(self) -> list:
        """Payloads of all sent data_dicts, in send order."""
        return [d.get('payload') for d in self.sent]


class LogCapture(logging.Handler):
    """Collects all log records."""

    def __init__(self) -> None:
        super().__init__(level=logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)

    def messages(self, level: int = logging.WARNING) -> list[str]:
        """Messages of all records of at least ``level``."""
        return [r.getMessage() for r in self.records if r.levelno >= level]


@dataclass
class PluginRig:
    """A loaded plugin with its recording scheduler and captured log records."""

    sh: MockSmartHome
    plugin: SmartPlugin
    scheduler: RecordingScheduler
    tmp_dir: str
    logs: LogCapture

    def item(self, path: str) -> Item:
        """Return the item at ``path``."""
        return self.sh.return_item(path)

    def rename(self, item: Item, new_path: str) -> None:
        """Rename ``item`` in place, as Items.rename_item() does towards plugins."""
        old_path = item.property.path
        item._path = new_path
        self.plugin.rename_item(item, old_path, new_path)

    def job(self, name: str) -> ScheduledJob | None:
        """Return the scheduler job the plugin added as ``scheduler_add(name, ...)``, or None."""
        prefix = self.plugin._pluginname_prefix + self.plugin.get_fullname()
        return self.scheduler.jobs.get(f'{prefix}.{name}' if name else prefix)

    def plugin_jobs(self) -> dict[str, ScheduledJob]:
        """All scheduler jobs added by the plugin, keyed by their plugin-relative name."""
        prefix = self.plugin._pluginname_prefix + self.plugin.get_fullname() + '.'
        return {k[len(prefix) :]: v for k, v in self.scheduler.jobs.items() if k.startswith(prefix)}


@dataclass
class SDPRig(PluginRig):
    """A loaded SDP plugin with its recording scheduler and its (usually recording) connection."""

    plugin: SmartDevicePlugin
    connection: SDPConnection


class PluginNotLoaded(RuntimeError):
    """The plugin loader did not load the plugin; ``logs`` holds the log records of the attempt."""

    def __init__(self, message: str, logs: LogCapture) -> None:
        super().__init__(message)
        self.logs = logs


def _reset_items() -> None:
    """Empty the class-level item tree and attribute registrations of Items."""
    lib.item.items._items_instance = None
    lib.item.item._items_instance = None
    Items._Items__items = []
    Items._Items__item_dict = {}
    Items._children = []
    Items.plugin_attributes = {}
    Items.plugin_attribute_prefixes = {}
    Items.plugin_prefixes_tuple = None


def _yaml_section(name: str, conf: dict[str, Any]) -> str:
    lines = [f'{name}:']
    lines += [f'    {key}: {val!r}' if isinstance(val, str) else f'    {key}: {val}' for key, val in conf.items()]
    return '\n'.join(lines) + '\n'


def load_plugin(
    tmp_dir: str,
    class_path: str,
    class_name: str,
    items_yaml: str,
    params: dict[str, Any] | None = None,
    section: str = 'plg',
    before_items: Callable[[SmartPlugin], None] | None = None,
    other_sections: dict[str, dict[str, Any]] | None = None,
) -> PluginRig:
    """
    Load a plugin through the real plugin loader and create its items.

    :param tmp_dir: writable directory for generated config files
    :param class_path: module path of the plugin
    :param class_name: plugin class name
    :param items_yaml: item definitions as yaml text
    :param params: plugin parameters
    :param section: plugin config section name
    :param before_items: called with the plugin before items are created
    :param other_sections: further sections of the plugin class with their parameters
    :return: the rig for ``section``; the plugin is not running
    :raises PluginNotLoaded: if the plugin loader did not load the plugin
    """
    sections = {section: params or {}, **(other_sections or {})}
    plugin_conf = os.path.join(tmp_dir, 'plugin')
    with open(plugin_conf + '.yaml', 'w') as f:
        for name, sec_params in sections.items():
            f.write(_yaml_section(name, {'class_path': class_path, 'class_name': class_name, **sec_params}))

    _reset_items()
    sh = MockSmartHome()
    logs = LogCapture()
    root = logging.getLogger()
    for handler in [h for h in root.handlers if isinstance(h, LogCapture)]:
        root.removeHandler(handler)
    root.addHandler(logs)
    root.setLevel(logging.DEBUG)
    sh._cache_dir = os.path.join(tmp_dir, 'cache') + os.path.sep
    os.makedirs(sh._cache_dir, exist_ok=True)
    scheduler = RecordingScheduler()
    sh.scheduler = scheduler
    plugin = sh.with_plugins_from(plugin_conf).return_plugin(section)
    if plugin is None:
        raise PluginNotLoaded(f'plugin {class_path}.{class_name} could not be loaded', logs)

    if before_items:
        before_items(plugin)

    items_file = os.path.join(tmp_dir, 'items.yaml')
    with open(items_file, 'w') as f:
        f.write(items_yaml)
    sh.with_items_from(items_file)

    return PluginRig(sh=sh, plugin=plugin, scheduler=scheduler, tmp_dir=tmp_dir, logs=logs)


def transport(conn: SDPConnection) -> SDPConnection:
    """The transport doing the I/O: ``conn`` itself, or the transport a protocol wraps."""
    return conn._connection if isinstance(conn, SDPProtocol) else conn


def _install_recording_connection(plugin: SmartDevicePlugin) -> None:
    config = DeviceConfig.from_params(plugin._connection_params())
    plugin._connection = RecordingConnection(config, plugin._connection_hooks(), plugin, plugin.get_fullname())


def _install_recording_transport(plugin: SmartDevicePlugin) -> None:
    protocol = plugin._connection
    if not isinstance(protocol, SDPProtocol):
        raise TypeError(f'plugin connection {protocol} is no protocol, no inner transport to replace')
    hooks = ConnectionHooks(
        on_data=protocol.on_data_received,
        on_connect=protocol.on_connect,
        on_disconnect=protocol.on_disconnect,
        on_abort=protocol._hooks.on_abort,
    )
    protocol._connection = RecordingConnection(protocol._config, hooks, plugin, plugin.get_fullname())


def load_sdp_plugin(
    tmp_dir: str,
    class_path: str,
    class_name: str,
    items_yaml: str,
    params: dict[str, Any] | None = None,
    section: str = 'sdp',
    record: bool = True,
    record_transport: bool = False,
) -> SDPRig:
    """
    Load an SDP plugin like load_plugin().

    :param record: replace the plugin's connection by a RecordingConnection
    :param record_transport: replace only the transport wrapped by the plugin's protocol
    """
    if record_transport:
        install = _install_recording_transport
    elif record:
        install = _install_recording_connection
    else:
        install = None
    rig = load_plugin(tmp_dir, class_path, class_name, items_yaml, params=params, section=section, before_items=install)
    connection = rig.plugin._connection
    if record_transport:
        connection = connection._connection
    return SDPRig(
        sh=rig.sh, plugin=rig.plugin, scheduler=rig.scheduler, tmp_dir=tmp_dir, logs=rig.logs, connection=connection
    )
