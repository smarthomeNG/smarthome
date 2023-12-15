
.. index:: Linux; Debian installieren

.. role:: bluesup
.. role:: redsup

=========================
Debian Linux installieren
=========================

Die genaue Schritt für Schritt Installation des Betriebsystems wird hier nicht beschrieben, das hier ist der falsche
Ort dafür. Jedoch werden als Referenz die Paketauswahlen während der Installation hier beschrieben.

Am kompaktesten ist die Netinstall ISO-Datei. Zur Installation auf einem externen Rechner (z.B. NUC o.ä.) kann die
ISO-Datei am einfachsten mit dem Tool `Balena Etcher <https://etcher.balena.io>`__ auf einen USB-Stick übertragen werden.

Es können auch andere Tools wie z.B. `Linux Live USB Creator <http://www.linuxliveusb.com/>`__,
`Universal-USB-Installer <http://www.pendrivelinux.com/universal-usb-installer-easy-as-1-2-3/>`__
oder `UNetbootin <https://unetbootin.github.io/>`__ dazu genutzt werden.

Diese Komplettanleitung wurde auf einer virtuellen Maschine unter VMWare mit einem
Debian bullseye 11.3 und Debian Bookworm 12.4 getestet.

Andere Linux Derivate können abweichen, man sollte dann mit den Unterschieden umgehen
können.


.. contents:: Schritte der Installation
   :local:


.. note::

   Die Installation auf einem **Raspberry Pi** kann idealerweise über ein fertiges
   `Image <https://github.com/smarthomeNG/raspberrypi-image/releases>`__ erfolgen bei dem fast alles
   vorbereitet ist. Ansonsten beginnt man am besten mit dem aktuellsten `Raspbian
   Image <https://www.raspberrypi.org/downloads/raspbian/>`__ von der
   `raspberrypi.org <https://raspberry.org>`__ Seite. Dieses Image kann mittels
   `Etcher <https://etcher.io/>`__ oder `Win32Diskimager <https://sourceforge.net/projects/win32diskimager/>`__
   auf eine SD-Karte übertragen werden. Die unten stehenden Schritte bis    **Einloggen via SSH** entfallen.
   Es ist allerdings notwendig, sich beim ersten Start direkt am Raspberry Pi einzuloggen (User: pi, Passwort:
   raspberry - Achtung, englische Tastatur!) und mittels

   .. code-block:: bash

      sudo systemctl start ssh
      sudo systemctl enable ssh

   den SSH Server jetzt und bei zukünftigen Neustarts automatisch zu zu starten.


Im Allgemeinen braucht ein Server keine grafische Benutzeroberfläche, also ganz normale Installation wählen.
Statt (oder zusätzlich zu) einer graphischen Oberfläche sollten die Optionen **SSH Server** und **Webserver**
ausgewählt werden, wenn diese Optionen (wie z.B. unter Debian 12 - Bookworm) zur Verfügung stehen.

Einige Einstellungen die jetzt vorgenommen werden sind:

- Sprache, Tastaturlayout
- Rechnername z.B. **sh**, **shmuc**, **smarthome23**, ...
- Das **root Passwort bitte leer lassen**
- Benutzer **smarthome** anlegen
  (bitte gerade am Raspi ein Passwort vergeben, sonst wird SSH für den Benutzer nicht aktiviert)
- Festplatte geführt partitionieren und gesamten Speicherbereich verwenden, nicht vergessen die
  Änderungen auch auf die Platten zu schreiben

Jetzt erfolgt die Grundinstallation des Systems aus dem Basispaket. Anschließend wird aufgrund der Landesauswahl der
Spiegelserver für die weiteren Dateien festgelegt. Nach der Festlegung konfiguriert das System **apt** und lädt
Pakete aus dem Spiegelserver nach. Das ist die Gelegenheit sich ein Heiß- oder Kaltgetränk nach Wahl zu
holen da der Vorgang je nach Hardware und Netzwerkgeschwindigkeit zwischen 4 und 8 Minuten dauert. Die Rückmeldung
des Systems an die Entwicklung darf abgelehnt werden.


Softwareauswahl
===============

Wenn keine grafische Benutzeroberfläche gebraucht wird, dann bitte
**abwählen**:

-  Debian Desktop Environment

ansonsten sind KDE und Gnome sehr mächtig aber es tut vielleicht ein LXDE auch.

**auswählen**:

-  Web Server (Apache2)
-  SSH Server (wird für SSH z.B. via PuTTY oder Bitvise SSH Client benötigt)
-  Standard-Systemwerkzeuge (falls diese Auswahlmöglichkeit besteht)

Nun ist es Zeit für das nächste Getränk, das Nachladen der zu installierenden Pakete dauert jetzt wiederum
5 bis 20 Minuten. Die angebotene Installation von GRUB sollte akzeptiert und anschließend ein Reboot durchgeführt
werden.


Einloggen via SSH oder an der Konsole
=====================================

| Mit einem **SSH Client** jetzt am Server einloggen:
  Unter **Mac OS X** dazu einfach eine Kommandozeile öffnen und
  folgendes eintippen: ``ssh smarthome@<ip_des_servers>``.
| Unter **Linux** genau das gleiche, Kommandozeile öffnen und folgendes
  eintippen: ``ssh smarthome@<ip_des_servers>``.
| Unter **Windows** gibt es Putty als SSH Client, `download
  hier <http://the.earth.li/~sgtatham/putty/latest/x86/putty.exe>`__.
  Noch komfortabler ist   `Kitty <http://www.9bis.net/kitty/?page=Download>`__. Einfach zunächst
  Putty installieren und umbenennen in Putty.exe.bak. Dann Kitty ins   Verzeichnis vom Putty schreiben
  und umbenennen als Putty.exe. Natürlich ``<ip_des_servers>`` ersetzen durch die IP Adresse oder den
  Namen des neuen SmartHomeNG Servers. **smarthome** ist der Username mit dem man sich anmelden möchte.

Oder alternativ (z.B. bei einer virtuellen Maschine) direkt an der **Konsole** anmelden.

Benutzer zum Anmelden ist **smarthome** und das weiter oben erstellte Passwort für diesen User. Wurde kein
Passwort angegeben und möchte man SSH so konfigurieren, dass man sich mit einem leeren Passwort einloggen
kann, sind folgende Operationen notwendig:

.. code-block:: bash

   sudo sed -i -e 's/#PermitEmptyPasswords no/PermitEmptyPasswords yes/g' /etc/ssh/sshd_config
   sudo sed -i -e '/console/s/.*/&\nssh/' /etc/securetty
   sudo systemctl restart sshd

Generell wird aber empfohlen, den SSH-Zugang mit Zertifikaten abzusichern und ein Einloggen mittels
Username/Passwort zu unterbinden.
Informationen zum `Erstellen von Zertifikaten <https://www.thomas-krenn.com/de/wiki/SSH_Key_Login>`__
gibt es z.B. bei Thomas Krenn.

|

Systemaktualisierung
====================

Nach der Anmeldung ist zunächst mit

.. code-block:: bash

   sudo apt update
   sudo apt upgrade

das frisch installierte System mit den neuesten Systemupdates zu versorgen. Eigentlich sollte dabei nix zu
installieren sein aber sicher ist sicher.

.. hint::

   Für den Fall das SmartHomeNG in einer virtuellen Maschine installiert wird,
   ist jetzt eine gute Gelegenheit diese herunterzufahren mit ``sudo poweroff``
   um einen Snapshot zu erstellen. Falls im weiteren etwas nicht so funktioniert
   wie erwartet, kann so neu angesetzt werden ohne alles erneut herunterladen
   zu müssen.
   Alternativ kann der Snapshot natürlich auch nach Abschluss der Restarbeiten
   weiter unten ausgeführt werden.

.. topic:: Raspberry Pi

   Hat man das Image auf einem Raspberry Pi installiert, können nach dem
   ersten Start sämtliche Einstellungen über ein übersichtliches Menü
   getätigt werden. Es empfiehlt sich, die Sprache auf de_DE.UTF-8 und das
   Tastaturlayout auf Deutsch umzustellen. Außerdem können hier diverse
   Services aktiviert und das Filesystem auf die Größe der SD-Karte
   erweitert werden.

   .. code-block:: bash

      sudo raspi-config


.. hint:: Alternative Netzwerk Konfiguration für feste IP:

   Hierfür sei `auf diese Seite verwiesen <https://wiki.debian.org/NetworkConfiguration>`__


.. tabs::

    .. tab:: Tools für VMWare

        Wenn die Installation in einer virtuellen Maschine unter VMWare erfolgt ist, so werden für
        Debian bullseye 11.3 bereits die open-vm-tools mitinstalliert.

        Für bereits existierende Systeme können die Tools nachinstalliert werden:

        Servervariante

        .. code-block:: bash

          sudo apt-get install open-vm-tools

        Grafische Benutzeroberfläche

        .. code-block:: bash

          sudo apt-get install open-vm-tools-desktop

        Die automatische Anpassung der Bildschirmgröße funktioniert erst nach einem Neustart.


    .. tab:: VirtualBox Gasterweiterungen

        Um die Gästeerweiterungen zu installieren zuerst unter **Geräte** ->
        **Gästeerweiterungen einlegen** anklicken. Diese nun via Terminal/Shell
        ausführen und den Anweisungen folgen:

        .. code-block:: bash

           sudo sh /media/cdrom/VBoxLinuxAdditions.run

        Nach einem Neustart passt sich nun bspw. bei Verwendung einer GUI die
        Auflösung dynamisch an.

|

Restarbeiten am System
======================

sudo für User smarthome
-----------------------

Falls kein Passwort für root vergeben wurde, dann wird der bei der Installation erstellte User (hier: smarthome)
automatisch in die Gruppe für sudo aufgenommen. Dann ist hier nichts weiter zu tun.

Falls man einen anderen Benutzernamen bei der Installation gewählt hat, muss man den User smarthome zunächst erstellen:

.. code-block:: bash

   sudo  adduser smarthome --disabled-password --gecos "First Last,RoomNumber,WorkPhone,HomePhone"

Den Benutzer **smarthome** in die **sudo** Gruppe hinzufügen:

.. code-block:: bash

    sudo usermod -aG sudo smarthome


Standby/Energiesparmodus abschalten
-----------------------------------

Standardmäßig gehen Debian Installationen nach einiger Zeit in den Energiesparmodus. Zur Nutzung für SmartHomeNG
ist das natürlich wenig hilfreich. Durch Editieren der Datei ``/etc/systemd/sleep.conf`` können der Sleep- und der
Hybernate Moduls abgeschaltet werden:

.. code-block:: ini

    [Sleep]
    AllowSuspend=no
    AllowHibernation=no
    AllowSuspendThenHibernate=no
    AllowHybridSleep=no

Damit diese Änderung wirksam wird, muss das System neu gestartet werden.


Anpassung für die smartVISU
---------------------------

Auch wenn der Benutzer smarthome schon existiert muss er für die Nutzung der smartVISU in die Gruppe www-data mit
folgendem Befehl eingetragen werden.

.. code-block:: bash

   sudo usermod -aG www-data smarthome


Anpassung der Userumgebung
--------------------------

Vor dem Neustart wird jetzt noch die Datei ``.bashrc`` bearbeitet um einige Befehle auf der Shell
(Kommandozeile bzw. Konsole) abzukürzen:

.. code-block:: bash

   cd ~
   nano .bashrc

Dort an am Ende anfügen oder wenn bereits vorhanden das Kommentarzeichen ``#`` am Zeilenanfang entfernen:

.. code-block:: bash

   alias la='ls -A'
   alias ll='ls -l'
   alias ..='cd ..'


System abschalten
-----------------

Der Benutzer **smarthome** muß nun abgemeldet und neu angemeldet werden, damit die Rechte neu eingelesen werden.
Dies ist eine gute Gelegenheit um einen alternativen Snapshot zu erstellen. Dazu dann wiederum das
System ausschalten mit:

.. code-block:: bash

   sudo poweroff

