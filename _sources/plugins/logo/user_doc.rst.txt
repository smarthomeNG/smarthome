.. index:: Plugins; logo
.. index:: logo

====
logo
====

Ansteuerung einer Siemens LOGO SPS.


Voraussetzungen
================

Das Plugin benötigt eine Siemens LOGO (Hardware-Version 0BA7 oder 0BA8) sowie die freie
Bibliothek ``libnodave`` zur Kommunikation mit Siemens-S7-SPSen (verwendete Version: 0.8.4.6,
http://libnodave.sourceforge.net/).

Auf dem Raspberry Pi genügt es, die mitgelieferte Datei ``libnodave.so`` nach ``/lib/libnodave.so``
zu kopieren::

    sudo cp /usr/smarthome/plugins/logo/libnodave.so /lib/libnodave.so

Auf anderen Systemen muss die Bibliothek heruntergeladen und mit ``make`` selbst gebaut werden.

.. important::

   ``libnodave`` läuft nur auf 32-Bit-Systemen.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/logo` beschrieben.

Item-Attribute
--------------

Mit **logo_read** und **logo_write** wird festgelegt, welcher Datenpunkt der LOGO gelesen bzw.
geschrieben wird. Bei mehreren Plugin-Instanzen wird die gewünschte Instanz mit ``@<instanz>`` an
das Attribut angehängt, z.B. **logo_read@logo1**.

Der Wert des Attributs besteht aus einem Kürzel für den Datenpunkttyp und dessen Nummer:

- ``I`` Eingangsbit, lesend (I1 ... I24)
- ``Q`` Ausgangsbit, lesend/schreibend (0BA7 bis Q16, 0BA8 bis Q20)
- ``M`` Merkerbit, lesend/schreibend (0BA7 bis M27, 0BA8 bis M64)
- ``AI`` Analogeingang (Wort), lesend (AI1 ... AI8)
- ``AQ`` Analogausgang (Wort), lesend/schreibend (0BA7 bis AQ2, 0BA8 bis AQ8)
- ``AM`` Analogmerker (Wort), lesend/schreibend (0BA7 bis AM16, 0BA8 bis AM64)
- ``NI`` Netzwerk-Eingangsbit, lesend (0BA8 bis NI64)
- ``NAI`` Netzwerk-Analogeingang (Wort), lesend (0BA8 bis NAI32)
- ``NQ`` Netzwerk-Ausgangsbit, lesend (0BA8 bis NQ64)
- ``NAQ`` Netzwerk-Analogausgang (Wort), lesend (0BA8 bis NAQ16)
- ``VM`` VM-Byte, lesend/schreibend (VM0 ... VM850)
- ``VMx.x`` VM-Bit, lesend/schreibend (z.B. VM0.0, VM3.4 ... VM850.7)
- ``VMW`` VM-Wort, lesend/schreibend (VMW0 ... VMW849)


Beispiele
=========

Konfiguration von zwei LOGO-Instanzen::

    logo1:
        plugin_name: logo
        host: 10.10.10.99
        instance: logo1
    logo2:
        plugin_name: logo
        host: 10.10.10.100
        version: 0BA8
        instance: logo2

Zugriff auf beide Instanzen aus den Items heraus::

    myroom:

        status_I1:
            type: bool
            logo_read@logo1: I1
            logo_read@logo2: I1

        lightM1:
            type: bool
            logo_write@logo1: M4

        temp_measure:
            type: num
            eval: value/10
            logo_read@logo1: AI1

        temp_set:
            type: num
            logo_write@logo1: VMW4
