
===================
Widgets für Plugins
===================

Entwickler von SmartHomeNG Plugins können Widgets für die smartVISU in ihr Plugin integrieren. Diese Widgets werden
dann beim Start von SmartHomeNG in der smartVISU installiert. Dieses erfolgt durch das Plugin **smartvisu**.


Ein Widget zu einem Plugin hinzufügen
=====================================

Um Widgets zu einem Plugin hinzuzufügen, muss das Plugin Verzeichnis ein Unterverzeichnis mit dem Namen ``sv_widgets``
haben, in welchem die Plugins abgelegt werden. Alle Dateien aus diesem Verzeichnis werden beim Start von SmartHomeNG
in die smartVISU Installation kopiert. Falls

Ab smartVISU v2.9 gibt es in der smartVISU hierzu ein Verzeichnis ``dropins``, wo die Dateien des Widgets abgelegt
werden. Die eigentlichen Widgets werden in ``dropins/widgets`` kopiert. Falls ein Widget Icons mitbringt
(*.png oder *.svg), werden diese in ``ropins/icons/ws`` kopiert.

.. note::

    In älteren Versionen der smartVISU gab es das noch nicht und die Widget Dateien mussten an anderen Stellen
    hinterlegt werden. Außerdem musste die Datei root.html modifiziert werden.

Widgets bestehen aus bis zu 3 Dateien die den gleichen Namen tragen und sich nur in der Extension unterscheiden:

    - eine html Datei (muss vorhanden sein)
    - eine javascript Datei (optional)
    - ein css Datei (optional)

Der Dateiname muss mit ```widget_``` beginnen.

Die Dateien können die Definition mehrerer Widgets enthalten, wie am folgenden Beispiel des rtr2 Plugins beschrieben
wird.

Das Plugin rtr2 enthält im Unterverzeichnis ``sv_widgets`` die Datei ``widget_rtr2.html``.
In der html Datei sind zwei Widgets definiert (die Makros ```rtr`` und ``plot``).

Aufgerufen werden die Widgets in der smartVISU (oder im sv_widget Attribut von Items) als ``{{ rtr2.rtr(...) }}`` bzw.
``{{ rtr2.plot(...) }}``. Die Klasse ```rtr2`` ist vom Namen der Widget Dateien abgeleitet. Würde die html Datei den
Namen ``widget_dummy.html`` tragen, müsste der Aufruf durch ``{{ dummy.rtr(...) }}`` bzw. ``{{ dummy.plot(...) }}``
erfolgen.

.. note::

    Es wird empfohlen für die Widget Klasse den Namen des Plugins zu verwenden, da dieses später im Gebrauch eine
    leichtere Zuordnung ermöglicht und Namens-Dubletten ausschließt.


Für eine tiefergehende Dokumentation zur Erstellung von Widgets sei hier auf die Dokumentation der smartVISU, sowie
auf die Dokumentation der in der smartVISU verwendeten Template Engine **Twig** verwiesen.


Notwendige Modifikationen der smartVISU vor v2.9
================================================

Um die Widgets in smartVISU Versionen vor v2.9 zu installieren, mussten einige Modifikationen an der smartVISU
Installation vorgenommen werden. Dieses erfolgt durch das **smartvisu** Plugin (bzw. das ältere **visu_smartvisu**
Plugin) bei der Installation der Widgets. Diese Änderungen wurden so minimal invasiv wie möglich vorgenommen und
sind glücklicherweise seit smartVISU v2.9 nicht mehr notwendig.

Durchgeführte Modifikationen
----------------------------

Das Plugin legt ein Verzeichnis mit dem Namen ``sh_widgets`` im Verzeichis ``widgets`` der smartVISU an, in welche
die Plugin Dateien kopiert werden.

Beim ersten Start des Plugins wird die Datei ``root.html`` im Verzeichnis ``pages/base`` auf den Namen ``root_master.html``
kopiert.

Bei jedem Start wird eine neue Datei ``root.html`` erstellt, welche eine Kopie der Datei ``root_master.html`` ist,
welche entsprechend der installierten Widgets modifiziert/ergänzt wird.

