
.. index:: structs

.. role:: bluesup
.. role:: redsup


=========================
structs (Item Strukturen)
=========================


Überblick
=========

Seit SmartHomeNG v1.6 werden Item-Struktur-Templates unterstützt, mit denen sich wiederholende Itemstrukturen einfach realisieren lassen.
Die Anwendung erfolgt mit Hilfe des **struct**-Attributes mit dem jeweiligen Namen des Item-Templates. Dies wird bei dem Item definiert,
unter dem die definierte Struktur (Teil-Item-Baum) eingefügt werden soll.

Prinzipiell gibt es 2 Anwendungsfälle:

 - Der Nutzer kann selbst entsprechende Item-Struktur-Templates anlegen und verwenden
 - Eine Reihe von Plugins benötigt eine bestimmte Item Struktur bzw. eine größere Zahl an Items um sinnvoll zu funktionieren.

Demzufolge können die Item-Struktur-Templates an zwei verschiedenen Stellen definiert werden:

 - der Nutzer kann die Strukturen in der Konfigurationsdatei ../etc/struct.yaml definieren
 - Autoren von Plugins können die Strukturen in den Metadaten des Plugins definieren. Beim Start von SmartHomeNG stehen die dann die Strukturen aller konfigurierten Plugins zur Verfügung.

Um eine doppelte Namensvergabe zu vermeiden, wird bei der Nutzung den structs, die in Plugins definiert wurden, der
Name des Plugins vorangestellt. Wenn z.B. die struct **weather** genutzt werden soll, die im Plugin **darksky**
definiert wurde, so muss als Referenz **darksky.weather** angegeben werden.

Eine Übersicht der zur Verfügung stehenden structs kann in der Admin GUI unter **Items/Struktur** Templates eingesehen werden.

Mit dem **struct**-Attribut kann nicht nur eine, sondern auch mehrere vordefinierte Item-Strukturen in den Item-Tree eingefügt werden.
Dazu wird im **struct**-Attribut eine Liste von **struct** Namen angegeben. Wenn eine Liste angegeben wird, werden
die Template Strukturen in der Reihenfolge angewendet, in der sie in der Liste angegeben wurden.

.. code-block:: yaml

    aussen:
        struct:
            - mein_wetter1
            - mein_wetter2
            - ....

struct bei Plugins
==================

Anwendung
---------

Das folgende Beispiel verdeutlicht das Vorgehen am Wettervorhersage-Plugin **darksky**:

Bisher musste man in den Items einen ganzen Teilbaum selbst eintragen (hier unter **aussen.mein_wetter**):

.. code-block:: yaml

    aussen:
        mein_wetter:
            latitude:
                type: num
                ds_matchstring: latitude
            longitude:
                type: num
                ds_matchstring: longitude
            timezone:
                type: str
                ds_matchstring: timezone
            currently:
                time:
                    type: num
                    ds_matchstring: currently/time

            ...


Das Plugin **darksky** bringt nun ein Template mit dem Namen **weather** mit, welcher mit **darksky.weather** angesprochen werden kann.

Um nun die ganzen Items für die Wettervorhersage anzulegen, muss nur noch für das Item **mein_wetter** das Attribut **struct** gesetzt werden:

.. code-block:: yaml
    :caption: items/item.yaml

    outside:
        my_weather:
            struct: darksky.weather


Wenn das Plugin darksky konfiguriert ist, kann man in der Administrationsoberfläche die gesamten Items, die zum Wetterbericht gehören, sehen.


Multi-Instance Unterstützung
----------------------------

Wenn mehrere Instanzen eines Plugins verwendet werden, so muss (wie zu erwarten) bei dem Item welches die **struct**
referenziert, das Attribute **instance** angegeben werden.

In der Definition der **structs** in den Multi-Instance fähigen Plugins wird vom Plugin Autor an Stelle des aktuellen
Instance Namen das Wort **instance** als Platzhalter angegeben (wie im folgenden Beispiel beim Attribut **ds_matchstring**:

.. code-block:: yaml
    :caption: plugins/darksky/plugin.yaml

    ...

    item_structs:
        weather:
            name: Weather report from darksky.net

            latitude:
                type: num
                ds_matchstring@instance: latitude

            ...


In der Definition der Items bestehen zwei Möglichkeiten einer **struct** die **instance** mitzugeben auf die sich die **struct** beziehen soll.


1. Die **instance** kann in dem Item in dem die **struct** referenziert wird, als zusätzliches Attribut definiert werden:

.. code-block:: yaml
    :caption: items/item.yaml

    ...:
        weather_home:
            struct: darksky.weather
            instance: home

        weather_summer_residence:
            struct: darksky.weather
            instance: summer_residence

Diese Angabe (**instance: \<instance>**) wird dann auf alle Items übertragen, die durch das Template hinzugefügt wurden.
Das kann man auch in der Administrationsoberfläche sehen.


2. Die **instance** kann direkt im **struct** Attribut mit angegeben werden:

.. code-block:: yaml
    :caption: items/item.yaml

        weather_home:
            struct: darksky.weather@home

        weather_summer_residence:
            struct: darksky.weather@summer_residence


.. note::

    Wenn man eigene Items, in den Teilbaum der durch das Template hinzugefügt wurde, einfügen will, muss man für diese
    selbst hinzugefügten Items natürlich das Attribut **instance** angeben.



struct bei selbst definierte Item-Struktur-Templates
====================================================

Anwendung
---------

Eigens definierte Item-Struktur-Templates werden in der Konfigurationsdatei **../etc/struct.yaml** abgelegt.

Hierbei gibt die oberste Ebene den Namen der Templates an. Darunter können Item-Strukturen definiert werden, wie man es
auch in der Item Definition in den items.yaml Dateien machen würde. Das folgende Beispiel zeigt die Definition von zwei
Strukturen (**my_struct_01** und **my_struct_02**):

.. code-block:: yaml
    :caption: etc/struct.yaml

    my_struct_01:
        name: Name der erste eigenen Item Struktur

        item_01:
            name: Erstes Item
            type: num
            ...
        item_02:
            name: Zweites Item
            type: bool
            ...
            subitem:
                name: Sub-Item
                type: str
                ...


    my_struct_02:
        name: Name der zweiten eigenen Item Struktur
        type: bool

        item_a:
            name: Item A
            type: num
            ...
        item_b:
            name: Item B
            type: str
            ...

Wenn jetzt in der Item Definition diese Strukturen referenziert werden:

.. code-block:: yaml
    :caption: items/items.yaml

    my_tree:
        my_complex_data:
            name: Geänderter Name für meine komplexen Daten
            struct: my_struct_01

            individual_item:
                name: Individuelles Item
                type: str
                ...


entsteht im Item-Tree die selbe Struktur, als wenn man folgendes direkt in die item.yaml eingetragen hätte:

.. code-block:: yaml
    :caption: items/items.yaml

    my_tree:
        my_complex_data:
            name: Geänderter Name für meine komplexen Daten
            #struct: my_struct_01

            item_01:
                name: Erstes Item
                type: num
                ...
            item_02:
                name: Zweites Item
                type: bool
                ...
                subitem:
                    name: Sub-Item
                    type: str
                    ...
            individual_item:
                name: Individuelles Item
                type: str
                ...


Beim Einfügen der Struktur bleibt das Attribut **struct** erhalten, so dass man zur Laufzeit sehen kann, 
dass die Struktur zumindest in Teilen aus einem Template stammt.
Die Definition des Attributes **name** aus dem Template wird durch die Angabe aus der Datei items/item.yaml ersetzt. 
Das **individual_item** wird an die Struktur des Templates angefügt.
(Siehe :doc:`Konfigurationsdateien/struct.yaml </konfiguration/konfigurationsdateien/struct>`)


Verschachtelte struct Definitionen (nested structs)
---------------------------------------------------

Ab SmartHomeNG v1.7 können Strukturdefinitionen verschachtelt werden. Wie Items, die mithilfe des Attributs **struct:**
auf eine Strukturdefinition verweisen, können dies jetzt auch Strukturen selbst tun.

In Strukturen wird das **struct** Attribut **nur** auf der obersten Ebene als Referenz ausgewertet.

SmartHomeNG löst alle Unterstrukturreferenzen vor dem Laden des Item Trees auf, um das Laden der Item Definitionen zu beschleunigen.

.. note::

  Wenn Unterstrukturdefinitionen aufgelöst werden, gibt es zwei Unterschiede zu der Art und Weise,
  wie Item Definitionen geladen werden. Die Unterschiede treten nur dann zutage, wenn Strukturen / Unterstrukturen
  Attribute re-definieren. (Siehe hierzu auch folgende Kapitel und :doc:`Konfiguration/structs </konfiguration/item_structs>`)


Re-Definieren von Attributen (außer list-Attributen)
----------------------------------------------------

Beim Definieren von Items ist es möglich, dasselbe Attribut für ein Item in mehreren Item YAML-Dateien zu definieren.
Grundsätzlich werden alle Attribute zu einem Item, dass in mehreren Item YAML-Dateien definiert wurde, gemerged, also zusammengeführt.

.. note::

    Gibt es eine Attributdefinition an mehreren Stellen, gelten folgende Regeln:
     - Beim Lesen der Item Definition gewinnt die Attributdefinition, welche zuletzt eingelesen wird. Regel: **"last wins"**
     - In Struktur- /Unterstrukturdefinitionen gewinnt die zuerst eingelesene Attributdefinition. Regel: **"first wins"**
     - Wenn ein Attribut in einem struct-Template und in den Item Definitionen definiert wird, "gewinnt" die Angabe aus der
       Item Definition. Regel: **"Item wins"**

Beim Auflösen von Unterstrukturen gewinnt die Definition der Struktur der oberen Ebene, wenn das Attribut
in der Struktur der oberen Ebene vor dem **struct**-Attribut definiert ist. Dies ermöglicht ein "Überschreiben"
von Attributwerten, die in einer Unterstruktur definiert wurden. Wenn das Attribut nach dem
**struct**-Attribut definiert ist, gewinnt die Definition in der Unterstruktur. Regel: **"first wins"**


Re-Definieren von list-Attributen
----------------------------------

Das Verhalten bei Re-Definieren von list-Attributen ist abhängig von der Anwendung. Zu unterscheiden gilt, ob es
  - ein struct in einem Item ist, oder
  - ein sub-struct in einem struct.

.. note::
    Gibt es eine Attributdefinition mit Listen an mehreren Stellen, gelten folgende Regeln:
      - Bei structs/substructs werden Listen immer gemergt.
      - Bei Items/structs nur, wenn dort Am Anfang einer der Spezialeinträge steht.


Verhalten bei struct in einem Item
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wenn ein Attribut eine Liste enthält, kann das Standardverhalten **"first wins"** in **merge** abgeändert werden.
Es können die Liste, die im Item definiert ist, und die Liste, die im **struct** Template definiert ist,
miteinander verbunden werden. Dabei wird die Liste aus dem **struct** Template an die Liste im Item Attribut
angehängt.

Dazu müssen folgende Voraussetzungen erfüllt sein:
  - Das zu mergende Attribut MUSS vor dem **struct** Attribut definiert werden
  - Das zu mergende Attribut MUSS im Item als Liste definiert sein
  - Das zu mergende Attribut MUSS im Item als ersten Eintrag **merge\*** oder **merge_unique\*** enthalten
    (Der Stern/Asterix muss direkt, ohne Leerzeichen, auf **merge** bzw. **merge_unique** folgen)

Falls der erste Listeintrag **merge\*** ist, bleiben doppelte Listeinträge erhalten.


Verhalten bei sub-struct in struct
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bei der Neudefinition von Attributen, bei denen es sich um Listen handelt, erfolgt kein "Überschreiben". Stattdessen
werden die Listen zusammengefügt. Die Reihenfolge der Listeneinträge wird durch die Reihenfolge bestimmt, in der die
Attributdefinitionen eingelesen werden.


Beispiele
=========

Ausführliche Beispiele sind im Abschnitt :doc:`Beispiele </beispiele/structs>` dieser Dokumentation zu finden.