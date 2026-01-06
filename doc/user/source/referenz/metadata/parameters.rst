
.. role:: redsup
.. role:: bluesup

.. index:: Parameter; Modul Metadaten
.. index:: Modul Metadaten; Parameter
.. index:: Parameter; Plugin Metadaten
.. index:: Plugin Metadaten; Parameter

parameters
----------

Parameter-Metadaten werden benutzt um die Gültigkeit von Parametern zu prüfen, die im Verzeichnis ``../etc``
konfiguriert wurden. Falls für einen Parameter ein ungültiger Wert konfiguriert wurde, wird eine Warnung im Logfile
von SmartHomeNG eingetragen.

Wenn ein gültiger Wert konfiguriert wurde, wird der Parameter an das Plugin/Modul übergeben, und zwar als der Datentyp,
der in den Metadaten definiert wurde.

Der ``parameters:`` Abschnitt hat für jeden definierten Parameter einen Unter-Abschnitt, der den Parameter genauer
beschreibt. Der Schlüssel des Unter-Abschnitts ist der Name des Parameters. Parameter Namen sollten keine
Großbuchstaben und Sonderzeichen enthalten. Sie dürfen nicht mit einer Ziffer beginnen.

Die Definitionen im Abschnitt ``parameters:``  werden für die Gültigkeitsprüfung der konfigurierten Werte, sowie
zur Dokumentation und zur Konfiguration in der Admin GUI benutzt.

.. code:: yaml

    parameters:
        param1:
            type: int
            default: 1234
            description:
                de: 'Deutsche Beschreibung'
                en: 'English description'
            valid_list:
              - 1234
              - 2222
              - 4321

        param2:
            type: ...


.. hint::

    Der Parameter ``webif_pagelength`` wird jedem Plugin automatisch hinzugefügt und sollte
    daher NICHT manuell im plugin.yaml File hinterlegt werden.

.. include:: /referenz/metadata/parameter_keys.rst


Plugins/Module ohne Parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Falls ein Plugin oder Modul keine Parameter hat, wird das durch den folgenden Eintrag in der
Datei ``plugin.yaml`` angezeigt:

.. code:: yaml

    parameters: NONE

.. hint::

    Bitte beachten, dass hier ``NONE`` vollständig in Großbuchstaben geschrieben werden muss.
