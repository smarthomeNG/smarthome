
:tocdepth: 5

.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup


.. index:: Logiken; Plgin Funktionen

=============================
Nutzung von Plugin Funktionen
=============================

Eine Reihe von Plugins stellt öffentliche Funktionen zur Verfügung, die in Logiken genutzt werden können.
Diese Funktionen sind in der Konfigurationsdokumentation des jeweiligen Plugins beschrieben.

Im folgenden wird die Nutzung am Beispiel der Funktion ``groupwrite()`` des **knx** Plugins erläutert.

Dokumentation der Plugin Funktion(en)
=====================================

Um die Dokumentation der Funktionen eins Plugins zu finden, bzw. herauszufinden, ob ein Plugin öffentliche
Funktionen anbietet, klickt man in der Navigation der Anwender Dokumentation auf **Plugins** und anschließend auf
den Unterpunkt für den Plugin Typ (für das **knx** Plugin auf **Gateway Plugins**). In der angezeigten Tabelle
von Plugins klickt man anschließend in der Spalte **Plugin** auf den Namen (also **knx**). Dadurch wird die
Konfigurations-Dokuemntation (Parameter, Item Attribute, etc.) des Plugins angezeigt.

Auf der Seite den Abschnitt **Plugins Functions** suchen. Für das **knx** Plugin sind hier mehrere Funktionen
aufgeführt, unter anderem auch die Funktion ``groupwrite(ga, data, dpt)`` mit der Beschreibung ihrer Parameter.


Aufruf der Plugin Funktion(en)
==============================

Funktionen von Plugins greifen intern auf Daten der laufenden Plugin Instanz zu. Es kann also in SmartHomeNG
mehrere Funktionen gleichen Namens geben, wenn man mehrere Instanzen eines Plugins konfiguriert hat. Deshalb kann
man nicht über den Namen des Plugins auf die Funktion zugreifen, sondern über den Konfiguration-Namen der jeweiligen
Instanz, also den Namen der Abschnitts in der Konfigurationsdatei ``etc/plugin.yaml``.

Der Aufruf der Funktion ``groupwrite(ga, data, dpt)`` hätte folgenden Sytax:

.. code-block:: python

    sh.<plugin_konfiguration>.groupwrite(ga, data, dpt)

Wenn das knx Plugin in der Datei ``etc/plugin.yaml`` folgendermaßen konfiguriert ist:

.. code-block:: yaml

    local_knxd:
        plugin_name: knx
        use_project_file: true

und auf die Gruppenadresse **1/2/1** der 8-Bit Wert (DPT **5**) **123** geschrieben werden soll, lautet der Aufruf
der Pluginfunktion so:

.. code-block:: python

    sh.local_knxd.groupwrite('1/2/1', 123, 5)


