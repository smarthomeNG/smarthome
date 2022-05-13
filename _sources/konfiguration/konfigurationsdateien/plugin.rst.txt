
.. index:: Plugin Konfiguration; Konfigurationsdatei /etc/plugin.yaml
.. index:: Konfigurationsdateien; /etc/plugin.yaml

.. _`plugin.yaml`:


plugin.yaml
===========

Plugins erweitern die Kern-Funktionalität von SmartHomeNG.
Das **../plugins** Verzeichnis enthält ein Unterverzeichnis für jedes verfügbare Plugin.
In der Konfigurationsdatei **../etc/plugin.yaml** wird die Konfiguration für jedes Plugin hinterlegt,
dass genutzt werden soll.

Das Beispiel unten konfiguriert das KNX-Plugin, so dass es Telegramme an einen **eibd** oder einen
**knxd** Daemon sendet bzw. von dort empfängt. **eibd** und **knxd** sind Software Gateways zum KNX Bus.

In diesem Fall ist der Name der Plugin Instanz **knx** und das Plugin wird im Verzeichnis **knx** im
Verzeichnis **../plugins** gesucht.


.. literalinclude:: ../../../../../etc/plugin.yaml.default
   :caption: plugin.yaml
   :language: yaml


Es existiert eine `README.md` Datei zu jedem Plugin. Diese Datei gibt ausführliche Informationen,
wie das Plugin zu konfigurieren ist. Die `README`s sind unter :doc:`Plugins <../plugins>` in der
Übersicht der Plugins zu finden. Wie die Konfiguration von Plugins grundsätzlich funktioniert ist
im Abschnitt **Konfiguration/Plugins** zu finden.


.. note::

    Die Konfigurationsparameter der Plugins, die in dieser Datei konfiguriert werden, können auch über das graphische
    Administrations-Interface geändert werden.



Referenzierung eines Plugins in der Konfiguration
-------------------------------------------------

Ab v1.4 ist es Standard, das Plugin über den einzigen Parameter ``plugin_name`` zu spezifizieren.
Dabei ist der Wert der Wert des früheren Parameters ``class_path`` ohne den Präfix ``plugins.``,
also der Name des Plugin Verzeichnisses. Da alle Plugins im Verzeichnis **../plugins** liegen, ist
**plugins.** redundante Information.

Bis zu SmartHomeNG v1.3 wurde ein Plugin in der Konfiguration über zwei Parameter ``class_name``
und ``class_path`` referenziert.

Wenn das Plugin eine Metadaten Definition enthält (was fast alle Plugins tun), so gibt es keine
Notwendigkeit den Parameter ``class_name`` anzugeben. Diese Information wird dann den Metadaten
entnommen.

.. note::

    Sollte es notwendig werden ein Plugin außerhalb des Verzeichnisses **../plugins** zu speichern,
    kann dieses Plugin (wie bisher) über ``class_path:`` referenziert werden.


Nutzung einer älteren Version eines Plugins
-------------------------------------------

Falls Du nicht die neueste Version von SmartHomeNG nutzt, kann es vorkommen, dass Du eine ältere
Version eines Plugins nutzen möchtest. Einige Plugins enthalten in Unterverzeichnissen ältere
Versionen. Um diese zu nutzen, muss in **../etc/plugin.yaml** in der Konfiguration der Parameter
``plugin_version:`` angegeben werden.

Um herauszufinden, ob ein Plugin mit einer (oder mehreren) älteren Version(en) installiert ist,
hilft ein Blick in das Plugin Verzeichnis. Falls es dort Unterverzeichnisses gibt, deren Name mit
`_pv_` beginnt, sind ältere Versionen vorhanden. Der Rest des jeweiligen Verzeichnisnamens gibt
an, welche Version sich in dem Verzeichnis befindet. Wenn Du ein Unterverzeichnis **_pv_1_3_0**
findest, enthält es die Version v1.3.0 des Plugins. Um diese Version, statt der aktuellen Version
zu laden, musst Du nur den Eintrag ``plugin_version: 1.3.0`` zur Plugin Konfiguration hinzufügen.



