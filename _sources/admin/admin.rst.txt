.. index:: Admin GUI
.. index:: Administrations-Interface
.. index:: Webinterfaces; Administrations GUI
.. index:: Webinterfaces; Administrations-Interface

.. role:: redsup
.. role:: bluesup
.. role:: darkbluesup
.. role:: greensup
.. role:: blacksup


Administrations-Interface :greensup:`Update`
============================================

Seit SmartHomeNG v1.6 steht ein graphisches Administrations-Interface zur Verfügung, welches die vollständige
Administration von SmartHomeNG ermöglicht.

Das Administrations-Interface wird durch folgenden Aufruf gestartet:

.. code::

   http://<ip Ihres SmartHomeNG-Servers>:8383/admin


Über die Systemkonfiguration kann eingestellt werden, dass ```http://<ip Ihres SmartHomeNG-Servers>:8383```
automatisch auf das Administrations-Interface verweist.


Falls in der Konfiguration für das http Modul eine User/Passwort Kombination konfiguriert wurde, wird diese benötigt um
auf das Admin-Interface zuzugreifen:


.. image:: assets/login.jpg
   :class: screenshot


Ansonsten wird direkt die Übersichtsseite der Systemeigenschaften angezeigt.

Wenn eine Anmeldung notwendig ist, so ist dieses nicht auf die Session beschränkt. Ein Beenden des Browsers meldet den
Anwender nicht ab. Hierzu muss der Abmelde-Button in der Navigation genutzt werden. Eine automatische Abmeldung erfolgt
nur, wenn das im Browser gespeicherte Token abläuft. Die Lebensdauer des Token ist in der Systemkonfiguration im Tab
**Admin Modul** konfigurierbar.



.. toctree::
   :maxdepth: 4
   :hidden:
   :titlesonly:

   system
   dienste
   items
   logiken
   scheduler
   plugins
   scenes
   threads
   logs


