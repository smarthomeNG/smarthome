
Steuerung des dyn. Zenith-Icons
===============================

Ziel
----

Ziel ist, das dynamische Icon icon.zenith in der smartVISU mit dem
richtigen aktuellen Sonnenstand darzustellen.

Logik
-----

Berechnungen für icon.zenith:

/usr/local/smarthome/logics/zenith.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   #!/usr/bin/env python3
   # zenith.py

   now = datetime.datetime.utcnow().hour * 60 + datetime.datetime.utcnow().minute
   sunrise = sh.sun.rise().hour * 60 + sh.sun.rise().minute
   sunset = sh.sun.set().hour * 60 + sh.sun.set().minute

   icon = int(round(255 * ((now - sunrise) / (sunset - sunrise)),0))
   sh.weather.sun.icon(icon)

/usr/local/smarthome/etc/logic.yaml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   zenith:
       filename: zenith.py
       cycle: 300


smartVISU
---------

Einbindung in der smartVISU:

.. code-block:: twig

    {% import "icon.html" as icon %}
    {{ icon.zenith('weather.sun.icon', '', 'weather.sun.icon') }}

