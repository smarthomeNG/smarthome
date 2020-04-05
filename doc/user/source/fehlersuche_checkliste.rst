
.. role:: bluesup
.. role:: redsup


.. index:: Fehlersuche; Checkliste

Checkliste für die Fehlersuche
==============================

Wenn etwas nach erfolgter Installation nicht funktioniert, kann anhand folgender Punkte geprüft
werden, was nicht klappt. Hilfe gibt es auch im `Supportforum im KNX-User-Forum <https://knx-user-forum.de/forum/supportforen/smarthome-py>`_
im KNX-User-Forum. Aber bitte erstmal alles durchdenken und prüfen. Wenn andere Euch weiterhelfen
sollen, dann müsst ihr Informationen beisteuern:

* Debug Ausgabe anhängen, mindestens bis das Problem ersichtlich geloggt wird. (Dazu SmartHome.py mit
  der Option **-d** starten)
* Error und Warnings soweit möglich bereits vorher beseitigen
* evtl. die etc/plugin.conf und die items mit denen Euer Problem zusammenhängt
* Wichtig ist auch u.U. die verwendete Hardware (VM oder Raspi 1, 2, 3) das Betriebssystem
  (Raspbian, Ubuntu x.y, Debian x.y) und ob eibd oder knxd genutzt werden.

Davor bitte einmal durch diese Liste durcharbeiten.


.. index:: Fehlersuche; Läuft SmartHomeNG?

Läuft SmartHomeNG?
------------------

Dazu (per SSH) eine shell auf den Rechner auf dem alles laufen soll öffnen. Um festzustellen ob SmartHomeNG läuft,
kann der folgende Befehl genutzt werden:

.. code-block:: bash

    ps -ef|grep smarthome|grep bin

Es sollte eine Zeile augegeben werden, die etwa so aussieht:

.. code-block:: bash

    smartho+ 28373     1  1 12:45 ?        00:00:02 python3 bin/smarthome.py

Die Zeile zeigt an, dass unter dem User **smarthome** (hier zu smartho+ abgekürzt) unter der PID **28373** seit **12:45**
Uhr SmartHomeNG (**python3 bin/smarthome.py**) ausgeführt wird.


------


Für SmartHomeNG gilt wie beim Highlander:  Es kann nur Einen geben. Daher wird ein Versuch SmartHomeNG aus einer
Installation heraus mehrfach zu starten durch SmartHomeNG verhindert.

Falls sich mehrere SmartHomeNG Installationen auf dem Rechner befinden, können diese nur parallel betrieben werden, wenn
bei der Konfiguration strikt darauf geachtet wird, dass alle IP Verbindungen der zweiten Instanz auf andere Ports
konfiguriert sind. Sonst wird der Start mit Problemen bei der Bindung an die IP quittiert. Das läßt sich gut im Log
von erkennen:

.. code::

   <Datum + Uhrzeit> ERROR    Connections  WebSocket: problem binding 192.168.x.y:2424 (TCP): [Errno 98] Address already in use
   <Datum + Uhrzeit> ERROR    Connections  CLI: problem binding 0.0.0.0:2323 (TCP): [Errno 98] Address already in use


Wenn Fehler dieser Art gezeigt werden dann ist dies ein klares Indiz dafür, das SmartHomeNG bereits läuft und die zwei
Instanzen nicht sauber konfiguriert sind. Um SmartHomeNG also im Debugmodus zu starten, muß die laufende Instanz erst
beendet werden. Das geht mit smarthome.py -s oder aber man startet auf der Shell

.. code::

   kill -9 <Prozess-ID>


wobei die <Prozess-ID> aus dem Aufruf ps -ef ersichtlich wird, siehe oben.


.. index:: Fehlersuche; SmartHomeNG im Debugmodus starten

SmartHomeNG im Debugmodus starten
---------------------------------

Eine einfache Möglichkeit Logeinträge bis zum Level DEBUG zu erhalten, ist es SmartHomeNG im Debug Modus zu starten.
Allerdings werden dabei aus allen Komponenten und Plugins die Logausgaben bis zum Level DEBUG erweitert. Dieses führt
zu einer sehr großen Anzahl von Log Einträgen und ist deshalb recht unübersichtlich.

.. note::

    Vorzuziehen ist eine gezielte Aktivierung der DBUG Ausgaben für einzelne Komponenten oder Plugins. Dieses geschieht
    über die Logging Konfiguration in /etc/logging.yaml bzw. über die GUI des Admin Interfaces.


.. code::

   cd /usr/local/smarthome/bin
   python3 smarthome.py -d


Jetzt sollte eine Menge an Loggingdaten aufgelistet werden. Der Debugmodus ist die Grundlage
für weitere Fehlersuche


.. index:: Fehlersuche; Zugriff auf den KNX via eibd

Zugriff auf den KNX via eibd
----------------------------

.. code::

   ps ax | grep eibd


Nun sollte so etwas ähnliches gezeigt werden:

.. code::

   smarthome@sh13:~$ ps ax | grep eibd
     908 ?        Ss     1:13 /usr/bin/eibd --daemon --Server --Tunnelling --no-tunnel-client-queuing --Discovery --GroupCache --listen-tcp -d/tmp/eibd.log --pid-file=/var/run/eibd.pid --eibaddr=1.1.208 ipt:<IP der KNX Schnittstelle>
   11045 pts/1    S+     0:00 grep --color=auto eibd
   smarthome@sh13:~$

Im obigen Fall handelt es sich beim laufenden eibd um eine Installation, die auf eine KNX
Schnittstelle zugreift. Wichtig ist hier, das die Zeile **/usr/bin/eibd** auftaucht. Wenn
das der Fall ist, dann läuft der eibd.

Ob der eibd auch schalten kann stellt man fest mit

.. code::

   groupswrite ip:localhost 1/0/170 1


wobei hier 1/0/170 die Gruppenadresse eines Schaltaktors ist, der mit 1 eingeschaltet werden soll.


.. index:: Fehlersuche; Zugriff auf den KNX via knxd

Zugriff auf den KNX via knxd
----------------------------

Hier hängt die weitere Vorgehensweise davon ab auf welchem System der knxd installiert ist.
Bei Ubuntu > 15.x oder Debian 8.x ist die Wahrscheinlichkeit recht hoch, das der Start vom
systemd übernommen wurde. Sollte es ein älteres System sein, dann kann es auch sein, das ein
herkömmliches Startskript verwendet wurde. In diesem Fall ist die Vorgehensweise wie oben unter
eibd, nur das nun synonym dazu knxd benutzt wird.

Für systemd ist es recht einfach festzustellen ob der knxd läuft:

.. code::

   systemctl status


Die Ausgabe sieht dann ähnlich aus wie hier:

.. code::

   smarthome@sh11:~$ systemctl status
   ● sh11
       State: running
        Jobs: 0 queued
      Failed: 0 units
       Since: Fr 2016-03-11 10:49:08 CET; 2 weeks 1 days ago
      CGroup: /
              ├─1 /sbin/init
              ├─system.slice
              │ ├─avahi-daemon.service
              │ │ ├─463 avahi-daemon: running [sh11.local
              │ │ └─489 avahi-daemon: chroot helpe
              ...
              │ ├─knxd.service
              │ │ └─1204 /usr/bin/knxd -u /tmp/eib -b ipt:<IP der knx Schnittstelle>
              ...
              └─user.slice
                └─user-1000.slice
                  ├─session-7.scope
                  │ └─2757 python3 ./smarthome.py -d
                  ├─user@1000.service
                  │ ├─1152 /lib/systemd/systemd --user
                  │ └─1153 (sd-pam)
                  └─session-1119.scope
                    ├─27926 sshd: smarthome [priv
                    ├─27928 sshd: smarthome@pts/
                    ├─27929 -bash
                    ├─28229 systemctl status
                    └─28230 pager
   lines ... -.../<n> (END)


Sollte der knxd.service nicht laufen, so müßt ihr den erstmal in Gang bekommen.
Wenn das aber geklappt hat, kann die Funktion des knxd getestet werden z. B. mit
(Gruppenadresse = 1/0/170 für einen Schaltaktor mit 1 oder 0=

.. code::

   knxtool groupswrite ip:localhost 1/0/170 1


Sollte sich jetzt nichts tun, dann gibt es irgendwo einen Fehler und alles muß noch einmal
geprüft werden. Vielleicht ist der Neustart des knxd vergessen oder beim Erstellen des knxd
packages ein Build-Fehler übersehen worden.


Kann SmartHomeNG schalten?
--------------------------

Nun kann geprüft werden, ob sich von SmartHomeNG ein Schaltvorgang auslösen läßt. Dieses kann über die GUI des
Adminstrations-Interfaces im Item Tree oder mithilfe des Plugins CLI erfolgen. Zur Nutzung von CLI muß zwingend das
Plugin installiert und konfiguriert sein.

Dazu wird eine zusätzliche Shell eröffnet (Nein, Windows Telnet funktioniert hier nicht) und
darin eingegeben

.. code::

   telnet localhost 2323


Nach erfolgreichem Aufbau der Verbindung dann **help** eingeben.

.. code::

   smarthome@<yourcomputer>:~$ telnet localhost 2323

   Trying fe80::c23f:d5ff:fe68:e9ae...
   -telnet: connect to address fe80::c23f:d5ff:fe68:e9ae: Connection refused
   Trying 127.0.1.1...
   Connected to smarthome.local.
   Escape character is '^]'.
   SmartHomeNG v1.4.0
   Enter 'help' for a list of available commands.
   CLI > help
   h: alias for help
   help [group]: show help for group of commands [item, log, logic, scheduler]
   if: list the first level items
   if [item]: list item and every child item (with values)
   ii [item]: dump detail-information about a given item - command alias: dump
   il: list all items (with values) - command alias: la
   iup: alias for iupdate - command alias: up
   iupdate [item] = [value]: update the item with value - command alias: update
   ld [logic]: disables logic - command alias: dl
   le [logic]: enables logic - command alias: el
   li [logic]: logic information - dump details about given logic
   ll: list all logics and next execution time - command alias: lo
   logc [log]: clean (memory) log
   logd [log]: log dump of (memory) log
   lr [logic]: reload a logic - command alias: rl
   lrr [logic]: reload and run a logic - command alias: rr
   lt [logic]: trigger a logic - command alias: tr
   rt: return runtime
   si [task]: show details for given scheduler task
   sl: list all scheduler tasks by name
   st: list all scheduler tasks by execution time
   tl: list current thread names
   quit, q: quit the session
   CLI >


Am einfachsten, die Befehle werden mal ausprobiert, z.B. **ls** um die First Level Items aufzulisten,
dann **ls item** um ein bestimmten item abzufragen und schließlich **update item = 1** für z.B. einen
Schaltaktor einer Lampe um das Licht anzuschalten.

Wenn es bis hierher geklappt hat, dann ist das Grundsystem funktional.


Kontakt mit SmartVISU
---------------------

Es ist wichtig für die Fehlersuche SmartHomeNG im Debugmodus zu starten. So kann bequem verfolgt
werden, was passiert, wenn z.B. auf der Visu ein Button geklickt wird.

Die häufigsten Fehler sind:

+-----------------------------------------+--------------------------------------------------------------------+-------------------------------------------------+
| Ursache                                 | Fehlerbild                                                         | Behebungsansatz                                 |
+=========================================+====================================================================+=================================================+
| Dateiformat der Item-Datei ist          | Beim Start von SmartHomeNG bricht der Einlesevorgang für die Items | Per Telnet verbinden und Items auflisten lassen |
| nicht im UTF-8 ohne BOM angelegt.       | in der betreffenden Datei ab und die Items werden nicht angelegt.  |                                                 |
+-----------------------------------------+--------------------------------------------------------------------+-------------------------------------------------+
| In der Smartvisu werden bei den Widgets | Keine Funktion bei einigen Widgets bzw. merkwürdige Seiteneffekte  | Debug-Ausgabe zeigt zu ändernde Items an,       |
| doppelte ID vergeben oder Itemname und  |                                                                    | diese auf Plausibilität prüfen                  |
| ID vertauscht oder aber Leerzeichen     |                                                                    |                                                 |
| innerhalb der ID oder des Itemnamen.    |                                                                    |                                                 |
+-----------------------------------------+--------------------------------------------------------------------+-------------------------------------------------+
| Zugriff auf ein Item ist über die Visu  | Kein Schalten möglich, Werte werden nicht aktualisiert             | visu_acl: rw oder visu: yes fehlt bei einem     |
| nicht gegeben.                          |                                                                    | Item oder als globales Setting beim Plugin      |
|                                         |                                                                    | visu_smartvisu                                  |
+-----------------------------------------+--------------------------------------------------------------------+-------------------------------------------------+


Zugriff auf SH.py via CLI Plugin aus Windows mit putty oder kitty
-----------------------------------------------------------------

Für den Zugriff via Telnet auf das CLI Plugin aus Windows, sind einige Dinge zu beachten:

In Putty bitte folgende Settings beachten, damit der Zugriff auf das CLI Plugin funktioniert:

Session:

- Connection type -> RAW wählen (nicht Telnet!)
- Host Namen des Servers eintragen, Port 2323 (oder wie er in der plugin.conf konfiguriert ist)<

Terminal:

- Implicit CR in every LF -> Haken setzen

Connection - Telnet:

- Keyboard sends Telnet special commands -> Haken setzen
- Return key sends Telnet New Line instead of ^M -> Haken entfernen

Mehr Informationen zum CLI Plugin unter: :doc:`./plugins/cli/README`

