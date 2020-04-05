
.. index:: structs

.. role:: bluesup
.. role:: redsup


=========================
structs (Item Strukturen)
=========================


Überblick
=========

Eine Reihe von Plugins benötigt eine bestimmte Item Struktur bzw. eine größere Zahl an Items um sinnvoll zu
funktionieren. Diese Items müssen dazu innerhalb des Item-Trees als Teilbaum angelegt werden (zum Teil auch mehrfach).

Seit SmartHomeNG v1.6 werden diese Strukturen/Templates unterstützt, die dann mit Hilfe des **struct**-Attributs in
den Item-Tree eingefügt werden können. Dazu muss bei dem Item an dessen Stelle der Teilbaum eingefügt werden soll,
der Name des Templates (der Item-Struktur) angegeben werden.

Die Item Strukturen/Templates können an zwei verschiedenen Stellen definiert werden:

- der Nutzer kann die Strukturen in der Konfigurationsdatei ../etc/struct.yaml definieren
- Autoren von Plugins können die Strukturen in den Metadaten des Plugins definieren. Beim Start von SmartHomeNG
  stehen die dann die Strukturen aller konfigurierten Plugins zur Verfügung.

Mit dem **struct**-Attribut kann nicht nur eine Item Struktur in den Item-Tree eingefügt werden, sondern auch mehrere.
Dazu wird im **struct**-Attribut eine Liste von **struct** Namen angegeben. Wenn eine Liste angegeben wird, werden
die Template Strukturen in der Reihenfolge angewendet, in der sie in der Liste angegeben wurden.

.. code-block:: yaml

    aussen:
        struct:
            - mein_wetter1
            - mein_wetter2
            - ....

Um eine doppelte Namensvergabe zu vermeiden, wird bei der Nutzung den structs, die in Plugins definiert wurden, der
Name des Plugins vorangestellt. Wenn z.B. die struct **weather** genutzt werden soll, die im Plugin **darksky**
definiert wurde, so muss als Referenz **darksky.weather** angegeben werden.

Eine Übersicht der zur Verfügung stehenden structs kann in der Admin GUI unter **Items/Struktur** Templates eingesehen
werden.


Das folgende Beispiel verdeutlicht das Vorgehen am Wettervorhersage-Plugin **darksky**:

Bisher musste man in den Items einen ganzen Teilbaum eintragen (hier unter **aussen.mein_wetter**):

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


Wenn das Plugin darksky konfiguriert ist, kann man in der Administrationsoberfläche die gesamten Items, die zum
Wetterbericht gehören, sehen.


Multi-Instance Unterstützung
============================

Wenn mehrere Instanzen eines Plugins verwendet werden, so muss (wie zu erwarten) bei dem Item welches die **struct**
referenziert, das Attribute **instance** angegeben werden.

In der Definition der structs in den Multi-Instance fähigen Plugins wird vom Plugin Autor an Stelle des aktuellen
Instance Namen das Wort **instance** als Platzhalter angegeben (wie im folgenden Beispiel beim Attribut
**ds_matchstring**:

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


In der Definition der Items bestehen zwei Möglichkeiten einer **struct** die **instance** mitzugeben auf die sich
die **struct** beziehen soll.


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

    ...:
        weather_home:
            struct: darksky.weather@home

        weather_summer_residence:
            struct: darksky.weather@summer_residence


.. note::

    Wenn man eigene Items in den Teilbaum der durch das Template hinzugefügt wurde einfügen will, muss man für diese
    selbst hinzugefügten Items natürlich das Attribut **instance** angeben.



Selbst definierte Item-Strukturen
=================================

Zusätzlich zu den Item-Strukturen, die Plugins als Template mitbringen, können eigene Strukturen angelegt werden. Diese
Strukturen werden in der Konfigurationdatei **../etc/struct.yaml** abgelegt werden. (Siehe
:doc:`Konfigurationsdateien/struct.yaml </konfiguration/konfigurationsdateien/struct>`)

Diese Templates werden mit dem Namen der Struktur ohne einen vorrangestellten Plugin-Namen angegeben:

.. code-block:: yaml
    :caption: items/item.yaml

    komplexes_item:
        struct: meine_struktur


Eigene Items und Attribute innerhalb der Strukturen
===================================================

Innerhalb der durch die Templates angelegten Strukturen können in der Item Definition eigene Items und Attribute
angegeben werden. Es ist dabei sogar möglich, Attribute die in den Templates gesetzt wurden zu überschreiben.

Wenn ein Attribut in einem **struct** Template und in den Item Definitionen definiert wird, "gewinnt" die Angabe
aus der Item Definition. Regel: "Item wins"


Besonderheit bei Attributen, die Listen enthalten
-------------------------------------------------

Wenn ein Attribut eine Liste enthält, kann das Standardverhalten "Angabe im Item gewinnt" abgeändert werden.
In diesem Fall können die Liste die im Item definiert ist und die Liste die im **struct** Template definiert ist,
miteinander verbunden werden. Dabei wird die Liste aus dem **struct** Template an die Liste im Item Attribut
angehängt.

Dazu müssen folgende Voraussetzungen erfüllt sein:

- Das zu mergende Attribut MUSS vor dem **struct** Attribut definiert werden
- Das zu mergende Attribut MUSS im Item als Liste definiert sein
- Das zu mergende Attribut MUSS im Item als ersten Eintrag **merge\*** oder **merge_unique\*** enthalten
  (Der Stern/Asterix muss direkt, ohne Leerzeichen, auf **merge** bzw. **merge_unique** folgen)

Falls der erste Listeintrag **merge\*** ist, bleiben doppelte Listeinträge erhalten.


Verwendung des *struct* Attributes in *struct* Definitionen
===========================================================

Innerhalb von **struct** Definitionen kann auf der obersten Ebene das Attribut **struct** angeben werden, um weitere
**struct** Templates in die **struct** einzubinden.

Unterschiede zum **struct** Attribut in Item Definitionen:

- Ob bei abweichenden Werten in einem Attribut der Wert der übergeordneten **struct** oder der referenzierten
  **struct** "gewinnt", hängt von der Reihenfolge der Definition ab. Falls das entsprechende Attribut vor dem
  **struct** Attribut definiert wird, bleibt der Wert der übergeordneten **struct** erhalten. Anderenfalls bleibt
  der Wert aus der referenzierten **struct** erhalten. Regel: "first wins"
- Innerhalb der **struct** Definitionen braucht das Attribut **merge\*** nicht angegeben zu werden.
  Listen von structs und sub-structs werden standardmäßig gemerged.


Beispiele
=========

Ausführliche Beispiele sind im Abschnitt :doc:`Beispiele </beispiele/structs>` dieser Dokumentation zu finden.
