
.. index:: Plugins; alexarc4shng (Remote Control for Alexa devices)
.. index:: Alexa; alexarc4shng Plugin


============
alexarc4shng
============

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left


Plugin zur Steuerung von Amazon Echo Geräten Zugriff via Web-Browser API und Cookie.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/alexarc4shng` beschrieben.


Web Interface
=============

Das AlexaRc4shNG Plugin verfügt über ein Webinterface.Hier werden die Zugangsdaten zur Amazon-Web-Api (Cookie) gepflegt.
Es können neue Kommandos erstellt werden

.. important::

   Das Webinterface des Plugins kann mit SmartHomeNG v1.5.2 und davor **nicht** genutzt werden.
   Es wird dann nicht geladen. Diese Einschränkung gilt nur für das Webinterface. Ansonsten gilt
   für das Plugin die in den Metadaten angegebene minimale SmartHomeNG Version.


Aufruf des Webinterfaces
------------------------

Das Plugin kann aus dem backend aufgerufen werden. Dazu auf der Seite Plugins in der entsprechenden
Zeile das Icon in der Spalte **Web Interface** anklicken.

Außerdem kann das Webinterface direkt über ``http://smarthome.local:8383/alexarc4shng`` aufgerufen werden.


Beispiele
---------

Folgende Informationen können im Webinterface angezeigt werden:

Oben rechts werden allgemeine Parameter zum Plugin angezeigt.

Im ersten Tab kann das Cookie File gespeichert werden - in die Textarea via Cut & Paste einfügen und speichern:

.. image:: assets/webif1.jpg
   :class: screenshot

Im zweiten Tab werden die verfügbaren Geräte angezeigt - Durch click auf ein Gerät wird dieses selektiert und steht für Tests zur Verfügung:

.. image:: assets/webif2.jpg
   :class: screenshot

Im dritten Tab werden die Commandlets verwaltet - mit Click auf die Liste der Commandlets wird dieses ins WebIF geladen:

.. image:: assets/webif3.jpg
   :class: screenshot


