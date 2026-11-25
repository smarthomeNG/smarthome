.. index:: Plugins; pushbullet
.. index:: pushbullet

==========
pushbullet
==========

Das Plugin verschickt Notizen, Links, Adressen, Listen und Dateien über den Pushbullet-Dienst an
ein oder mehrere Geräte.

Voraussetzungen
================

Ein Pushbullet-Konto sowie ein persönlicher API-Key werden benötigt, siehe
`pushbullet.com <http://www.pushbullet.com>`_.

Die Ziel-**deviceid** eines Geräts lässt sich ermitteln, indem man sich unter
`pushbullet.com <http://www.pushbullet.com>`_ einloggt, das gewünschte Gerät auswählt und den Teil
der Browser-URL hinter ``device_iden=`` kopiert.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/pushbullet`
beschrieben.

**apikey** und **deviceid** können global in ``etc/plugin.yaml`` gesetzt werden. Ist einer der
beiden Werte dort nicht gesetzt, muss er beim jeweiligen Funktionsaufruf mitgegeben werden.

Verwendung
==========

Die Funktionen **note()**, **link()**, **address()**, **list()** und **file()** des Plugins sind
unter :doc:`/plugins_doc/config/pushbullet` beschrieben und können aus Logiken heraus aufgerufen
werden, z.B.::

    sh.pushbullet.note("Note to myself.", "Call my mother.")

Zusätzlich steht die Funktion **delete()** zur Verfügung, mit der ein zuvor verschickter Push
wieder gelöscht werden kann::

    sh.pushbullet.delete(pushid, apikey=None)

**pushid**
    ID des zu löschenden Push. Wird beim Versand von den anderen Funktionen im Ergebnis-Objekt
    zurückgegeben (Feld ``iden``).

**apikey**
    (optional) Überschreibt den global in ``etc/plugin.yaml`` gesetzten API-Key für diesen Aufruf.

Beispiel::

    result = sh.pushbullet.note("Note to myself.", "Call my mother.")
    sh.pushbullet.delete(result['iden'])
