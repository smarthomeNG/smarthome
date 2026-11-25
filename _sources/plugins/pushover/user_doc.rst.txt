.. index:: Plugins; pushover (Pushover Benachrichtigungsdienst)
.. index:: pushover

========
pushover
========

Das pushover-Plugin verschickt Push-Benachrichtigungen über den Pushover-Dienst an Android-, iOS-
und Windows-Clients.


Voraussetzungen
================

Ein Pushover API-Key wird benötigt, kostenlos erhältlich nach Registrierung unter
`pushover.net/apps <https://pushover.net/apps/>`_.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/pushover` beschrieben.


Verwendung
==========

Nachrichten werden aus Logiken heraus über die Funktion **sh.po()** verschickt (Instanzname
entsprechend der eigenen Konfiguration)::

    sh.po(title, message, priority, retry, expire, ttl, sound, url, url_title, device, userKey, apiKey)

Nur **message** ist zwingend erforderlich, alle anderen Parameter sind optional::

    # Einfache Nachricht ohne Titel
    sh.po(None, "Dies ist eine Testnachricht.")

    # Nachricht mit Titel
    sh.po("Einfacher Test", "Dies ist eine Testnachricht.")

    # Nachricht mit hoher Priorität
    sh.po("Warnung", "Die Tür ist nicht verschlossen!", 1)

    # Nachricht an ein bestimmtes Gerät
    sh.po("Einfacher Test", "Dies ist eine Testnachricht", device="e6653")

    # Nachricht mit angehängtem Bild (z.B. Kamera-Snapshot)
    sh.po(title="Einfacher Test", message="Dies ist eine Testnachricht", attachment="/tmp/snapshot.jpg")

Parameter
---------

**priority**
    Priorität der Nachricht, siehe `Pushover API: Priority <https://pushover.net/api#priority>`_.

**retry** / **expire**
    Bei Notfall-Priorität: Wiederholungsintervall bzw. Gesamtdauer der Wiederholungen in Sekunden,
    siehe `Pushover API: Priority <https://pushover.net/api#priority>`_.

**ttl**
    Time to live in Sekunden (wird bei Priorität 2 ignoriert), siehe
    `Pushover API: TTL <https://pushover.net/api#ttl>`_.

**sound**
    Überschreibt den vom Nutzer eingestellten Standard-Ton, siehe
    `Pushover API: Sounds <https://pushover.net/api#sounds>`_.

**url** / **url_title**
    Zusätzliche URL (und deren Titel), die nicht im Nachrichtentext enthalten, aber anklickbar ist,
    siehe `Pushover API: URLs <https://pushover.net/api#urls>`_.

**device** / **userKey** / **apiKey**
    Überschreiben die global in ``etc/plugin.yaml`` gesetzten Werte für diesen Aufruf.

**attachment**
    Pfad zu einer Datei (meist ein Bild), die der Nachricht angehängt wird.
