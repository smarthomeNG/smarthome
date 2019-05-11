sh.tools Methoden
-----------------

Das sh.tools Objekt stellt einige nützliche Funktionen zur Verfügung:


sh.tools.ping()
^^^^^^^^^^^^^^^

Sendet ein Ping an einen Computer und liefert True zurück, falls der Computer antwortet.

.. code-block:: python

   sh.office.laptop(sh.tools.ping('hostname'))

speichert das Ergebnis des Pings von 'hostname' in das Item office.laptop:


sh.tools.dewpoint()
^^^^^^^^^^^^^^^^^^^

Errechnet der Taupukt für die gegebene Temperatur und Luftfeuchtigkeit.

.. code-block:: python

   sh.office.dew(sh.tools.dewpoint(sh.office.temp(), sh.office.hum())


sh.tools.fetch_url()
^^^^^^^^^^^^^^^^^^^^

Liefert den Inhalt einer Website als String oder ``False``, falls das Lesen der Website fehlschlägt.


.. code-block:: python

   sh.tools.fetch_url('https://www.regular.com') 

Es ist möglich ‘username’ und ‘password’ anzugeben, um sich bei der Website zu authentifizieren:

.. code-block:: python

   sh.tools.fetch_url('https://www.special.com', 'username', 'password') 

Es ist auch möglich das Standard Timeout von 2 Sekunden für den Aufruf zu ändern:

.. code-block:: python

   sh.tools.fetch_url('https://www.regular.com', timeout=4)


sh.tools.dt2ts(dt)
^^^^^^^^^^^^^^^^^^

Converts an datetime object to a unix timestamp.


sh.tools.dt2js(dt)
^^^^^^^^^^^^^^^^^^

Konvertiert ein datetime Objekt zu einem Json Timestamp.


sh.tools.rel2abs(temp, hum)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Konvertiert die relative Luftfeuchtigkeit zur absoluten Luftfeuchtigkeit


sh.tools.runtime()
^^^^^^^^^^^^^^^^^^

Liefert die Laufzeit von SmartHomeNG zurück.



