.. index:: Standard-Attribute; cycle
.. index:: cycle

cycle
=====

Das Attribut definiert ein regelmäßiges Aufrufen des Items (und damit
der verknüpften Logik oder Eval-Funktion).

.. code-block:: yaml

   item:
       cycle: 10
       enforce_updates: 'true'

ruft das Item alle 10 Sekunden auf und sorgt dadurch für das triggern
von verknüpften Logiken und/oder Eval-Funktionen. Dazu muss
``enforce_updates`` auf ``true``\ stehen, damit das Triggern erfolgt,
auch wenn sich der Wert des Items nicht ändert.

.. code-block:: yaml

   item:
       type: num
       cycle: 10 = 0
   #    enforce_updates: true

setzt alle 10 Sekunden den Wert des Items auf 0. Wenn mit diesem Item
Logiken und/oder Eval-Funktionen verknüpft sind, muss
``enforce_updates`` auf ``true``\ stehen, damit das Triggern erfolgt,
auch wenn sich der Wert des Items nicht ändert.

Bitte beachten: `Datentyp der
Wertzuweisung <#datentyp-der-wertzuweisung>`__

**Ab SmartHomeNG v1.3** werden die Konfigurationsmöglichkeiten
erweitert.

Der Wert für ``dauer`` kann auf folgende Weise angegeben werden:

1. eine Zahl, die die Anzahl an Sekunden angibt, optional kann ein ``s`` angehängt werden.
2. eine Zahl gefolgt von ``m``, gibt die Anzahl an Minuten an

Außerdem kann ab SmartHomeNG v1.3 der `Datentyp der
Wertzuweisung <#datentyp-der-wertzuweisung>`__ beeinflusst werden.

Datentyp der Wertzuweisung
--------------------------

Bei der Nutzung von ``autotimer``\ und ``cycle`` ist eine Besonderheit
zu beachten: Unabhängig vom mit ``type:`` angegebenen Datentyp erfolgt
in smarthome.py und SmartHomeNG **bis v1.2** die Zuweisung **immer** als
String! Das ist inkonsistent und kann zu unerwarteten Ergebnissen
führen, wenn das Item in ``eval``-Ausdrücken verwendet wird.

**Ab SmartHomeNG v1.3** kann alternativ die Zuweisung des Wertes in dem
Datentyp erfolgen, der mit ``type:`` angegebenen wurde. Das kann jedoch
zu Kompatibilitätsproblemen führen, falls jemand in ``eval``-Ausdrücken
berücksichtigt hat, dass bisher die Wertzuweisung immer als String
erfolgte. Um diese Probleme zu umgehen, kann das Verhalten (Zuweisung
als String oder Zuweisung im richtigen Datentyp) angegeben werden. Die
beiden Modi sind:

-  ``compat_1.2`` - Verhalten, wie in den vorherigen Versionen von
   smarthome.py/SmartHomeNG
-  ``latest`` - Zuweisung der Werte in dem Datentyp, der für das Item
   angegeben ist.

Aus Kompatibilitätsgründen ist der voreingestellte Modus in SmartHomeNG
v1.3 ``compat_1.2``.

Das Verhalten kann global für die SmartHomeNG Installation vorgegeben
werden, indem der Konfigurationsdatei **etc/smarthome.yaml** der Eintrag

.. code-block:: yaml

   assign_compatibility: latest

hinzugefügt wird.

Falls eine Umstellung nicht installationsweit erfolgen soll, kann der
Modus bei jedem ``autotimer`` oder ``cycle`` Attribut als optionaler
dritter Parameter angegeben werden. Wenn keine Angabe des
Kompatibilitätsmodus erfolgt, wird die globale Voreinstellung genutzt.

Die Angabe des Kompatibilitätsmodus erfolgt folgendermaßen:

.. code-block:: yaml

   item:
       cycle: <dauer> = <wert> = <kompatibilität>

Beispiel:

.. code-block:: yaml

   item:
       type: num
       cycle: 5m = 0 = compat_1.2

   item2:
       type: bool
       cycle: 5m = true = latest

Nach auslösen des cycle wird ``item`` der String ``'0'``\ zugewiesen
und ``item2`` wird der boolsche Wert ``True``\ zugewiesen.
