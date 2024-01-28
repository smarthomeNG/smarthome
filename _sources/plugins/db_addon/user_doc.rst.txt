
.. index:: Plugins; db_addon (Datenbank Unterstützung)
.. index:: db_addon

========
db_addon
========

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left


Das Plugin bietet eine Funktionserweiterung zum Database Plugin und ermöglicht die einfache Auswertung von Messdaten.
Basierend auf den Daten in der Datenbank können bspw. Auswertungen zu Verbrauch (heute, gestern, ...) oder zu Minimal-
und Maximalwerten gefahren werden.
Diese Auswertungen werden zyklisch zum Tageswechsel, Wochenwechsel, Monatswechsel oder Jahreswechsel, in Abhängigkeit
der Funktion erzeugt.
Um die Zugriffe auf die Datenbank zu minimieren, werden diverse Daten zwischengespeichert.

Sind Items mit einem DatabaseAddon-Attribut im gleichen Pfad, wie das Item, für das das Database Attribut
konfiguriert ist, wird dieses Item automatisch ermittelt. Bedeutet: Sind die Items mit dem DatabaseAddon-Attribute Kinder
oder Kindeskinder oder Kindeskinderkinder des Items, für das das Database Attribut konfiguriert ist, wird dieses automatisch
ermittelt.

Alternativ kann mit dem Attribute "db_addon_database_item"  auch der absolute Pfad des Items angegeben werden, für das das Database Attribut konfiguriert ist.

.. code-block:: yaml

    temperatur:
        type: bool
        database: yes

        auswertung:
            type: foo

            heute_min:
                type: num
                db_addon_fct: heute_min

            gestern_max:
                type: num
                db_addon_fct: heute_minus1_max


    tagesmitteltemperatur_gestern:
        type: num
        db_addon_fct: heute_minus1_avg
        db_addon_database_item: 'temperatur'


Anforderungen
=============

Es muss das Database Plugin konfiguriert und aktiv sein. In den Plugin Parametern ist der Name der Konfiguration des
Database-Plugins anzugeben. Damit ist auch eine etwaig definierte Instanz des Database-Plugins definiert.
Die Konfiguration des DatabaseAddon-Plugin erfolgt automatisch bei Start.


Hinweis: Das Plugin selbst ist aktuell nicht multi-instance fähig. Das bedeutet, dass das Plugin aktuell nur eine Instanz
des Database-Plugin abgebunden werden kann.


Hinweise
========

 - Das Plugin startet die Berechnungen der Werte nach einer gewissen (konfigurierbaren) Zeit (Attribut `startup_run_delay`)
   nach dem Start von shNG, um den Startvorgang nicht zu beeinflussen.

 - Bei Start werden automatisch nur die Items berechnet, für das das Attribute `db_addon_startup` gesetzt wurde. Alle anderen
   Items werden erst zur konfigurierten Zeit berechnet. Das Attribute `db_addon_startup` kann auch direkt am `Database-Item`
   gesetzt werden. Dabei wird das Attribut auf alle darunter liegenden `db_addon-Items` (bspw. bei Verwendung von structs) vererbt.
   Über das WebIF kann die Berechnung aller definierten Items ausgelöst werden.

 - Für sogenannte `on_change` Items, also Items, deren Berechnung bis zum Jetzt (bspw. verbrauch-heute) gehen, wird die Berechnung
   immer bei eintreffen eines neuen Wertes gestartet. Zu Reduktion der Belastung auf die Datenbank werden die Werte für das Ende der
   letzten Periode gecached.

 - Berechnungen werden nur ausgeführt, wenn für den kompletten abgefragten Zeitraum Werte in der Datenbank vorliegen. Wird bspw.
   der Verbrauch des letzten Monats abgefragt wobei erst Werte ab dem 3. des Monats in der Datenbank sind, wird die Berechnung abgebrochen.

 - Mit dem Attribut `use_oldest_entry` kann dieses Verhalten verändert werden. Ist das Attribut gesetzt, wird, wenn für den
   Beginn der Abfragezeitraums keinen Werte vorliegen, der älteste Eintrag der Datenbank genutzt.

 - Für die Auswertung kann es nützlich sein, bestimmte Werte aus der Datenbank bei der Berechnung auszublenden. Hierfür stehen 2 Möglichkeiten zur Verfügung:

    - Plugin-Attribut `ignore_0`: (list of strings) Bei Items, bei denen ein String aus der Liste im Pfadnamen vorkommt,
      werden 0-Werte (val_num = 0) bei Datenbankauswertungen ignoriert. Hat also das Attribut den Wert ['temp'] werden bei allen Items mit
      'temp' im Pfadnamen die 0-Werte bei der Auswertung ignoriert.
    - Item-Attribut `db_addon_ignore_value`: (num) Dieser Wert wird bei der Abfrage bzw. Auswertung der Datenbank für dieses Item ignoriert.

 - Das Plugin enthält sehr ausführliche Logginginformation. Bei unerwartetem Verhalten, den LogLevel entsprechend anpassen, um mehr information zu erhalten.

 - Berechnungen des Plugins können im WebIF unterbrochen werden. Auch das gesamte Plugin kann pausiert werden. Dies kann bei starker Systembelastung nützlich sein.


mysql Datenbank
---------------

Bei Verwendung von mysql sollten einige Variablen der Datenbank angepasst werden, so dass die komplexeren Anfragen
ohne Fehler bearbeitet werden.

Dazu folgenden Block am Ende der Datei */etc/mysql/my.cnf* einfügen bzw den existierenden ergänzen.


.. code-block:: bash

    [mysqld]
    connect_timeout = 60
    net_read_timeout = 60
    wait_timeout = 28800
    interactive_timeout = 28800



Konfiguration
=============

Diese Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/db_addon` beschrieben.

Die folgenden Kapitel wurde automatisch durch Ausführen des Skripts in der Datei 'item_attributes_master.py' erstellt.

Nachfolgend eine Auflistung der möglichen Attribute für das Plugin im Format: Attribute: Beschreibung | Berechnungszyklus | Item-Type

db_addon_fct
------------

- verbrauch_heute: Verbrauch am heutigen Tag (Differenz zwischen aktuellem Wert und den Wert am Ende des vorherigen Tages) | Berechnung: onchange | Item-Type: num

- verbrauch_tag: Verbrauch am heutigen Tag (Differenz zwischen aktuellem Wert und den Wert am Ende des vorherigen Tages) | Berechnung: onchange | Item-Type: num

- verbrauch_woche: Verbrauch in der aktuellen Woche | Berechnung: onchange | Item-Type: num

- verbrauch_monat: Verbrauch im aktuellen Monat | Berechnung: onchange | Item-Type: num

- verbrauch_jahr: Verbrauch im aktuellen Jahr | Berechnung: onchange | Item-Type: num

- verbrauch_last_24h: Verbrauch innerhalb letzten 24h | Berechnung: hourly | Item-Type: num

- verbrauch_last_7d: Verbrauch innerhalb letzten 7 Tage | Berechnung: hourly | Item-Type: num

- verbrauch_heute_minus1: Verbrauch gestern (heute -1 Tag) (Differenz zwischen Wert am Ende des gestrigen Tages und dem Wert am Ende des Tages davor) | Berechnung: daily | Item-Type: num

- verbrauch_heute_minus2: Verbrauch vorgestern (heute -2 Tage) | Berechnung: daily | Item-Type: num

- verbrauch_heute_minus3: Verbrauch heute -3 Tage | Berechnung: daily | Item-Type: num

- verbrauch_heute_minus4: Verbrauch heute -4 Tage | Berechnung: daily | Item-Type: num

- verbrauch_heute_minus5: Verbrauch heute -5 Tage | Berechnung: daily | Item-Type: num

- verbrauch_heute_minus6: Verbrauch heute -6 Tage | Berechnung: daily | Item-Type: num

- verbrauch_heute_minus7: Verbrauch heute -7 Tage | Berechnung: daily | Item-Type: num

- verbrauch_heute_minus8: Verbrauch heute -8 Tage | Berechnung: daily | Item-Type: num

- verbrauch_tag_minus1: Verbrauch gestern (heute -1 Tag) (Differenz zwischen Wert am Ende des gestrigen Tages und dem Wert am Ende des Tages davor) | Berechnung: daily | Item-Type: num

- verbrauch_tag_minus2: Verbrauch vorgestern (heute -2 Tage) | Berechnung: daily | Item-Type: num

- verbrauch_tag_minus3: Verbrauch heute -3 Tage | Berechnung: daily | Item-Type: num

- verbrauch_tag_minus4: Verbrauch heute -4 Tage | Berechnung: daily | Item-Type: num

- verbrauch_tag_minus5: Verbrauch heute -5 Tage | Berechnung: daily | Item-Type: num

- verbrauch_tag_minus6: Verbrauch heute -6 Tage | Berechnung: daily | Item-Type: num

- verbrauch_tag_minus7: Verbrauch heute -7 Tage | Berechnung: daily | Item-Type: num

- verbrauch_tag_minus8: Verbrauch heute -8 Tage | Berechnung: daily | Item-Type: num

- verbrauch_woche_minus1: Verbrauch Vorwoche (aktuelle Woche -1) | Berechnung: weekly | Item-Type: num

- verbrauch_woche_minus2: Verbrauch aktuelle Woche -2 Wochen | Berechnung: weekly | Item-Type: num

- verbrauch_woche_minus3: Verbrauch aktuelle Woche -3 Wochen | Berechnung: weekly | Item-Type: num

- verbrauch_woche_minus4: Verbrauch aktuelle Woche -4 Wochen | Berechnung: weekly | Item-Type: num

- verbrauch_monat_minus1: Verbrauch Vormonat (aktueller Monat -1) | Berechnung: monthly | Item-Type: num

- verbrauch_monat_minus2: Verbrauch aktueller Monat -2 Monate | Berechnung: monthly | Item-Type: num

- verbrauch_monat_minus3: Verbrauch aktueller Monat -3 Monate | Berechnung: monthly | Item-Type: num

- verbrauch_monat_minus4: Verbrauch aktueller Monat -4 Monate | Berechnung: monthly | Item-Type: num

- verbrauch_monat_minus12: Verbrauch aktueller Monat -12 Monate | Berechnung: monthly | Item-Type: num

- verbrauch_jahr_minus1: Verbrauch Vorjahr (aktuelles Jahr -1 Jahr) | Berechnung: yearly | Item-Type: num

- verbrauch_jahr_minus2: Verbrauch aktuelles Jahr -2 Jahre | Berechnung: yearly | Item-Type: num

- verbrauch_rolling_12m_heute_minus1: Verbrauch der letzten 12 Monate ausgehend im Ende des letzten Tages | Berechnung: daily | Item-Type: num

- verbrauch_rolling_12m_tag_minus1: Verbrauch der letzten 12 Monate ausgehend im Ende des letzten Tages | Berechnung: daily | Item-Type: num

- verbrauch_rolling_12m_woche_minus1: Verbrauch der letzten 12 Monate ausgehend im Ende der letzten Woche | Berechnung: weekly | Item-Type: num

- verbrauch_rolling_12m_monat_minus1: Verbrauch der letzten 12 Monate ausgehend im Ende des letzten Monats | Berechnung: monthly | Item-Type: num

- verbrauch_rolling_12m_jahr_minus1: Verbrauch der letzten 12 Monate ausgehend im Ende des letzten Jahres | Berechnung: yearly | Item-Type: num

- verbrauch_jahreszeitraum_minus1: Verbrauch seit dem 1.1. bis zum heutigen Tag des Vorjahres | Berechnung: daily | Item-Type: num

- verbrauch_jahreszeitraum_minus2: Verbrauch seit dem 1.1. bis zum heutigen Tag vor 2 Jahren | Berechnung: daily | Item-Type: num

- verbrauch_jahreszeitraum_minus3: Verbrauch seit dem 1.1. bis zum heutigen Tag vor 3 Jahren | Berechnung: daily | Item-Type: num

- zaehlerstand_heute_minus1: Zählerstand / Wert am Ende des letzten Tages (heute -1 Tag) | Berechnung: daily | Item-Type: num

- zaehlerstand_heute_minus2: Zählerstand / Wert am Ende des vorletzten Tages (heute -2 Tag) | Berechnung: daily | Item-Type: num

- zaehlerstand_heute_minus3: Zählerstand / Wert am Ende des vorvorletzten Tages (heute -3 Tag) | Berechnung: daily | Item-Type: num

- zaehlerstand_tag_minus1: Zählerstand / Wert am Ende des letzten Tages (heute -1 Tag) | Berechnung: daily | Item-Type: num

- zaehlerstand_tag_minus2: Zählerstand / Wert am Ende des vorletzten Tages (heute -2 Tag) | Berechnung: daily | Item-Type: num

- zaehlerstand_tag_minus3: Zählerstand / Wert am Ende des vorvorletzten Tages (heute -3 Tag) | Berechnung: daily | Item-Type: num

- zaehlerstand_woche_minus1: Zählerstand / Wert am Ende der vorvorletzten Woche (aktuelle Woche -1 Woche) | Berechnung: weekly | Item-Type: num

- zaehlerstand_woche_minus2: Zählerstand / Wert am Ende der vorletzten Woche (aktuelle Woche -2 Wochen) | Berechnung: weekly | Item-Type: num

- zaehlerstand_woche_minus3: Zählerstand / Wert am Ende der aktuellen Woche -3 Wochen | Berechnung: weekly | Item-Type: num

- zaehlerstand_monat_minus1: Zählerstand / Wert am Ende des letzten Monates (aktueller Monat -1 Monat) | Berechnung: monthly | Item-Type: num

- zaehlerstand_monat_minus2: Zählerstand / Wert am Ende des vorletzten Monates (aktueller Monat -2 Monate) | Berechnung: monthly | Item-Type: num

- zaehlerstand_monat_minus3: Zählerstand / Wert am Ende des aktuellen Monats -3 Monate | Berechnung: monthly | Item-Type: num

- zaehlerstand_jahr_minus1: Zählerstand / Wert am Ende des letzten Jahres (aktuelles Jahr -1 Jahr) | Berechnung: yearly | Item-Type: num

- zaehlerstand_jahr_minus2: Zählerstand / Wert am Ende des vorletzten Jahres (aktuelles Jahr -2 Jahre) | Berechnung: yearly | Item-Type: num

- zaehlerstand_jahr_minus3: Zählerstand / Wert am Ende des aktuellen Jahres -3 Jahre | Berechnung: yearly | Item-Type: num

- minmax_last_24h_min: minimaler Wert der letzten 24h | Berechnung: daily | Item-Type: num

- minmax_last_24h_max: maximaler Wert der letzten 24h | Berechnung: daily | Item-Type: num

- minmax_last_24h_avg: durchschnittlicher Wert der letzten 24h | Berechnung: daily | Item-Type: num

- minmax_last_7d_min: minimaler Wert der letzten 7 Tage | Berechnung: daily | Item-Type: num

- minmax_last_7d_max: maximaler Wert der letzten 7 Tage | Berechnung: daily | Item-Type: num

- minmax_last_7d_avg: durchschnittlicher Wert der letzten 7 Tage | Berechnung: daily | Item-Type: num

- minmax_heute_min: Minimalwert seit Tagesbeginn | Berechnung: onchange | Item-Type: num

- minmax_heute_max: Maximalwert seit Tagesbeginn | Berechnung: onchange | Item-Type: num

- minmax_heute_avg: Durschnittswert seit Tagesbeginn | Berechnung: onchange | Item-Type: num

- minmax_heute_minus1_min: Minimalwert gestern (heute -1 Tag) | Berechnung: daily | Item-Type: num

- minmax_heute_minus1_max: Maximalwert gestern (heute -1 Tag) | Berechnung: daily | Item-Type: num

- minmax_heute_minus1_avg: Durchschnittswert gestern (heute -1 Tag) | Berechnung: daily | Item-Type: num

- minmax_heute_minus2_min: Minimalwert vorgestern (heute -2 Tage) | Berechnung: daily | Item-Type: num

- minmax_heute_minus2_max: Maximalwert vorgestern (heute -2 Tage) | Berechnung: daily | Item-Type: num

- minmax_heute_minus2_avg: Durchschnittswert vorgestern (heute -2 Tage) | Berechnung: daily | Item-Type: num

- minmax_heute_minus3_min: Minimalwert heute vor 3 Tagen | Berechnung: daily | Item-Type: num

- minmax_heute_minus3_max: Maximalwert heute vor 3 Tagen | Berechnung: daily | Item-Type: num

- minmax_heute_minus3_avg: Durchschnittswert heute vor 3 Tagen | Berechnung: daily | Item-Type: num

- minmax_tag_min: Minimalwert seit Tagesbeginn | Berechnung: onchange | Item-Type: num

- minmax_tag_max: Maximalwert seit Tagesbeginn | Berechnung: onchange | Item-Type: num

- minmax_tag_avg: Durschnittswert seit Tagesbeginn | Berechnung: onchange | Item-Type: num

- minmax_tag_minus1_min: Minimalwert gestern (heute -1 Tag) | Berechnung: daily | Item-Type: num

- minmax_tag_minus1_max: Maximalwert gestern (heute -1 Tag) | Berechnung: daily | Item-Type: num

- minmax_tag_minus1_avg: Durchschnittswert gestern (heute -1 Tag) | Berechnung: daily | Item-Type: num

- minmax_tag_minus2_min: Minimalwert vorgestern (heute -2 Tage) | Berechnung: daily | Item-Type: num

- minmax_tag_minus2_max: Maximalwert vorgestern (heute -2 Tage) | Berechnung: daily | Item-Type: num

- minmax_tag_minus2_avg: Durchschnittswert vorgestern (heute -2 Tage) | Berechnung: daily | Item-Type: num

- minmax_tag_minus3_min: Minimalwert heute vor 3 Tagen | Berechnung: daily | Item-Type: num

- minmax_tag_minus3_max: Maximalwert heute vor 3 Tagen | Berechnung: daily | Item-Type: num

- minmax_tag_minus3_avg: Durchschnittswert heute vor 3 Tagen | Berechnung: daily | Item-Type: num

- minmax_woche_min: Minimalwert seit Wochenbeginn | Berechnung: onchange | Item-Type: num

- minmax_woche_max: Maximalwert seit Wochenbeginn | Berechnung: onchange | Item-Type: num

- minmax_woche_minus1_min: Minimalwert Vorwoche (aktuelle Woche -1) | Berechnung: weekly | Item-Type: num

- minmax_woche_minus1_max: Maximalwert Vorwoche (aktuelle Woche -1) | Berechnung: weekly | Item-Type: num

- minmax_woche_minus1_avg: Durchschnittswert Vorwoche (aktuelle Woche -1) | Berechnung: weekly | Item-Type: num

- minmax_woche_minus2_min: Minimalwert aktuelle Woche -2 Wochen | Berechnung: weekly | Item-Type: num

- minmax_woche_minus2_max: Maximalwert aktuelle Woche -2 Wochen | Berechnung: weekly | Item-Type: num

- minmax_woche_minus2_avg: Durchschnittswert aktuelle Woche -2 Wochen | Berechnung: weekly | Item-Type: num

- minmax_monat_min: Minimalwert seit Monatsbeginn | Berechnung: onchange | Item-Type: num

- minmax_monat_max: Maximalwert seit Monatsbeginn | Berechnung: onchange | Item-Type: num

- minmax_monat_minus1_min: Minimalwert Vormonat (aktueller Monat -1) | Berechnung: monthly | Item-Type: num

- minmax_monat_minus1_max: Maximalwert Vormonat (aktueller Monat -1) | Berechnung: monthly | Item-Type: num

- minmax_monat_minus1_avg: Durchschnittswert Vormonat (aktueller Monat -1) | Berechnung: monthly | Item-Type: num

- minmax_monat_minus2_min: Minimalwert aktueller Monat -2 Monate | Berechnung: monthly | Item-Type: num

- minmax_monat_minus2_max: Maximalwert aktueller Monat -2 Monate | Berechnung: monthly | Item-Type: num

- minmax_monat_minus2_avg: Durchschnittswert aktueller Monat -2 Monate | Berechnung: monthly | Item-Type: num

- minmax_jahr_min: Minimalwert seit Jahresbeginn | Berechnung: onchange | Item-Type: num

- minmax_jahr_max: Maximalwert seit Jahresbeginn | Berechnung: onchange | Item-Type: num

- minmax_jahr_minus1_min: Minimalwert Vorjahr (aktuelles Jahr -1 Jahr) | Berechnung: yearly | Item-Type: num

- minmax_jahr_minus1_max: Maximalwert Vorjahr (aktuelles Jahr -1 Jahr) | Berechnung: yearly | Item-Type: num

- minmax_jahr_minus1_avg: Durchschnittswert Vorjahr (aktuelles Jahr -1 Jahr) | Berechnung: yearly | Item-Type: num

- tagesmitteltemperatur_heute: Tagesmitteltemperatur heute | Berechnung: onchange | Item-Type: num

- tagesmitteltemperatur_heute_minus1: Tagesmitteltemperatur des letzten Tages (heute -1 Tag) | Berechnung: daily | Item-Type: num

- tagesmitteltemperatur_heute_minus2: Tagesmitteltemperatur des vorletzten Tages (heute -2 Tag) | Berechnung: daily | Item-Type: num

- tagesmitteltemperatur_heute_minus3: Tagesmitteltemperatur des vorvorletzten Tages (heute -3 Tag) | Berechnung: daily | Item-Type: num

- tagesmitteltemperatur_tag: Tagesmitteltemperatur heute | Berechnung: onchange | Item-Type: num

- tagesmitteltemperatur_tag_minus1: Tagesmitteltemperatur des letzten Tages (heute -1 Tag) | Berechnung: daily | Item-Type: num

- tagesmitteltemperatur_tag_minus2: Tagesmitteltemperatur des vorletzten Tages (heute -2 Tag) | Berechnung: daily | Item-Type: num

- tagesmitteltemperatur_tag_minus3: Tagesmitteltemperatur des vorvorletzten Tages (heute -3 Tag) | Berechnung: daily | Item-Type: num

- serie_minmax_monat_min_15m: monatlicher Minimalwert der letzten 15 Monate (gleitend) | Berechnung: monthly | Item-Type: list

- serie_minmax_monat_max_15m: monatlicher Maximalwert der letzten 15 Monate (gleitend) | Berechnung: monthly | Item-Type: list

- serie_minmax_monat_avg_15m: monatlicher Mittelwert der letzten 15 Monate (gleitend) | Berechnung: monthly | Item-Type: list

- serie_minmax_woche_min_30w: wöchentlicher Minimalwert der letzten 30 Wochen (gleitend) | Berechnung: weekly | Item-Type: list

- serie_minmax_woche_max_30w: wöchentlicher Maximalwert der letzten 30 Wochen (gleitend) | Berechnung: weekly | Item-Type: list

- serie_minmax_woche_avg_30w: wöchentlicher Mittelwert der letzten 30 Wochen (gleitend) | Berechnung: weekly | Item-Type: list

- serie_minmax_tag_min_30d: täglicher Minimalwert der letzten 30 Tage (gleitend) | Berechnung: daily | Item-Type: list

- serie_minmax_tag_max_30d: täglicher Maximalwert der letzten 30 Tage (gleitend) | Berechnung: daily | Item-Type: list

- serie_minmax_tag_avg_30d: täglicher Mittelwert der letzten 30 Tage (gleitend) | Berechnung: daily | Item-Type: list

- serie_verbrauch_tag_30d: Verbrauch pro Tag der letzten 30 Tage | Berechnung: daily | Item-Type: list

- serie_verbrauch_woche_30w: Verbrauch pro Woche der letzten 30 Wochen | Berechnung: weekly | Item-Type: list

- serie_verbrauch_monat_18m: Verbrauch pro Monat der letzten 18 Monate | Berechnung: monthly | Item-Type: list

- serie_zaehlerstand_tag_30d: Zählerstand am Tagesende der letzten 30 Tage | Berechnung: daily | Item-Type: list

- serie_zaehlerstand_woche_30w: Zählerstand am Wochenende der letzten 30 Wochen | Berechnung: weekly | Item-Type: list

- serie_zaehlerstand_monat_18m: Zählerstand am Monatsende der letzten 18 Monate | Berechnung: monthly | Item-Type: list

- serie_waermesumme_monat_24m: monatliche Wärmesumme der letzten 24 Monate | Berechnung: monthly | Item-Type: list

- serie_kaeltesumme_monat_24m: monatliche Kältesumme der letzten 24 Monate | Berechnung: monthly | Item-Type: list

- serie_tagesmittelwert_0d: Tagesmittelwert für den aktuellen Tag | Berechnung: daily | Item-Type: list

- serie_tagesmittelwert_stunde_0d: Stundenmittelwert für den aktuellen Tag | Berechnung: daily | Item-Type: list

- serie_tagesmittelwert_stunde_30_0d: Stundenmittelwert für den aktuellen Tag | Berechnung: daily | Item-Type: list

- serie_tagesmittelwert_tag_stunde_30d: Stundenmittelwert pro Tag der letzten 30 Tage (bspw. zur Berechnung der Tagesmitteltemperatur basierend auf den Mittelwert der Temperatur pro Stunde | Berechnung: daily | Item-Type: list

- general_oldest_value: Ausgabe des ältesten Wertes des entsprechenden "Parent-Items" mit database Attribut | Berechnung: no | Item-Type: num

- general_oldest_log: Ausgabe des Timestamp des ältesten Eintrages des entsprechenden "Parent-Items" mit database Attribut | Berechnung: no | Item-Type: list

- kaeltesumme: Berechnet die Kältesumme für einen Zeitraum, db_addon_params: (year=optional, month=optional) | Berechnung: daily | Item-Type: num

- waermesumme: Berechnet die Wärmesumme für einen Zeitraum, db_addon_params: (year=optional, month=optional) | Berechnung: daily | Item-Type: num

- gruenlandtempsumme: Berechnet die Grünlandtemperatursumme für einen Zeitraum, db_addon_params: (year=optional) | Berechnung: daily | Item-Type: num

- wachstumsgradtage: Berechnet die Wachstumsgradtage auf Basis der stündlichen Durchschnittswerte eines Tages für das laufende Jahr mit an Angabe des Temperaturschwellenwertes (threshold=Schwellentemperatur) | Berechnung: daily | Item-Type: num

- wuestentage: Berechnet die Anzahl der Wüstentage des Jahres, db_addon_params: (year=optional) | Berechnung: daily | Item-Type: num

- heisse_tage: Berechnet die Anzahl der heissen Tage des Jahres, db_addon_params: (year=optional) | Berechnung: daily | Item-Type: num

- tropennaechte: Berechnet die Anzahl der Tropennächte des Jahres, db_addon_params: (year=optional) | Berechnung: daily | Item-Type: num

- sommertage: Berechnet die Anzahl der Sommertage des Jahres, db_addon_params: (year=optional) | Berechnung: daily | Item-Type: num

- heiztage: Berechnet die Anzahl der Heiztage des Jahres, db_addon_params: (year=optional) | Berechnung: daily | Item-Type: num

- vegetationstage: Berechnet die Anzahl der Vegatationstage des Jahres, db_addon_params: (year=optional) | Berechnung: daily | Item-Type: num

- frosttage: Berechnet die Anzahl der Frosttage des Jahres, db_addon_params: (year=optional) | Berechnung: daily | Item-Type: num

- eistage: Berechnet die Anzahl der Eistage des Jahres, db_addon_params: (year=optional) | Berechnung: daily | Item-Type: num

- tagesmitteltemperatur: Berechnet die Tagesmitteltemperatur auf Basis der stündlichen Durchschnittswerte eines Tages für die angegebene Anzahl von Tagen (timeframe=day, count=integer) | Berechnung: daily | Item-Type: list

- db_request: Abfrage der DB: db_addon_params: (func=mandatory, item=mandatory, timespan=mandatory, start=optional, end=optional, count=optional, group=optional, group2=optional) | Berechnung: group | Item-Type: list

- minmax: Berechnet einen min/max/avg Wert für einen bestimmen Zeitraum:  db_addon_params: (func=mandatory, timeframe=mandatory, start=mandatory) | Berechnung: timeframe | Item-Type: num

- minmax_last: Berechnet einen min/max/avg Wert für ein bestimmtes Zeitfenster von jetzt zurück:  db_addon_params: (func=mandatory, timeframe=mandatory, start=mandatory, end=mandatory) | Berechnung: timeframe | Item-Type: num

- verbrauch: Berechnet einen Verbrauchswert für einen bestimmen Zeitraum:  db_addon_params: (timeframe=mandatory, start=mandatory end=mandatory) | Berechnung: timeframe | Item-Type: num

- zaehlerstand: Berechnet einen Zählerstand für einen bestimmen Zeitpunkt:  db_addon_params: (timeframe=mandatory, start=mandatory) | Berechnung: timeframe | Item-Type: num


db_addon_info
-------------

- db_version: Version der verbundenen Datenbank | Berechnung: no | Item-Type: str


db_addon_admin
--------------

- suspend: Unterbricht die Aktivitäten des Plugin | Berechnung: no | Item-Type: bool

- recalc_all: Startet einen Neuberechnungslauf aller on-demand Items | Berechnung: no | Item-Type: bool

- clean_cache_values: Löscht Plugin-Cache und damit alle im Plugin zwischengespeicherten Werte | Berechnung: no | Item-Type: bool



Beispiele
=========

Verbrauch
---------

Soll bspw. der Verbrauch von Wasser ausgewertet werden, so ist dies wie folgt möglich:


.. code-block:: yaml

    wasserzaehler:
        zaehlerstand:
            type: num
            knx_dpt: 12
            knx_cache: 5/3/4
            eval: round(value/1000, 1)
            database: init
            struct:
                  - db_addon.verbrauch_1
                  - db_addon.verbrauch_2
                  - db_addon.zaehlerstand_1

Die Werte des Wasserzählerstandes werden in die Datenbank geschrieben und darauf basierend ausgewertet. Die structs
'db_addon.verbrauch_1' und 'db_addon.verbrauch_2' stellen entsprechende Items für die Verbrauchsauswerten zur Verfügung.


minmax
------

Soll bspw. die minimalen und maximalen Temperaturen ausgewertet werden, kann dies so umgesetzt werden:

.. code-block:: yaml

    temperature:
        aussen:
            nord:
                name: Außentemp Nordseite
                type: num
                visu_acl: ro
                knx_dpt: 9
                knx_cache: 6/5/1
                database: init
                struct:
                  - db_addon.minmax_1
                  - db_addon.minmax_2

Die Temperaturwerte werden in die Datenbank geschrieben und darauf basierend ausgewertet. Die structs
'db_addon.minmax_1' und 'db_addon.minmax_2' stellen entsprechende Items für die min/max Auswertung zur Verfügung.


Verwendung von eigenen Zeiträumen
---------------------------------

Die Verwendung vorgefertigter Attribute wie bspw "minmax_tag_minus1" bieten eine gute und einfache Möglichkeit, entsprechende Werte ermitteln zu lassen.
Mehr Möglichkeiten bieten die Attribute "minmax", "minmax_last", "zaehlerstand" und "verbrauch". Hier müssen die weiteren Parameterwerte über das Attribut
"db_addon_params_dict" oder "db_addon_params" definiert werden.

Bei Verwendung von "db_addon_params" müssen die Parameter im Format 'kwargs' eingerahmt von Quotes angegeben werden: 'func=min, timeframe=day'
Bei Verwendung von "db_addon_params_dict" müssen die Parameter im Format 'dicht' eingerahmt von Quotes angegeben werden: "{'func': 'min', 'timeframe': 'day', 'start': 1}"

Hier ein Beispiel:

.. code-block:: yaml

        temperature:
            type: num

            minmax_test_min_gestern:
                name: Minimaler Wert gestern
                type: num
                db_addon_fct: minmax
                db_addon_params_dict: "{'func': 'min', 'timeframe': 'day', 'start': 1}"
                db_addon_startup: yes

minmax
------

Berechnet einen min/max/avg Wert für einen bestimmen Zeitraum.
In den db_addon_params müssen folgenden Parameter definiert sein:

- func: min/max/avg
- timeframe: day/week/month/year
- start: integer wert

Hier ein Beispiel:

.. code-block:: yaml

        minmax_min_gestern:
            name: Minimaler Wert gestern
            type: num
            db_addon_fct: minmax
            db_addon_params_dict: "{'func': 'min', 'timeframe': 'day', 'start': 1}"


minmax_last
-----------
'Berechnet einen min/max/avg Wert für ein bestimmtes Zeitfenster von jetzt zurück.
In den db_addon_params müssen folgenden Parameter definiert sein:

- func: min/max/avg
- timeframe: day/week/month/year
- start: integer wert
- end: integer wert

.. code-block:: yaml

        minmax_last_21:
            type: num
            db_addon_fct: minmax_last
            db_addon_params_dict: "{'func': 'min', 'timeframe': 'day', 'start': 2, 'end': 1}"


verbrauch
---------
Berechnet einen Verbrauchswert für einen bestimmen Zeitraum:

- timeframe: day/week/month/year
- start: integer wert
- end: integer wert

.. code-block:: yaml

        verbrauch_gestern:
            type: num
            db_addon_fct: verbrauch
            db_addon_params_dict: "{'timeframe': 'day', 'start': 2, 'end': 1}"


zaehlerstand
------------

Berechnet einen Zählerstand für einen bestimmen Zeitpunkt:

- timeframe: day/week/month/year
- start: integer wert

.. code-block:: yaml

        zaehlerstand_gestern:
            type: num
            db_addon_fct: zaehlerstand
            db_addon_params_dict: "{'timeframe': 'day', 'start': 1}"


Web Interface
=============

Das WebIF stellt neben der Ansicht verbundener Items und deren Parameter und Werte auch Funktionen für die
Administration des Plugins bereit.

Es stehen Button für:

- Neuberechnung aller Items
- Abbruch eines aktiven Berechnungslaufes
- Pausieren des Plugins
- Wiederaufnahme des Plugins

bereit.

.. warning::

    Das Auslösen einer kompletten Neuberechnung aller Items kann zu einer starken Belastung der Datenbank
    aufgrund vieler Leseanfragen führen.


db_addon Items
--------------

Dieser Reiter des Webinterface zeigt die Items an, für die ein DatabaseAddon Attribut konfiguriert ist.


db_addon Maintenance
--------------------

Das Webinterface zeigt detaillierte Informationen über die im Plugin verfügbaren Daten an.
Dies dient der Maintenance bzw. Fehlersuche. Dieser Tab ist nur bei Log-Level "Debug" verfügbar.


Erläuterungen zu Temperatursummen
=================================


Grünlandtemperatursumme
-----------------------

Beim Grünland wird die Wärmesumme nach Ernst und Loeper benutzt, um den Vegetationsbeginn und somit den Termin von Düngungsmaßnahmen zu bestimmen.
Dabei erfolgt die Aufsummierung der Tagesmitteltemperaturen über 0 °C, wobei der Januar mit 0.5 und der Februar mit 0.75 gewichtet wird.
Bei einer Wärmesumme von 200 Grad ist eine Düngung angesagt.

Siehe: `Wikipedia Grünlandtemperatursumme <https://de.wikipedia.org/wiki/Gr%C3%BCnlandtemperatursumme>`_

Folgende Parameter sind möglich / notwendig:


.. code-block:: yaml

    db_addon_params: "year=current"

- year: Jahreszahl (str oder int), für das die Berechnung ausgeführt werden soll oder "current" für aktuelles Jahr  (default: 'current')


Wachstumsgradtag
----------------
Der Begriff Wachstumsgradtage (WGT) ist ein Überbegriff für verschiedene Größen.
Gemeinsam ist ihnen, daß zur Berechnung eine Lufttemperatur von einem Schwellenwert subtrahiert wird.
Je nach Fragestellung und Pflanzenart werden der Schwellenwert unterschiedlich gewählt und die Temperatur unterschiedlich bestimmt.
Verfügbar sind die Berechnung über 0) "einfachen Durchschnitt der Tagestemperaturen", 1) "modifizierten Durchschnitt der Tagestemperaturen"
und 2) Anzahl der Tage, deren Mitteltempertatur oberhalb der Schwellentemperatur lag.

siehe `Wikipedia Wachstumsgradtag <https://de.wikipedia.org/wiki/Wachstumsgradtag>`_

Folgende Parameter sind möglich / notwendig:

.. code-block:: yaml

    db_addon_params: "year=current, method=1, threshold=10"

- year: Jahreszahl (str oder int), für das die Berechnung ausgeführt werden soll oder "current" für aktuelles Jahr  (default: 'current')
- method: 0-Berechnung über "einfachen Durchschnitt der Tagestemperaturen", 1-Berechnung über "modifizierten Durchschnitt (default: 0) der Tagestemperaturen" 2-Anzahl der Tage, mit Mitteltempertatur oberhalb Schwellentemperatur// 10, 11 Ausgabe aus Zeitserie
- threshold: Schwellentemperatur in °C (int) (default: 10)


Wärmesumme
----------

Die Wärmesumme soll eine Aussage über den Sommer und die Pflanzenreife liefern. Es gibt keine eindeutige Definition der Größe "Wärmesumme".
Berechnet wird die Wärmesumme als Summe aller Tagesmitteltemperaturen über einem Schwellenwert ab dem 1.1. des Jahres.

siehe `Wikipedia Wärmesumme <https://de.wikipedia.org/wiki/W%C3%A4rmesumme>`_

Folgende Parameter sind möglich / notwendig:

.. code-block:: yaml

    db_addon_params: "year=current, month=1, threshold=10"

- year: Jahreszahl (str oder int), für das die Berechnung ausgeführt werden soll oder "current" für aktuelles Jahr (default: 'current')
- month: Monat (int) des Jahres, für das die Berechnung ausgeführt werden soll (optional) (default: None)
- threshold: Schwellentemperatur in °C (int) (default: 10)


Kältesumme
----------

Die Kältesumme soll eine Aussage über die Härte des Winters liefern.
Berechnet wird die Kältesumme als Summe aller negativen Tagesmitteltemperaturen ab dem 21.9. des Jahres bis 31.3. des Folgejahres.

siehe `Wikipedia Kältesumme <https://de.wikipedia.org/wiki/K%C3%A4ltesumme>`_

Folgende Parameter sind möglich / notwendig:

.. code-block:: yaml

    db_addon_params: "year=current, month=1"

- year: Jahreszahl (str oder int), für das die Berechnung ausgeführt werden soll oder "current" für aktuelles Jahr (default: 'current')
- month: Monat (int) des Jahres, für das die Berechnung ausgeführt werden soll (optional) (default: None)


Tagesmitteltemperatur
---------------------

Die Tagesmitteltemperatur wird auf Basis der stündlichen Durchschnittswerte eines Tages (aller in der DB enthaltenen Datensätze)
für die angegebene Anzahl von Tagen (days=optional) berechnet.



Vorgehen bei Funktionserweiterung des Plugins bzw. Ergänzung weiterer Werte für Item-Attribute
----------------------------------------------------------------------------------------------

Aufgrund der Vielzahl der möglichen Werte der Itemattribute, insbesondere des Itemattributes `db_addon_fct`, wurde die Erstellung/Update
der entsprechenden Teile der `plugin.yam` sowie die Erstellung der Datei `item_attributes.py`, die vom Plugin verwendet wird, automatisiert.

Die Masterinformationen für alle Itemattribute sowie die Skripte zum Erstellen/Update der beiden Dateien sind in der
Datei `item_attributes_master.py` enthalten.

.. important::

    Korrekturen, Erweiterungen etc. der Itemattribute sollten nur in der Datei `item_attributes_master.py`
    im Dict der Variable `ITEM_ATTRIBUTS` vorgenommen werden. Das Ausführen der Datei `item_attributes_master.py` (main)
    erstellt die `item_attributes.py` und aktualisiert die `plugin.yaml` entsprechend.
