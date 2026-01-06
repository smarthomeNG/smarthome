Alternativ knxd compilieren
===========================

In älteren Debian Linux Versionen ist kein Installationspaket für knxd enthalten. Unter diesen Versionen
muss knxd zuerst aus dem Quellcode compiliert werden.

Grundsätzlich findet sich auf der `knxd-Seite <https://github.com/knxd/knxd>`__ die Anleitung für die
Installation. Auf der Github Seite kann unter **Code** immer der Branch ausgewählt werden. Jeder Branch
hat sein eigenes Read.me.

.. important::

    Der knxd wird derzeit aktiv weiterentwickelt. Auch bitte **vor** der
    Installation hier noch einen Blick auf `knxd-Seite <https://github.com/knxd/knxd>`__ werfen
    um aktuelles nicht zu verpassen.

    Diese Anleitung ist eher eine historische Referenz und wird nicht regelmäßig aktualisiert.

Die folgenden Installationsschritte beziehen sich auf Version **0.14**.


zusätzliche Pakete zum Bau installieren
---------------------------------------

Zunächst müssen für den Bau einige grundlegende Tools installiert
werden:

.. code-block:: bash

    sudo apt-get install git-core build-essential dh-systemd autoconf libtool libusb-1.0-0-dev pkg-config libsystemd-dev libev-dev cmake


Quellcode laden, compilieren und ein Paket schnüren
---------------------------------------------------

Zunächst den Quellcode für den knxd vom github laden und sicherstellen,
das der 0.14 branch gewählt wird:

.. code-block:: bash

    git clone https://github.com/knxd/knxd.git
    cd knxd
    git checkout v0.14

Im Unterverzeichnis ``tools``\ findet sich ein Skript was benötigt wird
um libfmt herunterzuladen und zu bauen

.. code-block:: bash

    tools/get_libfmt

Dann übersetzen und das Paket schnüren:

.. code-block:: bash

    dpkg-buildpackage -b -uc

Wichtig ist, das am Ende der Paketerstellung keine Fehler gemeldet
wurden.

Sollte die Paketerstellung fehlerfrei ablaufen, dann kann das Paket nun
noch installiert werden mit:

.. code-block:: bash

    cd ..
    sudo dpkg -i knxd_*.deb knxd-tools_*.deb

