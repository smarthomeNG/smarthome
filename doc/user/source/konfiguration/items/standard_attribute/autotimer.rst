.. index:: Standard-Attribute; autotimer
.. index:: autotimer

*autotimer*
===========

Das Attribut setzt den Wert des Items nach einer Zeitspanne auf einen
bestimmten Wert. Der Timer beginnt zu laufen, wenn dem Item ein Wert
zugewiesen wird. Wenn während der Autotimer läuft dem Item erneut ein
Wert zugewiesen wird, beginnt der Timer erneut zu laufen. Damit lässt
sich z.B. ein Treppenhauslicht realisieren.

.. code-block:: yaml

   item:
       type: num
       autotimer: 5m = 0

setzt nach 5 Minuten den Wert des Items auf 0.

Das allgemeine Format für die Angabe des **autotimer** Attributs ist:

.. code-block:: yaml

   item:
       autotimer: <dauer> = <wert>

Der Wert für *dauer* kann auf folgende Weise angegeben werden:

1. eine Zahl, die die Anzahl an Sekunden angibt
2. eine Zahl gefolgt von **m**, gibt die Anzahl an Minuten an

Bitte beachten: `Datentyp der
Wertzuweisung <#datentyp-der-wertzuweisung>`__

**Ab SmartHomeNG v1.3** werden die Konfigurationsmöglichkeiten
erweitert:

Alternativ zur Angabe von absoluten Werten für *dauer* und *wert*,
können nun auch Items als *dauer* und/oder *wert* angegeben werden:

.. code-block:: yaml

   item:
       type: num
       autotimer: sh.item.dauer() = 0
       dauer:
           initial_value: 45
       wert:
           initial_value: 1

setzt nach der in *item.dauer* angegebenen Dauer (hier initial 45
Sekunden) den Wert des Items auf in *item.wert* (hier initial mit 1
angegebenen). Die Angabe der Items kann auch als relative Angabe erfolgen
(bspw. *sh..dauer()*)

Der Wert für *dauer* kann auf folgende Weise angegeben werden:

1. eine Zahl, die die Anzahl an Sekunden angibt
2. eine Zahl gefolgt von **m**, gibt die Anzahl an Minuten an
3. eine Zahl gefolgt von **s**, gibt die Anzahl an Sekunden an
   (alternative Schreibweise zur Variante 1)

Außerdem kann ab SmartHomeNG v1.3 der `Datentyp der
Wertzuweisung <#datentyp-der-wertzuweisung>`__ beeinflusst werden.

Datentyp der Wertzuweisung
--------------------------

Bei der Nutzung von *autotimer* und *cycle* ist eine Besonderheit zu
beachten: Unabhängig vom mit ``type:`` angegebenen Datentyp erfolgt in
smarthome.py und SmartHomeNG **bis v1.2** die Zuweisung **immer** als
String! Das ist inkonsistent und kann zu unerwarteten Ergebnissen
führen, wenn das Item in ``eval``-Ausdrücken verwendet wird.

**Ab SmartHomeNG v1.3** kann alternativ die Zuweisung des Wertes in dem
Datentyp erfolgen, der mit ``type:`` angegebenen wurde. Das kann jedoch
zu Kompatibilitätsproblemen führen, falls jemand in **eval**-Ausdrücken
berücksichtigt hat, dass bisher die Wertzuweisung immer als String
erfolgte. Um diese Probleme zu umgehen, kann das Verhalten (Zuweisung
als String oder Zuweisung im richtigen Datentyp) angegeben werden. Die
beiden Modi sind:

-  **compat_1.2** - Verhalten, wie in den vorherigen Versionen von
   smarthome.py/SmartHomeNG
-  **latest** - Zuweisung der Werte in dem Datentyp, der für das Item
   angegeben ist.

Aus Kompatibilitätsgründen ist der voreingestellte Modus in SmartHomeNG
v1.3 **compat_1.2**.

Das Verhalten kann global für die SmartHomeNG Installation vorgegeben
werden, indem der Konfigurationsdatei **../etc/smarthome.yaml** der
Eintrag

.. code-block:: yaml

   assign_compatibility: latest

hinzugefügt wird.

Falls eine Umstellung nicht installationsweit erfolgen soll, kann der
Modus bei jedem *autotimer* oder *cycle* Attribut als optionaler dritter
Parameter angegeben werden. Wenn keine Angabe des Kompatibilitätsmodus
erfolgt, wird die globale Voreinstellung genutzt.

Die Angabe des Kompatibilitätsmodus erfolgt folgendermaßen:

.. code-block:: yaml

   item:
       autotimer: <dauer> = <wert> = <kompatibilität>

Beispiel:

.. code-block:: yaml

   item:
       type: num
       autotimer: 5m = 0 = compat_1.2

   item2:
       type: bool
       autotimer: 5m = true = latest

Nach auslösen der Autotimer wird *item* der String **‘0’** zugewiesen
und *item2* wird der boolsche Wert **True** zugewiesen.
