:tocdepth: 1

FAQ - Häufig gestellte Fragen
=============================

Das Schalten von KNX Aktoren aus der smartVISU funktioniert nicht
-----------------------------------------------------------------

**Antwort**: Da sind drei unterschiedliche Tools involviert, die
miteinander reden müssen:

1. **EIBD oder KNXD**: (welcher daemon genutzt ist dabei nicht
   erheblich). Die Funktionsfähigkeit des daemon kann mit dem Kommando
   ``groupswrite``  getestet werden. Solange das nicht funktioniert, kann
   auch die Ansteuerung aus SmartHomeNG und smartVISU nicht
   funktionieren.

2. **SmartHomeNG**: Damit SmartHomeNG mit dem KNX Bus reden kann, muss
   das KNX-Plugin richtig konfiguriert sein. Dieses erfolgt in der Datei
   ``/etc/plugin.yaml``

   Um zu testen, ob SmartHomeNG mit dem KNX Bus redet, kann man
   Quick-and-Dirty in der Konfigurationsdatei bei dem Item das geschaltet werden
   soll, einen Eintrag value = 1 oder value = 0 ergänzen und SmartHomeNG
   neu starten. Dann sollte der KNX Aktor zusammen mit dem Start von SmartHomeNG
   ein- bzw. ausschalten.

   Erst wenn diese Kommunikation funktioniert, macht es Sinn sich der
   Visu zuzuwenden.

3. **smartVISU**: Die smartVISU muss richtig konfiguriert sein, damit
   sie mit SmartHomeNG spricht. Sonst sieht es zwar aus, als würde sie
   schalten, tut sie aber nicht.

   Auf der Konfigurationsseite muss unter I/O-Connection folgendes
   eingetragen sein:

   -  Driver: Smarthome.py
   -  Address:
      ``<IP Adresse oder DNS Name der SmartHomeNG Installation>``
   -  Port: 2424
   -  Realtime: on

   Wichtig: Der Eintrag **localhost** als Adresse funktioniert
   **nicht**!

FAQ auf der Website von SmartHomeNG
-----------------------------------

Eine aktuellere (weil zeitnah pflegbare) Sammlung der FAQ ist auf der
Website von SmartHomeNG unter https://www.smarthomeng.de/faq-page zu
finden
