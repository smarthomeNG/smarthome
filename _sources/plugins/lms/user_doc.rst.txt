.. index:: Plugins; lms
.. index:: lms

===
lms
===

.. image:: webif/static/img/plugin_logo.svg
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: center

Steuerung des Logitech Mediaservers über die CLI Schnittstelle.


Konfiguration
=============

Diese Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/lms` beschrieben. `recursive_custom` sollte jedenfalls aktiv sein,
wenn man den Itembaum nicht manuell aufbauen will, sondern structs nutzt (siehe weiter unten).


plugin.yaml
-----------

.. code-block:: yaml

    # etc/plugin.yaml
    lms:
        plugin_name: lms
        timeout: 3
        terminator: "\r"
        binary: false
        autoreconnect: true
        autoconnect: true
        connect_retries: 5
        connect_cycle: 3
        message_timeout: 5
        message_retries: 3
        host: 192.168.0.111
        port: 9090
        web_port: 9000
        recursive_custom: true
        conn_type: net_tcp_client
        command_class: SDPCommandParseStr


Struct Vorlagen
===============

Der Itembaum sollte jedenfalls über die structs Funktion eingebunden werden. Mittels `ALL`
werden die Ebenen Server, Database und Player unter dem selben Hauptitem angelegt, was aber
nur in den seltensten Fällen Sinn machen dürfte. Stattdessen sollte ein einzigartiges Item für
`lms.server` und `lms.database` angelegt werden. Das struct `lms.player` wird dann
pro Abspielgerät genutzt, wobei hier wichtig ist, mittels `lms.sqb_custom1` die MAC Adresse
des Players mit anzugeben.

.. code-block:: yaml

    # items/my.yaml
    squeezebox:
      struct:
        - sdp_squeezebox.database
        - sdp_squeezebox.server

    squeezebox_player1:
        sqb_custom1: <MAC Adresse>

        struct: sdp_squeezebox.player

    squeezebox_player2:
        sqb_custom1: <MAC Adresse>

        struct: sdp_squeezebox.player


Kommandos
=========

Ein Großteil der CLI unterstützten Befehle ist in der `commands.py` und somit in den structs
abgedeckt. Bei Bedarf können weitere Befehle hinzugefügt werden, wobei das Ergebnis via
Pull Request oder über den Plugin Maintainer allen zur Verfügung gestellt werden sollte.


Web Interface
=============

Aktuell ist kein Web Interface integriert. In naher Zukunft soll dies über die
SmartDevicePlugin Bibliothek automatisch zur Verfügung gestellt werden.
