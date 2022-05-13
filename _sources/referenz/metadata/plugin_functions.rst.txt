
.. role:: redsup
.. role:: bluesup

.. index:: plugin_functions; Plugin Metadaten
.. index:: Plugin Metadaten; plugin_functions

plugin_functions
----------------

Dieser Abschnitt beschreibt die öffentlichen Funktionen, die in einem Plugin implementiert sind.

``plugin_functions:`` enthält einen Abschnitt für jede implementierte Funktion, die öffenlich (also von außerhalb
des Plugins aufrufbar) sein soll. Der Name des Abschnitts ist der Name der Funktion.

Jede Funktionsdefinition enhält einen Abschnitt ``parameters:``, welcher die Parameter der Funktion im Detail
beschreibt.

Die Definitionen im Abschnitt ``plugin_functions:`` werden für die Erstellung der Dokumentation genutzt. In der
Zukunft sollen die Definitionen für die Konfiguration in der Admin GUI genutzt werden.

.. code:: yaml

    plugin_functions:
        example_function:
            type: str
            description:
                de: 'Deutsche Beschreibung der Funktion'
                en: 'English description of the function'
            parameters:
                param1:
                    type: int
                    default: 1234
                    description:
                        de: 'Deutsche Beschreibung des Funktionsparameters'
                        en: 'English description of the function's parameter'
                    valid_list:
                      - 1234
                      - 2222
                      - 4321

                param2:
                    type: ...


.. include:: /referenz/metadata/parameter_keys.rst


Plugins ohne Plugin Funktionen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Falls ein Plugin keine öffentlichen Plugin Funktionen definiert, wird das durch den folgenden Eintrag in
der Datei ``plugin.yaml`` angezeigt:

.. code:: yaml

    plugin_functions: NONE

.. hint::

    Bitte beachten, dass hier ``NONE`` vollständig in Großbuchstaben geschrieben werden muss.


Funktionen ohne Parameter
~~~~~~~~~~~~~~~~~~~~~~~~~

Falls eine Plugin-Funktion keine Parameter hat, darf der Eintrag ``parameters:`` nicht in die plugin.yaml aufgenommen werden. Er entfällt ohne weitere Angaben.


Aufruf von Funktionen
~~~~~~~~~~~~~~~~~~~~~

Wenn Plugin-Funktionen in einer Logik verwendet werden sollen, kann dies in der folgenden Form erfolgen: 

``result = sh.plugins.return_plugin("<Plugin-Name>").<Funktionsname>(<Argumente>)``
