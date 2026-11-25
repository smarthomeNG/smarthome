. index:: Konfiguration
.. index:: Konfiguration; Sichern und Wiederherstellen

.. role:: redsup
.. role:: bluesup
.. role:: greensup

===================================================
Update von einer älteren Version :greensup:`Update`
===================================================

Es kann verschiedene Szenarien geben von denen aus man ein Update machen möchte. Es gibt unterschiedliche Ansätze
wenn es sich um eine Virtuelle Maschine handelt oder wenn ein Raspberry Pi upgedated werden soll. Es gibt hier
leider nicht **die** Methode. Leider gibt es derzeit auch keine vollständige Systemübergreifende Backup Methode.
Es ist also ein wenig ein Stückwerk.

Für das Update auf SmartHomeNG v2.0 gelten zusätzlich die Hinweise im folgenden Abschnitt.


.. _update_auf_2_0:

Update auf SmartHomeNG v2.0 :redsup:`neu`
=========================================

SmartHomeNG v2.0 ist ein Major-Release: Funktionen, die seit längerem als veraltet gekennzeichnet waren, sind
entfernt, und einige Voreinstellungen sind geändert. Eine bestehende Installation läuft deshalb nach dem Update nicht
unbedingt ohne Anpassung weiter. Die meisten Anpassungen erledigt das Tool
:doc:`upgrade_check.py </tools/tools_upgrade_check>`. Die vollständige Liste der Änderungen steht in den
:ref:`Release Notes <releasenotes_2_0_0_update>`.

Was sich ändert
---------------

* **Python**: SmartHomeNG v2.0 startet nur mit Python 3.11 oder neuer (siehe
  :ref:`Python-Versionen <python_versionen>`).

* **Verzeichnisse**: ``items``, ``logics``, ``scenes``, ``structs`` und ``functions`` liegen jetzt unterhalb von
  ``etc``. SmartHomeNG verschiebt vorhandene Verzeichnisse beim ersten Start selbst dorthin. Eigene Skripte, Backups
  oder Freigaben, die auf die alten Pfade zugreifen, müssen angepasst werden.

* **Mehrfach eingebundene Plugins**: Der Name des Abschnitts in der ``etc/plugin.yaml`` ist jetzt der Name der
  Instanz, ``instance:`` wird dort nicht mehr ausgewertet. Das Item-Attribut ``instance`` wird an untergeordnete
  Items vererbt. Die ``etc/plugin.yaml`` und die betroffenen Items müssen dazu passen.

* **Logiken und eval-Ausdrücke**: Die veralteten Methoden des ``sh``-Objekts (z.B. ``sh.return_item()``,
  ``sh.now()``) und ``sh.tools`` gibt es nicht mehr, sie müssen durch die aktuellen ersetzt werden (z.B.
  ``sh.items.return_item()``, ``sh.shtime.now()``).

* **Mehrzeilige Werte in Item- und Struct-Dateien**: Ist ein Wert über mehrere Zeilen geschrieben, werden die Zeilen
  jetzt mit einem Leerzeichen zusammengesetzt, bisher ohne. Solche Stellen müssen geprüft werden.

* **Dateien im .conf-Format** werden nicht mehr gelesen. Sie lassen sich mit
  :doc:`conf_to_yaml_converter.py </tools/tools_conf_to_yaml_converter>` umwandeln.

* **Plugins denon, epson, kodi, lms, oppo, pioneer und viessmann**: Einige Parameter in der ``etc/plugin.yaml`` sind
  entfallen oder umbenannt (siehe Release Notes und die Dokumentation des jeweiligen Plugins).

Schritt für Schritt
-------------------

Die Schritte ergänzen die allgemeine :ref:`Vorgehensweise <update_vorgehensweise>` weiter unten, dort sind die
einzelnen Befehle beschrieben.

1. **Python-Version prüfen** (``python3 --version``): mindestens 3.11. Bei einer älteren Version zuerst das
   `Betriebssystemupdate`_ durchführen.

2. **Sichern**: die Konfiguration (Admin-GUI, Seite **Dienste**, oder wie unter
   :doc:`/konfiguration/konfiguration_backup_restore` beschrieben) und die Daten aus ``var`` (Datenbank, Cache).

3. **SmartHomeNG beenden**. Läuft SmartHomeNG als Dienst, den Dienst vorher abschalten.

4. **Core und Plugins aktualisieren**, und zwar beide: Plugins, die den Core 2.0 benötigen, laden mit einem älteren
   Core nicht.

5. **Konfiguration prüfen und anpassen**, bevor SmartHomeNG v2.0 zum ersten Mal gestartet wird:

   .. code:: bash

       /usr/local/smarthome$ python3 tools/upgrade_check.py

   Das Tool listet die Stellen auf, die angepasst werden müssen, und verändert dabei nichts. Die mit ``[fixable]``
   gekennzeichneten Stellen ändert es mit der Option ``--fix`` selbst. Jede geänderte Datei wird vorher nach
   ``etc/upgrade_check_backup/<Zeitstempel>/`` kopiert:

   .. code:: bash

       /usr/local/smarthome$ python3 tools/upgrade_check.py --fix

   Was das Tool danach noch meldet (z.B. mehrzeilige Werte oder Dateien im .conf-Format), muss von Hand geprüft und
   angepasst werden.

   Das Tool muss mit dem Python gestartet werden, mit dem auch SmartHomeNG läuft (ein Virtual Environment vorher
   aktivieren). Meldet es ``ruamel.yaml is not installed``, fehlt in dieser Python-Umgebung das Paket ``ruamel.yaml``,
   z.B. nach einem Betriebssystemupdate. Es lässt sich mit ``pip3 install "ruamel.yaml>=0.16.7,<0.20"`` installieren.

6. **SmartHomeNG von Hand in der Konsole starten**, nicht über den Dienst:

   .. code:: bash

       /usr/local/smarthome$ python3 bin/smarthome.py

   Beim ersten Start installiert SmartHomeNG die benötigten Bibliotheken und verschiebt die Verzeichnisse ``items``,
   ``logics``, ``scenes``, ``structs`` und ``functions`` nach ``etc``.

   .. attention::

      Liegt im Zielverzeichnis bereits eine Datei mit demselben Namen (z.B. ``items/licht.yaml`` und
      ``etc/items/licht.yaml``), verschiebt SmartHomeNG diese Datei nicht. Es listet die betroffenen Dateien in der
      Konsole auf und beendet sich mit dem Exit-Code 255. Die Meldung steht nicht im Log von SmartHomeNG. Die übrigen
      Dateien sind zu diesem Zeitpunkt schon verschoben. Die genannten Dateien müssen von Hand verschoben oder
      gelöscht werden, danach kann SmartHomeNG erneut gestartet werden.

7. **Logs prüfen**: Fehler und Warnungen in ``var/log`` bzw. in der Admin-GUI ansehen. Läuft alles, den Dienst wieder
   in Betrieb nehmen.

Bisheriges Verhalten vorübergehend beibehalten
----------------------------------------------

Wer die Umstellung der Verzeichnisse oder der Instanznamen nicht sofort durchführen kann, kann dafür das bisherige
Verhalten übergangsweise beibehalten. Dazu in der ``etc/smarthome.yaml`` eintragen:

.. code:: yaml

    config_etc: false          # Verzeichnisse bleiben im Hauptverzeichnis
    legacy_instances: true     # Instanznamen aus 'instance:', keine Vererbung des Item-Attributs instance

Die Einträge müssen **vor dem ersten Start** von SmartHomeNG v2.0 gesetzt sein: Ohne ``config_etc: false`` werden die
Verzeichnisse beim ersten Start verschoben. Beide Schalter sind nur als Übergang gedacht. Alle anderen Änderungen
gelten unabhängig davon.

Plugins
-------

Die Plugins darksky, deebot_ozmo, harmony, roomba_980 und zwave funktionieren nicht mehr, die Plugins influxdb und
influxdb2 sind veraltet. Ersatz und Alternativen nennen die
:ref:`Release Notes <releasenotes_2_0_0_outdated_plugins>`.


.. _update_vorgehensweise:

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
- Installation von SmartHomeNG gemäß Komplettanleitung :doc:`/installation/komplettanleitung/03_smarthomeng`
- Wenn alles funktioniert, kann die Sicherung mit den Konfigurationsdateien zurückgespielt werden.
- Dann SmartHomeNG wiederum beenden und die gesicherten Daten wie Datenbank, cache, logfiles, rrd etc.
  zurückspielen und SmartHomeNG starten
- Anschliessend -- wenn wirklich alles läuft -- kann gemäß Komplettanleitung :doc:`/installation/komplettanleitung/03_smarthomeng`
  ein automatischer Start eingerichtet werden

Jemand der sich mit Linux und Git auskennt, kann natürlich auch direkt im Basisverzeichnis und im Pluginverzeichnis
jeweils ein ``git pull`` ausführen und dann per Admin Interface neu starten. Das klappt prinzipiell auch,
nur muß man wissen was man bei einem Fehlschlag tun muß.


Betriebssystemupdate
====================

Jede SmartHomeNG Version erhöht die Anforderungen an die benötigte Python Version gemäß der Übersicht
:doc:`/installation/anforderungen` daher sollte vor dem Update von SmarthomeNG
das Betriebssystem aktualisiert werden.

Bei **Linux** Systemen ist damit ein Distributionsupgrade gemeint, z.B. ein Upgrade auf Debian 13 (Trixie). Welche
Debian Version welche Python Version mitbringt, kann im `Debian Wiki <https://wiki.debian.org/Python>`__
nachgelesen werden.

Zusätzlich müssen noch die in der Komplettanleitung :doc:`/installation/komplettanleitung/03_smarthomeng`
unter *zusätzliche Linux Pakete installieren* angegebenen Pakete installiert werden.

Für Windows bietet sich eine manuelle Installation der letzten Revision einer der aktuell unterstützten Python
Versionen an - siehe die Übersicht unter :doc:`/installation/anforderungen`.

SmartHomeNG wird benötigte Python Bibliotheken selbständig beim ersten Programmstart installieren.

Varianten des Updates
=====================

Update durch Neuinstallation
----------------------------

Statt ein Update durchzuführen, kann die bestehende Konfiguration gesichert werden, eine Neuinstallation durchgeführt
werden und anschließend die gesicherte Konfiguration eingespielt werden. Das vereinfacht auch das Update, wenn man das
Raspberry Pi Image verwendet.

Wie das Sichern und Wiederherstellen der Konfiguration funktioniert, ist auf der Seite
:doc:`/konfiguration/konfiguration_backup_restore` beschrieben.

.. warning::

    Ganz ausdrücklich werden keine Daten aus dem Unterverzeichnis ``var`` gesichert.
    Also keine Datenbank aus ``var/db`` oder ``var/rrd``, keine Logfiles aus ``log`` und auch keine Cache Daten aus ``var/cache``
    die via Attribut ``cache: True`` befüllt werden.

    Sollen diese Daten gesichert werden, so muß SmartHomeNG zuerst beendet und danach die gewünschten Dateie manuell gesichert werden.


Update mit git
--------------

Wenn man SmarthomeNG laut der Komplettanleitung :doc:`/installation/komplettanleitung/03_smarthomeng`
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
Diese werden von `Pypi <https://Pypi.org>`_  bereitgestellt.
Bei SmartHomeNG gibt es zum einen den Programmkern und die Plugins.
Die Abhängigkeiten von externen Bibliotheken sind für den Programmkern und die Plugins aufgeteilt.
Um eine Liste der Abhängigkeiten zu erstellen, gibt es ein Skript das unter
anderem alle Plugin Unterverzeichnisse durchläuft und die Abhängigkeiten
der Plugins ermittelt. Dies Skript wird aufgerufen mit:

.. code-block:: bash

    python3 tools/build_requirements.py


.. note::

   Falls dieser Schritt ausgelassen wird, werden die Requirements beim Start von SmartHomeNG bestimmt.
   Dabei werden die Packages bestimmt, die vom Core und von den konfigurierten
   Plugins benötigt werden. Sind die Requirements
   nicht erfüllt, beendet sich SmartHomeNG mit einem entsprechenden Eintrag im Log.


.. attention::

    Auf aktuellen Betriebssystemen (Debian ab Version 12/Bookworm, Ubuntu ab 23.04, ...) markiert Python die
    System-Installation als *externally managed* (`PEP 668 <https://peps.python.org/pep-0668/>`_) - ``pip install``
    schlägt dort fehl, egal ob mit oder ohne ``sudo`` bzw. ``--user``. Die Installation von Python Bibliotheken für
    SmartHomeNG **muss** deshalb in einem virtuellen Environment erfolgen. Wie ein virtuelles Environment angelegt
    und aktiviert wird, ist unter :doc:`/referenz/python/virtual_environments` beschrieben - dieser Schritt sollte
    vor den folgenden ``pip3 install`` Kommandos durchgeführt werden.

Vom Programmkern benötigte Bibliotheken herunterladen und installieren mit:

   .. code-block:: bash

       pip3 install -r requirements/base.txt

Und dann für jedes Plugin einzeln die benötigten Bibliotheken herunterladen
und installieren mit:

   .. code-block:: bash

       pip3 install -r plugins/<pluginname>/requirements.txt


Zum Abschluss dann SmarthomeNG starten. Um zu prüfen, ob sich vielleicht
Fehler oder Änderungen in den Plugins ergeben haben, sollte man dies im
von der Kommandozeile aus machen:

.. code-block:: bash

    python3 bin/smarthome.py


Jetzt heißt es genau zu schauen, was an **WARNING** oder **ERROR** gemeldet wird. Logfiles findet man im
Verzeichnis ``var/log`` (in der Standardinstallation unter ``/usr/local/smarthome/var/log``).
Von da aus kann man sie mit einem Editor in Ruhe anschauen und auf Fehler durchsuchen.

Wenn dann die Konfiguration stimmt, kann man natürlich den automatischen
Neustart von SmartHomeNG wieder einschalten. In der Komplettanleitung
ist beschrieben, welche Schritte dafür bei Verwendung von systemd
durchgeführt werden müssen.


Konvertierung von \*.conf-Dateien
==================================

Möchte man vom alten ``*.conf`` Format der Konfigurationsdateien
(das nicht mehr unterstützt wird) auf das
``*.yaml`` Format umschwenken, so kann der im Verzeichnis ``tools``
bereitgestellte Konverter ``conf_to_yaml_converter.py`` genutzt werden
um das automatisch zu tun.

.. note::

    Nacharbeiten empfehlen sich auf jeden Fall für Item Attribute deren
    Werte als String erwartet werden, die aufgrund ihrer Struktur aber als
    float eingelesen werden. Ein prominentes Beispiel sind Onewire Adressen:
    Bei ``ow_addr:  28.169712030000`` wird ein float ``28.16971203`` erkannt,
    bei ``ow_addr:  '28.169712030000'`` hingegen wird die Adresse korrekt als
    String ``'28.169712030000'`` erkannt mit den Nullen am Ende.
