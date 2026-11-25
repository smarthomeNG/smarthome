.. index:: Plugins; kathrein
.. index:: kathrein

========
kathrein
========

Ansteuerung von Kathrein-Receivern über deren Netzwerkschnittstelle.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/kathrein` beschrieben.

Item-Attribute
--------------

Das Attribut **kathrein** kann auf zwei Arten verwendet werden:

- an einem Item vom Typ ``str``, mit dem Wert ``true``: jeder Wert, der dann auf das Item
  geschrieben wird, wird als Kommando an den Kathrein-Receiver gesendet.
- an einem Item vom Typ ``bool``, mit einem Kommando-Schlüsselwort als Wert: sobald das Item auf
  ``true`` gesetzt wird, sendet das Plugin das hinterlegte Kommando. Mehrere Kommandos lassen sich
  durch ``|`` getrennt angeben. Für ein reines Kommando-Item empfiehlt sich zusätzlich
  **enforce_updates**.

Die möglichen Kommando-Schlüsselwörter sind unter :doc:`/plugins_doc/config/kathrein` aufgeführt.

**kathreinid** ist ebenfalls unter :doc:`/plugins_doc/config/kathrein` beschrieben.


Beispiele
=========

::

    receiver:
        name: Receiver
        type: str
        kathrein: 'true'
        kathreinid: 1
        enforce_updates: 'true'

        mute:
            name: Mute
            type: bool
            visu_acl: rw
            kathrein: mute
            kathreinid: 1
            enforce_updates: 'true'

        media:
            name: Media
            type: bool
            visu_acl: rw
            kathrein: media
            kathreinid: 1
            enforce_updates: 'true'
