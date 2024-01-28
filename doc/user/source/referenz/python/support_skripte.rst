
.. index:: Support Skripte; Virtual Python Environments
.. index:: Virtuelle Umgebungen; Support Skripte

.. role:: bluesup
.. role:: greensup
.. role:: redsup

===============================
Support Skripte für SmartHomeNG
===============================

Für das arbeiten mit virtuellen Python Environments bringt SmartHomeNG zwei Support-Skripte mit. Diese Skripte sind
im Tools Verzeichnis abgelegt.

|

make_venv Skript
================

Das Skript **make_venv** dient zum Erzeugen von virtuellen Python Umgebungen. Es wird mit einem oder zwei Parametern
aufgerufen. Der erste (Pflicht-)Parameter ist die Python Version. Der zweite optionale Parameter ist der Name
des Environments. Wenn dieser Parameter weg gelassen wird, wird die Python Version als Name des Environments
herangezogen.

.. note::

    Die Python Version, für die ein virtuelles Environment erzeugt werden soll, muss auf dem System bereits installiert
    sein. Details zur Installation von Python sind im Abschnitt
    :ref:`Python Version Installieren <Python_Version_Installieren>` beschrieben.


Um zum Beispiel ein Environment für Python 3.8 zu erzeugen, kann einfach der folgende Befehl eingegeben werden:

.. code-block:: bash

    $ make_venv 3.8

    Python virtual environment 'py_3.8' (Python 3.8.3) created
    in SmartHomeNG installation '/usr/local/shng_dev'

    Package    Version
    ---------- -------
    pip        23.2.1
    setuptools 41.2.0
    wheel      0.41.1

    $

Um dieses Environment nu nutzen, muss es noch mit Hilfe des Skriptes **act** aktiviert werden.

|

act Skript
==========

Das Skript **act** dient zum Aktivieren von vorher erzeugten virtuellen Python Umgebungen. Es wird mit einem
Parameter aufgerufen. Der Parameter ist der Name des Environments. Dem Aufruf des Skriptes muss ``source``
vorangestellt werden, damit die Ergebisse des Skripts auf die aktuelle Shell wirken. Wird ``source`` vergessen,
gibt das skript eine Fehlermeldung aus.

Um zum Beispiel das Environment für Python 3.8 zu aktivieren, kann einfach der folgende Befehl eingegeben werden:

.. code-block:: bash

    $ source act 3.8

    Activating virtual environment py_3.8 (Python 3.8.3)

    To deactivate the virtual environment simply type the command 'deactivate'

    (py_3.8) $

Ein aktives virtuelles Environment wird mit dem Befehl **deactivate** verlassen:

.. code-block:: bash

    (py_3.8) $ deactivate
    $


|

