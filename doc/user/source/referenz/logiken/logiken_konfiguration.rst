:tocdepth: 5

.. role:: bluesup

.. index:: Konfiguration; Logiken
.. index:: Logiken; Konfiguration


===================
Logik Konfiguration
===================

Details zur Konfiguration von Logiken finden sich :doc:`hier <../../konfiguration/logiken>` .


Zur Konfiguration einer Logik wird in der Datei **../etc/logic.yaml** ein Abschnitt für die
Logik angelegt. Unter dem Namen dieses Abschnitts wird die Logik an anderen Stellen referenziert.

In diesem Abschnitt muss SmartHomeNG mitgeteilt werden, welche Code Datei ausgeführt werden soll
und unter welchen Umständen. Dazu werden die im Folgenden beschriebenen Parameter genutzt.


.. include:: logiken_standardparameter.rst


Die folgenden Parameter können genutzt werden um eine Logik und ihre Ausführungsumstände festzulegen:

.. _logik_parameter_watch_item:

watch_item
~~~~~~~~~~

Die Liste der angegebenen Items wird auf Änderungen überwacht

.. code-block:: yaml
   :caption:  etc/logic.yaml

   logicnamehere:
      watch_item:
       - house.alarm
       - garage.alarm


Jede Änderung bei den Items **house.alarm** oder **garage.alarm** löst die Ausführung der angegebenen Logik aus.
Es ist möglich einen Stern * für einen Pfadbestandteil zu setzen, ähnlich eines regulären Ausdrucks:

.. code-block:: yaml

   watch_item: '*.door'

Eine Änderung von **garage.door** oder auch **house.door** wird die Ausführung der Logik auslösen aber **nicht**
eine Änderung von **house.hallway.door**


.. _logik_parameter_cycle:

cycle
~~~~~

Sorgt für eine zyklische Ausführung der Logik

.. code-block:: yaml

   cycle: 60


Optional kann ein Argument übergeben werden

.. code-block:: yaml

   cycle: 60 = 100


Dadurch wird die Logik alle 60 Sekunden ausgeführt und der Wert 100 an die Logik übergeben.
Innerhalb der Logik kann auf den Wert über ``trigger['value']`` zugegriffen werden


.. _logik_parameter_crontab:

crontab :bluesup:`Update`
~~~~~~~~~~~~~~~~~~~~~~~~~

.. Der Inhalt der Beschreibung von crontab wurde aus referenz/items/standard_attribute/crontab.rst 1:1 kopiert

Es gibt drei verschiedene Parametersätze für ein Crontab Attribut:

.. tabs::

      .. tab:: init
         Das Item wird zum Start von SmarthomeNG aktualisiert und triggert
         dadurch unter Umständen eine zugewiesene Logik:

         .. code-block:: yaml

            crontab: init

         Hier kann auch zusätzlich ein Offset angegeben werden um den
         tatsächlichen Zeitpunkt zu verschieben:

         .. code-block:: yaml

            crontab: init+10    # 10 Sekunden nach Start

      .. tab:: Zeitpunkte

         Das Item soll zu bestimmten Zeitpunkten aktualisiert werden.
         Die Schreibweise ist an Linux Crontab angelehnt, entspricht diesem aber nicht genau.
         Es gibt je nach Parameteranzahl 3 Varianten:

         * ``crontab: <Minute> <Stunde> <Tag> <Wochentag>``
         * ``crontab: <Minute> <Stunde> <Tag> <Monat> <Wochentag>``
         * ``crontab: <Sekunde> <Minute> <Stunde> <Tag> <Monat> <Wochentag>``

         Dabei sind je nach Variante folgende Werte zulässig:

         * Sekunde: ``0`` bis ``59``
         * Minute: ``0`` bis ``59``
         * Stunde: ``0`` bis ``23``
         * Tag: ``1`` bis ``31``
         * Monat: 1 bis 12  oder ``jan`` bis ``dec``
         * Wochentag ``0`` bis ``6``   oder ``mon``, ``tue``, ``wed``, ``thu``, ``fri``, ``sat``, ``sun``

         Alle Parameter müssen durch ein Leerzeichen getrennt sein und innerhalb eines Parameters
         darf kein zusätzliches Leerzeichen vorhanden sein, sonst kann der Parametersatz nicht ausgewertet werden.

         Im folgenden Beispiel wird jeden Tag um 23:59 ein Trigger erzeugt und der Wert 70 gesetzt.

         .. code-block:: yaml

            crontab: 59 23 * * = 70

         Für jede dieser Zeiteinheiten (Minuten, Stunde, Tag, Wochentag) werden
         folgende Muster unterstützt (Beispiel jeweils ohne Anführungszeichen verwenden):

         * eine einzelne Zahl, z.B. ``8`` → immer zur/zum 8. Sekunde/Minute/Stunde/Tag/Wochentag
         * eine Liste von Zahlen, z.B. ``2,8,16`` → immer zur/zum 2., 8. und 16. Sekunde/Minute/Stunde/Tag/Monat/Wochentag
         * ein Wertebereich, z.B. ``1-5`` → immer zwischen dem/der 1. und 5. Sekunde/Minute/Stunde/Tag/Monat/Wochentag
         * einen Interval, z.B. ``\*\/4`` → immer alle 4 Sekunden/Minuten/Stunden/Tage/Wochentage
         * einen Stern, z.B. ``*`` → jede Sekunde/Minute/Stunde/Tag/Monat/Wochentag

      .. tab:: Zeitpunkte bezogen auf Aufgang von Sonne oder Mond

         Nach dem Muster ``[H:M<](sunrise|sunset|moonrise|moonset)[+|-][offset][<H:M] (<day> <month> <weekday>)`` kann ein Triggerpunkt bezogen
         auf Sonne oder Mond berechnet werden:

         * ``sunrise`` → immer zum Sonnenaufgang
         * ``sunset`` → immer zum Sonnenuntergang
         * ``sunrise`` und untere Begrenzung → ``06:00<sunrise`` zum Sonnenaufgang, frühestens um 6 Uhr
         * ``sunrise`` und obere Begrenzung →  ``sunrise<09:00`` zum Sonnenaufgang, spätestens um 6 Uhr
         * ``sunset``  und obere und untere Begrenzung → ``17:00<sunset<20:00`` zum Sonnenuntergang, frühestens um 17:00 und spätestens um 20:00 Uhr
         * ``sunrise`` und Minuten-Offset → ``sunrise+10m`` 10 Minuten nach Sonnenaufgang
         * ``sunset``  und Minuten-Offset → ``sunset-10m`` 10 Minuten vor Sonnenuntergang
         * ``sunset`` und Grad-Offset → ``sunset+6`` Sonnenuntergang wenn Sonne 6 Grad am Horizont erreicht

         Soll die erweiterte Variante mit Angabe von Tag, Monat und Wochentag genutzt werden, so müssen immer alle Parameter angegeben werden.
         Die Zusatzangaben müssen dann durch einen Leerschritt getrennt werden.
         Sofern Zusatzangaben vorhanden sind, werden sie UND verknüpft. Das folgende Beispiel würde einen Triggerzeitpunkt festlegen für den nächsten
         Sonnenuntergang der an einem 24. Dezember stattfindet und ein Sonntag ist. (das wäre am 24.Dezember 2023)

         .. code-block:: yaml

            crontab: sunset 24 12 sun

         Das Item soll zu einem bestimmten Sonnenstand aktualisiert werden:

         .. code-block:: yaml

            crontab: sunrise-10m
            crontab: sunset+6
            crontab: sunset


Sämtliche Optionen können in einer \*.yaml durch Listenbildung erstellt werden. Im Admin Interface können die einzelnen Parametersätze durch `` | `` getrennt werden.

Durch Anhängen eines ``= value`` wird der entsprechende Wert ``value`` mitgesendet.
Das Beispiel setzt den Wert des Items täglich um Mitternacht auf ``20``:


.. code-block:: yaml

   crontab:
      - 0 0 * * = 20
      - sunrise

Möchte man einen Wert im Minutentakt aktualisieren, ist es notwendig den Ausdruck ``* * * *`` unter Anführungszeichen zu setzen.

.. code-block:: yaml

   crontab: '* * * * = 1'

Folgendes Beispiel zeigt wie alle 15 Sekunden der Wert ``42`` gesendet wird:

.. code-block:: yaml

   crontab: '*/15 * * * * * = 42'


.. _logik_parameter_enabled:

enabled
~~~~~~~

``enabled`` kann auf ``False`` gesetzt werden um die Ausführung der Logik auszusetzen
Der Ausführungsstatus der Logik kann über das CLI-Plugin oder das Admin Interface gesetzt werden


.. _logik_parameter_prio:

prio
~~~~

Setzt die Priorität der Logik im Kontext des Schedulers.
Jeder Wert zwischen ``1`` und ``10`` ist erlaubt mit ``1`` für die höchste Priorität und ``10`` die niedrigste.
Im Normalfall ist eine Angabe der Priorität nicht notwendig, die Vorgabe für alle Logiken ohne
Prioritätsangabe ist ``5``.


.. _logik_parameter_user_parameter:

User Parameter
~~~~~~~~~~~~~~

Weitere Parameter können innerhalb der Logik mit ``self.parameter_name`` abgefragt werden.
Im ersten Beispiel ist für die vierte definierte Logik ein Parameter ``usage_warning: 500`` angelegt worden.





Details zur Erstellung von Logiken finden sich unter  :doc:`Logiken </logiken/logics>`
und :doc:`Entwicklung/Logiken </entwicklung/logiken/logiken>`.