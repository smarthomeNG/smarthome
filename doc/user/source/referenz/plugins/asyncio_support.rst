
.. index:: Referenz; Asyncio in Plugins
.. index:: Asyncio in Plugins
.. index:: Plugins; Asyncio in Plugins

.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup



asyncio Unterstützung in Plugins :redsup:`Neu`
==============================================

Python Packages zur Ansteuerung von Peripherie werden zunehmend unter Verwendung von asyncio erstellt. Um diese
Packages in Plugins nutzen zu können, muss das jeweilige Plugin asyncio unterstützen. Die Implementierung hiervon
ist nicht tirvial und die ersten Plugins die asyncio implementiert haben, tun das sehr unterschiedlich und unter
Nutzung der Low-Level Funktionen von asyncio (was ein erhebliches Error-Handling im Plugin voraussetzt).

Um die Nutzung von asyncio zu vereinfachen und in den Plugins zu standardisieren, unterstützt SmartHomeNG ab
v1.11 die Nutzung von asyncio in Plugins durch eine Erweiterung der SmartPlugin Klasse um einige Methoden.

|

Methoden zur Unterstützung von asyncio
--------------------------------------

.. autoclass:: lib.model.smartplugin.SmartPlugin
    :members: asyncio_state, start_asyncio, stop_asyncio, run_asyncio_coro, wait_for_asyncio_termination,
              put_command_to_run_queue, get_command_from_run_queue,
              list_asyncio_tasks
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

