
.. index:: Admin GUI; Logiken
.. index:: Logiken; Admin GUI

=======
Logiken
=======

Liste der Logiken
=================

Unter **Logiken** wird eine Liste der konfigurierten Logiken mit einer Reihe von Informationen angezeigt.
Rechts in der jeweiligen Zeile sind Buttons, über die

- eine Logik ausgelöst (getriggert) werden kann,
- eine Logik neu geladen werden kann,
- eine Logik deaktiviert bzw. aktiviert werden kann,
- eine Logik entladen werden kann,
- eine Logik inclusive Code und Parametern gelöscht werden kann

Die Liste der geladenen Logiken ist nach dem Namen der Logik alphabetisch sortiert.

Nicht geladene Logiken werden am unteren Ende der Liste angezeigt. Für nicht geladene Logiken stehen
nur zwei Buttons zum Auslösen von Aktionen zur Verfügung, über die

- eine Logik geladen werden kann,
- eine Logik inclusive Code und Parametern gelöscht werden kann

Oberhalb der Liste findet sich ein Button, der die Erstellung einer neuen Logik ermöglicht.

Auf einem 2. Tab kann eine Liste der Systemlogiken eingesehen werden.

.. image:: assets/logics.jpg
   :class: screenshot



.. index:: Logiken; Editor

Ab **SmartHomeNG v1.10** können die Logiken in dieser Ansicht gruppiert werden. Wenn mindestens eine Logik einer Gruppe
zugeordnet wird, ändert sich die Ansicht von einer flachen Liste, in eine Liste aufklappbarer Gruppen.

.. image:: assets/logics-grouped.jpg
   :class: screenshot


|

Logik Editor
============

Der Logik Editor ermöglicht es Logiken zu erstellen oder zu ändern, sowie die Parameter zu konfigurieren, welche
die Ausführung der Logik steuern. Der Logik Editor wird durch einen Klick auf den entsprechenden Dateinamen in
der Liste der Logiken oder durch den Button **Neue Logik** gestartet.


Code Editor
-----------

Das Tab mit dem Code Editor ermöglicht den Python Code der Logik zu erfassen/zu ändern.

.. image:: assets/logics-codeeditor.jpg
   :class: screenshot

Ab **SmartHomeNG v1.10** sind Buttons zum Aktivieren/Deaktivieren und zum neu Laden der Logik hinzugekommen.


Parameter Editor
----------------

Das Tab mit den Parametern ermöglicht die Konfiguration der Ausführung der Logik. Hier können verschiedene Trigger
für die Logik konfiguriert werden.

.. image:: assets/logics-parametereditor.jpg
   :class: screenshot

Ab **SmartHomeNG v1.10** sind Felder für die Beschreibung der Logik und zur Zuordnung zu einer bzw. mehreren Gruppen
hinzu gekommen.

Beschreibung
~~~~~~~~~~~~

Hier kann eine Beschreibung der Logik angegeben werden, die dann in der Liste der Logiken angezeigt wird.


Gruppe(n)
~~~~~~~~~

Wenn mehrere Einträge als Liste eingegeben werden sollen, so sind die Einträge durch ein | Zeichen zu trennen.



Cycle
~~~~~

Hier kann angegeben werden, nach wieviel Sekunden die Logik getriggert werden soll.


Crontab
~~~~~~~

Wenn mehrere Einträge als Liste eingegeben werden sollen, so sind die Einträge durch ein | Zeichen zu trennen.


Watch Items
~~~~~~~~~~~

Eine Liste mit Vorschlägen zur Autovervollständigung wird nach Eingabe der ersten 3 Zeichen angezeigt.
Mit den Pfeiltasten kann in der Liste navigiert werden. Mit ENTER wird die Auswahl als Watch-Item hinzugefügt.


Plugin spezifische Parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Falls ein geladenes Plugin einen Logik-Parameter definiert, so wird er in dieser Liste dargestellt und kann bei
Bedarf konfiguriert werden.
