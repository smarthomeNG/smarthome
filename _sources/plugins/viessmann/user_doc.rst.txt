.. index:: Plugins; viessmann
.. index:: viessmann

=========
viessmann
=========

.. image:: webif/static/img/plugin_logo.svg
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Das Viessmann-Plugin ermöglicht die Verbindung zu einer Viessmann-Heizung über einen IR-Adapter (z.B. Optolink oder Nachbauten, wie im OpenV-Wiki beschrieben) und das Lesen und Schreiben von Parametern der Heizung.
Derzeit sind das P300- und das KW-Protokoll unterstützt. Weitere Gerätetypen, die diese Protokolle unterstützen, können einfach hinzugefügt werden. Für weitere Protokolle (z.B. GWG) wird zusätzliche Entwicklungsarbeit notwendig sein.

Details zu den betroffenen Geräten und Protokollen finden sich im
`OpenV Wiki <https://github.com/openv/openv/wiki/vcontrold>`_

Dieses Plugin nutzt eine separate Datei ``commands.py``, in der die Definitionen für Protokolle, Gerätetypen und Befehlssätze enthalten sind. Neue Geräte können hinzugefügt werden, indem die entsprechenden Informationen in der ``commands.py`` ergänzt werden.

Das Plugin unterstützt die serielle Kommunikation mit dem Lesekopf (ggf. über einen USB-Seriell-Adapter).

Zur Identifizierung des Heizungstyps kann das Plugin auch im Standalone-Modus betrieben werden (s.u.)

Changelog
=========

1.2.2
-----

-  Funktion zum manuellen Schreiben von Werten hinzugefügt

1.2.0
-----

-  Komplette Überarbeitung von Code und Webinterface (AJAX)
-  Code refaktorisiert und besser strukturiert
-  Funktion zum Lesen mehrerer Werte gleichzeitig im KW-Protokoll
-  Verbesserte Fehler- und Locking-Behandlung
-  Funktionen zum manuellen Auslesen von konfigurierten und unbekannten Adressen, z.B. zum Testen von Adressen
-  Webinterface mit der Möglichkeit, Adressen manuell auszulesen

1.1.0
-----

-  Unterstützung für das KW-Protokoll

1.0.0
-----

-  Erste Version

Anforderungen
=============

Das Plugin benötigt die ``pyserial``-Bibliothek und einen seriellen IR-Adapter.

Unterstützte Geräte
===================

Jede Viessmann-Heizung mit Optolink-Anschluss wird grundsätzlich unterstützt.

Derzeit sind Gerätekonfigurationen (Befehlssätze) für die folgenden Type verfügbar:

-  V200KO1B
-  V200HO1C
-  V200KW2
-  V200WO1C
-  VScotHO1_200_11

Weitere Gerätetypen können problemlos hinzugefügt werden, wenn die entsprechenden Befehlsadressen bekannt sind.

Konfiguration
=============

Diese Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/viessmann` beschrieben.

plugin.yaml
-----------

.. code:: yaml

    viessmann:
        protocol: P300
        plugin_name: viessmann
        heating_type: V200KO1B
        serialport: /dev/ttyUSB_optolink


items.yaml
----------

Die Verknüfpung von SmartHomeNG-Items und Heizungsparametern ist vollständig flexibel und konfigurierbar. Mit den Item-Attributen kann das Verhalten des Plugins festgelegt werden.

Die folgenden Attribute werden unterstützt:


viess_command
~~~~~~~~~~~~~

Legt das Kommando aus der ``commands.py`` fest, mit dem dieses Item verknüpft ist. Wird zusammen mit ``viess_read`` und/oder ``viess_write`` verwendet.

.. code-block:: yaml

    item:
        viess_command: Raumtemperatur_Soll_Normalbetrieb_A1M1
        viess_read: true


viess_read
~~~~~~~~~~

Aktiviert das Lesen des über ``viess_command`` angegebenen Parameters; der gelesene Wert wird dem Item zugewiesen.

.. code-block:: yaml

    item:
        viess_command: Raumtemperatur_Soll_Normalbetrieb_A1M1
        viess_read: true


viess_write
~~~~~~~~~~~

Aktiviert das Schreiben: Änderungen an diesem Item werden über das mit ``viess_command`` angegebene Kommando an die Heizung gesendet.

.. code-block:: yaml

    item:
        viess_command: Raumtemperatur_Soll_Normalbetrieb_A1M1
        viess_read: true
        viess_write: true


viess_readafterwrite
~~~~~~~~~~~~~~~~~~~~~

Wenn dieses Attribut mit einer Dauer in Sekunden angegeben ist, wird nach einem Schreibvorgang die angegebene Anzahl an Sekunden gewartet und der Wert erneut vom Gerät gelesen.

.. code-block:: yaml

    item:
        viess_command: Raumtemperatur_Soll_Normalbetrieb_A1M1
        viess_read: true
        viess_write: true
        viess_readafterwrite: 1  # seconds


viess_read_cycle
~~~~~~~~~~~~~~~~

Mit einer Angabe in Sekunden wird ein individuelles periodisches Lesen für dieses Item angefordert.

.. code-block:: yaml

    item:
        viess_command: Raumtemperatur_Soll_Normalbetrieb_A1M1
        viess_read: true
        viess_read_cycle: 3600  # every hour


viess_read_cyclic
~~~~~~~~~~~~~~~~~

Aktiviert periodisches Lesen mit dem plugin-weiten Intervall (Parameter ``cycle`` in der ``plugin.yaml``), als Alternative zu einem individuellen Intervall über ``viess_read_cycle``.

.. code-block:: yaml

    item:
        viess_command: Raumtemperatur_Soll_Normalbetrieb_A1M1
        viess_read: true
        viess_read_cyclic: true


viess_read_initial
~~~~~~~~~~~~~~~~~~~

Wenn dieses Attribut auf ``true`` gesetzt ist, wird das Item nach dem Start von SmartHomeNG einmalig gelesen.

.. code-block:: yaml

    item:
        viess_command: Raumtemperatur_Soll_Normalbetrieb_A1M1
        viess_read: true
        viess_read_initial: true


viess_read_group / viess_read_group_trigger
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``viess_read_group`` ordnet ein Item einer oder mehreren Gruppen (int, str oder Liste davon) zum gesammelten Lesen zu.

Wird einem Item mit ``viess_read_group_trigger`` ein beliebiger Wert zugewiesen, werden alle zum Lesen konfigurierten Items der angegebenen Gruppe neu vom Gerät gelesen; bei Gruppe ``0`` werden alle zum Lesen konfigurierten Items aktualisiert. Ein Item mit ``viess_read_group_trigger`` darf nicht gleichzeitig ``viess_command`` verwenden.

.. code-block:: yaml

    aussentemperatur:
        viess_command: Aussentemperatur
        viess_read: true
        viess_read_group: 1

    alles_neu_lesen:
        type: bool
        viess_read_group_trigger: 0


viess_lookup
~~~~~~~~~~~~

Der Inhalt der Lookup-Tabelle mit dem angegebenen Namen wird beim Start einmalig als dict oder list in das Item geschrieben. Durch Anhängen von ``#<mode>`` an den Namen der Tabelle kann die Art der Tabelle ausgewählt werden:

- ``fwd`` liefert die Tabelle Gerät -> SmartHomeNG (Standard)
- ``rev`` liefert die Tabelle SmartHomeNG -> Gerät
- ``rci`` liefert die Tabelle SmartHomeNG -> Gerät in Kleinbuchstaben
- ``list`` liefert die Liste der Namen für SmartHomeNG

Damit kann z.B. eine Liste der gültigen Betriebsarten für die Verwendung in SmartVISU bereitgestellt werden:

.. code-block:: yaml

    item:
        viess_lookup: operatingmodes#list

.. code-block:: html

    {{ basic.select('heizen_ba_item', 'heizung.betriebsart', 'menu', '', '', '', '', '', 'heizung.ba_list') }}

Dies erzeugt eine ("Menü"-) Auswahlliste, aus der die Betriebsart ausgewählt werden kann, die dann vom Plugin an die Heizung übergeben wird.


viess_custom1 / viess_custom2 / viess_custom3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Der Inhalt dieses Items kann vom jeweiligen Gerät für spezielle Zwecke genutzt werden. Durch den Parameter ``recursive_custom: 1`` (bzw. ``2``/``3``) in der Geräte-Konfiguration wird der Wert rekursiv für alle Unteritems gesetzt.

.. code-block:: yaml

    item:
        viess_custom1: 'wert'


.. note::

    Die früher unterstützten Attribute ``viess_trigger`` (automatisches Nachlesen anderer Items nach einem Schreibvorgang) und ``viess_timer`` (Wochenschaltzeiten im UZSU-Format) werden von der aktuellen, auf dem SmartDevicePlugin-Framework basierenden Version des Plugins nicht unterstützt.


Beispiel
--------

Here you can find a configuration sample using the commands for
V200KO1B:

.. code-block:: yaml

    viessmann:
        viessmann_update:
            name: Update aller Items der Gruppe 0 (= alle lesbaren Items)
            type: bool
            visu_acl: rw
            viess_read_group_trigger: 0
            enforce_updates: true
            autotimer: 1 = false = latest

        allgemein:
            aussentemp:
                name: Aussentemperatur
                type: num
                viess_command: Aussentemperatur
                viess_read: true
                viess_read_cycle: 300
                viess_read_initial: true
                database: true

            aussentemp_gedaempft:
                name: Aussentemperatur
                type: num
                viess_command: Aussentemperatur_TP
                viess_read: true
                viess_read_cycle: 300
                viess_read_initial: true
                database: true

        kessel:
            kesseltemperatur_ist:
                name: Kesseltemperatur_Ist
                type: num
                viess_command: Kesseltemperatur
                viess_read: true
                viess_read_cycle: 180
                viess_read_initial: true
                database: init
            kesseltemperatur_soll:
                name: Kesselsolltemperatur_Soll
                type: num
                viess_command: Kesselsolltemperatur
                viess_read: true
                viess_read_cycle: 180
                viess_read_initial: true
            abgastemperatur:
                name: Abgastemperatur
                type: num
                viess_command: Abgastemperatur
                viess_read: true
                viess_read_cycle: 180
                viess_read_initial: true
                database: init
        heizkreis_a1m1:
           betriebsart:
                betriebsart_aktuell:
                    name: Aktuelle_Betriebsart_A1M1
                    type: str
                    viess_command: Aktuelle_Betriebsart_A1M1
                    viess_read: true
                    viess_read_cycle: 3600
                    viess_read_initial: true
                betriebsart:
                    name: Betriebsart_A1M1
                    type: num
                    viess_command: Betriebsart_A1M1
                    viess_read: true
                    viess_write: true
                    viess_readafterwrite: 5
                    viess_read_initial: true
                    cache: true
                    enforce_updates: true
                    visu_acl: rw
                sparbetrieb:
                    name: Sparbetrieb_A1M1
                    type: bool
                    viess_command: Sparbetrieb_A1M1
                    viess_read: true
                    viess_write: true
                    viess_readafterwrite: 5
                    viess_read_initial: true
                    visu_acl: rw
           ferienprogramm:
                status:
                    name: Ferienprogramm_A1M1
                    type: num
                    viess_command: Ferienprogramm_A1M1
                    viess_read: true
                    viess_read_cycle: 3600
                    viess_read_initial: true
                starttag:
                    name: Ferien_Abreisetag_A1M1
                    type: str
                    viess_command: Ferien_Abreisetag_A1M1
                    viess_read: true
                    viess_write: true
                    viess_readafterwrite: 5
                    viess_read_initial: true
                    visu_acl: rw
                    eval: value[:10]
                endtag:
                    name: Ferien_Rückreisetag_A1M1
                    type: str
                    viess_command: Ferien_Rückreisetag_A1M1
                    viess_read: true
                    viess_write: true
                    viess_readafterwrite: 5
                    viess_read_initial: true
                    visu_acl: rw


Funktionen
==========

read_addr(addr)
---------------

Diese Funktion löst das Lesen des Parameters mit der übergebenen Adresse ``addr`` aus. Die Adresse muss als vierstellige Hex-Zahl im String-Format übergeben werden. Es können nur Adressen ausgelesen werden, die im Befehlssatz für den aktiven Heizungstyp enthalten sind. Unabhängig von der Itemkonfiguration werden durch ``read_addr()`` keine Werte an Items zugewiesen.
Der Rückgabewert ist das Ergebnis des Lesevorgangs oder None, wenn ein Fehler aufgetreten ist.


read_temp_addr(addr, length=1, mult=0, signed=False)
-----------------------------------------------------

Diese Funktion versucht, den Parameter an der Adresse ``addr`` zu lesen, unabhängig davon, ob die Adresse im Befehlssatz für den aktiven Heizungstyp definiert ist. Die Adresse muss als vierstellige Hex-Zahl im String-Format übergeben werden. ``length`` gibt die erwartete Länge des Werts in Byte an, ``mult`` einen Multiplikator (Zehnerpotenz) und ``signed``, ob der Wert vorzeichenbehaftet interpretiert werden soll.
Der Rückgabewert ist das Ergebnis des Lesevorgangs oder None, wenn ein Fehler aufgetreten ist.


write_addr(addr, value)
-----------------------

Diese Funktion versucht, den Wert ``value`` an die angegebene Adresse zu schreiben. Die Adresse muss als vierstellige Hex-Zahl im String-Format übergeben werden. Es können nur Adressen beschrieben werden, die im Befehlssatz für den aktiven Heizungstyp enthalten sind. Durch ``write_addr`` werden Itemwerte nicht direkt geändert; wenn die geschriebenen Werte von der Heizung wieder ausgelesen werden (z.B. durch zyklisches Lesen), werden die geänderten Werte in die entsprechenden Items übernommen.

.. warning::

    Das Schreiben von beliebigen Werten oder Werten, deren Bedeutung nicht klar ist, kann im Heizungsgerät möglicherweise unerwartete Folgen haben. Auch eine Beschädigung der Heizung ist nicht auszuschließen.

.. hint::

    Wenn eine der Plugin-Funktionen in einer Logik verwendet werden sollen, kann dies in der folgenden Form erfolgen:

.. code-block:: yaml

    result = sh.plugins.return_plugin('viessmann').read_temp_addr('00f8', 2, 0, False)


Web Interface
=============

Im Web-Interface gibt es neben den allgemeinen Statusinformationen zum Plugin zwei Seiten.

Auf einer Seite werden die Items aufgelistet, die Plugin-Attributen konfiguriert haben. Damit kann eine schnelle Übersicht über die Konfiguration und die aktuellen Werte geboten werden.

Auf der zweiten Seite werden alle im aktuellen Befehlssatz enthaltenen Parameter aufgelistet. Dabei besteht für jeden Wert einzeln die Möglichkeit, einen Lesevorgang auszulösen. Die Rückgabewerte werden in die jeweilige Tabellenzeile eingetragen. Dieser entspricht der Funktion ``read_addr()``, d.h. es werden keine Item-Werte aktualisiert.

Weiterhin kann in der Zeile für den Parameter "_Custom" eine freie Adresse angegeben werden, die analog zur Funktion ``read_temp_addr()`` einen Lesevorgang auf beliebigen Adressen erlaubt. Auch hier wird der Rückgabewert in die jeweilige Tabellenzeile eingetragen. Damit wird ermöglicht, ohne großen Aufwand Datenpunkte und deren Konfiguration (Einheit und Datenlänge) zu testen.


Standalone-Modus
================

Wenn der Heizungstyp nicht bekannt ist, kann das Plugin im Standalone-Modus (also ohne SmartHomeNG zu starten) genutzt werden. Es versucht dann, mit der Heizung zu kommunizieren und den Gerätetyp zu identizifieren.

Dazu muss das Plugin im Plugin-Ordner direkt aufgerufen werden. Die Konfiguration erfolgt über ``schlüssel=wert``-Paare als Kommandozeilenargumente, analog zu den Parametern in der ``plugin.yaml``:

``./__init__.py serialport=/dev/ttyUSB0``

Der serielle Port (``serialport``) ist dabei die Gerätedatei bzw. der entsprechende Port, an dem der Lesekopf angeschlossen ist, z.B. ``/dev/ttyUSB0``. Dieser Parameter ist verpflichtend; fehlt er, bricht der Aufruf mit einer entsprechenden Fehlermeldung ab, statt mit einem unklaren Fehler tiefer im Code zu scheitern.

Alle weiteren Parameter aus der ``plugin.yaml`` (z.B. ``viess_proto`` oder ``p300_init_retries``) können auf die gleiche Weise gesetzt werden; ohne Angabe wird jeweils der Standardwert aus der ``plugin.yaml`` verwendet. Mit ``./__init__.py -h`` wird eine vollständige Liste aller verfügbaren Parameter mit Typ, Standardwert (bzw. Vermerk, falls verpflichtend) und Beschreibung ausgegeben.

Das optionale Argument ``-v`` weist das Plugin an, zusätzliche Debug-Ausgaben zu erzeugen. Solange keine Probleme beim Aufruf auftreten, ist das nicht erforderlich.

Sollte die Datei sich nicht starten lassen, muss ggf. der Dateimodus angepasst werden. Mit ``chmod u+x __init__.py`` kann die z.B. unter Linux erfolgen.
