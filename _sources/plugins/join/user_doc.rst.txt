.. index:: Plugins; join
.. index:: join

====
join
====

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Dieses Plugin erlaubt das Senden von Kommandos an das Smartphone mittels
`Join API <https://joaoapps.com/join/api/>`_

Konfiguration
=============

.. important::

   Die Informationen zur Konfiguration des Plugins sind unter :doc:``/plugins_doc/config/join`` beschrieben.

plugin.yaml
-----------

.. code-block:: yaml

   join:
       plugin_name: join
       device_id: <your deviceid>
       api_key: <your apikey>


Pluginfunktionen
================

send()
------

send(title=None, text=None, icon=None, find=None, smallicon=None, device_id=None, device_ids=None, device_names=None, url=None, image=None, sound=None, group=None, clipboard=None, file=None, callnumber=None, smsnumber=None, smstext=None, mmsfile=None, wallpaper=None, lockWallpaper=None, interruptionFilter=None, mediaVolume=None, ringVolume=None, alarmVolume=None)

Bezüglich einer genauen Beschreibung der einzelnen Variablen ist die Dokumentation zur
`Join API <https://joaoapps.com/join/api/>`_ heranzuziehen.

get_devices()
-------------

Gibt ein Array aller Geräte, die für die Join API registriert sind, zurück.

Logikbeispiele
--------------

.. code-block:: python

   if (sh.your.item() == 1):
       sh.join.send(smsnumber="0123456789", smstext="Hello World") # Senden einer SMS ans Zielgerät

   if (sh.your.item() == 1):
       sh.join.send(title="01234567892", text="Hello World") # Schicken einer Benachrichtung ans Mobilgerät

   if (sh.your.item() == 1):
       sh.join.send(find="true") # Finden von Geräten

Web Interface
=============

Das Plugin stellt kein Web Interface zur Verfügung.
