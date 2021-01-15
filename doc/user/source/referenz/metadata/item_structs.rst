
.. role:: redsup
.. role:: bluesup

.. index:: item_structs; Plugin Metadaten
.. index:: structs; Plugin Metadaten
.. index:: Plugin Metadaten; item_structs
.. index:: Plugin Metadaten; structs

item_structs
------------

Der Abschnitt ``item_structs:`` erlaubt die Definition von Structure Templates, also von Sub-Trees von Items,
die an verschiedenen Stellen in den Item Tree eingefügt werden können.

Definitionen von ``item_structs:`` haben das folgende Format:

.. code:: yaml

    item_structs:
        struct1:

            item1:
                type: int
            item2:
                item3:
                    name: 'my item 3'
                    type: str
                    plg_attr1: 'plugin specific'
                item4:
                    type: bool
                    initial_value: True

        struct2:

            ... (sub-tree with item definitions)


Zur Konfiguration von SmartHomeNG werden diese structs durch die Angabe einer Referenz in den Item Tree eingefügt.
Das erfolgt in den Konfigurationsdateien für Items im Verzeichnis ``../items``:

.. code:: yaml

   item_name_of_struct:
       struct: <plugin name>.<struct name>



Falls ``struct1`` des oben angegebenen Beispiels in einem Plugin mit dem Namen ``example_plugin`` definiert wurde,
sieht die Konfiguration um die Structure einzufügen folgendermaßen aus:

.. code:: yaml

   item_name_of_struct:
       struct: example_plugin.struct1


Geschachtelte Structuren
~~~~~~~~~~~~~~~~~~~~~~~~

Beginnend mit SmartHomeNG v1.7 können Struktur Definitionen ineinander geschatelt werden.

Wie Items die eine Struktur mit dem ``struct`` Attribut referenzieren, kann auch eine Struktur Definition eine
eine andere Struktur referenzieren. SmartHomeNG löst alle Struktur Referenzen in Strukturen auf, bevor der
Item Tree geladen wird.

.. note::

   Bitte beachten: Wenn Sub-Struktur Referenzen aufgelöst werden, gibt es zwei Unterschiede in der Art wie
   Item Definitionen geladen werden. Diese Unterschiede werden nur sichtbar, falls Strukturen Item Attribute
   redefinieren.


Redefininieren von Attributen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Wenn Items definiert werden ist es möglich, das selbe Attribut eines Items in mehreren YAML Dateien zu definieren.
Beim Einlesen der Item Definitionen "gewinnt" die Attribut Definition die zuletzt eingelesen wurde.

In struct/sub-struct Definitionen hingegen, "gewinnt" die erste Definition eines Attributes.

Beim auflösen von sub-structs soll normalerweise der übergeordnete Level gewinnen. Das ermöglicht es zm Beispiel
in einer Item Definition eine Attribut Definition zu überschreiben, welche in einer Structure bereits festgelegt wurde.
Damit das so erfolgt, muss das betreffende Attribut im Item in der Reihenfolge vor dem ``struct`` Attribut definiert
werden. Falls das Attribut im Item erst nach dem ``struct`` Attribut definiert wird, "gewinnt" die Definition in der
Structure. Dieses Verhalten gilt analog beim verschachteln von Strukturen.


Redefininieren von list-Attributen
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Wenn Attribute die redefiniert werden Listen sind, findet kein überschreiben der Definition statt. Stattdessen werden
die Listen aneinander gehängt. Das geschieht in der Reihenfolge in der die Attribut Definitionen eingelesen werden.


Definitions for multi-instance plugins
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wenn ein Plugin Multi-Instance fähig ist, ist es wahrscheinlich, dass Item Strukturen Instanz-spezifische Attribute
enthalten. In Item Definitionen wird bei solchen Attributen `'@<instance-name>`` an den Attribut Namen angefügt.

Um in Strukturen zu kennzeichnen, welche Attribute einen Instanz Namen hinzugefügt bekommen sollen, wird bei diesen
Attributen der konstante String ``@instance`` hinzugefügt. Dieser String wird beim Aufbau des Item Trees durch den
realen Instanz Namen ersetzt.

.. code:: yaml

    item_structs:
        struct1:

            item1:
                type: int
            item2:
                item3:
                    name: 'my item 3'
                    type: str
                    plg_attr1@instance: 'plugin specific'
                item4:
                    type: bool
                    initial_value: True


In der Item Konfiguration in den Dateien im Verzeichnis ``../items`` wird der Instanz Name der Struktur mitgegeben.
Das sieht z.B. folgendermaßen aus:

.. code:: yaml

   item_name_of_struct:
       struct: example_plugin.struct1
       instance: plg_instance


Im geladenen Item (bei Verwendung der Admin GUI), wird ``item3`` dann ein Attribut haben, das
``plg_attr1@plg_instance`` benannt ist.


Plugins ohne item-structs
~~~~~~~~~~~~~~~~~~~~~~~~~

Falls ein Plugin keine Item Attribute hat, wird das durch den folgenden Eintrag in der
Datei ``plugin.yaml`` angezeigt:

.. code:: yaml

    item_structs: NONE

.. hint::

    Bitte beachten, dass hier ``NONE`` vollständig in Großbuchstaben geschrieben werden muss.

