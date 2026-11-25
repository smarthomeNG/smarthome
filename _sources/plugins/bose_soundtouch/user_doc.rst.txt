.. index:: Plugins; bose_soundtouch
.. index:: bose_soundtouch

bose_soundtouch
===============

Das Plugin dient zum Steuern von `Bose Soundtouch <https://www.bose.de/de_de/products/speakers/smart_home/soundtouch_family.html>`_
Systemen.

Es werden folgende Funktionen unterstützt:

- Grundfunktionen (Ein-/Ausschalten, Play, Pause, Mute, nächster/vorheriger Titel, ...)
- Lautstärkeregelung
- Statusinformationen (aktueller Titel, Cover, Quelle, ...)
- Auslesen und Auswählen von Presets

.. important::

   Es wird aktuell nur ein Bose Soundtouch Gerät unterstützt. Zonen- bzw. Multiroom-Betrieb
   wird nicht unterstützt.

   Das Plugin kann mit SmartHomeNG v1.6 und höher genutzt werden.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/bose_soundtouch` beschrieben.

Für die Item-Konfiguration stehen fertige Structs zur Verfügung, die direkt eingebunden werden können:

.. code:: yaml

    BoseSoundtouch:
      actions:
        struct: bose_soundtouch.actions
      presets:
        struct: bose_soundtouch.presets
      status:
        struct: bose_soundtouch.status
      volume:
        struct: bose_soundtouch.volume

- **actions**: Items zur Steuerung der Grundfunktionen (Ein-/Ausschalten, Play, Pause, Mute, nächster/vorheriger Titel, ...)
- **presets**: (nur lesend) Informationen zu den Presets
- **status**: (nur lesend) Statusinformationen (aktueller Titel, Cover, Quelle, ...)
- **volume**: Lautstärkeregelung
