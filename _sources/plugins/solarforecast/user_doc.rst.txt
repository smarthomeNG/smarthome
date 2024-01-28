.. index:: Plugins; solarforecast (Solarforecast REST API Unterstützung)
.. index:: solarforecast

=============
solarforecast
=============

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Dieses Plugin unterstützt Solare.forecast Vorhersagen von Solaretrag (Energieertrag).

Für weitere Informationen empfiehlt sich die Lektüre der offiziellen
`Solar.forecast API Dokumentation <https://doc.forecast.solar/doku.php?id=start>`_

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/solarforecast` beschrieben.

Requirements
============

The plugin does not need a license key in public mode. An API key can be obtained, which is optional.


Beispiele
=========

Beispiel für jeweils zwei Items mit vorhergesagtem Energieertrag für heute und morgen.

.. code:: yaml

    solarforecast:

        today:
            type: num
            visu_acl: ro
            name: Forecast energy for today in Wh
            solarforecast_attribute: energy_today

            date:
                type: str
                visu_acl: ro
                solarforecast_attribute: date_today

        tomorrow:
            type: num
            visu_acl: ro
            name: Forecast energy for tomorrow in Wh
            solarforecast_attribute: energy_tomorrow

            date:
                type: str
                visu_acl: ro
                solarforecast_attribute: date_tomorrow

Web Interface
=============

Das solarforecast Plugin verfügt über ein Webinterface.



Aufruf des Webinterfaces
------------------------

Das Plugin kann aus dem Admin Interface aufgerufen werden. Dazu auf der Seite Plugins in der entsprechenden
Zeile das Icon in der Spalte **Web Interface** anklicken.

Außerdem kann das Webinterface direkt über ``http://smarthome.local:8383/solarforecast`` aufgerufen werden.


