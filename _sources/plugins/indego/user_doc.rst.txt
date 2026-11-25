.. index:: Plugins; indego
.. index:: indego

======
indego
======

Das Plugin verbindet SmartHomeNG über den Bosch-Server mit einem Indego Mähroboter mit
Connect-Funktion (GSM). Es unterstützt sowohl die neueren Modelle (350/400) als auch die älteren
800/1000/1200 mit Connect-Nachrüstung.

Über das Plugin lassen sich folgende Befehle an den Mäher senden:

- Mähen starten
- Pausieren
- zur Ladestation zurückkehren
- Smart-Mowing ein-/ausschalten (der Server legt Start- und Stoppzeiten selbst fest, abhängig von
  Temperatur und Wetter)
- die Häufigkeit des Smart-Mowing setzen bzw. abfragen (-100 für die niedrigste, +100 für die
  höchste Frequenz)

Außerdem liest das Plugin folgende Informationen aus:

- die aktuelle Karte des Gartens inkl. bereits gemähter Fläche und Position des Mähers
- den Fortschritt der aktuellen Mähsession in Prozent
- den Status des Mähers (z.B. dockt, mäht, lernt den Garten, fährt zur Station)
- Verlaufsdaten (Gesamtbetriebszeit, Ladezeit, nächster geplanter Smart-Mowing-Termin)
- Gerätedaten (Benutzername, Modus, Firmware-Version, Seriennummer)
- Alarmmeldungen inkl. Zeitpunkt, mit der Möglichkeit, sie anschließend auf dem Server zu löschen
- eine Wettervorhersage für die hinterlegte Adresse für die nächsten vier Tage (u. a. Sonnenstunden,
  Regenwahrscheinlichkeit, Regenmenge je Tageszeit)

Das Setzen der Mähzeiten selbst ist über das Plugin nicht möglich, dies bleibt der Indego-App
vorbehalten.

Voraussetzungen
================

Der Mäher muss über die Indego-App eingerichtet und registriert sein. Benutzername und Passwort
der App werden für die Anmeldung des Plugins am Bosch-Server benötigt. Für die Nutzung von
Smart-Mowing muss außerdem der Standort in der App hinterlegt sein.

Unterstützte Hardware:

- Indego Connect 350
- Indego Connect 400
- Indego 800/1000/1200 mit Connect-Nachrüstung

.. important::

   Der Bosch-Server erlaubt jeweils nur eine aktive Verbindung. Wird gleichzeitig mit der App
   verbunden, verliert das Plugin seine Verbindung und authentifiziert sich neu, wodurch wiederum
   die Sitzung der App ungültig wird. App und Plugin sollten daher nicht gleichzeitig verwendet
   werden.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/indego`
beschrieben.

Item-Attribute
--------------

**indego_command**
    Bool-Item. Der Attributwert ist der als JSON-String kodierte Befehl, der beim Setzen des Items
    auf ``True`` an den Mäher gesendet wird, z.B. ``{"state":"mow"}``, ``{"state":"pause"}`` oder
    ``{"state":"returnToDock"}``.

**indego_smart**
    Bool-Item. Schaltet Smart-Mowing ein (``True``) oder aus (``False``).

**indego_frequency**
    Num-Item. Setzt bzw. liest die Smart-Mowing-Frequenz (-100 bis +100).

**indego_add_key**
    Str-Item. Der Attributwert benennt ein zusätzliches Feld aus der Statusantwort des Servers
    (z.B. ``config_change``, ``mow_trig``), das keinem der fest vorgegebenen Items entspricht und
    stattdessen in dieses Item geschrieben wird.

Beispiele
=========

Eine vollständige Item-Struktur mit allen vom Plugin befüllten Items liegt dem Plugin als
``example.yaml`` bei, inklusive der Wettervorhersage-Struktur für 20 Drei-Stunden-Intervalle und
5 Tage. Das Basis-Item ``indego`` kann umbenannt werden, ist aber als Elternitem erforderlich.

Die folgenden Items zeigen den Einsatz der Plugin-eigenen Attribute::

    indego:

        SMART:
            type: bool
            visu_acl: rw
            indego_smart: 'yes'
            cache: 'on'

            frequenz:
                type: num
                indego_frequency: 'yes'
                cache: 'on'

        MOW:
            type: bool
            visu_acl: rw
            indego_command: '{"state":"mow"}'
            autotimer: 5 = False

        PAUSE:
            type: bool
            visu_acl: rw
            indego_command: '{"state":"pause"}'
            autotimer: 5 = False

        RETURN:
            type: bool
            visu_acl: rw
            indego_command: '{"state":"returnToDock"}'
            autotimer: 5 = False

        config_change:
            type: bool
            indego_add_key: config_change

        mow_trig:
            type: bool
            indego_add_key: mow_trig

Für SmartVISU stellt das Plugin im Verzeichnis ``smartVISU_dropins`` passende Icons und
Beispielseiten bereit, die über den Dropins-Mechanismus von SmartVISU eingebunden werden können.
