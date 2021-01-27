
=====================
Bau der Dokumentation
=====================

Diese Dokumentation ist Teil des github Repository von SmartHomeNG. Eine aktuelle Version dieser Dokumentation
kann aus dem **develop** Branch mit Hilfe der folgenden Instruktionen gebaut werden.

Zurzeit gibt es eine Anwender Dokumentation und eine separate Entwickler Dokumentation. Die Entwickler Dokumentation
wird nach und nach in die Anwender Dokumentation integriert werden, so dass am Ende nur noch eine Dokumentation
übrig bleiben wird.


----------------------------------
Checkout und Bau der Dokumentation
----------------------------------

Zuerst muss ein lokaler Ordner für den Build-Prozess angelegt werden:

.. code-block:: bash

   cd /usr/local
   sudo mkdir shng_doc
   sudo chown -R smarthome:smarthome /usr/local/shng_doc


Das Build-Skript muss aus der lokalen SmartHomeNG Installation in diesen Ordner kopiert und
ausführbar gemacht werden:

.. code-block:: bash

   cd shng_doc
   cp /usr/local/smarthome/doc/build_doc.sh .
   chmod 755 build_doc.sh


Die Python Packages, die für den Bau der Dokumentation benötigt werden, müssen installiert werden:

.. code-block:: bash

   pip3 install sphinx sphinx_rtd_theme recommonmark


Der eigentliche Bau der Dokumentation erfolgt mit dem folgenden Befehl:

.. code-block:: bash

   ./build_doc.sh


Dieses Skript erzeugt einen Unterordner **work** in welchem der eigentliche Build Prozess abläuft und die
Ergebnisse gespeichert werden.

Nachdem das Skript beendet ist, ist die Anwender Dokumentation im Ordner

  /usr/local/smarthome/doc/build_doc/work/doc/user/build/html

gespeichert und die Entwickler Dokumentation ist im Ordner

  /usr/local/smarthome/doc/build_doc/work/doc/developer/build/html

gespeichert. Jede dieser beiden Dokumentationen kann durch öffnen der zugehörigen index.html
im Browser getrachtet werden.


--------------------------
Optionen des Build Skripts
--------------------------

Das Skript build_doc.sh einige Optionen die hilfreich sind, wenn die Dokumentation wiederholt gebaut
werden soll.

Wenn das Build Skript ein zweiter mal gestartet wird, wird die Dokumentation aus den Dateien gebaut, die bereits
bei einem vorangegangenen Bau aus github ausgecheckt wurden. Wenn die Dateien erneut ausgecheckt werden sollen, muss
das Skript build_doc.sh mit der Option **-f** aufgerufen werden. (-f = force checkout)

Falls nur eine Dokumentation gebaut werden soll (**user** oder **developer**), muss das Skript mit den
Optionen **-u** oder --*d** aufgerufen werden.

Falls die Dokumentation aus dem **master** Branch gebaut werden soll, muss die Option **-m** angegeben werden.
Das sollte mit der Option **force checkout** kombiniert werden, um sicherzustellen, dass die richtigen Dateien
ausgecheckt sind: build_doc.sh -f -m
