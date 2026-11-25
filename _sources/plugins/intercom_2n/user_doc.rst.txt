.. index:: Plugins; intercom_2n
.. index:: intercom_2n

===========
intercom_2n
===========

Integration von 2N SIP-Türsprechanlagen. Das Plugin bindet Ereignisse und Befehle der `2N Helios
HTTP API <https://wiki.2n.cz/hip/hapi/latest/en>`_ als Items an SmartHomeNG an.

Voraussetzungen
================

Das Plugin ist für 2N-Türsprechanlagen (Hersteller `2N <http://www.2n.cz/en/>`_) ausgelegt und
wurde mit einem **2N Helios IP Verso** getestet. Es sollte mit jedem Gerät funktionieren, das die
2N Helios HTTP API implementiert.

Die meisten Befehle setzen die Lizenz **Enhanced Integration** auf der Türsprechanlage voraus, der
``AudioLoopTest``-Ereignistyp zusätzlich die Lizenz **Enhanced Audio**. Der reine Ereignisempfang
funktioniert ohne zusätzliche Lizenz.

Außerdem benötigt der für das Plugin verwendete Benutzer die passenden Berechtigungen. Diese werden
in der Weboberfläche der Türsprechanlage vergeben. Die folgende Tabelle zeigt, welcher Dienst und
welche Berechtigung für welchen Befehl bzw. welche interne Funktion nötig ist und ob dafür die
Lizenz Enhanced Integration erforderlich ist:

.. list-table::
   :header-rows: 1
   :widths: 20 20 25 15

   * - Befehl / Funktion
     - Dienst
     - Berechtigung
     - Lizenz Enhanced Integration
   * - system_info
     - System
     - System Control
     - nein
   * - system_status
     - System
     - System Control
     - ja
   * - system_restart
     - System
     - System Control
     - ja
   * - firmware_upload
     - System
     - System Control
     - ja
   * - firmware_apply
     - System
     - System Control
     - ja
   * - config_get
     - System
     - System Control
     - ja
   * - config_upload
     - System
     - System Control
     - ja
   * - factory_reset
     - System
     - System Control
     - ja
   * - switch_caps
     - Switch
     - Switch Monitoring
     - ja
   * - switch_status
     - Switch
     - Switch Monitoring
     - ja
   * - switch_control
     - Switch
     - Switch Control
     - ja
   * - io_caps
     - I/O
     - I/O Monitoring
     - ja
   * - io_status
     - I/O
     - I/O Monitoring
     - ja
   * - io_control
     - I/O
     - I/O Control
     - ja
   * - phone_status
     - Phone/Call
     - Call Monitoring
     - ja
   * - call_status
     - Phone/Call
     - Call Monitoring
     - ja
   * - call_dial
     - Phone/Call
     - Call Control
     - ja
   * - call_answer
     - Phone/Call
     - Call Control
     - ja
   * - call_hangup
     - Phone/Call
     - Call Control
     - ja
   * - camera_caps
     - Camera
     - Camera Monitoring
     - nein
   * - camera_snapshot
     - Camera
     - Camera Monitoring
     - nein
   * - display_caps
     - Display
     - Display Control
     - ja
   * - display_upload_image
     - Display
     - Display Control
     - ja
   * - display_delete_image
     - Display
     - Display Control
     - ja
   * - log_caps
     - Logging
     - --
     - nein
   * - audio_test
     - Audio
     - Audio Control
     - ja
   * - email_send
     - E-mail
     - E-mail Control
     - ja
   * - pcap
     - System
     - System Control
     - ja
   * - pcap_restart
     - System
     - System Control
     - ja
   * - pcap_stop
     - System
     - System Control
     - ja

Das Ereignis-Abonnement selbst (Dienst Logging, intern über das Plugin verwaltet, siehe
:ref:`Ereignisse <ereignisse-intercom_2n>`) benötigt keine eigene Berechtigung, für einzelne
Ereignistypen aber teils zusätzliche Berechtigungen (siehe unten).

.. important::
   Sicherheitseinstellungen lassen sich in der Weboberfläche der Türsprechanlage pro API einzeln
   konfigurieren, das Plugin unterstützt aber nur eine einheitliche Einstellung für alle APIs.
   Alle Sicherheitsparameter unter *Dienste → HTTP-API* müssen daher auf denselben Wert gesetzt
   werden wie der **auth_type**-Parameter des Plugins.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/intercom_2n`
beschrieben.

Bei Digest-Authentifizierung (``auth_type: 2``) protokolliert die zugrunde liegende Python-Bibliothek
für jeden Aufruf zunächst eine ``401``-Fehlermeldung, bevor der eigentliche authentifizierte Aufruf
erfolgt. Das ist beabsichtigtes Verhalten des Digest-Verfahrens und kein Fehler.

Item-Attribute
--------------

Das Plugin bindet Items über drei eigene Attribute an Ereignisse bzw. Befehle der Türsprechanlage:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Attribut
     - Bedeutung
   * - **event_2n**
     - Name des Ereignistyps (siehe :ref:`Ereignisse <ereignisse-intercom_2n>`), am Item, das als
       Container für das Ereignis dient.
   * - **event_data_2n**
     - Name des Datenfelds innerhalb der Ereignis-Nutzdaten, an einem Kind-Item von
       **event_2n**. Der Wert dieses Datenfelds wird bei Eintreten des Ereignisses in das Item
       geschrieben.
   * - **command_2n**
     - Name des Befehls (siehe :ref:`Befehle <befehle-intercom_2n>`), am Item, dessen Wert nach
       Ausführung das Ergebnis des Befehls enthält. Ein Kind-Item mit ``command_2n: execute`` löst
       den Befehl aus, sobald es auf einen wahren Wert gesetzt wird. Etwaige Befehlsparameter werden
       über weitere Kind-Items mit dem jeweiligen Parameternamen als Item-Namen übergeben.

.. _ereignisse-intercom_2n:

Ereignisse
==========

Ereignis-Abonnement und -Verlängerung übernimmt das Plugin automatisch, dafür ist keine eigene
Konfiguration nötig. Tritt ein Ereignis ein, werden alle Kind-Items des zugehörigen
**event_2n**-Items mit dem passenden Wert aus den Ereignisdaten belegt. Ein Ereignis kann beliebig
viele solcher Kind-Items haben.

.. list-table::
   :header-rows: 1
   :widths: 25 60 15

   * - Ereignis
     - Beschreibung
     - Hinweis
   * - AudioLoopTest
     - Meldet Ablauf und Ergebnis eines automatischen Audio-Loop-Tests.
     - nur mit Enhanced-Audio-Lizenz
   * - CallStateChanged
     - Meldet Aufbau, Ende oder Wechsel eines aktiven Gesprächszustands.
     - --
   * - CardEntered
     - Meldet das Auflegen einer RFID-Karte am Kartenleser.
     - nur bei Geräten mit RFID-Kartenleser
   * - CodeEntered
     - Meldet die Eingabe eines Benutzercodes über die Zifferntastatur.
     - nur bei Geräten mit Zifferntastatur
   * - DeviceState
     - Meldet Systemereignisse bei Zustandsänderungen des Geräts, z. B. einen Neustart.
     - --
   * - DoorOpenTooLong
     - Meldet eine zu lange geöffnete Tür oder einen Fehler beim Schließen innerhalb des Timeouts.
     - nur bei Geräten mit digitalem Eingang
   * - InputChanged
     - Meldet eine Zustandsänderung eines logischen Eingangs.
     - --
   * - KeyPressed
     - Meldet das Drücken einer Kurzwahl- oder Zifferntastaturtaste.
     - --
   * - KeyReleased
     - Meldet das Loslassen einer Kurzwahl- oder Zifferntastaturtaste.
     - --
   * - LoginBlocked
     - Meldet eine vorübergehende Sperrung des Logins zur Weboberfläche.
     - --
   * - MotionDetected
     - Meldet eine über eine Kamera erkannte Bewegung.
     - nur bei Geräten mit Kamera
   * - NoiseDetected
     - Meldet einen erhöhten Geräuschpegel.
     - nur bei Geräten mit Mikrofon/Mikrofoneingang
   * - OutputChanged
     - Meldet eine Zustandsänderung eines logischen Ausgangs.
     - --
   * - RegistrationStateChanged
     - Meldet eine Änderung des SIP-Registrierungsstatus.
     - --
   * - SwitchStateChanged
     - Meldet eine Zustandsänderung von Schalter 1 bis 4.
     - --
   * - TamperSwitchActivated
     - Meldet die Aktivierung des Sabotageschalters (Gehäuse geöffnet).
     - nur bei Geräten mit Sabotageschalter
   * - UnauthorizedDoorOpen
     - Meldet ein unautorisiertes Öffnen der Tür.
     - nur bei Geräten mit digitalem Eingang
   * - UserAuthenticated
     - Meldet eine Benutzerauthentifizierung mit anschließendem Türöffnen.
     - --

Für einige Ereignistypen benötigt der verwendete Benutzer zusätzlich eine bestimmte Berechtigung,
sonst werden die Ereignisse beim Abonnement stillschweigend ausgefiltert:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Benötigte Berechtigung
     - Betroffene Ereignisse
   * - Keypad monitoring
     - KeyPressed, KeyReleased, CodeEntered
   * - UID monitoring (cards/Wiegand)
     - CardEntered
   * - I/O monitoring
     - InputChanged, OutputChanged, SwitchStateChanged
   * - Call/phone monitoring
     - CallStateChanged, RegistrationStateChanged
   * - keine
     - alle übrigen Ereignisse aus obiger Tabelle

.. _befehle-intercom_2n:

Befehle
=======

Ein Befehl wird ausgeführt, indem das Kind-Item mit ``command_2n: execute`` auf einen wahren Wert
gesetzt wird. Das Ergebnis wird als JSON-Text in den Wert des übergeordneten **command_2n**-Items
geschrieben. Einige Befehle nehmen einen lokalen Dateipfad als Parameter entgegen
(**firmware_file**, **config_file**, **snapshot_file**, **pcap_file**, **gif_file**) - dieser Pfad
bezieht sich auf das Dateisystem, auf dem SmartHomeNG läuft, nicht auf die Türsprechanlage.

.. list-table::
   :header-rows: 1
   :widths: 18 20 22 40

   * - Befehl
     - Pflichtparameter
     - Optionale Parameter
     - Beschreibung
   * - system_info
     - --
     - --
     - Basisinformationen zum Gerät (Typ, Seriennummer, Firmware-Version usw.).
   * - system_status
     - --
     - --
     - Aktueller Systemstatus (Systemzeit, Betriebsdauer).
   * - system_restart
     - --
     - --
     - Startet die Türsprechanlage neu.
   * - firmware_upload
     - **firmware_file**
     - --
     - Lädt eine neue Firmware auf das Gerät hoch.
   * - firmware_apply
     - --
     - --
     - Bestätigt eine zuvor hochgeladene Firmware und startet das Gerät neu.
   * - config_get
     - **config_file**
     - --
     - Lädt die Gerätekonfiguration herunter und speichert sie lokal.
   * - config_upload
     - **config_file**
     - --
     - Lädt eine Konfigurationsdatei auf das Gerät hoch.
   * - factory_reset
     - --
     - --
     - Setzt das Gerät auf Werkseinstellungen zurück.
   * - switch_caps
     - --
     - --
     - Aktuelle Einstellungen und Steuerungsoptionen der Schalter.
   * - switch_status
     - --
     - **switch** (Nummer, 0 = alle)
     - Aktueller Status der Schalter.
   * - switch_control
     - **switch**, **action** (``on``/``off``/``trigger``)
     - **response**
     - Steuert einen Schalter.
   * - io_caps
     - --
     - **port**
     - Verfügbare Ein-/Ausgänge (Ports).
   * - io_status
     - --
     - **port**
     - Aktueller Status der logischen Ein-/Ausgänge.
   * - io_control
     - **port**, **action** (``on``/``off``)
     - **response**
     - Steuert einen logischen Ausgang.
   * - phone_status
     - --
     - **account** (1 oder 2)
     - Status der SIP-Konten.
   * - call_status
     - --
     - **session**
     - Status aktiver Anrufe.
   * - call_dial
     - **number**
     - --
     - Startet einen abgehenden Anruf zu einer Rufnummer oder SIP-URI.
   * - call_answer
     - **session**
     - --
     - Nimmt einen eingehenden Anruf an.
   * - call_hangup
     - **session**
     - **reason** (``normal``/``rejected``/``busy``)
     - Beendet einen Anruf.
   * - camera_caps
     - --
     - --
     - Verfügbare Videoquellen und Auflösungen für Schnappschüsse.
   * - camera_snapshot
     - **width**, **height**, **snapshot_file**
     - **source**, **time**
     - Lädt ein Kamerabild herunter und speichert es lokal.
   * - display_caps
     - --
     - --
     - Verfügbare Displays und deren Eigenschaften.
   * - display_upload_image
     - **gif_file**, **display**
     - --
     - Lädt ein GIF-Bild auf das Display hoch.
   * - display_delete_image
     - **display**
     - --
     - Löscht den Bildinhalt eines Displays.
   * - log_caps
     - --
     - --
     - Vom Gerät unterstützte Ereignistypen.
   * - audio_test
     - --
     - --
     - Startet einen automatischen Test von Mikrofon und Lautsprecher; das Ergebnis wird als
       AudioLoopTest-Ereignis gemeldet.
   * - email_send
     - **to**, **subject**
     - **body**, **picture_count**, **width**, **height**, **timespan**
     - Versendet eine E-Mail, optional mit angehängten Kamerabildern.
   * - pcap
     - **pcap_file**
     - --
     - Lädt eine Mitschnittdatei (pcap) des Netzwerkverkehrs herunter und speichert sie lokal.
   * - pcap_restart
     - --
     - --
     - Löscht alle Mitschnitte und startet die Netzwerkverkehrsaufzeichnung neu.
   * - pcap_stop
     - --
     - --
     - Stoppt die Netzwerkverkehrsaufzeichnung.

Beispiele
=========

Ereignis-Item mit einem Datenfeld als Kind-Item::

    DeviceState:
        event_2n: DeviceState

        device_state:
            type: str
            event_data_2n: state

Ändert sich der Gerätezustand (z. B. nach einem Neustart), wird
``DeviceState.device_state`` z. B. auf ``startup`` gesetzt.

Befehls-Item mit ``execute``-Kind-Item::

    system_info:
        type: str
        command_2n: system_info

        execute:
            type: bool
            command_2n: execute
            enforce_updates: 'true'

Wird ``system_info.execute`` auf ``True`` gesetzt, wird der Befehl ausgeführt und das Ergebnis in
``system_info`` geschrieben, z. B.::

    {
        "success" : true,
        "result" : {
            "variant" : "2N Helios IP Vario",
            "serialNumber" : "08-1240-1138",
            "hwVersion" : "535v1",
            "swVersion" : "2.10.0.19.2",
            "buildType" : "beta",
            "deviceName" : "2N Helios IP Vario"
        }
    }

Eine vollständige Item-Vorlage mit allen Ereignissen und Befehlen liefert die Datei
``example/2n_intercom.yaml`` im Plugin-Verzeichnis. Sie kann als Ganzes oder in Teilen (jeweils
vollständige Ereignis- bzw. Befehls-Teilbäume) in das Items-Verzeichnis kopiert werden.
