Aufbau der Konfigurationsdateien
================================

Die Konfiguration von SmartHomeNG erfolgt über Dateien. Die
Funktionalität wird für **Items**, **Logiken** und **Plugins** in
jeweils eigenen Konfigurationsdateien vorgenommen.

Diese Seite beschäftigt sich mit dem grundlegenden Format der
Konfigurationsdateien. Für die vollständigen
Konfigurationsmöglichkeiten, bitte auf den jeweiligen Wiki Seiten
nachsehen.

Seit dem Release 1.3 von SmartHomeNG können zur Konfiguration von
**Items**, **Logiken** und **Plugins** auch Dateien im YAML Format
eingesetzt werden. Dieses ist das ab Release 1.5 das Standardformat. Das
Format der YAML Dateien (Endung **.yaml**) wird im folgenden
beschrieben.

Bisher erfolgt die Konfiguration in **.conf** Dateien in einem
smarthome-spezifischen Format. Das **.conf** Format wird noch weiterhin
unterstützt. Dokumentiert wird jedoch nur noch das **yaml** Format. Das
**.conf** Format wird ab einem späteren Release (voraussichtlich v2.0)
nicht mehr unterstützt werden.

Ganz neu war die Nutzung des YAML Formats für SmartHomeNG im Release 1.3
nicht. Seit dem Übergang von smarthome.py zu SmartHomeNG wird bereits
dass Logging in einer YAML Datei konfiguriert.

Zur Konvertierung von **.conf** in **.yaml** Dateien, ist ab Release 1.3
von SmartHomeNG ein Tool beigefügt, welches diese Konvertierung für die
Item Dateien durchführt.

**.conf** und **.yaml** Dateien können gemischt eingesetzt werden. Es
ist dabei unbedingt darauf zu achten, dass keine Konfiguration doppelt
(1 mal in .conf und 1 mal in .yaml) vorgenommen wird bzw. von
SmartHomeNG eingelesen werden kann. Es darf für Plugins und Logiken also
nur entweder eine .conf oder .yaml Datei geben. Sollte doch eine .conf
und eine .yaml Datei für Plugins oder Logiken im /etc Verzeichnis
liegen, so wird die .conf Datei ignoriert und die Konfiguration aus der
.yaml Datei gelesen. Im Items-Verzeichnis können beide Dateitypen
gleichzeitig vorkommen. Hier ist bei der Umstellung nur darauf zu
achten, dass nicht aus Versehen ein Item sowohl in einer .conf **und**
einer .yaml Datei definiert ist.

Altes Dateiformat - .conf Dateien
---------------------------------

Die .conf Dateien bestehen aus einer Reihe von Sektionen (Plugin- bzw.
Logikdefinitionen), die Key/Value-Listen enthalten. Für Plugins und
Logiken sind Sektionen nur auf der obersten Ebene zulässig.

::

   [section1]
       key1 = value1
       key2 = value2

   [section2]
       key3 = value3
       key4 = value4

Für Items können Sektionen (Itemdefinitionen) weitere Unter-Sektionen
(weitere Itemdefinitionen) enthalten.

::

   [section]
       key1 = value1
       key2 = value2

       [[subsection]]
           key3 = value3

           [[[sub_subsection]]]
               key4 = value4

Vorteile von YAML
-----------------

-  Standard Dateiformat
-  bessere Lesbarkeit
-  Tools zur formalen Prüfung der YAML-Konformität von Dateien verfügbar
-  leichtere Editierbarkeit:

   -  Sytax Highlighting mit diversen Editoren möglich
   -  Code-Faltung zur besser Übersicht in großen Dateien mit diversen
      Editoren möglich
   -  Ein- und Ausrücken von Items (bzw. Item-Strukturen) mit diversen
      einfach möglich, ohne Notwendigkeit weiterer Anpassungen (Anzahl
      eckiger Klammern bei jedem bewegtem Item)

Neues Dateiformat - .yaml Dateien
---------------------------------

Das YAML Format wird erst ab SmartHomeNG **Release 1.3** unterstützt
(werden).

Dieser Abschnitt beschäftigt sich nur mit den Teilen der
Markup-Language, die für SmartHomeNG relevant sind. Bei einem
weitergehenden Interesse an YAML, bitte auf Wikipedia oder
`yaml.org <http://yaml.org>`__ (auf Englisch) nachlesen. Der aktuell in
SmartHomeNG eingesetzte Parser unterstützt die YAML Version 1.1.

Im YAML Format sehen die Beschreibungen für **Plugins** und **Logiken**
dann folgendermaßen aus:

.. code-block:: yaml

   section1:
       key1: value1
       key2: value2

   section2:
       key3: value3
       key4: value4

Und die Beschreibungen für **Items** sehen so aus:

.. code-block:: yaml

   section:
       key1: value1
       key2: value2

       subsection:
           key3: value3

           sub_subsection:
               key4: value4

Wichtig ist dabei folgendes: - In YAML Dateien sind keine TABs erlaubt.
Es müssen Leerzeichen verwendet werden. - Im Gegensatz zu
Item\ **.conf** Dateien, bei denen die Struktur durch die Anzahl eckiger
Klammern um den Sektions(Item)-Namen bestimmt wird, wird die Struktur
einer YAML Datei durch Einrückungen bestimmt. - Der Doppelpunkt, der
einem Sektions-/Key-Namen folgt, kann direkt nach diesem Namen folgen.
Er **muss** jedoch von einem Leerzeichen gefolgt werden

Formate von Values in YAML Dateien
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Values können in YAML Dateien alles, von einfachen Werten über binäre
Daten bis hin zu Python Objekten sein. Für die Konfigurationsdateien
werden folgende Value-Typen unterstützt:

-  Numerische Werte
-  Strings
-  Listen

Besonderheiten boolscher Werte
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

SmartHomeNG verarbeitet, wie schon smarthome.py, die Values als Strings.
Dies gilt insbesondere bei der Übergabe von Werten an Plugins. Das ist
besonders bei der Angabe boolscher Werte zu beachten. Da der YAML Parser
bei einer Angabe wie **``boolwert: true``** einen boolschen Wert in die
Item Hierarchie von SmartHomeNG schreiben würde, muss durch Quotes
sichergestellt werden, dass ein String übergeben wird, also
folgendermaßen: **``boolwert: 'true'``**.

YAML interpretiert bis inclusive Version 1.1 auch **yes** und **no** als
boolsche Werte. Deshalb müssen auch diese Werte in Quotes eingeschlossen
werden. Es ist empfehlenswert nur **true** und **false** für boolsche
Werte zu verwenden.

Besonderheiten bei der Angabe von Wertelisten
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Im Gegensatz zu den bisherigen .conf Dateien, in denen Wertelisten auf
einer Zeile spezifiziert wurden und die Werte durch ein ‘\|’-Zeichen
getrennt wurden, ist die Spezifikation in einer YAML Datei vorzugsweise
mehrzeilig.

Statt

::

       [section]
           key1 = value1 | value2

gibt man jetzt folgendes an:

.. code-block:: yaml

   section:
      key1:
         - value1
         - value2

Beispiel von Item Definitionen in YAML
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   # items.yaml
   wohnung:
       kochen:
           strahler:
               name: Strahler Küchenwand
               type: bool
               knx_dpt: 1
               knx_send: 1/1/6
               knx_init: 1/2/6

               level:
                   type: num
                   knx_dpt: 5
                   knx_send: 1/4/6
                   knx_init: 1/5/6

   # ...

           kochfeldgesamt:
               name: Kochfeld Gesamt
               watt:
                   type: num
                   sqlite: 'true'
                   eval: sh.wohnung.kochen.kochfeld1.watt() + sh.wohnung.kochen.kochfeld2.watt()
                   eval_trigger:
                   - wohnung.kochen.kochfeld1.watt
                   - wohnung.kochen.kochfeld2.watt

In YAML Dateien können String-Values mehrzeilig sein. Der lesbarste Weg
ist es, den String-Value mit einem ‘\|’-Zeichen anfangen zu lassen und
den eigentlichen Wert auf der Folgezeile zu beginnen. Der gesamte String
muss/darf dann nicht in Single-Quotes (’) oder Double-Quotes (")
eingeschlossen werden. Wenn innerhalb dieses Strings Double-Quotes
verwendet werden sollen, so müssen diese *escaped* werden (").

Im folgenden Beispiel wird das anhand einer Widget Definition für
smartVISU gezeigt:

.. code-block:: yaml

   wohnung:
       kochen:
           sv_page: room
           name: Kochen
           visu_downlights:
               name: Downlights Tresen
               sv_widget: |
                   {{ device.dimmer('wohnung.kochen.dl_aussen', 'Äußere Downlights', 'wohnung.kochen.dl_aussen', ''wohnung.kochen.dl_aussen.level'') }}
                   {{ device.dimmer('wohnung.kochen.dl_innen', 'Innere Downlights', 'wohnung.kochen.dl_innen', ''wohnung.kochen.dl_innen.level'') }}
                   {{ device.dimmer('wohnung.kochen.dl_mitte', 'Mittleres Downlight', 'wohnung.kochen.dl_mitte', 'wohnung.kochen.dl_mitte.level') }}

Bei einzeiligen String-Values muss der String in Single-Quotes oder
Double-Quotes eingeschlossen werden. Wenn der String selbet Quotes (’)
enthält, kann der gesamte String mit Doppel-Quotes (") an Stelle der
Single-Quotes (’) eingeschlossen werden. Dann braucht man Single-Quotes
nicht zu *escapen*. Allerdings müssen dann evtl. vorkommende
Doppel-Quotes escaped werden.

Beispiel:

.. code-block:: yaml

   wohnung:
       kochen:
           sv_page: room
           name: Kochen
           visu_downlights:
               name: Downlights Tresen
               sv_widget: "{{ device.dimmer('wohnung.kochen.dl_aussen', 'Äußere Downlights', 'wohnung.kochen.dl_aussen', 'wohnung.kochen.dl_aussen.level') }}"

Konvertierung von .conf Dateien in das YAML Format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Im Verzeichnis **../tools** von SmartHomeNG liegt ein Tool
(conf_to_yaml_converter.py) zur Konvertierung der .conf Dateien in YAML
Dateien.

Der Konverter konvertiert sowohl die .conf Dateien im **../items**
Verzeichnis, als auch die .conf Dateien im **../etc** Verzeichnis. Nach
dem Start des Konverters fragt er für jedes der beiden Verzeichnisse ab,
ob die Dateien in dem Verzeichnis konvertiert werden sollen. Wichtig:
Der Konverter muss vom Verzeichnis tools gestartet werden.

   Wenn in den .conf Dateien Blöcke auskommentiert sind, so werden diese
   als Kommentare übernommen und nicht konvertiert. Falls es gewünscht
   ist diese Blöcke zu konvertieren, so muss die Auskommentierung der
   Zeilen vor der Konvertierung entfernt werden und nach der
   Konvertierung wieder hinzugefügt werden.

Die ursprünglichen .conf Dateien bleiben bei der Konvertierung
unverändert in den Verzeichnissen liegen.

Nacharbeiten
^^^^^^^^^^^^

**../items**-Verzeichnis: Als Nacharbeiten **müssen** die .conf Dateien
aus dem **../items** Verzeichnis heraus bewegt werden, da SmartHomeNG im
**../items** Verzeichnis alle .conf und alle .yaml Dateien einliest.
Dabei würden die Definitionen der Items zweimal eingelesen (einmal aus
der .conf Datei und einmal aus der .yaml Datei).

**../etc**-Verzeichnis: Als Nacharbeiten sollten die .conf Dateien aus
dem **../etc** Verzeichnis heraus bewegt werden, um Verwirrungen zu
vermeiden. Das herausbewegen ist nicht unbedingt notwendig, da die
SmartHomeNG beim Einlesen der Konfigurationsdateien nur eine Version
einliest. Ist eine .yaml Datei vorhanden, wird diese eingelesen. Nur
wenn keine .yaml Datei vorhanden ist, wird die .conf Datei gelesen.
