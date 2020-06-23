.. index:: Build Tool für Python Requirements
.. index:: Tools; Build Tool für Python Requirements

build_requirements.py
=====================

Dieses Skript stellt eine vollständige Liste der Anforderungen (benötigte Python Module) für 
den SmartHomeNG-Core und alle Plugins zusammen.

Die Liste wird nicht auf ihre Richtigkeit oder auf andere bzw. gegenläufige Anforderungen geprüft.

Das Verfahren zum Zusammenstellen der Anforderungen ist wie folgt:

1) Durchsucht die Unterverzeichnisse des **../plugins** Verzeichnisses und sammelt alle Dateien mit Anforderungen
2) Lesen der Anforderungen für den Core
3) Lesen aller gefundenen Dateien mit Anforderungen und hinfügen (mit der Quellangabe) der Anforderung zu einem dict
4) Schreiben aller gefundenen Anforderungen in die Datei **all.txt** im Verzeichnis **../requirements**


Anschließend kann die Python Installation mit dem folgenden Kommando auf den erforderlichen
Stand gebracht werden.

.. code::

   smarthome@<yourcomputer>:/usr/local/smarthome$ sudo pip3 install -r requirements/base.txt

.. attention::

   Bitte darauf achten das Kommando **pip3** zu verwenden. Bei Verwendung von **pip** wird, falls
   eine Python v2.7 Installation auf dem Computer existiert, diese aktualisiert und nicht die
   Python 3 Version.
