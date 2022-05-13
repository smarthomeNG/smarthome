
.. index:: Plugins; mpd

===
mpd
===

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left


Anforderungen
-------------
Eine oder mehrere Music Player Daemon müssen funktionsfähig installiert sein.
Für detailierte Informationen zu den Kommandos des MPD siehe
`Hauptseite <http://www.musicpd.org>`_ des Projektes
und die `Dokumentation <https://mpd.readthedocs.io/en/latest/>`_

Notwendige Software
~~~~~~~~~~~~~~~~~~~

Es müssen keine zusätzlichen Module installiert werden

Konfiguration
-------------

plugin.yaml
~~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.

items.yaml
~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


logic.yaml
~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


Funktionen
~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


Beispiele
---------

Für eine Nutzung von zwei Instanzen dient das folgende Konfigurationsbeispiel.
Es soll je eine Instanz für ein Badezimmer und eine Küche angesteuert werden

.. code:: yaml

    mpd_bad:
        plugin_name: mpd
        instance: bad
        host: 192.168.0.45
        port: 6601

    mpd_kueche:
        plugin_name: mpd
        instance: kueche
        host: 192.168.0.55
        port: 6602

Ein Beispiel das für alle Kommandos jeweils ein Item anlegt:

.. code:: yaml

    Bad:
        Musik:
            volume:
                type: num
                mpd_status@bad: volume
                mpd_command@bad: setvol
                enforce_updates: true

            repeat:
                type: bool
                mpd_status@bad: repeat
                mpd_command@bad: repeat
                enforce_updates: true

            playpause:
                type: bool
                mpd_status@bad: playpause
                mpd_command@bad: playpause
                enforce_updates: true

            mute:
                type: bool
                mpd_status@bad: mute
                mpd_command@bad: mute
                enforce_updates: true

            random:
                type: bool
                mpd_status@bad: random
                mpd_command@bad: random
                enforce_updates: true

            single:
                type: bool
                mpd_status@bad: single
                mpd_command@bad: single
                enforce_updates: true

            consume:
                type: bool
                mpd_status@bad: consume
                mpd_command@bad: consume
                enforce_updates: true

            playlist:
                type: num
                mpd_status@bad: playlist

            playlistlength:
                type: num
                mpd_status@bad: playlistlength

            state:
                type: str
                mpd_status@bad: state

            song:
                type: num
                mpd_status@bad: song

            songid:
                type: num
                mpd_status@bad: songid

            nextsongid:
                type: num
                mpd_status@bad: nextsongid

            time:
                type: str
                mpd_status@bad: time

            elapsed:
                type: str
                mpd_status@bad: elapsed

            duration:
                type: num
                mpd_status@bad: duration

            bitrate:
                type: num
                mpd_status@bad: bitrate

            xfade:
                type: num
                mpd_status@bad: xfade
                mpd_command@bad: crossfade
                enforce_updates: true

            mixrampdb:
                type: num
                mpd_status@bad: mixrampdb
                mpd_command@bad: mixrampdb
                enforce_updates: true

            mixrampdelay:
                type: num
                mpd_status@bad: mixrampdelay
                mpd_command@bad: mixrampdelay
                enforce_updates: true

            audio:
                type: str
                mpd_status@bad: audio

            updating_db:
                type: str
                mpd_status@bad: updating_db

            error:
                type: str
                mpd_status@bad: error

            file:
                type: str
                mpd_songinfo@bad: file

            Last-Modified:
                type: str
                mpd_songinfo@bad: Last-Modified

            Artist:
                type: str
                mpd_songinfo@bad: Artist

            Album:
                type: str
                mpd_songinfo@bad: Album

            Title:
                type: str
                mpd_songinfo@bad: Title

            Name:
                type: str
                mpd_songinfo@bad: Name

            Track:
                type: str
                mpd_songinfo@bad: Track

            Time:
                type: str
                mpd_songinfo@bad: Time

            Pos:
                type: str
                mpd_songinfo@bad: Pos

            Id:
                type: str
                mpd_songinfo@bad: Id

            artists:
                type: num
                mpd_statistic@bad: artists

            albums:
                type: num
                mpd_statistic@bad: albums

            songs:
                type: num
                mpd_statistic@bad: songs

            uptime:
                type: num
                mpd_statistic@bad: uptime

            db_playtime:
                type: num
                mpd_statistic@bad: db_playtime

            db_update:
                type: num
                mpd_statistic@bad: db_update

            playtime:
                type: num
                mpd_statistic@bad: playtime

            next:
                type: bool
                mpd_command@bad: next
                enforce_updates: true

            pause:
                type: bool
                mpd_command@bad: pause
                enforce_updates: true

            play:
                type: num
                mpd_command@bad: play
                enforce_updates: true

            playid:
                type: num
                mpd_command@bad: playid
                enforce_updates: true

            previous:
                type: bool
                mpd_command@bad: previous
                enforce_updates: true

            seek:
                type: str
                mpd_command@bad: seek
                enforce_updates: true

            seekid:
                type: str
                mpd_command@bad: seekid
                enforce_updates: true

            seekcur:
                type: str
                mpd_command@bad: seekcur
                enforce_updates: true

            stop:
                type: bool
                mpd_command@bad: stop
                enforce_updates: true

            rawcommand:
                type: str
                mpd_rawcommand@bad: rawcommand
                enforce_updates: true

            radio1:
                type: bool
                mpd_url@bad: "http://streamurlofradio1.de/"
                enforce_updates: true

            radio2:
                type: bool
                mpd_url@bad: "http://streamurlofradio2.de/"
                enforce_updates: true

            plradio1:
                type: bool
                mpd_localplaylist@bad: plradio1
                enforce_updates: true

            plradio2:
                type: bool
                mpd_localplaylist@bad: plradio2
                enforce_updates: true

            playlist1:
                type: bool
                mpd_localplaylist@bad: playlist1
                enforce_updates: true

            playlist2:
                type: bool
                mpd_localplaylist@bad: playlist2
                enforce_updates: true

            updatedatabase:
                type: str
                mpd_database@bad: update
                enforce_updates: true

            rescandatabase:
                type: str
                mpd_database@bad: rescan
                enforce_updates: true

Das zweite Beispiel für die Küche zeigt nur Items die in einer SmartVISU dargestellt werden sollen:

.. code:: yaml

    Kueche:
        Musik:
            volume:
                type: num
                mpd_status@kueche: volume
                mpd_command@kueche: setvol
                enforce_updates: true

            repeat:
                type: bool
                mpd_status@kueche: repeat
                mpd_command@kueche: repeat
                enforce_updates: true

            playpause:
                type: bool
                mpd_status@kueche: playpause
                mpd_command@kueche: playpause
                enforce_updates: true

            mute:
                type: bool
                mpd_status@kueche: mute
                mpd_command@kueche: mute
                enforce_updates: true

            random:
                type: bool
                mpd_status@kueche: random
                mpd_command@kueche: random
                enforce_updates: true

            state:
                type: str
                mpd_status@kueche: state

            Artist:
                type: str
                mpd_songinfo@kueche: Artist

            Album:
                type: str
                mpd_songinfo@kueche: Album

            Title:
                type: str
                mpd_songinfo@kueche: Title

            Name:
                type: str
                mpd_songinfo@kueche: Name

            Track:
                type: str
                mpd_songinfo@kueche: Track

            next:
                type: bool
                mpd_command@kueche: next
                enforce_updates: true

            previous:
                type: bool
                mpd_command@kueche: previous
                enforce_updates: true

            stop:
                type: bool
                mpd_command@kueche: stop
                enforce_updates: true




Web Interface
-------------

Todo: Ein Webinterface muss noch erstellt werden

Die Datei ``dev/sample_plugin/webif/templates/index.html`` sollte als Grundlage für Webinterfaces genutzt werden. Um Tabelleninhalte nach Spalten filtern und sortieren zu können, muss der entsprechende Code Block mit Referenz auf die relevante Table ID eingefügt werden (siehe Doku).

SmartHomeNG liefert eine Reihe Komponenten von Drittherstellern mit, die für die Gestaltung des Webinterfaces genutzt werden können. Erweiterungen dieser Komponenten usw. finden sich im Ordner ``/modules/http/webif/gstatic``.

Wenn das Plugin darüber hinaus noch Komponenten benötigt, werden diese im Ordner ``webif/static`` des Plugins abgelegt.
