.. index:: admin
.. index:: modules; admin

.. role:: redsup
.. role:: bluesup

##########################
Module admin :redsup:`neu`
##########################

Dieses Modul erlaubt es SmartHomeNG über einen Webbrowser zu konfigurieren. Voraussetzung ist, dass auch das Modul
http geladen und konfiguriert ist.


.. index:: Konfigurationsdateien; /etc/module.yaml

Konfiguration
=============

--------------------------
Datei *../etc/module.yaml*
--------------------------

.. code-block:: yaml
   :caption: ../etc/module.yaml

   # etc/module.yaml
   admin:
       module_name: admin
   #    login_expiration: 168
   #    pypi_timeout: 5
   #    itemtree_fullpath: True
   #    itemtree_searchstart: 3


.. note::

    Die Konfigurationsparameter des admin Modules, die in dieser Datei konfiguriert werden, können auch über das graphische
    Administrations-Interface geändert werden.


+-------------------------+------------------------------------------------------------------------------------------------------+
| Parameter               | Bemerkung                                                                                            |
+=========================+======================================================================================================+
| login_expiration        | **Optional**: Gültigkeitsdauer des Tokens nach einem Login in Stunden (Nachkommastellen können       |
|                         | angegeben werden). Standard ist 168 -> eine Woche                                                    |
+-------------------------+------------------------------------------------------------------------------------------------------+
| pypi_timeout            | **Optional**: Anzahl Sekunden die auf eine Antwort von pypi.org gewartet wird.                       |
+-------------------------+------------------------------------------------------------------------------------------------------+
| itemtree_fullpath       | **Optional**: Falls dieser Parameter auf **True** gesetzt wird, werden auf der Item Seite im Tree    |
|                         | Items mit vollem Pfad angezeigt, fallse der Wert auf **False** gesetzt wird, wird die Kurzform       |
|                         | verwendet.                                                                                           |
+-------------------------+------------------------------------------------------------------------------------------------------+
| itemtree_searchstart    | **Optional**: Anzahl Zeichen die eingegeben sein muss, damit die Suche im Itemtree startet.          |
|                         | Standardmäßig wird nach der Eingabe des dritten Zeichens mit der Suche begonnen.                     |
+-------------------------+------------------------------------------------------------------------------------------------------+

