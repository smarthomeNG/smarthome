multidevice
===========

Anforderungen
-------------

Nix besonderes.

Notwendige Software
~~~~~~~~~~~~~~~~~~~

* pyserial

Unterstützte Geräte
~~~~~~~~~~~~~~~~~~~

Alle Geräte, für die jemand die Konfiguration und ggf. notwendige Methoden
implementiert. Derzeit sind dies:

* Pioneer AV-Receiver (pioneer)

  * SC-LX87
  * SC-LX77
  * SC-LX57
  * SC-2023
  * SC-1223
  * VSX-1123
  * VSX-923

* Denon AV-Receiver (denon)

  * AVR-X6300H
  * AVR-X4300H
  * AVR-X3300W
  * AVR-X2300W
  * AVR-X1300W

* Kodi Mediencenter (kodi)

* Squeezebox Medienserver

* Viessmann-Heizungen (viessmann)

  * V200KW2
  * V200KO1B
  * V200WO1C
  * V200HO1C

* Yamaha MusicCast-Geräte (musiccast)

Konfiguration
-------------

plugin.yaml
~~~~~~~~~~~

Liste von Geräten und ggf. deren Konfiguration.

Geräte-ID ist eine eindeutige Kennzeichnung, die auch in der Item-Konfiguration
in der Option ``md_device`` angegeben wird; Geräte-Typ ist der Name des Gerätes
im Ordner ``dev_<Geräte-Typ>``.

Mindestangabe ist der Geräte-Typ; wenn keine Geräte-ID vergeben wird, ist diese
gleich dem Geräte-Typ (beachte: pro Geräte-Typ nur einmal möglich).

Unterhalb der Listenebene der Geräte sind weitere Konfigurations- attribute für
die Geräte in der Listenform <Attribut>: <Wert> möglich, z.B.
Verbindungsattribute wie `host`, `port`, `serial` o.ä.

Eine Auflistung der grundsätzlich unterstützten Attribute findet sich in der
Datei ``MD_Globals.py``. Dort finden sich auch symbolische Bezeichner
("Konstanten") für einige der Attribute. Diese können in der Konfiguration für
bessere Übersichtlichkeit verwendet werden.

Für die Konfiguration der einzelnen Geräte sollte sich die Dokumentation der
jeweils notwendigen und unterstützen Attribute im Geräte-Ordner
``dev_<device>`` finden.

Beispiel:

.. code:: yaml

	devices:
	    - <Geräte-Typ>         # Geräte-ID = Geräte-Typ
	    - <Geräte-Typ>:        # Geräte-ID = Geräte-Typ
	        - <Attribut1>: <Wert1>
	        -...
	    - <Geräte-ID>: <Geräte-Typ>
	    - <Geräte-ID>:         # Geräte-Typ = Geräte-ID
	        - <Attribut1>: <Wert1>
	        - ...
	    - <Geräte-ID>:
	        - device_type: <Geräte-Typ>
	        - <Attribut1>: <Wert1>
	        - ...


Bitte zusätzlich die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


items.yaml
~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


logic.yaml
~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


Funktionen
~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


Standalone-Modus
----------------

Das Plugin kann auch im Standalone-Modus verwendet werden. Dazu wird es aus dem
SmartHomeNG-Ordner mit einem Gerätetypen <device> als erstem Argument aufgerufen.


Gerätefunktion
~~~~~~~~~~~~~~

Im Standardmodus wird die Standalone-Funktion des jeweiligen Gerätes aufgerufen,
sofern diese implementiert ist. Da Geräte modular erweitert werden können, ist
es nicht möglich, eine Übersicht über unterstützte Geräte und deren Funktionen
zu geben.

Ggf. notwendige Konfigurationsparameter (z.B. ``host`` oder ``serialport``)
müssen in Form von param=Wert oder in Form eines Python-dicts (in Hochkommata)
als zweitem (und ggf. folgendem) Parameter übergeben werden.
Falls derselbe Parameter mehrfach angegeben wird, wird der Wert des letzten
Auftretens verwendet.

.. code:: bash

    python3 plugins/multidevice/__init__.py <device> host=www.smarthomeng.de port=80

oder

.. code:: bash

    python3 plugins/multidevice/__init__.py <device> '{"host": "www.smarthomeng.de", "port": 80}'


Wenn das Plugin mit ``-v`` als Parameter aufgerufen wird, werden zusätzliche
Debug-Informationen angezeigt.

.. code:: bash

    python3 plugins/multidevice/__init__.py <device> -v


Struct-Erzeugung
~~~~~~~~~~~~~~~~

Wenn das Plugin mit dem Parameter -s nach dem Gerätetyp aufgerufen wird, gibt es
ein Struktur-Template (struct.yaml) aus, das für die Itemkonfiguration
verwendet werden kann und beim Start von SmartHomeNG eingelesen wird:

.. code:: bash

    python3 plugins/multidevice/__init__.py <device> -s

Wenn es mit dem Parameter -S aufgerufen wird, wird die Struktur nicht auf
ausgegeben, sondern automatisch im Ordner des jeweiligen Gerätes als
``struct.yaml`` gespeichert.

.. code:: bash

    python3 plugins/multidevice/__init__.py <device> -S

.. warning::
    Vorhandene Dateien werden dabei ohne Rückfrage überschrieben!

Die Einrückweite für die Strukturausgabe beträgt standardmäßig 4 Spalten. Die
Angabe einer Zahl als Parameter (zusätzlich zu -s oder -S) legt eine abweichende
Einrückweite fest:

.. code:: bash

    python3 plugins/multidevice/__init__.py <device> -s -a

Das zusätzlich Argument -a veranlasst die Ausgabe des ``visu_acl:``-Attributs
für alle Items, die ein Kommando enthalten. Dabei ist der Wert des Attributs
abhängig davon, ob das Kommando schreibbar ist oder nicht.


Web Interface
-------------

Das Web-Interface bietet eine Übersicht über die konfigurierten Geräte mit ihren
Parameter und ermöglicht es, Geräte zu stoppen, zu starten und die Parameter zu
ändern.

Weiterhin gibt es eine Übersicht über die Items, die für das Plugin konfiguriert
und verknüpft sind.


Entwicklung von eigenen Geräte-Klassen
======================================

Die Entwicklerdokumentation existiert derzeit nur auf englisch. Eine
detailliertere Dokumentation findet sich im Unterordner ``doc`` des
Plugin-Verzeichnisses.


.. automodule:: plugins.multidevice
