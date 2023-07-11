Plugin-Dokumentation
====================

Es gibt eine Dokumentations-Datei die für ein Plugin erstellt werden kann (und soll).

.. hint::

    Das in früheren Versionen verwendete ``README.md``-Format für die Dokumentation von Plugins ist veraltet.
    Ein Großteil der Dokumentation ist in die Metadaten-Dokumentation in ``plugin.yaml`` übergegangen. Die
    restliche Dokumentation sollte nur noch im ``user_doc.rst``-Format erfolgen.

    Soweit möglich, sollten bestehende ``README.md`` im Rahmen von Aktualisierungen in entsprechende ``user_doc.rst``
    überführt werden.


user_doc.rst
------------

Die ``user_doc.rst``-Datei soll im Dateiformat restructured text (rST) erstellt werden. Die Dokumentation sollte
durchgängig auf Deutsch erfolgen; nur wenn der Plugin-Autor kein Deutsch spricht, kann die Dokumentation auf
Englisch erfolgen. Der Grund dafür ist, dass die englischsprachige Dokuemntation mit Hilfe von Google-Translate
erstellt wird.

Die Datei ``user_doc.rst`` wird im Rahmen des Build-Prozesses dynamisch in die Nutzerdokumentation von SmartHomeNG
integriert, u.a. auch auf der Homepage.

.. important::

   Die erste Überschrift der Dokumentationsdatei (``user_doc.rst``) **muss** dem Kurznamen des Plugins in
   Kleinbuchstaben entsprechen.

   Dieser Eintrag wird als Einstiegspunkt für die Navigation in der Dokumentation genutzt.
   Ein anderer Eintrag als Überschrift sorgt für Inkonsistenzen in den Navigationselementen.


Zum Beispiel:

Das ``backend`` Plugin beinhaltet eine Datei ``user_doc.rst``.
Diese Datei ist in den Navigationsbaum der Dokumentation integriert.
Dieser Eintrag wird angezeigt, wenn die entsprechende Plugin-Kategorie ausgewählt wird:

.. image:: assets/backend_user_doc_tree.png


Wenn der Eintrag im Navigationspanel ausgewählt wird, wird die Seite aufgerufen:

.. image:: assets/backend_user_doc_page.png


Die Dokumentation kann Bilder enthalten. Diese müssten in eim Unterordner ``assets`` des Plugin-Ordners abgelegt werden.

In restructured text (rST) Dateien können Bilder mit der folgenden Anweisung eingebunden werden:

  .. code::

    .. image:: assets/<picture-filename>


