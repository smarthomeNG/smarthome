.. index:: New; Webinterface

.. role:: redsup
.. role:: bluesup


==============================
Webinterface :bluesup:`update`
==============================

:Note: Diese Dokumentation bezieht sich auf Versionen nach v1.4.2. Sie gilt nicht für Versionen bis inklusive v1.4.2

Webinterfaces werden durch das http-Modul implementiert. Dieses muss konfiguriert und gestartet sein, um Webinterfaces nutzen zu können.

Das Webinterface eines Plugins erlaubt es, Plugin-Daten und -Konfiguration im Browser anzuzeigen. Der Link zum Webinterface wird im Admin UI in der Liste der aktiven Plugins angezeigt.

SmartHomeNG ermöglicht die Implementation eines Webinterfaces auf sehr einfache Weise. Das Beispielplugin hat eine vollständige Implementation eines Webinterfaces. Es muss nur die Anzeige der Plugindatem im Template ergänzt werden. Die Templateengine (Jinja2) erhält die Daten von Python, wenn die Webinterface-Seite zur Laufzeit gerendert wird.

Das Standardtemplate für Webinterfaces hat einen Kopfteil mit den folgenden Informationen:

  - einem Bild,
  - Name, Version und Status des Plugins,
  - einen Bereich rechts am oberen Rand der Webseite, der für die Anzeige von globalen Informationen oder Parametern des Plugins zur Verfügung steht,
  - einen Bereich für Buttons unterhalb der globalen Informationen.

Auf den Kopfteil folgt der Rest der Seite mit bis zu 4 Tabs, abhängig von den anzuzeigenden Informationen.


Ein leeres Webinterface sieht wie folgt aus:

.. image:: assets/sample_plugin_webIf.jpg

popper.js kann genutzt werden, um (aktuell pro Seite maximal zehn) "stabile"
und ansprechende Tooltips zu integrieren. Alle nötigen
Dateien sind hierbei schon automatisch integriert. Um Buttons mit Tooltips auszustatten,
muss ihnen die CSS Klasse ``button-tooltip`` zugewiesen werden. Außerdem sind
folgende Codezeilen in der index.html Datei notwendig:

.. code-block:: HTML

  {% block pluginscripts %}
    <script>
      $(document).ready(function(){
        const tooltipList = ['Tooltip 1', 'Tooltip 2', 'Tooltip 3'];
        createTooltips(tooltipList);
      }
    </script>
  {% endblock pluginscripts %}
  {% block content -%}
    <button onclick="" type="button" class="button-tooltip">Button</button>
  {%- endblock content %}


Detaillierte Informationen zur Erstellung von Webinterfaces finden sich auf den folgenden Seiten:

.. toctree::
   :maxdepth: 1
   :titlesonly:

   webinterface_extend_plugin
   webinterface_filling_webinterface
   webinterface_multilanguage
   webinterface_automatic_update
   webinterface_plugin_interaction
   webinterface_3rdparty_components
