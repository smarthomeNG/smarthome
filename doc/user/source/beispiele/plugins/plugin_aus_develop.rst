
.. index:: Tipps & Tricks; Plugins: Ein Plugin aus develop installieren

Ein Plugin aus develop installieren
===================================

Falls in Probleme mit einem Plugin auftreten, kann es hilfreich sein eine neuere Version des Plugins aus dem develop
Branch auf GitHub zu installieren, ohne deshalb die eigene Installation vollständig auf die (nicht notwendigerweise
stabile) develop Version von SmartHomeNG zu wechseln.

Im folgenden wird ein mögliches Vorgehen beschrieben, um ein Plugin aus dem develop Branch in eine Release Installation
zu installieren. Dazu sind folgende Schritte durchzuführen:

Plugins Repository aufrufen
---------------------------

Im Browser die Seite http://www.github.com/smarthomeng/plugins aufrufen:

.. image:: ../assets/plugin_install_1.jpg
   :class: screenshot

|

und in den develop Branch wechseln:

.. image:: ../assets/plugin_install_2.jpg
   :class: screenshot

|

Plugins Repository Download
---------------------------

Anschließend auf den grünen **Code** Button klicken und **Download ZIP** auswählen:

.. image:: ../assets/plugin_install_3.jpg
   :class: screenshot

|

Falls der Browser das ZIP Archiv nicht bereits entpackt hat, das Archiv ``plugins-develop.zip`` entpacken.

|

Gewünschtes Plugin installieren
-------------------------------

Um zub Beispiel ein Plugin mit dem Namen **xyz** durch die Version aus dem develop Branch zu ersetzen, sollte
zuerst das Verzeichnis der bestehenen Version im ``plugins`` Verzeichnis von **xyz** in **xyz.mstr** umbenannt werden,
damit man später bei Bedarf darauf zurück wechseln kann.

Anschließend kann das Verzeichnis **xyz** (mit allen Bestandteilen/Unterordnern) aus dem beim Entpacken entstandenen
Verzeichnis ``plugins-develop`` in das ``plugins`` Verzeichnis der SmartHomeNG Installation kopiert werden.

Um das neue Plugin zu aktivieren, muss SmartHomeNG nun neu gestartet werden. Falls die neue Version
Konfigurationsänderungen benötigen sollte, sind diese vor dem Neustart durchzuführen.

Nun kann das Verzeichnis ``plugins-develop`` gelöscht werden.

