Navigation: Zusätzliche Infos
=============================

Möglichkeiten
-------------

Das folgende Beispiel zeigt die Möglichkeiten zur Anzeige von
zusätzlichen Informationen in der Navigation. Es können zwei Zeilen
angezeigt werden. Im Beispiel wird in der ersten Zeile die aktuelle
Raumtemperatur angezeigt und in der zweiten Zeile werden Icons
angezeigt, die den Zustand von Geräten in dem Raum anzeigen.

.. figure:: assets/navigation.jpg
   :alt: Navigation Zusatzinfos

   Navigation Zusatzinfos

Das Beispiel zeigt folgendes an:

- Kaffeemaschine auf Standby in der Küche
- TV an im Wohnzimmer
- Im Gästezimmer und im Bad wird geheizt
- Im Büro läuft das TV im Audio Mode
- Die Waschmaschine läuft

Am Beispiel der Küche zeigt die folgende Konfiguration, wie die
zusätzlichen Informationen konfiguriert werden:

.. code-block:: yaml

    %YAML 1.1
    ---

    wohnung:

        kochen:
            name: Kochen
            sv_page: room
            sv_img: scene_cooking.png
            sv_nav_aside: "{{ basic.float('m_kochen.ist', 'wohnung.kochen.heizung.ist', '°') }}"
            sv_nav_aside2: "{{ basic.symbol('m_kochen_kaffee2', 'wohnung.kochen.kaffeeautomat.status', '', 'icons/ws/scene_coffee_maker_automatic.png', '2') }} {{ basic.symbol('m_kochen_kaffee3', 'wohnung.kochen.kaffeeautomat.status', '', 'icons/or/scene_coffee_maker_automatic.png', '3') }} {{ basic.symbol('m_kochen_heizen', 'wohnung.kochen.heizung.heizen', '', icon1~'sani_heating.png') }}"

Wie in den bisherigen Releases:

- ``sv_page`` zeigt an, dass
  [wohnung.kochen] ein Raum ist und für diesen ein Navigationseintrag und
  eine Seite generiert werden soll.
- ``sv_img`` gibt an, welches Icon in
  der Navigation und auf der Seite angezeigt werden soll.

Neu:

- ``sv_nav_aside`` spezifiziert, was an der Seite in der oberen
  Zeile angezeigt werden soll. In diesem Fall ist das die aktuelle
  Raumtemperatur.
- ``sv_nav_aside2`` spezifiziert,was an der Seite in
  der unteren Zeile angezeigt werden soll. In diesem Fall ist das eine
  Reihe von Symbolen:

  – Kaffeeautomat im Standby

  – Kaffeeautomat heizt

  – Die Heizung heizt

Wenn die Stati nicht aktiv sind, werden die jeweiligen Icons nicht
angezeigt. Da der Kaffeeautomat nur entweder im Standby sein kann oder
heizt, wird nur eines der Icons angezeigt. Wenn der Kaffeeautomat
ausgeschaltet ist, wird kein Icon angezeigt.
