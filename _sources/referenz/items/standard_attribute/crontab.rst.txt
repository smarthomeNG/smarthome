.. index:: Standard-Attribute; crontab
.. index:: crontab

.. role:: bluesup

crontab :bluesup:`Update`
===========================

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
  