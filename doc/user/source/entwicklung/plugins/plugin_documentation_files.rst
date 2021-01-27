Dateien der Plugin-Dokumentation
================================

Es gibt zwei Dokumentations-Dateien die für ein Plugin erstellt werden können (und sollten).

.. hint::

   Das in früheren Versionen verwendete ``README``-Format für die Dokumentation von Plugins ist veraltet. Ein Großteil der Dokumentation ist in die Metadaten-Dokumentation in ``plugin.yaml`` übergegangen. Die restliche Dokumentation sollte nur noch im ``user_doc``-Format erfolgen. 

   Soweit möglich, sollten bestehende ``README`` im Rahmen von Aktualisierungen in entsprechende ``user_doc`` überführt werden.


user_doc.rst / user_doc.md
--------------------------

Die ``user_doc``-Datei kann in in den Dateiformaten restructured text (rST) oder markdown (md) erstellt werden. 
Das restructured text-Format sollte dabei bevorzugt werden, da es mehr Möglichkeiten bietet. 
Die Dokumentation sollte durchgängig auf Deutsch erfolgen; nur wenn der Plugin-Autor kein Deutsch spricht, 
kann die Dokumentation auf Englisch erfolgen.
Der Grund dafür ist die vorgesehene Umstellung auf Mehrsprachenunterstützung, welche **eine** einheitliche Quellsprache erfordert.

Diese Datei wird im Rahmen des Build-Prozesses dynamisch in die Nutzerdokumentation von SmartHomeNG integriert, u.a. auch auf der Homepage.

.. important::

   Die erste Überschrift der Dokumentationsdateien (``user_doc`` und ``developer_doc``) **muss** dem Kurznamen des Plugins in Kleinbuchstaben entsprechen.

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



developer_doc.rst / developer_doc.md
------------------------------------

Die ``developer_doc``-Datei kann in den Dateiformaten restructured text (rST) oder markdown (md) erstellt werden.
Das restructured text-Format sollte dabei bevorzugt werden, da es mehr Möglichkeiten bietet. Die Dokumentation sollte durchgängig auf Deutsch erfolgen.

Diese Datei wird im Rahmen des Build-Prozesses dynamisch in die Nutzerdokumentation von SmartHomeNG integriert, u.a. auch auf der Homepage.

Zum Beispiel:

Die Plugins ``visu_websocket`` und ``visu_smartvisu`` haben jeweils Seiten mit Dokumentation speziell für Entwickler:

.. image:: assets/visu_developer_doc_tree.jpg

