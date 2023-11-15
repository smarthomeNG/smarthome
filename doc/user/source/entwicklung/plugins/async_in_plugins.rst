
.. index:: AsyncIO in Plugins
.. index:: Plugin; AsyncIO

.. role:: redsup
.. role:: bluesup

================================
AsyncIO in Plugins :redsup:`neu`
================================

SmartHomeNG ist eine Thread-basierte Anwendung. Mit Version 3.4 kam eine initiale Unterstützung von asynchronem
In- und Output (asyncio) in Python hinzu. Asyncio ist ein Teil der Standard Bibliothek von Python. Mit den ersten
Releases gab es noch eine größere Anzahl Änderungen am asyncio API. Seit Python 3.8 hat asyncio einen recht stabilen
Zustand erreicht.

Viele der neueren Packages für Python nutzen asyncio. Diese Packages in Plugins zu integrieren ist nicht ohne Haken
und Ösen. Im Folgenden sind einige Informationen zusammengestellt, um in einem (tread-basierten) Plugin asyncio zu
nutzen.

|

Methoden des Plugins
====================

Eine Reihe von Methoden eines Plugins werden von außerhalb des Plugins aufgerufen. Diese Aufrufe erfolgen in
unterschiedlichen Threads. die Eventloop von asyncio läuft dem gegenüber nur in einem Thread

.. csv-table:: Threads in denen Plugin Methoden ausgeführt werden
  :header: "Methode des Plugins", "Aufruf erfolgt in Thread"

   "init()",                               "Main Thread von SmartHomeNG"
   "parse_item()",                         "Main Thread von SmartHomeNG"
   "run(), beim Start von SmartHomeNG",    "Thread des Plugins"
   "stop(), beim Start von SmartHomeNG",   "Main Thread von SmartHomeNG"
   "poll_device()",                        "ein Thread Worker-Pool des Schedulers"

|

Asyncio und Threads kombinieren
===============================

Bei der Kombination von Threads und asyncio gibt es zwei zu berücksichtigende Übergänge:

  - Aufruf von IO-Blocking Code in async Co-Routinen
  - Aufruf von asyncio Code in einem Thread basierte Programm

Eine gut Beschreibung zu den Herausforderungen und Lösungen findet sich in dem Artikel
`Combining Traditional Thread-Based Code and Asyncio in Python <https://https://www.dataleadsfuture.com/combining-traditional-thread-based-code-and-asyncio-in-python/>`__

