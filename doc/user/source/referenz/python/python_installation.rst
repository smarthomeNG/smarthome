
.. index:: Python installieren

.. role:: bluesup
.. role:: greensup
.. role:: redsup

=========================================
Python Version Installieren :redsup:`Neu`
=========================================

Im folgenden wird beschrieben, wie weitere Python Versionen unter Linux installiert werden. Das wird am Beispiel der
Python Version 3.10.12 beschrieben,

|

Installation von benötigten Paketen
===================================

Für das Compilieren von Python müssen einige Linux Pakete installiert werden. Es muss sichergestellt sein, dass
weitere Software installiert ist. Das ist z.B. der ``gcc`` Compiler und ``make``. Der Compiler und make werden
durch Installation von ``build-essential`` installiert. Bei Debian 12 (Bookworm) ist ``build-essential`` bereits
vorinstalliert.

.. code-block:: bash

    sudo apt install build-essential
    sudo apt install libssl-dev

|

Download des Source Codes
=========================

Auf der website **python.org** unter **Downloads/Source Code** die gewünschte Version suchen und die das entsprechende
Archiv (XZ compressed source tarball) herunter laden. Die Datei träget den Namen **Python-3.10.12.tar.xz**.
Anschließend diese Datei auf dem SmartHomeNG-System in das Verzeichnis **/usr/local/src** kopieren. (Aufgrund der
Verzeichnisrechte muss das evtl. mit sudo geschehen)

|

Das Archiv auspacken
====================

Zum auspacken des Archivs in das Verzeichnis **/usr/local/src** wechseln und anschließend mit **tar** das Archiv
auspacken.

.. code-block:: bash

    cd /usr/local/src
    sudo tar -xf Python-3.10.12.tar.xz

Dabei wird das Verzeichnis **Python-3.10.12** angelegt und das Archiv wird in dieses Verzeichnis entpackt.

|

Source Code konfigurieren
=========================

Sobald der Python-Source-Code extrahiert wurde, zum Konfigurationsskript navigieren und es ausführen:

.. code-block:: bash

    cd Python-3.10.12
    ./configure

Die Konfiguration kann einige Zeit dauern. Bitte warten, bis der Vorgang erfolgreich abgeschlossen wurde und
erst dann fortfahren.

|

Den Build-Prozess starten
=========================

Der Build-Prozess wird mit

.. code-block:: bash

    sudo make altinstall

gestartet.

Wenn der Build Prozess erfolgreich war, wird die Python Version in das Verzeichnis **/usr/local/bin** installiert.

Dieses kann mit

.. code-block:: bash

    python3.10 --version

überprüft werden. Als Ausgabe sollte **Python 3.10.12** angezeicgt werden.

