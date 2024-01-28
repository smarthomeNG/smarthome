.. index:: Plugins; epson
.. index:: epson

=====
epson
=====

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 768px
   :height: 249px
   :scale: 25 %
   :align: center

Steuerung eines Epson Projektors über RS232 Schnittstelle. Theoretisch klappt auch
die Verbindung via TCP - wurde aber nicht getestet!

Das Plugin unterstützt eine Reihe von Epson Projektoren. Folgendes Modell wurde
konkret berücksichtigt, andere Modelle funktionieren aber mit hoher Wahrscheinlichkeit
auch.

-   TW-5000


Konfiguration
=============

Diese Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/epson` beschrieben.


plugin.yaml
-----------

.. code-block:: yaml

    # etc/plugin.yaml
    epson:
        plugin_name: epson
        model: TW-5000
        timeout: 3
        terminator: "\r"
        binary: false
        autoreconnect: true
        autoconnect: true
        connect_retries: 5
        connect_cycle: 3
        serialport: /dev/ttyUSB0
        conn_type: serial_async
        command_class: SDPCommandParseStr


Struct Vorlagen
===============

Der Itembaum sollte jedenfalls über die structs Funktion eingebunden werden. Hierzu gibt es vier
Varianten, wobei die letzte die optimale Lösung darstellt:

- einzelne Struct-Teile wie epson.power
- epson.ALL: Hierbei werden sämtliche Kommandos eingebunden, die vom Plugin vorgesehen sind
- epson.TW-5000 bzw. die anderen unterstützten Modelle, um nur die relevanten Items einzubinden
- epson.MODEL: Es wird automatisch der Itembaum für das Modell geladen, das im plugin.yaml angegeben ist.

Sollte das selbst verwendete Modell nicht im Plugin vorhanden sein, kann der Plugin Maintainer
angeschrieben werden, um das Modell aufzunehmen.

.. code-block:: yaml

    # items/my.yaml
    Epson:
        type: foo
        struct: epson.MODEL


Kommandos
=========

Die RS232 oder IP-Befehle des Geräts sind in der Datei `commands.py` hinterlegt. Etwaige
Anpassungen und Ergänzungen sollten als Pull Request oder durch Rücksprache mit dem Maintainer
direkt ins Plugin einfließen, damit diese auch von anderen Nutzer:innen eingesetzt werden können.


Web Interface
=============

Aktuell ist kein Web Interface integriert. In naher Zukunft soll dies über die
SmartDevicePlugin Bibliothek automatisch zur Verfügung gestellt werden.
