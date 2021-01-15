
.. index:: smartVISU; Automatische Generierung

========================
Automatische Generierung
========================

Im Vergleich zum **visu_smartvisu** Plugin der vorhergehenden SmartHomeNG Releases, wurden die
Möglichkeiten zur automatischen Generierung von Seiten für die smartVISU erweitert. Die
bisherigen Features sind mit einer Ausnahme auch im neuen **smartvisu** Plugin vorhanden. Die
Version 3 des Nutzdaten Protokolls wurde nicht erneut implememtiert. Daher entfällt die Unterstützung
für smartVISU v2.7. Unterstützt werden nun smartVISU v2.8 und v2.9 und folgende.

Neu hinzugekommen sind folgende Features:

- **Deprecated Widget Warnings**: Ab dem auf v2.9.2 folgenden Release liefert die smartVISU informationen
  welche Widgets der smartVISU als veraltet (deprecated) gekennzeichnet wurden und welche Widgets entfernt
  wurden.
- **Navigation Structure Definition**: Bisher wurde die Navigation der smartVISU strikt in der Reihenfolge
  erzeugt, in der die Items beim Start von SmartHomeNG eingelesen werden. Nun ist es möglich, diese
  Navigations-Struktur (inclusive Icons und Sidebar Infos) in einer zentralen Datei zu konfigurieren und
  damit die Reihenfolge aus den Item-Definitionen zu übersteuern.
- **Pages from multiple sub-trees**: Items aus mehreren unterschiedlichen Sub-Trees können zusammen in eine
  Seite der Visualisierung generiert werden.


Die zusätzlichen Item Attribute, die vom **smartvisu** Plugin zur Nutzung in den Item Definitionen definiert
werden, sind auf der Seite :doc:`item_attributes` im Detail beschrieben.


Diese Seite und die zugehörien Unterseiten sollen einige der Möglichkeiten aufzeigen, die sich durch die
Erweiterungen bieten. Es ist auch möglich einen Teil der Seiten generieren zu lassen und einen anderen Teil der
Seiten manuell zu erstellen.


Features der Generierung
========================


.. index:: smartVISU Autogenerierung; Zusätzliche Infos in der Navigation anzeigen

Zusätzliche Infos in der Navigation anzeigen
--------------------------------------------

In der Navigation können eine Reihe zusätzlicher Informationen angezeigt werden.

Das folgende Beispiel zeigt die Möglichkeiten zur Anzeige von zusätzlichen Informationen in der Navigation.
Es können zwei Zeilen angezeigt werden. Im Beispiel wird in der ersten Zeile die aktuelle Raumtemperatur angezeigt
und in der zweiten Zeile werden Icons angezeigt, die den Zustand von Geräten in dem Raum anzeigen.

.. figure:: assets/navigation.jpg
   :alt: Navigation Zusatzinfos

   Navigation Zusatzinfos

Das Beispiel zeigt folgendes an:

- Kaffeemaschine auf Standby in der Küche
- TV an im Wohnzimmer
- Im Gästezimmer und im Bad wird geheizt
- Im Büro läuft das TV im Audio Mode
- Die Waschmaschine läuft

Am Beispiel der Küche zeigt die folgende Konfiguration, wie die zusätzlichen Informationen konfiguriert werden:

.. code-block:: yaml

    %YAML 1.1
    ---

    wohnung:

        kochen:
            name: Kochen
            sv_page: room
            sv_img: scene_cooking.png
            sv_nav_aside: "{{ basic.print('m_kochen.ist', 'wohnung.kochen.heizung.ist', '°') }}"
            sv_nav_aside2: "{{ basic.symbol('m_kochen_kaffee2', 'wohnung.kochen.kaffeeautomat.status', '', 'icons/ws/scene_coffee_maker_automatic.png', '2') }} {{ basic.symbol('m_kochen_kaffee3', 'wohnung.kochen.kaffeeautomat.status', '', 'icons/or/scene_coffee_maker_automatic.png', '3') }} {{ basic.symbol('m_kochen_heizen', 'wohnung.kochen.heizung.heizen', '', icon1~'sani_heating.png') }}"

Wie in den bisherigen Releases:

- ``sv_page`` zeigt an, dass
  [wohnung.kochen] ein Raum ist und für diesen ein Navigationseintrag und eine Seite generiert werden soll.
- ``sv_img`` gibt an, welches Icon in der Navigation und auf der Seite angezeigt werden soll.

Neu:

- ``sv_nav_aside`` spezifiziert, was an der Seite in der oberen Zeile angezeigt werden soll. In diesem Fall ist das
  die aktuelle Raumtemperatur.
- ``sv_nav_aside2`` spezifiziert,was an der Seite in der unteren Zeile angezeigt werden soll. In diesem Fall ist
  das eine Reihe von Symbolen:

  – Kaffeeautomat im Standby

  – Kaffeeautomat heizt

  – Die Heizung heizt

Wenn die Stati nicht aktiv sind, werden die jeweiligen Icons nicht angezeigt. Da der Kaffeeautomat nur entweder
im Standby sein kann oder heizt, wird nur eines der Icons angezeigt. Wenn der Kaffeeautomat ausgeschaltet ist,
wird kein Icon angezeigt.


.. index:: smartVISU Autogenerierung; Konfigurationsseiten

Generierung einer Konfigurations-Navigation
-------------------------------------------

Zusätzlich zum Aufbau einer Navigation über die Seiten der Räume, kann eine Navigation über
mehrere Konfigurationsseiten aufgebaut werden.

Das folgende Beispiel zeigt die Möglichkeiten zum generieren einer
Kategorie Navigation. Die Kategorie Navigation wird durch anklicken des
Hand-Symbols in der Titelzeile der smartVISU aktiviert.

.. figure:: assets/category_nav.jpg
   :alt: Kategorie Navigation

   Kategorie Navigation

Am Beispiel der obigen Konfigurations-Navigation zeigt die nachfolgende
Konfigurationsdatei, wie die Navigation konfiguriert wird:

.. code-block:: yaml

    %YAML 1.1
    ---

    config:

        konfiguration:
            name: Konfiguration
            sv_page: category
            sv_img: control_all_on_off.png

        beschattung:
            name: Beschattung
            sv_page: category
            sv_img: fts_shutter_40.png

        beleuchtung:
            name: Beleuchtungsautomatik
            sv_page: category
            sv_img: light_light_dim_00.png


``sv_page`` ist zum Generieren eines Eintrages für die
Konfigurations-Navigation auf den Seitentyp **``category``**
einzustellen.


.. index:: smartVISU Autogenerierung; Trenner in der Navigation

Trenner in der Navigation
-------------------------

Die Navigation kann durch Trenner unterteilt werden, um die Übersichtlichkeit zu erhöhen.

Das folgende Beispiel zeigt die Möglichkeiten zur Anzeige von Trennern
in der Navigation. Zwischen den Navigationseinträgen können mehrere
Trenner angezeigt werden. Das Beispiel zeigt nicht die Raum-Navigation,
sondern die Navigation auf der Konfigurationsseite.

.. figure:: assets/divider.jpg
   :alt: Navigation Trenner

   Navigation Trenner

Das Beispiel zeigt folgende Trenner: - Tests - Kategorien

Am Beispiel des Trenners **``Tests``** zeigt die folgende Konfiguration,
wie Trenner konfiguriert werden:

.. code-block:: yaml

    %YAML 1.1
    ---

    config:

        verteilung:
            name: Verteilung
            sv_page: category
            sv_img: measure_current.png

        separator_test:
            name: Tests
            sv_page: cat_separator

        fritzboxen:
            name: Fritzboxen
            sv_page: category
            sv_img: it_router.png

``sv_page`` ist zum generieren eines Trenners auf einen speziellen
Seitentyp einzustellen. - Wenn ein Trenner in die normale Raumnavigation
eingefügt werden soll, so muss **``sv_page = separator``** angegeben
werden. - Wenn ein Trenner in die Konfigurationsnavigation eingefügt
werden soll, so muss **``sv_page = cat_separator``** angegeben werden.


.. index:: smartVISU Autogenerierung; Unterschiedliche Visu-Styles

Unterschiedliche Visu-Styles
----------------------------

Zusätzlich zum von bisherigen Releases unterstützen Standard-Style, wird der Style **black**
unterstützt.

Das folgende Beispiel zeigt die Möglichkeiten zur Auswahl des Styles der
für smartVISU generierten Seiten.

Bisher wurden Blöcke generiert, die so aussahen (Style ‘Standard’):

.. figure:: assets/style_std.jpg
   :alt: Style Standard

   Style Standard

In der aktuellen Version ist es möglich, die Blöcke in folgender Optik
generieren zu lassen (Style ‘Black’):

.. figure:: assets/style_blk.jpg
   :alt: Style Black

   Style Black

Dieses ist eine Visu-weite Einstellung, die in der Datei
/etc/plugin.conf vorgenommen wird. Dort kann ``visu_style: std``
oder ``visu_style: blk`` eingetragen werden.

Eine vollständige Seite im Style **Black** sieht z.B. folgendermaßen aus:

.. figure:: assets/style_blk_visu.jpg
   :alt: Visu Black

   Visu Black


.. index:: smartVISU Autogenerierung; Unterschiedliche Blockgrößen

Unterschiedliche Blockgrößen
----------------------------

Die Blöcke in denen Widgets angezeigt werden, hatten in den bisherigen Releases eine fest
definierte (Mindest-)Größe. Jetzt stehen drei unterschiedliche Mindestgrößen zur Verfügung.

Die smartVISU unterstützt Blöcke mit drei unterschiedlichen Größen.
Gemeint ist hierbei die Mindestgröße des Blocks. Wenn in dem Block
Widgets platziert werden, die mit dem Platz nicht auskommen, wird der
Block automatisch höher. Die Blockhöhen unterscheiden sich in etwa um
die Höhe der Heading-Zeile.

In den bisherigen Releases von smarthome.py/SmartHomeNG wurden beim
automatischen generieren von smartVISU Seiten immer Blöcke der Größe
**2** (mittel) verwendet.

Im aktuellen Release können auch Blöcke der Größen **1** (groß) und
**3** (klein) in die Seiten generiert werden.

Dieses kann als Item-Attribut **``sv_blocksize``** festgelegt werden.

Am Beispiel des Trenners **``Tests``** zeigt die folgende Konfiguration,
wie Trenner konfiguriert werden:

.. code-block:: yaml

    %YAML 1.1
    ---

    wohnung:

        buero:

            verbraucher:
                name: Verbraucher
                sv_blocksize: 1
                sv_widget: "{{ basic.switch('wohnung.buero.tv', 'wohnung.buero.tv', icon0~'control_on_off.png', icon0~'control_standby.png') }} <br> {{ basic.switch('wohnung.buero.computer', 'wohnung.buero.computer', icon0~'control_on_off.png', icon0~'control_standby.png') }} <br> {{ basic.switch('wohnung.buero.schrank', 'wohnung.buero.schrank', icon0~'control_on_off.png', icon0~'control_standby.png') }} <br> {{ basic.switch('wohnung.buero.steckdose_tuer', 'wohnung.buero.steckdose_tuer', icon0~'control_on_off.png', icon0~'control_standby.png') }}"

``sv_blocksize`` dient zur Einstellung der (minimalen) Blockhöhe und
darf die Werte 1, 2 oder 3 annehmen. Wird ``sv_blocksize``\ nicht
angegeben, so wird der Default-Wert **2** benutzt.


.. index:: smartVISU Autogenerierung; Unterschiedliche Blocktypen

Unterschiedliche Blocktypen
---------------------------

Die Blöcke in denen Widgets angezeigt werden, hatten in den bisherigen Releases einen festen
Typ. Nun ist ein Typ **Dual** hinzugekommen.

Die smartVISU unterstützt Blöcke zusätzlich zu den Standard-Blöcken auch
Blöcke mit “2 Seiten”, die in den bisherigen Releases von
smarthome.py/SmartHomeNG nicht unterstützt wurden.

Im aktuellen Release können auch diese Dual-Blöcke in der automatischen
Seitengenerierung verwendet werden.

Hier ein Beispiel, wie ein solcher DualBlock aussehen kann:

.. figure:: assets/blocktype_dual_1.jpg
   :alt: Dual-Block

   Dual-Block

.. figure:: assets/blocktype_dual_2.jpg
   :alt: Dual-Block 2

   Dual-Block 2

Ein solcher Dual-Block hat immer die Größe eines großen Blocks. Damit
die Visu-Seite “aufgeräumt” aussieht, sollte für den daneben liegenden
Block die große Form gewählt werden (``sv_blocksize = 1``). Diehe dazu
auch Seite `Unterschiedliche
Blockgrößen <https://github.com/smarthomeNG/smarthome/wiki/visu_smartvisu_autogen_blocksizes>`__.

Hier ist ein Beispiel auf einer Visu Seite:

.. figure:: assets/blocktype_dual_visu.jpg
   :alt: Navigation Trenner

   Navigation Trenner


.. index:: smartVISU Autogenerierung; Manuell erstellte Visu Seiten
.. index:: smartVISU; Manuell erstellte Visu Seiten

Manuell erstellte Seiten
------------------------

In smartVISU können manuell erstellte oder modifizierte Seiten in die Autogenerierung eingemischt werden.

Normalerweise werden durch das Plugin alle notwendigen Seiten für smartVISU generiert und im Bereich **pages** unter
**smarthome** abgelegt.

Diese Seiten werden in smartVISU dann folgendermaßen ausgewählt:

.. figure:: assets/config_fullauto.jpg
   :alt: Vollständige Autogenerierung


smartVISU bietet jedoch eine Möglichkeit um manuell erstellte Seiten und automatisch generierte Seiten zu mischen.

Dazu muss man in smartVISU einen ordner unter **pages** anlegen und die manuell erstellten Seiten dort hineinkopieren.
Anschließend muss man in smartVISU dann zur Darstellung diesen Bereich auswählen:

.. figure:: assets/config_partlyauto.jpg
   :alt: Teil-Autogenerierung


Beim Zugriff auf Seiten versucht smartVISU nun die entsprechende Seite aus dem unter **pages** angelegten Bereich zu
laden. Wird die angeforderte Seite dort nicht gefunden, versucht smartVISU die Seite aus dem Bereich **smarthome** zu
laden.

Man kann also SmartHomeNG die Seiten vollständig generieren lassen und eine Seite, die manuelle Modifikationen enthalten
soll aus dem Ordner **smarthome** in den unter **pages** angelegten Bereich kopieren und anschließend in dieser Kopie
die gewünschten Modifikationen vornehmen.

.. note::

   Die modifizierte Seite erhält keine Änderungen mehr aus SmartHomeNG.

   Falls Änderungen aus SmartHomeNG in diese Seite übernommen werden sollen, müssen diese aus der generierten Seite
   (im Ordner **smarthome**) in die manuell modifizierte Seite übernommen werden.

   Alternativ kann die generierte Seite erneut kopiert werden und die Änderungen können dort eingearbeitet werden,
   wie dieses ursprünglich erfolgt ist.


Deprecated Widget Warnings
==========================

Ab dem auf v2.9.2 folgenden Release liefert die smartVISU informationen welche Widgets der smartVISU
als veraltet (deprecated) gekennzeichnet wurden und welche Widgets entfernt wurden. Ab SmartHomeNG v1.8
können diese Informationen ausgewertet werden und Warnungen geloggt werden falls veraltete order entfernte
Widgets in der automatischen Generierung genutzt werden sollen.

Standardmäßig wird eine Warning bei Verwendung veralteter (deprecated) Widgets erzeugt. Der Log Eintrag
enthält eine Liste aller verwendeten Widgets mit der Anzahl Items in denen diese Widgets genutzt werden.

Im folgenden Beispiel wird aufgezeigt, dass das Widget **plot.multiaxis** an 9 Stellen verwendet wird.

.. code:: text

    2020-09-14  21:26:43 WARNING  plugins.smartvisu    Deprecated widget usage={'plot.multiaxis': 9}


Standardmäßig wird ein Error bei Verwendung entfernter (removed) Widgets erzeugt. Es wird ein Error erzeugt,
da die generierten Visu Seiten die diese Widgets enthalten nicht funktionieren werden.

Im folgenden Beispiel wird aufgezeigt, dass das einige Widgets an mehreren Stellen verwendet werden.

.. code:: text

    2020-09-14  21:26:43 ERROR    plugins.smartvisu    Removed widget usage={'basic.button': 18, 'basic.dual': 3, 'basic.switch': 11, 'basic.text': 13}


Weiterhin werden Warnungen geloggt, falls Widgets die von Plugins "mitgebracht" werden, veraltete Widgets
der smartVISU nutzen:

.. code:: text

    2020-09-12  10:37:53 ERROR    plugins.smartvisu    deprecated_widgets: Removed widget(s) ['basic.button', 'basic.formula', 'basic.switch'] used in plugin-widget 'widget_window' of plugin 'priv_widgets'


In der Konfiguration des smartvisu Plugins kann eingestellt werden, dass zusätzlich Warnings/Errors mit
den Details der Nutzung in den Item Definitionen geloggt werden. Diese Logeinträge enthalten die Angabe
des Items und des Attributes des Items, in dem das entsprechende Widget genutzt wird:

.. code:: text

    2020-09-12  10:37:53 WARNING  plugins.smartvisu    Deprecated widget used in item wohnung.kochen.plot_temperaturen 'sv_widget': 'plot.multiaxis'
    2020-09-12  10:56:03 ERROR    plugins.smartvisu    Removed widget used in item wohnung.kochen.visu_insel 'sv_widget': 'basic.button'


Navigation Structure Definition
===============================

Bisher wurde die Navigation der smartVISU ausschließlich in der Reihenfolge erzeugt, in der die Items
beim Start von SmartHomeNG eingelesen werden. Seit SmartHomeNG v1.8 ist es möglich, diese Navigations-Struktur
(inclusive Icons und Sidebar Infos) in einer zentralen Datei zu konfigurieren und damit die Reihenfolge aus
den Item-Definitionen zu übersteuern.

In der Datei ```../etc/visu.yaml``` können auch die Einstellungen für die Attribute **sv_img**, **sv_nav_aside**
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



Seiten aus mehreren Sub-Trees
=============================

Ab SmartHomeNG v1.8 können Items aus mehreren unterschiedlichen Sub-Trees zusammen in eine Seite der
Visualisierung generiert werden.

Bisher wurden alle Widgets die unterhalb eines Items definiert wurden, welches ein **sv_page** Attribut hat
in eine Visu Seite generiert. Wenn in einem anderen Teilbaum des Item-Trees ein weitere **sv_page** Definition
mit dem selben Seiten Namen (**name:**) erfolgte, wurde eine weitere Seite generiert, die in der Navigation den
selben Namen hatte wie die erste Seite.

Nun werden die Widgets aus dem zweiten Teilbaum in diesem Fall nicht mehr in eine eigene Seite generiert,
sondern an die erste Seite angefügt.

Falls es erwünscht ist zwei Navigationseinträge mit dem selben Namen zu haben (z.B. **Bad**  wenn die Navigation
durch Trenner "Erdgeschoss" und "Obergeschoss" strukturiert ist, so muss an den Namen der Definition für den
zweiten Teilbaum nur ein Leerzeichen angefügt werden:

.. code:: yaml

    myitems:
        eg:
            bad:
                sv_page: room
                name: Bad

        ...

        og:
            bad:
                sv_page: room
                name: "Bad "

