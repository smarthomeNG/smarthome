.. index:: Web Interface

.. role:: redsup
.. role:: bluesup

Erweitern eines bestehenden Plugins
-----------------------------------

Für bestehende SmartPlugins kann die Erweiterung um ein Webinterface wie folgt durchgeführt werden:

   1. das ``webif``-Verzeichnis aus dem Beispiel in das eigene Plugin kopieren
   2. die import-Anweisungen für ``lib.smartplugin`` von
      ``from lib.model.smartplugin import SmartPlugin`` ändern zu
      ``from lib.model.smartplugin import *``
   3. der ``__init__``-Methode des Plugins den Aufruf von ``self.init_webinterface()`` hinzufügen (am Ende der Initialisierung)
   4. der Plugin-Klasse die Methode ``init_webinterface()`` aus dem Beispielplugin hinzufügen
   5. die ``WebInterface``-Klasse aus dem Beispiel-Plugin ans Ende der Plugin-Datei kopieren

Nun hat das Plugin ein funktionierendes, wenngleich leeres Webinterface:

.. image:: assets/sample_plugin_webIf.jpg


Die Methode ``index`` der Klasse ``WebInterface`` implementiert die Seitenerstellung des Webinterfaces. Es rendert das Template (``webif/templates/index.html``) und macht das Plugin für den Renderer als ``p`` verfügbar (``return tmpl.render(p=self.plugin)``). Darüber hinaus erforderliche Daten können dem Aufruf von ``tmpl.render()`` einfach angefügt werden und stehen dann im Template zur Verfügung.

Das Einzige, was jetzt noch verbleibt, ist die Einbindung der anzuzeigenden Daten im Template.

Details dazu finden sich im folgenden Abschnitt. (**Das Webinterface mit Inhalt füllen**)
