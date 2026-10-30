
.. index:: Referenz; Asyncio in Plugins
.. index:: Asyncio in Plugins
.. index:: Plugins; Asyncio in Plugins

.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup



asyncio Unterstützung in Plugins
================================

Python Packages zur Ansteuerung von Peripherie werden zunehmend unter Verwendung von asyncio erstellt. Um diese
Packages in Plugins nutzen zu können, muss das jeweilige Plugin asyncio unterstützen. Die Implementierung hiervon
ist nicht tirvial und die ersten Plugins die asyncio implementiert haben, tun das sehr unterschiedlich und unter
Nutzung der Low-Level Funktionen von asyncio (was ein erhebliches Error-Handling im Plugin voraussetzt).

Um die Nutzung von asyncio zu vereinfachen und in den Plugins zu standardisieren, unterstützt SmartHomeNG
die Nutzung von asyncio in Plugins durch eine Erweiterung der SmartPlugin Klasse um einige Methoden.

Ein Plugin welches die asyncio Unterstützung nutzt, ist das hue3 Plugin. Es kann bei der der Erstellung eines
neuen Plugins als Beispiel herangezogen werden.

Die Worker-Threads des Default-Executors der Eventloop (``run_in_executor(None, ...)``, ``asyncio.to_thread()``,
DNS-Abfragen) tragen den Namen ``plugins.<Plugin-Name>.asyncio_<n>``, so dass sie z.B. auf der Seite **Threads**
der Admin GUI dem Plugin zugeordnet werden können. Für die mit ``start_asyncio()`` gestartete Eventloop geschieht das
automatisch. Ein Plugin, das eine eigene Eventloop erzeugt, ruft dafür direkt nach dem Erzeugen der Eventloop
``set_asyncio_executor_names(loop)`` auf.

|

Methoden zur Unterstützung von asyncio
--------------------------------------

Im folgenden sind die Methoden beschrieben, die zur asyncio Unterstützung zur SmartPlugin Klasse hinzugekommen sind.

.. autoclass:: lib.model.smartplugin.SmartPlugin
  :members:
  :noindex:
  :undoc-members:
  :show-inheritance:
  :member-order: bysource
