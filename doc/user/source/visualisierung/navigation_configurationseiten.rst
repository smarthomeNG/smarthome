.. index:: smartVISU Autogenerierung; Konfigurationsseiten

Navigation: Konfigurationsseiten
================================

Möglichkeiten
-------------

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
