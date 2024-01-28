.. index:: Plugins; oppo
.. index:: oppo

====
oppo
====

.. image:: webif/static/img/plugin_logo.svg
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: center

Steuerung eines Oppo UHD Gerätes über TCP/IP oder RS232 Schnittstelle.

Das Plugin unterstützt folgende Modelle

-   UDP-203


Konfiguration
=============

Diese Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/oppo` beschrieben.


plugin.yaml
-----------

.. code-block:: yaml

    # etc/plugin.yaml
    oppo:
        plugin_name: oppo
        model: UDP-203
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

- einzelne Struct-Teile wie oppo.info, oppo.general, oppo.tuner, oppo.zone1, oppo.zone2, oppo.zone3
- oppo.ALL: Hierbei werden sämtliche Kommandos eingebunden, die vom Plugin vorgesehen sind
- oppo.UDP-203 bzw. die anderen unterstützten Modelle, um nur die relevanten Items einzubinden
- oppo.MODEL: Es wird automatisch der Itembaum für das Modell geladen, das im plugin.yaml angegeben ist.

Sollte das selbst verwendete Modell nicht im Plugin vorhanden sein, kann der Plugin Maintainer
angeschrieben werden, um das Modell aufzunehmen.

.. code-block:: yaml

    # items/my.yaml
    Denon:
        type: foo
        struct: oppo.MODEL


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
