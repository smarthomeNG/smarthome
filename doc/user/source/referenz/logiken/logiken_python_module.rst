:tocdepth: 5

.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup

.. index:: Python Module; Logiken
.. index:: Logiken; Python Module


==============================
Bereits geladene Python Module
==============================

Im Logik Environment sind diverse Python Module bereits geladen. Auf die Funktionen der folgenden Python Packages
kann also zugegriffen werden, ohne sie vorher explizit importieren zu müssen.

Standard Python Packages:

+-----------------+------------------------------------------------+
| Package         | Beschreibung                                   |
+=================+================================================+
| ``sys``         | System-specific parameters and functions       |
+-----------------+------------------------------------------------+
| ``os``          | Miscellaneous operating system interfaces      |
+-----------------+------------------------------------------------+
| ``time``        | Time access and conversions                    |
+-----------------+------------------------------------------------+
| ``datetime``    | Basic date and time types                      |
+-----------------+------------------------------------------------+
| ``random``      | Generate pseudo-random numbers                 |
+-----------------+------------------------------------------------+
| ``queue``       | A synchronized queue class                     |
+-----------------+------------------------------------------------+
| ``subprocess``  | Subprocess management                          |
+-----------------+------------------------------------------------+


weitere Packages von pypi.org:

+-----------------+------------------------------------------------+
| Package         | Beschreibung                                   |
+=================+================================================+
| ``ephem``       | Compute positions of the planets and stars     |
+-----------------+------------------------------------------------+


Import weiterer Python Module
=============================

Weitere Module können normal mit dem import Statement importiert werden.

Beim import von Modulen in Logiken ist eine Besonderheit zu beachten, falls in der Logik Funktionen definiert
werden: Eine Logik verhält sich nicht wie ein Python Modul!

.. important::

    Sollen in der Logik weitere Python Module genutzt werden, so muss bis zu SmartHomeNG v1.9.2 der Import des
    Moduls innerhalb der Funktion erfolgen, die eine Funktion aus dem zu importierenden Python Modul nutzt.

    Ab der Folgeversion v1.9.3 reicht es, wenn der Import in der Hauptroutine am Anfang der Logik erfolgt.

