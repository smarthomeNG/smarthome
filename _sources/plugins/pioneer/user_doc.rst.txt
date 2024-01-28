.. index:: Plugins; pioneer
.. index:: pioneer

=======
pioneer
=======

.. image:: webif/static/img/plugin_logo.svg
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: center

Steuerung eines Pioneer AV Gerätes über TCP/IP oder RS232 Schnittstelle.

Das Plugin unterstützt eine Vielzahl von Pioneer Verstärkern. Folgende Modelle wurden
konkret berücksichtigt, andere Modelle funktionieren aber mit hoher Wahrscheinlichkeit
auch.

-   SC-LX87
-   SC-LX77
-   SC-LX57
-   SC-2023
-   SC-1223
-   VSX-1123
-   VSX-923


Konfiguration
=============

Diese Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/pioneer` beschrieben.


plugin.yaml
-----------

.. code-block:: yaml

    # etc/plugin.yaml
    pioneer:
        plugin_name: pioneer
        model: VSX-923
        timeout: 3
        terminator: "\r"
        binary: false
        baudrate: 9600
        bytesize: 8
        parity: N
        stopbits: 1
        autoreconnect: true
        autoconnect: true
        connect_retries: 5
        connect_cycle: 3
        host: 192.168.0.111
        port: 8102
        serialport: /dev/ttyUSB0
        conn_type: serial_async
        command_class: SDPCommandParseStr


Struct Vorlagen
===============

Der Itembaum sollte jedenfalls über die structs Funktion eingebunden werden. Hierzu gibt es vier
Varianten, wobei die letzte die optimale Lösung darstellt:

- einzelne Struct-Teile wie pioneer.info, pioneer.general, pioneer.tuner, pioneer.zone1, pioneer.zone2, pioneer.zone3
- pioneer.ALL: Hierbei werden sämtliche Kommandos eingebunden, die vom Plugin vorgesehen sind
- pioneer.AVR-X6300H bzw. die anderen unterstützten Modelle, um nur die relevanten Items einzubinden
- pioneer.MODEL: Es wird automatisch der Itembaum für das Modell geladen, das im plugin.yaml angegeben ist.

Sollte das selbst verwendete Modell nicht im Plugin vorhanden sein, kann der Plugin Maintainer
angeschrieben werden, um das Modell aufzunehmen.

.. code-block:: yaml

    # items/my.yaml
    pioneer:
        type: foo
        struct: pioneer.MODEL


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
