
.. index:: Sample MQTT Plugin
.. index:: Plugin; Sample MQTT Plugin
.. index:: MQTT; Sample MQTT Plugin

.. role:: redsup
.. role:: bluesup

Beispielplugin mit MQTT-Unterstützung
=====================================

Dieser Abschnitt zeigt ein Beispielplugin mit MQTT-Unterstützung. Es kann mit oder ohne Webinterface umgesetzt werden.

Das komplette Plugin mit allen Dateien kann auf github unter https://github.com/smarthomeng/smarthome im ``/dev``-Ordner gefunden werden.

:Note: Diese Dokumentation bezieht sich auf Versionen ab v1.7.0. Sie gilt nicht für Versionen vor v1.7.0

Auf dieser Seiten finden sich Dateien und Anregungen für neue Plugins, die MQTT nutzen. Das Plugin selbst besteht aus einer Datei mit Python-Code (__init__.py), einer Datei mit Metadaten (plugin.yaml) und der Dokumentation (user_doc.rst). Ein Satz Beispieldateien wird weiter unten gezeigt.

Eine formatierte Version der Beispieldokumentation findet sich hier: :doc:`user_doc.rst </dev/sample_mqttplugin/user_doc>`

Eine Version im Quelltext als Grundlage für eigene Dokumentationen ist unterhalb der Python-Quellcodes verfügbar.


Die Metadaten-Datei:
--------------------

.. literalinclude:: /dev/sample_mqttplugin/plugin.yaml
    :caption: plugin.yaml


Der Quelltext:
--------------

.. literalinclude:: /dev/sample_mqttplugin/__init__.py
    :caption: __init__.py


Das Webinterface (template file):
---------------------------------

Das Template hat bis zu fünf Inhaltsblöcke, die mit den Daten des Plugins befüllt werden können:

   1. Kopfdaten auf der rechten Seite ``{% block headtable %}``
   2. Tab 1 der Hauptteils der Seite ``{% block bodytab1 %}``
   3. Tab 2 der Hauptteils der Seite ``{% block bodytab2 %}``
   4. Tab 3 der Hauptteils der Seite ``{% block bodytab3 %}``
   5. Tab 4 der Hauptteils der Seite ``{% block bodytab4 %}``

Die Anzahl der anzuzeigenden ``bodytab``-Blöcke wird mit der folgenden Anweisung festgelegt:
``{% set tabcount = 4 %}``

.. literalinclude:: /dev/sample_mqttplugin/webif/templates/index.html
    :tab-width: 4
    :caption: templates/index.html


Die Datei für Mehrsprachigkeit:
-------------------------------

.. literalinclude:: /dev/sample_mqttplugin/locale.yaml
    :caption: locale.yaml


Die Dokumentation:
------------------

Die folgende Datei skizziert den Mindestumfang für die Plugin-Dokumentation.

.. literalinclude:: /dev/sample_mqttplugin/user_doc.rst
    :caption: user_doc.rst

.. hint::

   Das in früheren Versionen verwendete **README**-Format für die Dokumentation von Plugins ist veraltet.
   Ein Großteil der Dokumentation ist in die Metadaten-Dokumentation in **plugin.yaml** übergegangen.
   Die restliche Dokumentation sollte nur noch im **user_doc**-Format erfolgen.

   Soweit möglich, sollten bestehende **README** im Rahmen von Aktualisierungen in entsprechende **user_doc** überführt werden.

