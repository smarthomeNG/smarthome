viessmann
=========

Das Viessmann-Plugin ermöglicht die Verbindung zu einer Viessmann-Heizung über einen IR-Adapter (z.B. Optolink oder Nachbauten, wie im OpenV-Wiki beschrieben) und das Lesen und Schreiben von Parametern der Heizung.
Derzeit sind das P300- und das KW-Protokoll unterstützt. Weitere Gerätetypen, die diese Protokolle unterstützen, können einfach hinzugefügt werden. Für weitere Protokolle (z.B. GWG) wird zusätzliche Entwicklungsarbeit notwendig sein.

Details zu den betroffenen Geräten und Protokollen finden sich im
.. _OpenV-Wiki: https://github.com/openv/openv/wiki/vcontrold

Dieses Plugin nutzt eine separate Datei ``commands.py``, in der die Definitionen für Protokolle, Gerätetypen und Befehlssätze enthalten sind. Neue Geräte können hinzugefügt werden, indem die entsprechenden Informationen in der ``commands.py`` ergänzt werden.

Das Plugin unterstützt die serielle Kommunikation mit dem Lesekopf (ggf. über einen USB-Seriell-Adapter).

Zur Identifizierung des Heizungstyps kann das Plugin auch im Standalone-Modus betrieben werden (s.u.)

Changelog
---------

1.2.2
~~~~~

-  Funktion zum manuellen Schreiben von Werten hinzugefügt

1.2.0
~~~~~

-  Komplette Überarbeitung von Code und Webinterface (AJAX)
-  Code refaktorisiert und besser strukturiert
-  Funktion zum Lesen mehrerer Werte gleichzeitig im KW-Protokoll
-  Verbesserte Fehler- und Locking-Behandlung
-  Funktionen zum manuellen Auslesen von konfigurierten und unbekannten Adressen, z.B. zum Testen von Adressen
-  Webinterface mit der Möglichkeit, Adressen manuell auszulesen

1.1.0
~~~~~

-  Unterstützung für das KW-Protokoll

1.0.0
~~~~~

-  Erste Version

Anforderungen
-------------

Das Plugin benötigt die ``pyserial``-Bibliothek und einen seriellen IR-Adapter.

Unterstützte Geräte
~~~~~~~~~~~~~~~~~~~

Jede Viessmann-Heizung mit Optolink-Anschluss wird grundsätzlich unterstützt.

Derzeit sind Gerätekonfigurationen (Befehlssätze) für die folgenden Type verfügbar:

-  V200KO1B
-  V200HO1C
-  V200KW2
-  V200WO1C

Weitere Gerätetypen können problemlos hinzugefügt werden, wenn die entsprechenden Befehlsadressen bekannt sind.

Konfiguration
-------------

plugin.yaml
~~~~~~~~~~~

.. code:: yaml

    viessmann:
        protocol: P300
        plugin_name: viessmann
        heating_type: V200KO1B
        serialport: /dev/ttyUSB_optolink


items.yaml
~~~~~~~~~~

Die Verknüfpung von SmartHomeNG-Items und Heizungsparametern ist vollständig flexibel und konfigurierbar. Mit den Item-Attributen kann das Verhalten des Plugins festgelegt werden. 

Die folgenden Attribute werden unterstützt:


viess\_read
^^^^^^^^^^^

Der Wert des angegebenen Parameters wird gelesen und dem Item zugewiesen.

.. code:: yaml

    item:
        viess_read: Raumtemperatur_Soll_Normalbetrieb_A1M1


viess\_send
^^^^^^^^^^^

Der angegebene Parameter wird bei Änderungen an diesem Item an die Heizung gesendet.

.. code:: yaml

    item:
        viess_send: Raumtemperatur_Soll_Normalbetrieb_A1M1

Sofern das Item sowohl zum Lesen als auch zum Schreiben eines Parameters konfiguriert wird, kann die vereinfachte Konfiguration mit ``true`` erfolgen:

.. code:: yaml

    item:
        viess_read: Raumtemperatur_Soll_Normalbetrieb_A1M1
        viess_send: true


viess\_read\_afterwrite
^^^^^^^^^^^^^^^^^^^^^^^

Wenn dieses Attribut mit einer Dauer in Sekunden angegeben ist, wird nach eine Schreibvorgang die angegebene Anzahl an Sekunden gewartet und ein erneuter Lesevorgang ausgelöst.

Damit dieses Attribut verwendet werden kann, muss das Item sowohl die Attribute ``viess_read`` als auch ``viess_send`` enthalten.

.. code:: yaml

    item:
        viess_read: Raumtemperatur_Soll_Normalbetrieb_A1M1
        viess_send: true
        viess_read_afterwrite: 1  # seconds


viess\_read\_cycle
^^^^^^^^^^^^^^^^^^

Mit einer Angabe in Sekunden wird ein periodisches Lesen angefordert. ``viess_read`` muss zusätzlich konfiguriert sein.

.. code:: yaml

    item:
        viess_read: Raumtemperatur_Soll_Normalbetrieb_A1M1
        viess_read_cycle: 3600  # every hour


viess\_init
^^^^^^^^^^^

Wenn dieses Attribut vorhanden und auf ``true`` gesetzt ist, wird das Item nach dem Start von SmartHomeNG einmalig gelesen. 
``viess_read`` muss zusätzlich konfiguriert sein.

.. code:: yaml

    item:
        viess_read: Raumtemperatur_Soll_Normalbetrieb_A1M1
        viess_init: true


viess\_trigger
^^^^^^^^^^^^^^

Enthält eine Liste von Parametern. Wenn dieses Item aktualisiert wird, wird ein Lesevorgang für jeden Eintrag in der Liste angestoßen. ``viess_send`` muss zusätzlich konfiguriert sein.

Zwischen dem Schreibvorgang und den folgenden Lesevorgängen ist standardmäßig eine Verzögerung von 5 Sekunden eingestellt. Diese kann mit ``viess_trigger_afterwrite`` verändert werden.

Beispiel: wenn der Betriebsmodus geändert wird, können neue Sollwerte für Raum- und Wassertemperaturen gelesen werden.

.. code:: yaml

    item:
        viess_send: Betriebsart_A1M1
        viess_trigger:
           - Raumtemperatur_Soll
           - Wassertemperatur_Soll


viess\_trigger\_afterwrite
^^^^^^^^^^^^^^^^^^^^^^^^^^

Wenn ein ``viess_trigger`` konfiguriert ist, kann mit diesem Attribut die Verzögerung zwischen Schreib- und Lesevorgang verändert werden.

Standardmäßig beträgt diese Verzögerung 5 Sekunden.

.. code:: yaml

    item:
        viess_send: Betriebsart_A1M1
        viess_trigger:
           - Raumtemperatur_Soll
           - Wassertemperatur_Soll
        viess_trigger_afterwrite: 10 # seconds


viess\_update
^^^^^^^^^^^^^
Das Zuweisen von ``true`` an ein Item mit diesem Attribut löst den Lesevorgang aller konfigurierter Items mit ``viess_read`` aus.

Der in der Itemkonfiguration angegebene Wert wird nicht ausgewertet.

.. code:: yaml

    item:
        viess_update: 'egal'


viess\_timer
^^^^^^^^^^^^
Das Item mit diesem Attribut übergibt als Attributwert den Namen einer Anwendung, z.B. Heizkreis_A1M1, und das Plugin gibt ein UZSU-formatiertes dict mit allen zugehörigen Timern der Heizung zurück
Beim Schreiben wird das UZSU-dict in die einzelnen Tagestimer aufgeteilt und an die Heizung gesendet.

.. code:: yaml

    item:
        viess_timer: 'Heizkreis_A1M1'


viess\_ba\_list
^^^^^^^^^^^^^^^
Das Item mit diesem Attribut erhält einmalig beim Start des Plugins die Liste der für den konfigurierten Heizungstyp gültigen Betriebsarten.

Diese kann z.B. in SmartVISU wie folgt eingebunden werden:

.. code:: yaml

    item:
        viess_ba_list: 'egal'

.. code::

    {{ basic.select('heizen_ba_item', 'heizung.betriebsart', 'menu', '', '', '', '', '', 'heizung.ba_list') }}

Dies erzeugt eine ("Menü"-) Auswahlliste, aus der die Betriebsart ausgewählt werden kann, die dann vom Plugin an die Heizung übergeben wird.


Beispiel
^^^^^^^^

Here you can find a configuration sample using the commands for
V200KO1B:

.. code:: yaml

    viessmann:
        viessmann_update:
            name: Update aller Items mit 'viess_read'
            type: bool
            visu_acl: rw
            viess_update: 1
            enforce_updates: true
            autotimer: 1 = false = latest

        allgemein:
            aussentemp:
                name: Aussentemperatur
                type: num
                viess_read: Aussentemperatur
                viess_read_cycle: 300
                viess_init: true
                database: true

            aussentemp_gedaempft:
                name: Aussentemperatur
                type: num
                viess_read: Aussentemperatur_TP
                viess_read_cycle: 300
                viess_init: true
                database: true
     
        kessel:
            kesseltemperatur_ist:
                name: Kesseltemperatur_Ist
                type: num
                viess_read: Kesseltemperatur
                viess_read_cycle: 180
                viess_init: true
                database: init
            kesseltemperatur_soll:
                name: Kesselsolltemperatur_Soll
                type: num
                viess_read: Kesselsolltemperatur
                viess_read_cycle: 180
                viess_init: true
            abgastemperatur:
                name: Abgastemperatur
                type: num
                viess_read: Abgastemperatur
                viess_read_cycle: 180
                viess_init: true
                database: init        
        heizkreis_a1m1:
           betriebsart:
                betriebsart_aktuell:
                    name: Aktuelle_Betriebsart_A1M1
                    type: str
                    viess_read: Aktuelle_Betriebsart_A1M1
                    viess_read_cycle: 3600
                    viess_init: true
                betriebsart:
                    name: Betriebsart_A1M1
                    type: num
                    viess_read: Betriebsart_A1M1
                    viess_send: true
                    viess_read_afterwrite: 5
                    viess_init: true
                    cache: true
                    enforce_updates: true
                    viess_trigger:
                      - Aktuelle_Betriebsart_A1M1
                    struct: viessmann.betriebsart
                    visu_acl: rw
                sparbetrieb:
                    name: Sparbetrieb_A1M1
                    type: bool
                    viess_read: Sparbetrieb_A1M1
                    viess_send: true
                    viess_read_afterwrite: 5
                    viess_trigger: 
                      - Betriebsart_A1M1
                      - Aktuelle_Betriebsart_A1M1
                    viess_init: true
                    visu_acl: rw
           schaltzeiten:
                montag:
                    name: Timer_A1M1_Mo
                    type: list
                    viess_read: Timer_A1M1_Mo
                    viess_send: true
                    viess_read_afterwrite: 5
                    viess_init: true
                    struct: viessmann.timer
                    visu_acl: rw
                dienstag:
                    name: Timer_A1M1_Di
                    type: list
                    viess_read: Timer_A1M1_Di
                    viess_send: true
                    viess_read_afterwrite: 5
                    viess_init: true
                    struct: viessmann.timer
                    visu_acl: rw
           ferienprogramm:
                status:
                    name: Ferienprogramm_A1M1
                    type: num
                    viess_read: Ferienprogramm_A1M1
                    viess_read_cycle: 3600
                    viess_init: true
                starttag:
                    name: Ferien_Abreisetag_A1M1
                    type: str
                    viess_read: Ferien_Abreisetag_A1M1
                    viess_send: true
                    viess_read_afterwrite: 5
                    viess_init: true
                    visu_acl: rw
                    eval: value[:10]
                endtag:
                    name: Ferien_Rückreisetag_A1M1
                    type: str
                    viess_read: Ferien_Rückreisetag_A1M1
                    viess_send: true
                    viess_read_afterwrite: 5
                    viess_init: true
                    visu_acl: rw


Funktionen
----------

update\_all\_read\_items()
~~~~~~~~~~~~~~~~~~~~~~~~~~

Diese Funktion stößt den Lesevorgang aller konfigurierten Items mit ``viess_read``-Attribut an. 


read\_addr(addr)
~~~~~~~~~~~~~~~~

Diese Funktion löst das Lesen des Parameters mit der übergebenen Adresse ``addr`` aus. Die Adresse muss als vierstellige Hex-Zahl im String-Format übergeben werden. Es können nur Adressen ausgelesen werden, die im Befehlssatz für den aktiven Heizungstyp enthalten sind. Unabhängig von der Itemkonfiguration werden durch ``read_addr()`` keine Werte an Items zugewiesen.
Der Rückgabewert ist das Ergebnis des Lesevorgangs oder None, wenn ein Fehler aufgetreten ist.


read\_temp\_addr(addr, length, unit)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Diese Funktion versucht, den Parameter an der Adresse ``addr`` zu lesen und einen Wert von ``length`` Bytes in die Einheit ``unit`` zu konvertieren. Die Adresse muss als vierstellige Hex-Zahl im String-Format übergeben werden, im Gegensatz zu ``read_addr()`` aber nicht im Befehlssatz definiert sein. ``length`` ist auf Werte zwischen 1 und 8 (Bytes) beschränkt. ``unit`` muss im aktuellen Befehlssatz definiert sein.
Der Rückgabewert ist das Ergebnis des Lesevorgangs oder None, wenn ein Fehler aufgetreten ist.


write\_addr(addr, value)
~~~~~~~~~~~~~~~~~~~~~~~~

Diese Funktion versucht, den Wert ``value`` an die angegebene Adresse zu schreiben. Die Adresse muss als vierstellige Hex-Zahl im String-Format übergeben werden. Es können nur Adressen beschrieben werden, die im Befehlssatz für den aktiven Heizungstyp enthalten sind. Durch ``write_addr`` werden Itemwerte nicht direkt geändert; wenn die geschriebenen Werte von der Heizung wieder ausgelesen werden (z.B. durch zyklisches Lesen), werden die geänderten Werte in die entsprechenden Items übernommen.


:Warning: Das Schreiben von beliebigen Werten oder Werten, deren Bedeutung nicht klar ist, kann im Heizungsgerät möglicherweise unerwartete Folgen haben. Auch eine Beschädigung der Heizung ist nicht auszuschließen.


:Note: Wenn eine der Plugin-Funktionen in einer Logik verwendet werden sollen, kann dies in der folgenden Form erfolgen:

.. code::yaml

    result = sh.plugins.return_plugin('viessmann').read_temp_addr('00f8', 2, 'DT')


Web-Interface
-------------

Im Web-Interface gibt es neben den allgemeinen Statusinformationen zum Plugin zwei Seiten.

Auf einer Seite werden die Items aufgelistet, die Plugin-Attributen konfiguriert haben. Damit kann eine schnelle Übersicht über die Konfiguration und die aktuellen Werte geboten werden.

Auf der zweiten Seite werden alle im aktuellen Befehlssatz enthaltenen Parameter aufgelistet. Dabei besteht für jeden Wert einzeln die Möglichkeit, einen Lesevorgang auszulösen. Die Rückgabewerte werden in die jeweilige Tabellenzeile eingetragen. Dieser entspricht der Funktion ``read_addr()``, d.h. es werden keine Item-Werte aktualisiert. 

Weiterhin kann in der Zeile für den Parameter "_Custom" eine freie Adresse angegeben werden, die analog zur Funktion ``read_temp_addr()`` einen Lesevorgang auf beliebigen Adressen erlaubt. Auch hier wird der Rückgabewert in die jeweilige Tabellenzeile eingetragen. Damit wird ermöglicht, ohne großen Aufwand Datenpunkte und deren Konfiguration (Einheit und Datenlänge) zu testen.


Standalone-Modus
----------------

Wenn der Heizungstyp nicht bekannt ist, kann das Plugin im Standalone-Modus (also ohne SmartHomeNG zu starten) genutzt werden. Es versucht dann, mit der Heizung zu kommunizieren und den Gerätetyp zu identizifieren.

Dazu muss das Plugin im Plugin-Ordner direkt aufgerufen werden:

``./__init__.py <serieller Port> [-v]``

Der serielle Port ist dabei die Gerätedatei bzw. der entsprechende Port, an dem der Lesekopf angeschlossen ist, z.B. ``/dev/ttyUSB0``. Dieses Argument ist verpflichtend.

Das optionale zweite Argument `-v` weist das Plugin an, zusätzliche Debug-Ausgaben zu erzeugen. Solange keine Probleme beim Aufruf auftreten, ist das nicht erforderlich.

Sollte die Datei sich nicht starten lassen, muss ggf. der Dateimodus angepasst werden. Mit ``chmod u+x __init__.py`` kann die z.B. unter Linux erfolgen.