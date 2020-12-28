. index:: Konfiguration
.. index:: Konfiguration; Sichern und Wiederherstellen

.. role:: redsup
.. role:: bluesup

==================================
Update von einer älteren Version
==================================

Es kann verschiedene Szenarien geben von denen aus man ein Update machen möchte. Es gibt unterschiedliche Ansätze
wenn es sich um eine Virtuelle Maschine handelt oder wenn ein Raspberry Pi upgedated werden soll. Es gibt hier
leider nicht **die** Methode. Leider gibt es derzeit auch keine vollständige Systemübergreifende Backup Methode.
Es ist also ein wenig ein Stückwerk.

Vorgehensweise
==============

Die Reihenfolge ist prinzipiell folgende:

- Unter Linux einen Dienst, der SmartHomeNG automatisch startet (systemd) abschalten, beispielsweise mit

  .. code:: bash

      /usr/local/smarthome$ sudo systemctl disable smarthome.service

- Über das Admin-Interface via **Dienste -> Konfiguration - letzte Sicherung -> Herunterladen** 
  eine Sicherung der Konfiguration erstellen (ein ZIP Archiv wird über den Browser heruntergeladen)
- SmartHomeNG selbst beenden beispielsweise mit 

  .. code:: bash

      /usr/local/smarthome$ python3 bin/smarthome.py -s

  oder wenn SmartHomeNG via systemd sonst automatisch gestartet wird mit

  .. code:: bash

      /usr/local/smarthome$ sudo systemctl stop smarthome.service

- Variable Daten sichern, die sich in ``var`` befinden:

    - Datenbank z.B. SQLite in ``var/db`` von SmartHomeNG 
    - Cache für die Itemwerte in ``var/cache``
    - ggf. Logfiles

- `Betriebssystemupdate`_ durchführen
- zusätzliche Dienste aktualisieren und prüfen

  - knxd
  - onewire, owserver
  - mqtt
  - SmartVISU

Der Weitere Weg hängt davon ab ob man eine Standardinstallation gemäß Komplettanleitung vorgenommen hat oder
ob man manuell neue Plugins angelegt hat oder sonstige Änderungen außerhalb der Konfigurationsdateien
vorgenommen hat. Kurz: ob ein ``git pull`` funktioniert oder nicht.

- Aktualisieren der Basisinstallation über ein ``git pull`` und
  aktualisieren der Plugins im plugin Verzeichnis ebenfalls über ein ``git pull``

  Falls dieser Schritt fehlschlägt, kann man auf `Plan B`_ verzweigen
  *Fehlschlagen* bedeutet in diesem Zusammenhang das es eine Meldung gibt das es ungesicherte Änderungen gibt.
  Wer sich mit Git auskennt, weiß dann das es gilt die Änderungen die man an lokalen Dateien des Core
  oder auch der Plugins gemacht hat zu sichern oder sie in die neue Version zu *mergen*, also zu integrieren.
  Für jemand der nicht genau weiß was passiert ist und der sich in solch einer Situation auch nicht zu helfen
  weiß geht daher auf `Plan B`_ weiter.

- Erstmaliges Starten aus dem Basisverzeichnis ``usr/local/smarthome/`` mit ``python3 bin/smarthome.py``
  --> Die neuen benötigten Bibliotheken werden von SmartHomeNG selbständig installiert

- Prüfen ob es in ``var/log/`` aktualisierte Log Dateien mit Warnungen oder Fehlern gibt.
  Wenn SmartHomeNG gestartet ist, kann davon ausgegangen werden, das alle benötigten Bibliotheken vorhanden sind. 
  Logs können dann über das Admin Interface überprüft werden.
  
  Alternativ kann auch der Inhalt von ``var/log/`` aufgelistet werden mit ``ls -la var/log/`` um Log-Dateien 
  zu finden, die sich gerade geändert haben. Diese lassen sich dann mit ``less`` oder ``cat`` anzeigen oder
  auch mit ``nano <Dateiname>`` innerhalb des Verzeichnisses ``var/log/`` editieren.

Plan B
------

- Umbenennen des Basisverzeichnisses ``/usr/local/smarthome`` in z.B. ``/usr/local/smarthome.old``
- Installation von SmartHomeNG gemäß Komplettanleitung :doc:`/installation/komplettanleitung/02_smarthomeng`
- Wenn alles funktioniert, kann die Sicherung mit den Konfigurationsdateien zurückgespielt werden.
- Dann SmartHomeNG wiederum beenden und die gesicherten Daten wie Datenbank, cache, logfiles, rrd etc. 
  zurückspielen und SmartHomeNG starten
- Anschliessend -- wenn wirklich alles läuft -- kann gemäß Komplettanleitung :doc:`/installation/komplettanleitung/02_smarthomeng`
  ein automatischer Start eingerichtet werden

Jemand der sich mit Linux und Git auskennt, kann natürlich auch direkt im Basisverzeichnis und im Pluginverzeichnis
jeweils ein ``git pull`` ausführen und dann per Admin Interface neu starten. Das klappt prinzipiell auch, 
nur muß man wissen was man bei einem Fehlschlag tun muß.


Betriebssystemupdate
====================

Jede SmartHomeNG Version erhöht die Anforderungen an die benötigte Python Version gemäß der Übersicht 
:doc:`/installation/anforderungen` daher sollte vor dem Update von SmarthomeNG 
das Betriebssystem aktualisiert werden.

Bei **Linux** systemen ist damit ein Distributionsupgrade gemeint. Für die aktuelle SmartHomeNG 1.8 also zum Beispiel 
ein Upgrade auf Debian Buster (10.7). Welche Debian Version welche Python Version mitbringt,
kann im `Debian Wiki <https://wiki.debian.org/Python>`__ nachgelesen werden.

Zusätzlich müssen noch die in der Komplettanleitung :doc:`/installation/komplettanleitung/02_smarthomeng`
unter *zusätzliche Linux Pakete installieren* angegebenen Pakete installiert werden.

Für Windows bietet sich eine manuelle Installation von Python 3.8 in der letzten Revision an.

SmartHomeNG 1.8 oder höher wird benötigte Python Bibliotheken selbständig beim ersten Programmstart installieren.

Versionsdetails
===============

Update von SmarthomeNG ab v1.6 und höher
-------------------------------------------

Wenn von einer Version v1.6 oder höher ein Update durchgeführt werden soll, gibt es eine neue Möglichkeit. Statt
ein Update durchzuführen, kann bestehende die Konfiguration gesichert werden, eine Neuinstallation durchgeführt werden
und anschließend die gesicherte Konfiguration eingespielt werden. Das vereinfacht auch das Update, wenn man das
Raspberry Pi Image verwendet.

Wie das Sichern und Wiederherstellen der Konfiguration funktioniert, ist auf der Seite
:doc:`/konfiguration/konfiguration_backup_restore` beschrieben.

.. warning::

    Ganz ausdrücklich werden keine Daten aus dem Unterverzeichnis ``var`` gesichert.
    Also keine Datenbank aus ``var/db`` oder ``var/rrd``, keine Logfiles aus ``log`` und auch keine Cache Daten aus ``var/cache``
    die via Attribut ``cache: True`` befüllt werden.

    Sollen diese Daten gesichert werden, so muß SmartHomeNG zuerst beendet und danach die gewünschten Dateie manuell gesichert werden.


Update von SmarthomeNG ab v1.1 und höher
-------------------------------------------

Wenn man SmarthomeNG laut der Komplettanleitung :doc:`/installation/komplettanleitung/02_smarthomeng`
(mithilfe "git clone [...]") installiert hat, in das Verzeichnis "smarthome" wechseln und anschliessend

.. code-block:: bash

    git pull

eingeben. Daraufhin sollte der Update-Vorgang starten.

Nachdem SmartHomeNG aktualisiert wurde, müssen unbedingt noch die **Plugins
aktualisiert** werden. Dazu in das **plugins** Verzeichnis wechseln und
einen Pull durchführen:

.. code-block:: bash

    cd plugins
    git pull
    cd ..

    .. note::

      Es kann durchaus vorkommen, das das ``git pull`` abgebrochen wird mit einer
      Fehlermeldung der Art:

      .. code-block: python

         error: Ihre lokalen Änderungen in den folgenden Dateien würden durch den
         Merge überschrieben werden:
         requirements/all.txt
         Bitte committen oder stashen Sie Ihre Änderungen, bevor sie mergen.
         Abbruch

      In diesem Fall würde ein ``git checkout -- requirements/all.txt`` aus dem
      aktuellen Branch die fragliche Datei auschecken und damit für ``git pull``
      wieder überschreibbar machen.

Anschließend müssen noch benötigte Pakete aktualisiert werden.
Diese werden von Pypi bereitgestellt. Bei SmartHomeNG gibt es zum einen den
Programmkern und die Plugins. Die Abhängigkeiten von externen Bibliotheken
sind für den Programmkern und die Plugins aufgeteilt.
Um eine Liste der Abhängigkeiten zu erstellen, gibt es ein Skript das unter
anderem alle Plugin Unterverzeichnisse durchläuft und die Abhängigkeiten
der Plugins ermittelt. Dies Skript wird aufgerufen mit:

.. code-block:: bash

    python3 tools/build_requirements.py


.. note::

   Ab SmartHomeNG v1.6 werden, falls dieser Schritt ausgelassen wird,
   die Requirements beim Start von SmartHomeNG bestimmt.
   Dabei werden die Packages bestimmt, die vom Core und von den konfigurierten
   Plugins benötigt werden. Sind die Requirements
   nicht erfüllt, beendet sich SmartHomeNG mit einem entsprechenden Eintrag im Log.


Vom Programmkern benötigte Bibliotheken herunterladen und installieren mit:

   .. code-block:: bash

       pip3 install -r requirements/base.txt --user

Und dann für jedes Plugin einzeln die benötigten Bibliotheken herunterladen
und installieren mit:

   .. code-block:: bash

       pip3 install -r plugins/<pluginname>/requirements.txt --user


.. attention::

    In früheren Beschreibungen wurde die globale Installation von Python Packages mit dem sudo Kommando
    beschrieben:

       sudo pip3 install -r requirements/base.txt

    Dieses funktioniert unter Debian Buster **NICHT** mehr. Zumindest unter Buster **muss** die Installation
    für den entsprechenden User mit **--user** erfolgen (wie oben beschrieben).


Zum Abschluss dann SmarthomeNG starten. Um zu prüfen, ob sich vielleicht
Fehler oder Änderungen in den Plugins ergeben haben, sollte man dies im
von der Kommandozeile aus machen:

.. code-block:: bash

    python3 bin/smarthome.py


Jetzt heißt es genau zu schauen, was an **WARNING** oder **ERROR** gemeldet wird. Logfiles findet man im
Verzeichnis ``../var/log`` (in der Standardinstallation unter ``/usr/local/smarthome/var/log``).
Von da aus kann man sie mit einem Editor in Ruhe anschauen und auf Fehler durchsuchen.

Wenn dann die Konfiguration stimmt, kann man natürlich den automatischen
Neustart von SmartHomeNG wieder einschalten. In der Komplettanleitung
ist beschrieben, welche Schritte dafür bei Verwendung von systemd
durchgeführt werden müssen.



Upgrade von Smarthome.py 
-------------------------

Das letzte Release von Smarthome.py wurde am 14. November 2013 veröffentlicht. 
Zu der Zeit war *Debian Wheezy* (7.x) gerade ein halbes Jahr alt, *systemd* war 
in den Kinderschuhen und den eibd mußte man sich selbst kopieren.
Es gibt daher in vielen Bereichen etliche Entwicklungsschübe die es rechtfertigen
eine vollständige Neuinstallation vorzuschlagen. Trotzdem sollte es möglich sein,
relativ problemlos auf SmartHomeNG umzusteigen.

.. note::

    Wichtig ist zu wissen, das sich die Struktur der Datenbank geändert hat und daher
    **eine existierende SQLite Datenbank nicht weiterverwendet werden kann**.

Vorgehensweise 
~~~~~~~~~~~~~~

Da nicht mehr viele User eine Umstellung vornehmen müssen und die Entwickler lange schon 
auf SmartHomeNG umgestiegen sind, ist die folgende Beschreibung eventuell nicht ganz vollständig
oder gegebenenfalls nicht exakt genug. Bei Fragen steht der gitter chat oder das Forum
zur Verfügung.
Die Vorgehensweise beim Upgrade ist prinzipiell folgende:

- Unter Linux automatischen Start von Smarthome.py abschalten
- Smarthome.py selbst beenden falls noch nicht geschehen
- Das komplette Smarthome.py Verzeichnis ``/usr/local/smarthome/`` **auf einem anderen Rechner** sichern.
- Betriebssystem neu aufsetzen und Installation von SmartHomeNG gemäß Komplettanleitung :doc:`/installation/komplettanleitung/02_smarthomeng`
  durchführen. SmartHomeNG sollte gestartet und via Admin Interface geprüft werden ob es fehlerfrei startet.
- Die im vorletzten Schritt gesicherte Installation von Smarthome.py kann nun zurückgesichert werden, 
  z.B. an ``/usr/local/smarthome.old``. Somit stehen die alten Konfigurationsdateien zur Verfügung für die Übernahme.

Plugins
~~~~~~~

Wenn das neue SmartHomeNG grundsätzlich startet, können **zunächst die Plugins** übernommen werden.
Es bietet sich an die Plugins entweder 

- über das Admin Interface hinzuzufügen und zu konfigurieren wobei eine
  parallel geöffnete ``/usr/local/smarthome.old/etc/plugins.conf`` als Referenz für die richtigen Werte ideal ist

oder manuell

- über das Admin Interface unter Dienste --> CONF-YAML Konverter den Inhalt der ``/usr/local/smarthome.old/etc/plugins.conf`` 
  in yaml Format umwandeln und das Ergebnis an die Datei ``/usr/local/smarthome/etc/plugins.yaml`` anhängen bzw. einarbeiten.
  Dabei muß natürlich selbst auf Doppelungen und die Einrückebene geachtet werden. 

Nun sollte ein Neustart von SmartHomeNG durchgeführt und die Logdateien auf Fehler kontrolliert werden. 
Das kann entweder über das Admin Interface geschehen oder es muß in ``/usr/local/smarthome/var/log/smarthome-warnings.log``
geschaut werden.

Eine falsche Konfiguration kann nach dem Neustart auch via Admin Interface angepasst werden. Wenn keine weiteren Fehler auftreten
können die Items übernommen werden.

Items
~~~~~~

Die empfohlene Vorgehensweise für die Übernahme der Items besteht aus den Schritten

- kopieren der Dateien mit den Definitionen der Items aus der alten Installation ``/usr/local/smarthome.old/items/``
  in das Verzeichnis ``/usr/local/smarthome/items/`` der neuen Installation.
- starten des Konvertierungstools:

  .. code-block:: bash
  
      /usr/local/smarthome$ python3 tools/conf_to_yaml_converter.py

  Bei erfolgreichem Durchlauf des Konverters ist jetzt für jede ``*.conf`` Datei eine passende ``*.yaml`` Datei erstellt worden.
  Wenn das überprüft wurde können die ``*.conf`` Dateien nun aus ``/usr/local/smarthome/items/`` gelöscht werden.

Nun sollte wiederum ein Neustart von SmartHomeNG durchgeführt und die Logdateien auf Fehler kontrolliert werden. 
Das kann entweder über das Admin Interface geschehen oder es muß in ``/usr/local/smarthome/var/log/smarthome-warnings.log``
geschaut werden.

Logiken
~~~~~~~~

Die empfohlene Vorgehensweise für die Übernahme der Logiken besteht aus den Schritten

- kopieren der Dateien mit den Definitionen der Logiken aus der alten Installation ``/usr/local/smarthome.old/logics/``
  in das Verzeichnis ``/usr/local/smarthome/logics/`` der neuen Installation.

- über das Admin Interface unter Dienste --> CONF-YAML Konverter den Inhalt der ``/usr/local/smarthome.old/etc/logics.conf`` 
  in yaml Format umwandeln und das Ergebnis an die Datei ``/usr/local/smarthome/etc/logics.yaml`` anhängen bzw. einarbeiten.
  Dabei muß natürlich selbst auf Doppelungen und die Einrückebene geachtet werden. 

Nun sollte wiederum ein Neustart von SmartHomeNG durchgeführt und die Logdateien auf Fehler kontrolliert werden. 
Das kann entweder über das Admin Interface geschehen oder es muß in ``/usr/local/smarthome/var/log/smarthome-warnings.log``
geschaut werden.

Konvertierung von \*.conf-Dateien
==================================

Möchte man vom alten ``*.conf`` Format der Konfigurationsdateien
(die ab Version 2.0 nicht weiter unterstützt werden) auf das neue
``*.yaml`` Format umschwenken, so kann der im Verzeichnis ``../tools``
bereitgestellte Konverter ``conf_to_yaml_converter.py`` genutzt werden
um das automatisch zu tun.

.. note::

    Nacharbeiten empfehlen sich auf jeden Fall für Item Attribute deren
    Werte als String erwartet werden, die aufgrund ihrer Struktur aber als
    float eingelesen werden. Ein prominentes Beispiel sind Onewire Adressen:
    Bei ``ow_addr:  28.169712030000`` wird ein float ``28.16971203`` erkannt,
    bei ``ow_addr:  '28.169712030000'`` hingegen wird die Adresse korrekt als 
    String ``'28.169712030000'`` erkannt mit den Nullen am Ende.

