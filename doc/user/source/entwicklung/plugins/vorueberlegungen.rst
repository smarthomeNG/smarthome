
Vorüberlegungen
===============

Fragestellungen
---------------

Bevor die Erstellung eines Plugins beginnt, muss man sich einige Fragen stellen und beantworten:

- Welchen Typ soll das Plugin haben, welches erstellt werden soll?
- Soll das externe System direkt angesteuert werden oder soll auf existierende Python Packages zurück gegriffen werden?

Typ des Plugins
---------------

...

Nutzung von Python Packages
---------------------------

Die Frage, ob fertige 3rd Party Packages eingesetzt werden sollen, ist gut abzuwägen. Als Vorteil ist anzuführen,
dass man sich evtl. erhebliche Programmierung spart. Allerdings kommt es immer wieder vor, dass Python Packages im
Zuge ihrer Weiterentwicklung Breaking Changes einführen und bei Einsatz dieser neuen Package Version (z.B. bei
einer Neuinstallation von SmartHomeNG), das Plugin plötzlich und unerwartet nicht mehr funktioniert.

Die Angabe einer bestimmten Version eines eingesetzten Packages ist jedoch auch keine Lösung, da Requirements aus
anderen Plugins oder auch Requirements in anderen eingesetzten Packages evtl. dazu führen, dass es keine geeignete
Package Version mehr gibt, die installiert werden könnte.


Python Version
--------------

Je nachdem unter welcher Python Version SmartHomeNG läuft, stehen Python Features zur Verfügung, oder eben auch nicht.
Es sollten nach Möglichkeit nur Python Features genutzt werden, die bereits in der ältesten unterstützten Python
Version (siehe ...) zur Verfügung stehen. Dadurch ist das Plugin am felxibelsten einsetzbar.

Sollte auf ein Python Features zurück gegriffen werden (müssen), welches erst in neueren Python Versionen zur
Verfügung steht, ist es wichtig, die minimale Python Version unter der das Plugin lauffähig ist, in den Metadaten
in der Datei plugin.yaml des Plugins anzugeben.

Sollte auf ein Python Features zurück gegriffen werden (müssen), welches in neueren Python nicht mehr zur Verfügung
steht, ist es wichtig, die maximale Python Version unter der das Plugin lauffähig ist, in den Metadaten
in der Datei plugin.yaml des Plugins anzugeben.

