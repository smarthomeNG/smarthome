
.. index:: Plugins; zwave (Z-Wave Unterstützung)
.. index:: zwave

=====
zwave
=====

Z-Wave Unterstützung über das Python-Paket ``python-openzwave``.

.. important::

   Dieses Plugin ist als **veraltet** (``deprecated``) markiert und wird mit dem nächsten Release entfernt.

   Das benötigte Paket ``python-openzwave`` wird nicht mehr gepflegt. Die letzte Version (0.4.19, März 2019) ist
   nicht mit Python 3.9 oder neuer kompatibel. Das Plugin ist deshalb auf Python 3.8 beschränkt
   (``py_maxversion``). Damit ist die Nutzung dieses Pakets mit dem aktuellen Core (benötigt Python 3.10) unmöglich.

Alternative: zwave-js über MQTT
===============================

Als Ersatz kann `zwave-js-ui <https://github.com/zwave-js/zwave-js-ui>`_ (bzw. `zwave-js <https://github.com/zwave-js>`_)
zusammen mit dem :doc:`mqtt Plugin </plugins_doc/config/mqtt>` verwendet werden. zwave-js-ui veröffentlicht die
Z-Wave Werte über MQTT, die Items binden diese über ``mqtt_topic_in`` und ``mqtt_topic_out`` an.

Beispiel für eine schaltbare Steckdose mit Leistungsmessung (Node-ID 2) von ThomasCR:

.. code-block:: yaml

    zwSteckdose1:
        name: Esszimmer
        type: bool
        on_change: .mqtt_out = value if not sh..self.changed_by() == "On_Change:{}".format(sh..mqtt_in.property.path) else None
        mqtt_in:
            type: dict
            visu_acl: ro
            mqtt_topic_in: zwave/2/37/0/currentValue
            on_change: .. = value['value']
        mqtt_out:
            type: bool
            visu_acl: ro
            mqtt_topic_out: zwave/2/37/0/targetValue/set
        watt:
            type: num
            visu_acl: ro
        watt_dict:
            type: dict
            visu_acl: ro
            mqtt_topic_in: zwave/2/49/0/Power
            on_change: ..watt = value['value']

Die Topics hängen von den Einstellungen in zwave-js-ui ab. Zum Auffinden der richtigen Topics eignet sich
`MQTT Explorer <http://mqtt-explorer.com/>`_.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/zwave` beschrieben.
