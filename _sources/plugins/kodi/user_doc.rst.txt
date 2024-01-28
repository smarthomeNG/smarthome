.. index:: Plugins; kodi
.. index:: kodi

kodi
####

Hinweise zur Umstellung
=======================

.. warning::

    Das kodi-Plugin wurde komplett auf smartdeviceplugin umgestellt. Damit gehen sowohl in der Struktur der items als auch der verfügbaren Kommandos erhebliche Änderungen einher, die eine Anpassung der Item-Konfiguration erfordern.


Wenn bisher die mitgelieferten Structs genutzt wurden, muss nur die struct-Einbindung geändert werden: aus

.. code-block:: yaml

    # items/media.yaml
    kodi:
        struct:
            - kodi.control
            - kodi.info


wird neu

.. code-block:: yaml

    # items/media.yaml
    kodi:
        struct:
            - kodi.old_control
            - kodi.old_info


Damit ist die alte Item-Struktur 1:1 übernommen und nutzt die neuen Funktionen.

Wenn die Items einzeln erstellt und konfiguriert wurden, muss die alte Item-Konfiguration
manuell umgestellt werden, indem die entsprechenden Item-Attribute des kodi-Plugins ersetzt werden.

.. code-block:: yaml

    kodi:
        volume:
            type: num
            kodi_item: volume

in der alten Form wird zu

.. code-block:: yaml

    kodi:
        volume:
            type: num
            kodi_command: control.volume
            kodi_read: true
            kodi_write: true

Die notwendige Konfiguration der einzelnen Items lässt sich in der `plugins/kodi/plugin.yaml` in der Definition der structs nachlesen.



Konfiguration
=============

.. important::

    Die Informationen zur Konfiguration des Plugins sind unter :doc:``/plugins_doc/config/kodi`` beschrieben.

    Eine minimale Konfiguration könnte so aussehen:

.. code-block:: yaml

    # etc/plugin.yaml
    kodi:
        plugin_name: kodi
        host: 10.0.0.42
        suspend_item: media.kodi.suspend

.. code-block:: yaml

    # items/media.yaml
    kodi:
        struct: kodi.ALL

        suspend:
            type: bool
            cache: true


Hinweise zu Verbindungen
========================

Über die plugin-Parameter `connect_retries` (Anzahl) und `connect_cycle` (Wartezeit) kann eingestellt werden, wie oft das Plugin versucht, eine Verbindung zu Kodi aufzubauen. 

Das weitere Verhalten wird über die Parameter `retry_cycle` (Wartezeit) und `retry_suspend` (Anzahl Zyklen) eingestellt. Nach Ablauf dieser Versuche wartet das Plugin 30 Sekunden (bzw. die in `retry_cycle` eingestellte Zeit), bevor das Ganze wiederholt wird. Wenn `retry_suspend` gesetzt ist, wechselt das Plugin nach dieser Anzahl von `retry_cycles` in den Suspend-Modus und beendet die Verbindungsversuche.
Um den Suspend-Modus zu beenden, kann mit dem Plugin-Attribut `suspend_item` ein Item konfiguriert werden, mit dem der Suspend-Modus ein- und ausgeschaltet werden kann. Alternativ stehen die Plugin-Funktionen `suspend()` und `resume()` zur Verfügung.
