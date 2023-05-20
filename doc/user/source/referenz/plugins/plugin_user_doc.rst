
.. index:: Referenz; Dokumentation für Plugins
.. index:: Referenz; user_doc
.. Index:: user_doc; Plugins Referenz

.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup


=========================
Dokumentation für Plugins
=========================

Die Dokumentation für Plugins wird in der Datei user_doc.rst abgelegt.

Die Konfigurationsparameter selbst müssen in der user_doc.rst nicht beschrieben werden. Die Dokumentation der
Konfigurationsparameter und der Item Attribute wird automatisch aus den Metadaten (aus der plugin.yaml) generiert.


Die user_doc.rst sollte folgendes Format haben:

.. include:: plugin_user_doc_template.rst

Die Dokumentation beginnt mit dem Titel, der dem Namen des Plugins entspricht. (in Lower Case - Plugin Namen sind
Case sensitive!)

.. important::

   Die erste Überschrift der Dokumentationsdatei ``user_doc`` MUSS dem Kurznamen des Plugins in Kleinbuchstaben entsprechen.

   Dieser Eintrag wird als Einstiegspunkt für die Navigation in der Dokumentation genutzt.
   Ein anderer Eintrag als Überschrift sorgt für Inkonsistenzen in den Navigationselementen.

|

Aus dem Sample Plugin:

.. literalinclude:: /dev/sample_plugin/user_doc.rst
    :caption: user_doc.rst
