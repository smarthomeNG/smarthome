.. index:: Plugins; denon
.. index:: denon

=====
denon
=====

.. image:: webif/static/img/plugin_logo.svg
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: center

Steuerung eines Denon AV Gerätes über TCP/IP oder RS232 Schnittstelle.

Das Plugin unterstützt eine Vielzahl von Denon Verstärkern. Folgende Modelle wurden
konkret berücksichtigt, andere Modelle funktionieren aber mit hoher Wahrscheinlichkeit
auch.

-   AVR-X6300H
-   AVR-X4300H
-   AVR-X3300W
-   AVR-X2300W
-   AVR-X1300W


Konfiguration
=============

Diese Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/denon` beschrieben.


plugin.yaml
-----------

.. code-block:: yaml

    # etc/plugin.yaml
    denon:
        plugin_name: denon
        model: AVR-X6300H
        timeout: 3
        terminator: "\r"
        binary: false
        autoreconnect: true
        autoconnect: true
        connect_retries: 5
        connect_cycle: 3
        host: 192.168.0.111
        port: 23
        serialport: /dev/ttyUSB0
        conn_type: serial_async
        command_class: SDPCommandParseStr


Struct Vorlagen
===============

Der Itembaum sollte jedenfalls über die structs Funktion eingebunden werden. Hierzu gibt es vier
Varianten, wobei die letzte die optimale Lösung darstellt:

- einzelne Struct-Teile wie denon.info, denon.general, denon.tuner, denon.zone1, denon.zone2, denon.zone3
- denon.ALL: Hierbei werden sämtliche Kommandos eingebunden, die vom Plugin vorgesehen sind
- denon.AVR-X6300H bzw. die anderen unterstützten Modelle, um nur die relevanten Items einzubinden
- denon.MODEL: Es wird automatisch der Itembaum für das Modell geladen, das im plugin.yaml angegeben ist.

Sollte das selbst verwendete Modell nicht im Plugin vorhanden sein, kann der Plugin Maintainer
angeschrieben werden, um das Modell aufzunehmen.

.. code-block:: yaml

    # items/my.yaml
    Denon:
        type: foo
        struct: denon.MODEL


Kommandos
=========

Die RS232 oder IP-Befehle des Geräts sind in der Datei `commands.py` hinterlegt. Etwaige
Anpassungen und Ergänzungen sollten als Pull Request oder durch Rücksprache mit dem Maintainer
direkt ins Plugin einfließen, damit diese auch von anderen Nutzer:innen eingesetzt werden können.

Über die Datei `datatypes.py` sowie die Lookup Tabellen im `commandy.py` File sind
bereits sämtliche nötige Konvertierungen abgedeckt. So werden
beispielsweise Lautstärkeangaben mit Kommawerten oder boolsche Werte automatisch
korrekt interpretiert.


Web Interface
=============

Aktuell ist kein Web Interface integriert. In naher Zukunft soll dies über die
SmartDevicePlugin Bibliothek automatisch zur Verfügung gestellt werden.
