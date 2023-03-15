
.. index:: Ablauf des Startups

.. role:: bluesup
.. role:: redsup


=================================
Ablauf des Starts von SmartHomeNG
=================================

Im folgenden ist der Ablauf der einzelnen Schritte beschrieben, die beim Start von SmartHomeNG abgearbeitet werden.


Erste Schritte der Initialisierung
==================================

Als allererstes werden die Python Requirements des Core geprüft. Falls sie nicht erfüllt sind (dann kann SmartHomeNG
evtl. nicht mal die Konfigurationsdateien lesen), werden die unbedingt benötigten Packages installiert und
SmartHomeNG wird neu gestartet. (In diesem Stadium erfolgen die Log Ausgaben noch auf den Bildschirm)

Anschließend werden Kommandozeilen Parameter ausgewertet, falls welche angegeben wurden.
Danach wird das smarthome Objekt erzeugt und wie im Folgenden beschrieben initialisert.


Initialisierung des smarthome Objektes
======================================

.. index:: SmartHomeNG Initialisierung

Die Schritte der Objekt Initialisierung sind in Gruppen zusammengefasst. Der Aktuelle Stand (welche Gruppe gerade
abgearbeitet wird bzw. abgearbeitet wurde) wird in der AdminGUI auf der Seite **Dienste** angezeigt.

Die einzelnen Stati haben zur Identifizierung innerhalb von SmartHomeNG jeweils eine eindeutige Nummer, die im
folgenden mit angegeben ist. Nummern kleiner als 10 identifizieren Schritte innerhalb der Objekt Initialisierung.
Schritte größer-gleich 10 und kleiner als 20 identifizieren Schritte innerhalb der start() Methode.


0 - Initialisierung
-------------------

Das smarthome Objekt wird erzeugt und initialisiert. Dazu werden die grundlegenden Variablen initialisiert.
Anschließend wird geprüft ob die benötigten Konfigurationsdateien existieren. Falls nicht, werden die
entsprechenden **<name>.yaml.default** Dateien umkopiert.

Es werden die Konfigurationsdateienb **smarthome.yaml** und **logging.yaml** eingelesen und das Logging wird
initialisiert.


1 - Initialisierung: Logging initialisiert
------------------------------------------

Dis initialisierung des Logging ist abgeschlossen (ab nun erfolgen die Log Ausgaben in die konfigurieten Log-Dateien)

SmartHomeNG wird "daemonized", läuft ab jetzt also im Hintergrund. Anschließend wird der initiale Log Eintrag mit
Versionsinformationen geschrieben.

Die Mehrsprachen Unterstützung wird initialisiert.

Es wird geprüft, ob die benötigten Packages für die Module und die konfigurierten Plugins installiert sind. Falls
nicht, werden die Packages installiert und SmartHomeNG wird neu gestartet.


2 - Initialisierung: Voraussetzungen überprüft
----------------------------------------------

Die benötigten Python Packages sind installiert.

Es werden die definierten Feiertage geladen.

Es wird geprüft, ob die Uhrzeit des Systems gesetzt ist. Falls nicht, wird gewartet bis das Datum des Systems
einen plausiblen Wert hat.

Es werden die Speicherstrukturen für das Memory-Log initialisiert. Diese Strukturen werden für das memlog Plugin
benötigt.


3 - Initialisierung: Prüfung der Prozessor-Geschwindigkeit
----------------------------------------------------------

SmartHomeNG prüft die CPU Geschwindigkeit. Dieses dient zur Optimierung einzelner Abläufe.

Die gemessene Geschwindigkeit wird persistent gespeichert, so dass die Messung bei einem Neustart nicht erneut
durchgeführt wird, es sei denn die Hardware hat sich geändert.


10 - Startet
------------

Es wird der Scheduler initialisiert und gestartet.
Es wird die Class für lib.network initialisiert.


11 - Startet: Initialisiert und startet ladbare Module
------------------------------------------------------

Es werden die konfigurierten Module in der Reihenfolge in der sie in der etc/module.yaml konfiguriert sind geladen
und initialisiert.

Es wird die Wrapper Class für die Items initialisiert.


12 - Startet: Initialisiert Plugins
-----------------------------------

Es werden die konfigurierten Plugins geladen und es wird je geladenem Plugin ein Worker-Thread erzeugt (falls
die Plugins nicht disabled sind)-


13 - Startet: Lädt Item Definitionen
------------------------------------

Es wird für jedes definierte Item ein Objekt erzeugt. Der Wert des Items wird aus den folgenden Quellen
(in der angegebenen Reihenfolge) initialisiert:

- aus dem **initial_value:** bzw. **value:** Attribut
- aus dem Cache, falls das Attribut **cache** auf **True** gesetzt ist.
- evtl. aus den parse_item() Methoden der geladenen Plugins.
  (Das wird z.B. im database Plugin genutzt, falls dort das Item Attribut **database:** auf **init** konfiguriert ist.)


14 - Startet: Geladene Items vorbereiten
----------------------------------------

Es wird für alle geladenen Items die _init_prerun() Methode aufgerufen. Diese erzeugt eval Ausdrücke und Trigger
vor dem ersten Lauf, falls Spezial-Funktionen (**and**, **or**, **sum**, **avg**, **min** oder **max**) verwendet
wurden.

Es wird für alle geladenen Items Scheduler gestartet, falls für das Item das Attribut **crontab:** oder **cycle:**
gesetzt wurde.

Es wird für alle geladenen Items bei denen eval-Ausdrücke **und** eval-Trigger definiert sind, die Berechungen
des eval-Ausdrucks ausgelöst.


15 - Startet: Initialisiert Logiken
-----------------------------------

Es werden die parse_logic() Methoden aller geladenen Plugins aufgerufen und es werden für alle geladenen Logiken
die in **watch_items** definierten Trigger gesetzt.

Anschließend werden die Szenen initialisiert.
Weiterhin wird der **Connections** Scheduler für lib.network gestartet.


16 - Startet: Startet Plugins
-----------------------------

Es wird die start() Methode aller geladenen Plugins aufgerufen.

Anschließend wird der Maintenance Scheduler **sh.gc** von SmartHomeNG gestartet, der regelmäßig eine Garbage
Collection durchführt.


Laufzeit von SmartHomeNG
========================

Der folgende Status tritt nach der Initialisierung ein und bleibt erhalten, bis SmartHomeNG beendet wird:

20 - Aktiv
----------

Die Initialisierung ist abgeschlossen und SmartHomeNG arbeitet normal.


Beendigung von SmartHomeNG
==========================

Die folgenden Stati treten auf, wenn SmartHomeNG beendet oder neu gestartet wird:


30 - Startet neu
----------------

Es wurde ein Neustart von SmartHomeNG ausgelöst.


31 - Stoppen
------------

SmartHomeNG wird beendet.


32 - Stoppen: Threads beenden
-----------------------------

SmartHomeNG beendet laufende Threads.


33 - Angehalten
---------------

SmartHomeNG wurde beendet.

|

Das shng_status dict
====================

.. index:: shng_status
.. index:: SmartHomeNG Status

Die oben beschriebenen Stati können über das ``shng_status`` dict des smarthome Objektes abgerufen werden.
Das Dict enthält zwei Einträge (``code`` und ``text``). Über den Key ``code`` kann auf den numerischen Wert des
Status von SmartHomeNG zugegriffen werden. Unter dem Key ``text`` ist der Status im Klartext hinterlegt. Diese
Texte werden in der Admin GUI unter Dienste angezeigt.

Um sicher zu stellen, dass bestimmter Code nur ausgeführt wird, wenn SmartHomeNG vollständig initialisiert ist und
nicht im Begriff ist sich zu beenden, kann abgefragt werden, ob der Status-Code 20 ist:

.. code-block:: python

    if self._sh.shng_status['code'] == 20:
        ...

