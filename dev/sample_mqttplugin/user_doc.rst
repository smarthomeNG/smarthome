.. index:: Plugins; Mqtt-Pluginname (in Kleinbuchstaben)
.. index:: Mqtt-Pluginname (in Kleinbuchstaben)


====================================
Mqtt-Pluginname (in Kleinbuchstaben)
====================================

Hier sollte eine allgemeine Beschreibung stehen, wozu das Plugin gut ist (was es tut).

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left


Anforderungen
=============

Anforderungen des Plugins auflisten. Werden spezielle Soft- oder Hardwarekomponenten benötigt?


Notwendige Software
-------------------

* die
* benötigte
* Software
* auflisten

Dies beinhaltet Python- und SmartHomeNG-Module

Unterstützte Geräte
-------------------

* die
* unterstütze
* Hardware
* auflisten

|

Konfiguration
=============

.. comment Den Text **Pluginname (in Kleinbuchstaben)** durch :doc:`/plugins_doc/config/pluginname` ersetzen

Die Plugin Parameter, die Informationen zur Item-spezifischen Konfiguration des Plugins und zur Logik-spezifischen
Konfiguration sind unter **Pluginname (in Kleinbuchstaben)** beschrieben.

Dort findet sich auch die Dokumentation zu Funktionen, die das Plugin evtl. bereit stellt.


Funktionen
----------

<Hier können bei Bedarf ausführliche Beschreibungen zu den Funktionen dokumentiert werden.>

<Sonst diesen Abschnitt löschen>

|

Beispiele
=========

Hier können ausführlichere Beispiele und Anwendungsfälle beschrieben werden. (Sonst ist der Abschnitt zu löschen)

|

Web Interface
=============

Die Datei ``dev/sample_plugin/webif/templates/index.html`` sollte als Grundlage für Webinterfaces genutzt werden. Um Tabelleninhalte nach Spalten filtern und sortieren zu können, muss der entsprechende Code Block mit Referenz auf die relevante Table ID eingefügt werden (siehe Doku).

SmartHomeNG liefert eine Reihe Komponenten von Drittherstellern mit, die für die Gestaltung des Webinterfaces genutzt werden können. Erweiterungen dieser Komponenten usw. finden sich im Ordner ``/modules/http/webif/gstatic``.

Wenn das Plugin darüber hinaus noch Komponenten benötigt, werden diese im Ordner ``webif/static`` des Plugins abgelegt.

|

Version History
===============

In diesem Abschnitt kann die Versionshistorie dokumentiert werden, falls der Plugin Autor dieses möchte. Diese Abschnitt
ist optional.

