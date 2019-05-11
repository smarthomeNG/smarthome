SmartHomeNG Items
=================

Unter ``env.core`` finden sich Items mit Daten zur Laufzeit von SmartHomeNG. Diese werden
standardmäßig mit der SmartVISU angezeigt.

::

    env.core.version                    # str: Version von SmarthomeNG
    env.core.update                     # boolean: ?
    env.core.upgrade                    # boolean: ?
    env.core.start                      # foo: Startzeit von SmarthomeNG
    env.core.memory                     # num: Arbeitsspeicherauslastung durch SmarthomeNG
    env.core.threads                    # num: Anzahl der Threads
    env.core.garbage                    # num: Garbage



Umgebungsbezogene Items
=======================

Tag/Nacht
---------

::

    env.location.day                    # boolean: True wenn Tag ist
    env.location.night                  # boolean: True wenn Nacht ist

* Weiterführende Informationen zur Nutzung der Tag-/Nacht-Items in KNX
  finden sich auf der Seite unter Konfiguration/Items auf der Seite
  **Tipps & Tricks**

Mondlicht / -stand
------------------

::

    env.location.moonrise               # Mondaufgang
    env.location.moonset                # Monduntergang
    env.location.moonphase              # Mondphase von 0 - 8
    env.location.moonlight              # Stärke des Mondlichts in %

Sonnenaufgang / Sonnenstand
---------------------------

::

    env.location.sunrise                        # Zeit des Sonnenaufgangs
    env.location.sunrise.azimut.degrees         # Horizontalwinkel bei Sonnenaufgang in Grad
    env.location.sunrise.elevation.degrees      # Höhenwinkel bei Sonnenaufgang in Grad
    env.location.sunrise.azimut.radians         # Horizontalwinkel bei Sonnenaufgang im Bogenmaß
    env.location.sunrise.elevation.radians      # Höhenwinkel bei Sonnenaufgang im Bogenmaß
    env.location.sunset                         # Zeit des Sonnenuntergangs
    env.location.sunset.azimut.degrees          # Horizontalwinkel bei Sonnenuntergang in Grad
    env.location.sunset.elevation.degrees       # Höhenwinkel bei Sonnenuntergang in Grad
    env.location.sunset.azimut.radians          # Horizontalwinkel bei Sonnenuntergang im Bogenmaß
    env.location.sunset.elevation.radians       # Höhenwinkel bei Sonnenuntergang im Bogenmaß
    env.location.sun_position.azimut.degrees    # Aktueller Horizontalwinkel in Grad
    env.location.sun_position.elevation.degrees # Aktueller Höhenwinkel in Grad
    env.location.sun_position.azimut.radians    # Aktueller Horizontalwinkel im Bogenmaß
    env.location.sun_position.elevation.radians # Aktueller Höhenwinkel im Bogenmaß

Zugriffsbeispiel:

::

     if sh.env.location.sun_position.azimut() < 215 and sh.env.location.sun_position.elevation() < 25: 
        ....

System Items
============

Unter ``env.system`` finden sich Informationen zum Betriebssystem wie Systemauslastung, freie Diskspeicher, etc.

::

    env.system.start                    # foo: Startzeit des Systems
    env.system.load                     # num: Load des Systems
    env.system.name                     # str: Name des Systems
    env.system.diskfree                 # num: Freier Speicher des Laufwerks auf dem SmarthomeNG läuft
    env.system.disksize                 # num: Größe des Laufwerks auf dem SmarthomeNG läuft
    env.system.diskusage                # num: Genutzte Größe des Laufwerks auf dem SmarthomeNG läuft
    env.system.diskusagepercent         # num: Genutzte Größe des Laufwerks auf dem SmarthomeNG  läuft (in Prozent)
    env.system.libs.ephem_version       # str: Installierte Version ephem
