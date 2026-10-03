#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
"""
Harness for running real plugins, especially the SmartDevicePlugin stack, in tests.

A plugin is loaded through the real ``lib.plugin.Plugins`` loader (metadata,
parameters, item attributes, for SDP plugins ``commands.py``) on a
``MockSmartHome``; items are created from yaml text, which runs the plugin's
real ``parse_item()``. Only the outer boundaries are replaced:

- the shng scheduler, by :class:`RecordingScheduler`, which records jobs
  instead of running them, so tests can inspect and fire them explicitly
- for SDP plugins, the device connection, by :class:`RecordingConnection`, which records
  outgoing ``data_dict``s and answers with scripted replies, and fires the
  connect/disconnect callbacks on open/close like a real transport does

Used by SDP framework tests in ``tests/`` and by characterization tests of
SDP-based plugins in ``plugins/<plugin>/tests/``.
"""

from __future__ import annotations

import builtins
import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

builtins.SDP_standalone = False

import tests.common as common  # noqa: E402

common.register_shng_log_levels()

from lib.item.item import Item  # noqa: E402
from lib.model.sdp.connection import SDPConnection  # noqa: E402
from lib.model.sdp.globals import PLUGIN_ATTR_CB_ON_CONNECT, PLUGIN_ATTR_CB_ON_DISCONNECT  # noqa: E402
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
    Transport stand-in: records every sent ``data_dict`` and returns the reply
    scripted for its payload (``None`` if none is scripted).

    Opening and closing fire the plugin's connect/disconnect callbacks, as
    the real network and serial transports do.
    """

    def __init__(self, data_received_callback: Callable | None, name: str | None = None, **kwargs) -> None:
        super().__init__(data_received_callback, name, **kwargs)
        self.sent: list[dict] = []
        self.replies: dict[Any, Any] = {}

    def _open(self) -> bool:
        self._is_connected = True
        if self._params[PLUGIN_ATTR_CB_ON_CONNECT]:
            self._params[PLUGIN_ATTR_CB_ON_CONNECT](self.__class__.__name__)
        return True

    def _close(self) -> None:
        if self._params[PLUGIN_ATTR_CB_ON_DISCONNECT]:
            self._params[PLUGIN_ATTR_CB_ON_DISCONNECT](self.__class__.__name__)

    def _send(self, data_dict: dict, **kwargs) -> Any:
        self.sent.append(data_dict)
        return self.replies.get(data_dict.get('payload'))

    @property
    def payloads(self) -> list:
        """Payloads of all sent data_dicts, in send order."""
        return [d.get('payload') for d in self.sent]


@dataclass
class PluginRig:
    """A loaded plugin with its recording scheduler."""

    sh: MockSmartHome
    plugin: SmartPlugin
    scheduler: RecordingScheduler
    tmp_dir: str

    def item(self, path: str) -> Item:
        """Return the item at ``path``."""
        return self.sh.return_item(path)

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

    :param tmp_dir: writable directory for the generated plugin config/item files
    :param class_path: module path of the plugin, e.g. ``tests.fixture_sdp_plugin``
    :param class_name: plugin class name
    :param items_yaml: item definitions as yaml text
    :param params: plugin parameters as in ``etc/plugin.yaml``
    :param section: plugin config section name
    :param before_items: called with the plugin after loading, before any item is created
    :param other_sections: further sections of the same plugin class by section name, with their
        parameters; with any given, every section's instance name is its section name
    :return: the loaded rig for ``section``; the plugin is not yet running
    :raises RuntimeError: if the plugin loader did not load the plugin
    """
    sections = {section: params or {}, **(other_sections or {})}
    plugin_conf = os.path.join(tmp_dir, 'plugin')
    with open(plugin_conf + '.yaml', 'w') as f:
        for name, sec_params in sections.items():
            f.write(_yaml_section(name, {'class_path': class_path, 'class_name': class_name, **sec_params}))

    sh = MockSmartHome()
    scheduler = RecordingScheduler()
    sh.scheduler = scheduler
    plugin = sh.with_plugins_from(plugin_conf).return_plugin(section)
    if plugin is None:
        raise RuntimeError(f'plugin {class_path}.{class_name} could not be loaded')

    if before_items:
        before_items(plugin)

    items_file = os.path.join(tmp_dir, 'items.yaml')
    with open(items_file, 'w') as f:
        f.write(items_yaml)
    sh.with_items_from(items_file)

    return PluginRig(sh=sh, plugin=plugin, scheduler=scheduler, tmp_dir=tmp_dir)


def _install_recording_connection(plugin: SmartDevicePlugin) -> None:
    plugin._connection = RecordingConnection(plugin.on_data_received, name=plugin.get_fullname(), **plugin._parameters)


def load_sdp_plugin(
    tmp_dir: str,
    class_path: str,
    class_name: str,
    items_yaml: str,
    params: dict[str, Any] | None = None,
    section: str = 'sdp',
    record: bool = True,
) -> SDPRig:
    """
    Load an SDP plugin through the real plugin loader and create its items.

    With ``record`` set, the plugin's connection is replaced by a
    :class:`RecordingConnection` built from the plugin's own resolved
    parameters (so its callbacks are wired exactly as the plugin wired them)
    before any item is created; otherwise the plugin keeps the connection it
    built itself, and ``SDPRig.connection`` is that connection.

    Parameters as for :func:`load_plugin`, plus:

    :param record: replace the plugin's connection by a recording one
    """
    rig = load_plugin(
        tmp_dir,
        class_path,
        class_name,
        items_yaml,
        params=params,
        section=section,
        before_items=_install_recording_connection if record else None,
    )
    return SDPRig(
        sh=rig.sh, plugin=rig.plugin, scheduler=rig.scheduler, tmp_dir=tmp_dir, connection=rig.plugin._connection
    )
