.. index:: Standard-Attribute; struct
.. index:: struct

.. index:: Items; Item-Struktur Template
.. index:: Items; struct
.. index:: Items; Template
.. index:: Item-Struktur Template
.. index:: Template

.. role:: bluesup
.. role:: redesup

`struct` :redsup:`new`
----------------------

Eine Reihe von Plugins benötigt eine bestimmte Item Struktur bzw. eine größere Zahl an Items um sinnvoll zu funktionieren.
Diese Items müssen dazu innerhalb des Item-Trees als Teilbaum angelegt werden (zum Teil auch mehrfach).

**Ab SmartHomeNG v1.6** können Plugin jetzt diese Strukturen als Templates zur Verfügung stellen, die dann mit Hilfe des
struct-Attributs in den Item-Tree eingefügt werden können. Dazu muss bei dem Item an dessen Stelle der Teilbaum eingefügt
werden soll, der Name des Templates (der Item-Struktur) angegeben werden. Der Name des zu verwendenden Template besteht
aus dem Name der Struktur (der der Plugin Dokumentation zu entnehmen ist), dem der Name des Plugins, abgetrennt mit einem
Punkt vorangestellt wird.

Das folgende Beispiel verdeutlicht das Vorgehen am Wettervorhersage-Plugin **darksky**:

Bisher musste man in den Items einen ganzen Teilbaum eintragen (hier unter aussen.mein_wetter):

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


Das Plugin **darksky** bringt nun ein Template mit dem Namen **weather** mit, welcher mit **darksky.weather** angesprochen
werden kann.

Um nun die ganzen Items für die Wettervorhersage anzulegen, muss nur noch für das Item **mein_wetter** das Attribut
**struct** gesetzt werden:

.. code-block:: yaml
    :caption: items/item.yaml

    outside:
        my_weather:
            struct: darksky.weather


Wenn das Plugin darksky konfiguriert ist, kann man in der Administrationsoberfläche die gesamten Items, die zum Wetterbericht
gehören, sehen.

Das Attribut **struct** kann dabei ein String oder eine Liste von Strings sein. Wenn eine Liste angegeben wird, werden
die Template Strukturen in der Reihenfolge angewendet, in der sie in der Liste angegeben wurden.


Multi-Instance Unterstützung
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wenn mehrere Instanzen eines Plugins verwendet werden, so muss (wie zu erwarten) bei dem Item welches die **struct**
referenziert, das Attribute **instance** angegeben werden.


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

.. note:

    Wenn man eigene Items in den Teilbaum der durch das Template hinzugefügt wurde einfügen will, muss man für diese selbst
    hinzugefügten Items natürlich das Attribut **instance** angeben.



Selbst definierte Item-Strukturen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Zusätzlich zu den Item-Strukturen, die Plugins als Template mitbringen, können eigene Strukturen angelegt werden. Diese
Strukturen werden in der Konfigurationdatei **../etc/struct.yaml** abgelegt werden. (Siehe Konfigurationsdateien/struct)

Diese Template werden mit dem Namen der Struktur ohne vorrangestellten Plugin-Namen angegeben:

.. code-block:: yaml
    :caption: items/item.yaml

    komplexes_item:
        struct: meine_struktur


Eigene Items und Attribute innerhalb der Strukturen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Innerhalb der durch die Templates angelegten Strukturen können in der Item Definition eigene Items und Attribute
angegeben werden. Es ist dabei sogar möglich, Attribute die in den Templates gesetzt wurden zu überschreiben.

Das kann man sich so vorstellen, als ob das Template in einer item.yaml Datei definiert wurde, die bereits verarbeitet wurde.

