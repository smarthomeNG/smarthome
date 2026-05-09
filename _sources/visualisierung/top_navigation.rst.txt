
.. role:: redsup
.. role:: bluesup
.. role:: darkbluesup
.. role:: greensup
.. role:: blacksup

.. index:: smartVISU; Top Navigation


Top Navigation auf Visu Seiten :redsup:`Neu`
============================================

Ab SmartHomeNG v1.12 / smartvisu Plugin v1.9 können Seiten mit einer Navigation oben auf der Seite
(Top Navigation) generiert werden. Im folgenden ist anhand eines Beispiels beschrieben, wie eine Top Navigation
konfiguriert wird.

Der Kopf der Beispiel Visu Seite ohne Top Navigation sieht so aus:

.. figure:: assets/topnav_wo.jpg
   :alt: Seite ohne Top Navigation

und ist folgendermaßen konfiguriert:

.. code-block:: yaml

    kochen:
        sv_page: room
        name: Kochen
        sv_img: scene_cooking.svg

        visu_szenen:
            name: Szenen Beleuchtung
            sv_widget: ...
        visu_fenster:
            name: Fenster Status
            sv_widget: ...

Jetzt soll eine Top Navigation bestehend aus 3 Buttons (möglich sind 2 bis 5 Buttons) hinzugefügt werden. Die
Buttons sollen "Standard", "Erweitert" und "Konfiguration" sein. Für jeden dieser drei Einträge muss eine
eigene Seite definiert werden und auf jeder dieser Seiten müssen die Buttons über das Attribut
``sv_heading_buttons`` definiert werden.

Die bisherige Seite **Kochen** wird folgendermaßen erweitert:

.. code-block:: yaml

    kochen:
        sv_page: room
        name: Kochen
        sv_img: scene_cooking.svg
        sv_heading_buttons:
          - ['Standard', 'Erweitert', 'Konfiguration']
          - ['Kochen', 'Kochen_Adv', 'Kochen_Cfg']

        visu_szenen:
            name: Szenen Beleuchtung
            sv_widget: ...
        visu_fenster:
            name: Fenster Status
            sv_widget: ...

``sv_heading_buttons`` ist eine Liste, die 2 Listen enthält, wobei jede dieser Listen soviel Einträge haben muss,
wie Buttons definiert werden sollen. Die erste Liste enthält die Beschriftungen der Buttons. Die zweite Liste
enthält den Namen von den jeweiligen Items, die die Seiten definieren.

Das Ergebnis sieht dann folgendermaßen aus:

.. figure:: assets/topnav_std1.jpg
   :alt: Seite mit Top Navigation

Da der erste Eintrag **Kochen** dem Namensattribut der Seite entspricht, ist der erste Button ausgewählt.
Ein Klick auf diesen Button führt zur angezeigten Seite. Ein Klick auf einen der beiden anderen Buttons führt
zu einem Seiten Ladefehler, da diese Seiten noch nicht definiert sind.

Im Attribut ``sv_heading_buttons`` ist definiert, dass die beiden anderen Seiten **Kochen_Adv** und **Kochen_Cfg**
heißen. Wenn jetzt die Seite für 'Erweitert' definiert wird, sieht die Konfiguration folgendermaßen aus:

.. code-block:: yaml

    kochen:
        sv_page: room
        name: Kochen
        sv_img: scene_cooking.svg
        sv_heading_buttons:
          - ['Standard', 'Erweitert', 'Konfiguration']
          - ['Kochen', 'Kochen_Adv', 'Kochen_Cfg']

        visu_szenen:
            name: Szenen Beleuchtung
            sv_widget: ...
        visu_fenster:
            name: Fenster Status
            sv_widget: ...

    kochen_erweitert:
        sv_page: room
        name: Kochen_Adv
        sv_img: scene_cooking.svg
        sv_heading_buttons:
          - ['Standard', 'Erweitert', 'Konfiguration']
          - ['Kochen', 'Kochen_Adv', 'Kochen_Cfg']

        visu_szenen:
            name: Szenen Beleuchtung
            sv_widget: ...
        visu_fenster:
            name: Fenster Status
            sv_widget: ...

Nun kann durch klicken des Buttons **Erweitert** die entsprechende Seite geladen werden. In der Visu sieht
das dann folgendermaßen aus:

.. figure:: assets/topnav_adv1.jpg
   :alt: Seite 'Erweitert' mit Top Navigation

Dabei fällt auf, dass diese Seite links in der Navigation auftaucht und dass die Überschrift nicht **Kochen**,
sondern **Kochen_Adv** ist.

Über das Attribut ``sv_page_in_navi`` kann gesteuert werden, dass die Seite nicht links in der Navigation
erscheint. Dazu wird ``sv_page_in_navi`` auf ``False`` gesetzt.

Dann sieht das in der Navi so aus:

.. figure:: assets/topnav_adv2.jpg
   :alt: Seite 'Erweitert' mit Top Navigation

Um zu verhindern, dass in der Überschrift **Kochen_Adv** erscheint, kann das Attribut ``sv_display_name``
gesetzt werden. Wenn dieses auf **Kochen** gesetzt wird, sieht das in der Visu so aus:

.. figure:: assets/topnav_adv3.jpg
   :alt: Seite 'Erweitert' mit Top Navigation

Analog zur Seite 'Erweitert' kann nun noch die Seite 'Konfiguration' definiert werden.
Die Konfiguration sieht nun folgendermaßen aus:

.. code-block:: yaml

    kochen:
        sv_page: room
        name: Kochen
        sv_img: scene_cooking.svg
        sv_heading_buttons:
          - ['Standard', 'Erweitert', 'Konfiguration']
          - ['Kochen', 'Kochen_Adv', 'Kochen_Cfg']

        visu_szenen:
            name: Szenen Beleuchtung
            sv_widget: ...
        visu_fenster:
            name: Fenster Status
            sv_widget: ...

    kochen_erweitert:
        sv_page: room
        sv_page_in_navi: False
        name: Kochen_Adv
        sv_display_name: Kochen
        sv_img: scene_cooking.svg
        sv_heading_buttons:
          - ['Standard', 'Erweitert', 'Konfiguration']
          - ['Kochen', 'Kochen_Adv', 'Kochen_Cfg']

        visu_szenen:
            name: Szenen Beleuchtung
            sv_widget: ...
        visu_fenster:
            name: Fenster Status
            sv_widget: ...

    kochen_konfiguration:
        sv_page: room
        sv_page_in_navi: False
        name: Kochen_Cfg
        sv_display_name: Kochen
        sv_img: scene_cooking.svg
        sv_heading_buttons:
          - ['Standard', 'Erweitert', 'Konfiguration']
          - ['Kochen', 'Kochen_Adv', 'Kochen_Cfg']

        visu_szenen:
            name: Szenen Beleuchtung
            sv_widget: ...
        visu_fenster:
            name: Fenster Status
            sv_widget: ...

|

Top Navigation mit Icons
------------------------

Falls es gewünscht ist, können die Buttons der Top Navigation mit Icons versehen werden. Dazu wird das
Attribut ``sv_heading_buttons`` um eine dritte Liste ergänzt. Die Einträge dieser Liste sind die Namen der
Icons ohne Extension, aso ohne '.svg'.

Wenn das Attribut  ``sv_heading_buttons`` folgendermaßen ergänzt wird

.. code-block:: yaml

        sv_heading_buttons:
          - ['Standard', 'Erweitert', 'Konfiguration']
          - ['Kochen', 'Kochen_Adv', 'Kochen_Cfg']
          - ['scene_cooking', 'scene_cooking_hob', 'vent_ventilation_level_manual_m']

sieht die Seite folgendermaßen aus:

.. figure:: assets/topnav_std2.jpg
   :alt: Seite mit Icons in der Top Navigation

Die Erweiterung des Attributs ``sv_heading_buttons`` muss natürlich in der Konfiguration von allen drei
Seiten vorgenommen werden.

|

