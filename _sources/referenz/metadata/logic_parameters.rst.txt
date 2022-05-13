
.. role:: redsup
.. role:: bluesup

.. index:: logic_parameters; Plugin Metadaten
.. index:: Plugin Metadaten; logic_parameters

logic_parameters
----------------

Die Daten der Logic Parameter werden für die Generierung der Dokumentation verwendet. Außerdem werden diese
Parameter für die Konfiguration von Logiken in der Admin GUI verwendet. Falls die konfigurierten Daten nicht gültig
sind, werden Warnungen in das Logfile von SmartHomeNG geschrieben.

Der Abschnitt ``logic_parameters:`` enthält einen Abschnitt für jeden Parameter der für eine Logik verwendet
werden kann. Der Name dieses Unter-Abschnitts ist der Name des Parameters der Logik.

.. code:: yaml

    logic_parameters:
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


.. include:: /referenz/metadata/parameter_keys.rst


Plugins ohne Logic Parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Falls ein Plugin keine Logik Parameter hat, wird das durch den folgenden Eintrag in der Datei ``plugin.yaml``
angezeigt:

.. code:: yaml

    logic_parameters: NONE

.. hint::

    Bitte beachten, dass hier ``NONE`` vollständig in Großbuchstaben geschrieben werden muss.

