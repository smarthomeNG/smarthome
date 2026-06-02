
.. index:: Standard-Attribute; struct
.. index:: struct; Item-Struktur Template

.. index:: Items; Item-Struktur Template
.. index:: Items; struct
.. index:: Items; Template
.. index:: Item-Struktur Template

.. role:: bluesup
.. role:: redsup

struct
------

Über das Attribut **struct** werden vordefinierte Item-Strukturen in den Item-Tree eingefügt. Dazu muss bei dem Item,
an dessen Stelle der Teilbaum eingefügt werden soll, der Name des Templates (der Item-Struktur) angegeben werden.

**Vollständige Struktur einbinden:**

.. code-block:: yaml

    myitem:
        struct: kodi.master          # fügt die gesamte Struktur 'kodi.master' ein

**Nur einen Teilbaum einbinden** :redsup:`new`:

Es kann auch nur ein Teil einer Struktur eingebunden werden, indem der Pfad zum gewünschten Teilbaum angegeben wird:

.. code-block:: yaml

    myitem:
        struct: kodi.master.bar      # fügt nur den 'bar'-Teilbaum von 'kodi.master' ein
        struct: kodi.master.bar.child1  # fügt einen noch tieferen Teilbaum ein

Weitere Informationen zu **structs** sind auf der Seite :doc:`Konfiguration/structs </konfiguration/item_structs>` und :doc:`Konfiguration/Konfigurationsdateien/struct.yaml </konfiguration/konfigurationsdateien/struct>`)
zu finden.

