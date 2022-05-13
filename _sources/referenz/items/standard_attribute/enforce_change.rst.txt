
.. index:: Items; enforce_change
.. index:: Standard-Attribute; enforce_change
.. index:: enforce_change


.. role:: redsup
.. role:: bluesup

enforce_change
==============

Das Attribut *enforce_change* ist die verschärfte Form des *enforce_updates* Attributes.

Während *enforce_updates* dafür sorgt, dass auch bei einem Update (ohne Wert Change) abhängige Trigger dafür sorgen,
dass Logiken oder die Berechnung anderer Items ausgeführt wird, sorgt *enforce_change* dafür, dass der Wert des Items
selbst als verändert geschrieben wird, auch wenn der Wert gleich geblieben ist. Es werden dabei die Werte der
Attribute *changed_by*, *last_change*, ... gesetzt.

Dieses Verhalten ist zum Beispiel hilfreich, wenn man erzwingen möchte, dass ein Wert in die Datenbank geschrieben
wird, auch wenn er sich nicht vom Vorgänger Wert unterscheidet. Normalerweise würde kein Wert geschrieben, sondern nur
die Dauer die der Wert bestand erhöht.

