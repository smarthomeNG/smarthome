.. index:: Plugins; jvcproj
.. index:: jvcproj

=======
jvcproj
=======

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Mit diesem Plugin können JVC D-ILA Projektoren über mittels
"JVC External Control Command Communication Specification" via TCP gesteuert werden.
Außerdem können mit jvcprojectortools erzeugte Gammatabellen übertragen werden.

Hinweis
=======

Die meisten Befehle werden nicht quittiert, wenn der Projektor kein Eingangssignal hat. Anfrage
Befehle werden noch nicht unterstützt. Die Gammatabellen-Konfigurationsdateien können
rohe Gammatabellen-Dateien sein (vom Projektor geladen mit
jvcprojectortools geladen) oder die Konfigurationsdateien, die mit
jvcprojectortools erzeugt werden, wenn Sie Ihre Parameter speichern. Bei Verwendung dieser Dateien
werden nur die hinterlegten Gamma-Rohdaten ("Tabellen"-Daten) benötigt und
übertragen.

Das Plugin sollte ab der Projektorengeneration X3/X7/X9 bis hin zu
X5900/X7900/X9900 und sicherlich auch für kommende Generationen.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/jvcproj` beschrieben.

plugin.yaml
-----------

.. code-block:: yaml

   jvcproj:
       plugin_name: jvcproj
       host: 1.1.1.1 # host address of the projector
       gammaconf_dir: ... # optional, location gamma table configuration files

Attribute
---------

jvcproj_cmd:
^^^^^^^^^^^^

Attribut, um einen (oder mehrere) Befehle an den Projektor zu senden. Die Befehle müssen
mit einem ``|`` getrennt werden. Wenn mehr als ein Befehl in einem Element angegeben wird
werden die Befehle nacheinander gesendet, bis die Liste vollständig abgearbeitet ist
oder ein Fehler auftritt. Die Befehle können mit oder ohne Leerzeichen aufgelistet werden
(21 89 01 50 57 31 0A oder 2189015057310A).

Beispiel: Objektivspeicher 1 setzen (mit Leerzeichen) und Objektivmaske auf Benutzer 1 setzen
(ohne Leerzeichen). Befehle werden mit "|" getrennt.

.. code-block:: yaml

       mem219:
       # command to set -lens memory 1- and -lens mask 1-
           type: bool
           visu_acl: rw
           jvcproj_cmd: 21 89 01 49 4E 4D 4C 30 0A | 21890149534D41300A
           enforce_updates: True

jvcproj_gamma:
^^^^^^^^^^^^^^

Attribut zum Senden einer Gammatabelle aus einer angegebenen Datei. Dieses Element benötigt genau
zwei Argumente! Das erste Argument ist der Name der Gammatabelle
Konfigurationsdatei, die geladen werden soll. Die Datei muss im angegebenen
Pfad in der plugin.yaml existieren (standardmäßig /usr/local/smarthome/etc/jvcproj/ ).
Das zweite Argument ist der Gammaslot, in den die Gammadaten geladen werden sollen. Diese
MUSS eine benutzerdefinierte Gammatabelle sein und kann mit
custom1/custom2/custom3 oder den kompatiblen Hex-Befehlen deklariert werden.

Zwei Beispiele, welche die Gammadaten aus einer Datei in den Gammaslot custom3 laden:

.. code-block:: yaml

       hdrmid:
       # command to set gammatable from file to -gamma custom 3-
           type: bool
           visu_acl: rw
           jvcproj_gamma: jvc_gamma_HDR_middynamic.conf | custom3
           enforce_updates: True

       hdrhigh:
       # command to set gammatable from file to -gamma custom 3-
           type: bool
           visu_acl: rw
           jvcproj_gamma: jvc_gamma_HDR_highdynamic.conf | 21 89 01 50 4D 47 54 36 0A
           enforce_updates: True

Kommandoerläuterung
===================

Das Plugin verwendet die rohen Hex-Befehle. Eine Liste aller Befehle
(abhängig von der Projektorserie) finden Sie auf der JVC
Support Homepage oder durch die Suche nach JVC Projektor RS-232 Befehlslisten.
Hier ist ein kleines Beispiel für einen Betriebsbefehl "Power On" (21 89 01 50
57 31 0A):

- ``21``: Header - ein Betriebsbefehl beginnt immer mit 21 (ASCII: "!")
- ``89 01``: Unit ID - ist für alle Modelle auf 89 01 festgelegt
- ``50 57``: Befehl - variiert je nach Befehl. In diesem Beispiel 50 57 (ASCII: "PW")
- ``30``: Daten - Dies ist der Wert, der auf den Befehl angewendet wird. Mit dem
   Power Beispiel oben, ist der Datenwert für On 31 (ASCII: "1"). Länge
   variiert je nach Befehl (nicht immer 1 Byte)!
- ``0A``: Ende - Dies bedeutet das Ende des Befehls und ist für alle Modelle gleich.

Web Interface
=============

Das Plugin stellt kein Web Interface zur Verfügung.
