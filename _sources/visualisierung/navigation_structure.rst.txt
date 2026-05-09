.. role:: redsup
.. role:: bluesup
.. role:: darkbluesup
.. role:: greensup
.. role:: blacksup

Navigation Structure Definition
===============================

Die Navigation der smartVISU wird in der Reihenfolge erzeugt, in der die Items 
beim Start von SmartHomeNG eingelesen werden. Es ist möglich, diese Navigations-Struktur
(inclusive Icons und Sidebar Infos) in einer zentralen Datei zu konfigurieren und damit die Reihenfolge aus
den Item-Definitionen zu übersteuern.

In der Datei ``etc/visu.yaml`` können auch die Einstellungen für die Attribute **sv_img**, **sv_nav_aside**
und **sv_nav_aside2** übersteuert und die Position von Trennern in der Navigation festgelegt werden.

Die Struktur der Datei ist folgende:

.. code:: yaml

    %YAML 1.1
    ---
    navigation:
        # Die gesamte Strukturierung der Navigation wird unterhalb  des Schlüssels 'navigagion:' definiert
        room:
          # Unter dem Schlüssel 'room:' wird die Struktur für die Seiten der Räume festgelegt.
          # Die Reihenfolge der Navigationseinträge wird als eine Liste von Unterstrukturen definiert.
          # Die Unterstrukturen müssen den Schlüssel 'name:' und einen Wert für den Namen enthalten.
          # Die weiteren Schlüssel 'img:', 'nav_aside:' und 'nav_aside2:' sind optional.
          - name: Kochen
            img: scene_cooking.svg

          - name: Wohnen
            img: scene_livingroom.svg

          - name: Essen

          - name: Terrasse

          # Wenn ein Trenner definiert werden soll, muss außer dem Namen der Schlüssel 'separator:'
          # angegeben werden und es muss der Wert 'True' zugewiesen werden
          - name: Obergeschoss
            separator: True

          - name: Flur

          - name: Gast

          - name: Schlafen

        category:
          # Unter dem Schlüssel 'room:' wird die Struktur für die Seiten der Räume festgelegt
          - name: Konfiguration

        ...

|

