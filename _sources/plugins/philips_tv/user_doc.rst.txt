.. index:: Plugins; philips_tv
.. index:: philips_tv

==========
philips_tv
==========

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Allgemein
=========

SmarthomeNG plugin mit Unterstützung für Philips Smart TVs mit OAuth Identifizierung.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/philips_tv` beschrieben.
Die Kopplung zwischen Plugin und TV erfolgt über das OAuth Verfahren. Das Webinterface führt Schritt für Schritt durch den Kopplungsprozess.

Requirements
=============
- requests

Supported Hardware
==================
Philips Smart TV mit OAuth Identifizierung


Web Interface
=============

Das philips_tv Plugin verfügt über ein Webinterface, um  für Philips TV das OAuth2 Authentifizierungsverfahren direkt durchzuführen
und die Anmeldedaten (user + password) persistent direkt in die Konfiguration (plugin.yaml) zu übernehmen.


Aufruf des Webinterfaces
------------------------

Das Plugin kann aus dem Admin Interface aufgerufen werden. Dazu auf der Seite Plugins in der entsprechenden
Zeile das Icon in der Spalte **Web Interface** anklicken.

Außerdem kann das Webinterface direkt über ``http://smarthome.local:8383/philips_tv`` aufgerufen werden.


Beispiele
---------

Folgende Informationen können im Webinterface angezeigt werden:

Im ersten Tab Philips OAuth2 findet sich direkt die Schritt für Schritt Anleitung zur OAuth2 Authentifizierung. 

Beispiele
=========


Beispiel für eine Philips TV Item Konfiguration:

.. code:: yaml

    Philips:
        volume:
            type: num
            philips_tv_rx_key: VOLUME
            visu_acl: ro
            initial_value: -1
        mute:
            type: bool
            initial_value: False
            philips_tv_rx_key: MUTE
            philips_tv_tx_key: MUTE
            visu_acl: rw
        ambilightstate:
            type: bool
            initial_value: False
            philips_tv_rx_key: AMBILIGHT_STATE
            philips_tv_tx_key: AMBILIGHT_STATE
            visu_acl: rw
            enforce_updates: True
        powerstate:
            type: bool
            initial_value: False
            philips_tv_rx_key: POWERSTATE
            visu_acl: ro
        powerstate_info:
            type: str
            initial_value: ''
            philips_tv_rx_key: POWERSTATEINFO
            visu_acl: ro
        channel:
            type: str
            initial_value: ''
            philips_tv_rx_key: CHANNEL
            visu_acl: ro
        error:
            type: str
            initial_value: '-'
            philips_tv_rx_key: ERROR
            visu_acl: ro
        power_off:
            type: bool
            initial_value: False
            philips_tv_tx_key: POWEROFF
            visu_acl: rw
            autotimer: 3 = False
            enforce_updates: True
        ambilight:
            name: Ambiant Light
            hue:
                type: list
                initial_value: [0,0,0]
                visu_acl: rw
                philips_tv_tx_key: AMBILIGHT_HUE
                philips_tv_rx_key: AMBILIGHT_HUE
                enforce_updates: True
