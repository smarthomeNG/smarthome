.. index:: Logiken; Logiken

#######
Logiken
#######

Logiken für SmartHomeNG sind Python Skripte. Zur Erstellung von Logiken müssen Sie über
Kenntnisse der Programmiersprache Python verfügen.

Die Logik-Skripte müssen im Verzeichnis **../logics** der SmartHomeNG Installation abgelegt werden.

Grundlegende Struktur
=====================

Das wichtigste Objekt, dass in Logiken verwendet wird, ist **sh**. Dies ist das Smarthome-Objekt.
Es enthält jedes Detail über die laufende SmartHomeNG Instanz. Mit diesem Objekt ist es möglich auf
alle Items, Plugins und Grundfunktionen von SmartHomeNG zuzugreifen. Um den Wert eines Items zu
erhalten, rufen Sie zum Beispiel den Namen auf: sh.path.item(). Um einen neuen Wert zu setzen,
geben Sie ihn einfach als Argument an: sh.path.item(neuer_wert).

Es ist sehr wichtig, immer mit Klammern **()** auf die Items zuzugreifen! Andernfalls würde ein
Fehler auftreten.


Eine Logik sieht prinzipiell folgendermaßen aus:

.. code-block:: python
   :caption: /usr/local/smarthome/logics/testlogik1.py

   #!/usr/bin/env python3
   # testlogik1.py

   #Code der Logik:

   # Das Deckenlicht im Büro einschalten, falls es nicht eingeschaltet ist
   if not sh.buero.deckenlicht():
       sh.buero.deckenlicht('on')


.. toctree::
   :maxdepth: 4
   :hidden:

   objekteundmethoden
   persistente_variablen
   beispiellogiken

