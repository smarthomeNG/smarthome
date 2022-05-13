
.. index:: smartVISU; Nutzdaten Protokoll - Server (SmartHomeNG) Requests
.. index:: websocket; smartVISU Nutzdaten Protokoll - Server (SmartHomeNG) Requests

Requests von SmartHomeNG an die smartVISU
-----------------------------------------

dialog
~~~~~~

``dialog`` ist ein Befehl, der vom Plugin an die smartVISU Clients gesendet wird.
Mit dem ``dialog`` Befehl wird die smartVISU angewiesen einen Dialog anzuzeigen.

Der folgende Befehl weist smartVISU an, den einen Dialog mit der Überschrift **This is the dialog header** und
dem Text **This is the dialog message** anzuzeigen:

.. code-block:: JSON

  {"cmd": "dialog", "header": "This is the dialog header", "content": "This is the dialog message"}

Die smartVISU gibt auf den Befehl ``dialog`` keine Antwort zurück.


url
~~~

--> Dieser Befehl funktioniert mit **smartVISU 2.9** und neuer.

``url`` ist ein Befehl, der vom Plugin an die smartVISU Clients gesendet wird.
Mit dem ``url`` Befehl wird die smartVISU angewiesen zu einer anderen Seite zu wechseln.

Der folgende Befehl weist smartVISU an, auf die Hauptseite zu wechseln:

.. code-block:: JSON

  {"cmd":"url", "url": "index.php"}

Die smartVISU gibt auf den Befehl ``url`` keine Antwort zurück.

