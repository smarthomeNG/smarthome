.. index:: New; Webinterface

.. role:: redsup
.. role:: bluesup


==============================
Webinterface :bluesup:`update`
==============================

:Note: Diese Dokumentation bezieht sich auf Versionen nach v1.4.2. Sie gilt nicht für Versionen bis inklusive v1.4.2

Allgemeines
===========

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


Tooltips
========

*popper.min.js* kann genutzt werden, um (aktuell pro Seite maximal zehn) "stabile"
und ansprechende Tooltips zu integrieren. Ab *SmarthomeNG 1.10* sind alle nötigen
Dateien hierbei schon automatisch integriert. Um Buttons mit Tooltips auszustatten,
muss ihnen die CSS Klasse ``button-tooltip`` zugewiesen werden. Außerdem sind
folgende Codezeilen in der index.html Datei notwendig:

.. code-block:: HTML

  {% block pluginscripts %}
    <script>
      $(document).ready(function(){
        const tooltipList = ['Tooltip 1', 'Tooltip 2', 'Tooltip 3'];
        createTooltips(tooltipList);
      });
    </script>
  {% endblock pluginscripts %}
  {% block content -%}
    <button onclick="" type="button" class="button-tooltip">Button</button>
  {%- endblock content %}


Cookies
=======

Um Einstellungen im Webinterface dauerhaft zu speichern, sollten die entsprechenden
Werte als Browser-Cookie gespeichert werden. Eine einfache Möglichkeit dazu wird
seit *SmarthomeNG 1.10* angeboten. Zum Speichern von Cookies steht die Funktion
``setCookie(<Cookiename>, <Cookiewert>, <Dauer der Speicherung>, <Pluginname>)`` bereit, für das Laden ``getCookie(<Cookiename>)``. Im Folgenden Beispiel wird beim Laden der Seite das Cookie
ausgelesen. Ist dieses (noch) nicht gesetzt, wird ein leerer Wert zurückgegeben,
der im Code entsprechend abgefangen werden muss. Beim Klick auf einen Button wird
beispielhaft ein Cookie namens "sort_order" mit dem Wert "alpha-asc" für ein Jahr (365 Tage) gespeichert.
Der Pluginname ist in der globalen Variable "window.pluginname" hinterlegt und sollte
genau so referenziert werden.

.. code-block:: HTML

  {% block pluginscripts %}
    <script>
      $(document).ready(function(){
        order = getCookie('sort_order');
        if (order == '')
          order = 'time-desc';
        const button = document.getElementById(order);
        button.click();
      });
    </script>
  {% endblock pluginscripts %}
  {% block content -%}
    <button onclick="setCookie('sort_order', 'time-desc', 365, window.pluginname);" type="button" class="button-tooltip" id="time-desc">Button</button>
  {%- endblock content %}


Icons
=====

Im Ordner ``/gstatic/img`` sind diverse globale Icons hinterlegt. Seit *SmarthomeNG 1.10*
stehen Icons für Sortierfunktionen zur Verfügung. Diese heißen wie folgt:

  - sort-alpha-asc.svg
  - sort-alpha-desc.svg
  - sort-num-asc.svg
  - sort-num-desc.svg
  - sort-time-asc.svg
  - sort-time-desc.svg
  - sort-asc.svg
  - sort-desc.svg

Diese können wie folgt per CSS entsprechend angepasst werden. Im Beispiel werden
aktivierte Icons/Buttons durch die Klasse "active" blau eingefärbt.

.. code-block:: HTML

  {% block pluginstyles %}
    <style>
      .sort {
        width: 20px;
        height: 20px;
        border: none;
        padding: 0;
        margin-left: 20px;
        margin-bottom: -5px;
      }
      .active {
        border: none;
        filter: invert(8%) sepia(100%) saturate(6481%) hue-rotate(246deg) brightness(102%) contrast(143%);
      }
    </style>
  {% endblock pluginstyles %}
  {% block pluginscripts %}
    <script>
      $(document).ready(function(){
        // Suchen des Elements mit der id "alpha-asc" und "alpha-desc"
        const alpha_asc = document.getElementById('alpha-asc');
        const alpha_desc = document.getElementById('alpha-desc');

        // Eventlistener, der auf Klick auf das Element reagiert.
        alpha_asc.addEventListener('click', function() {
          // Bei sämtlichen anderen Elementen muss die "active" Klasse entfernt werden.
          alpha_desc.classList.remove('active');
          // Beim geklickten Element wird die "active" Klasse hinzugefügt.
          this.classList.add('active');
        });
        alpha_desc.addEventListener('click', function() {
          // Bei sämtlichen anderen Elementen muss die "active" Klasse entfernt werden.
          alpha_asc.classList.remove('active');
          // Beim geklickten Element wird die "active" Klasse hinzugefügt.
          this.classList.add('active');
        });
      });
    </script>
  {% endblock pluginscripts %}
  {% block content -%}
    <!-- Hier werden die zwei Inputelement (Buttons) im content-Block definiert. -->
    <input type= "image" id="alpha-asc" class="sort button-tooltip" onclick="<Function>" src="/gstatic/img/sort-alpha-asc.svg" />
    <input type= "image" id="alpha-desc" class="sort button-tooltip" onclick="<Function>" src="/gstatic/img/sort-alpha-desc.svg" />
  {%- endblock content %}


Kalenderansicht
===============

*bootstrap-datepicker.min.js* kann genutzt werden, um über eine Kalenderansicht verschiedene
Kalendertage auszuwählen. Das Beispiel implementiert eine Kalenderansicht und zeigt beispielhaft,
wie mit Hilfe der entsprechenden Funktionen die Ansicht aktualisiert und ausgelesen werden kann.

.. code-block:: HTML

  {% block pluginscripts %}
    <script src="/gstatic/bootstrap-datepicker/js/bootstrap-datepicker.min.js"></script>
    <script src="/gstatic/bootstrap-datepicker/locales/bootstrap-datepicker.de.min.js"></script>
    <script src="/gstatic/bootstrap-datepicker/locales/bootstrap-datepicker.fr.min.js"></script>
    <script>
      // Datepicker anhand des Elements mit der ID "datepicker" initialisieren
    	$('#datepicker').datepicker({
    		language: "{{ language }}",
    		autoclose: true,
    		todayHighlight: true,
    		todayBtn: "linked",
    		endDate: "{% if language == 'en' %}{{ now.strftime('%m/%d/%Y') }}{% else %}{{ now.strftime('%d.%m.%Y') }}{% endif %}"
    	});
      // Sobald das Datum geändert wird, wird das eingestellte Datum eruiert.
    	$('#datepicker').datepicker().on('changeDate', function(e) {
    		date = $('#datepicker').datepicker('getDate');
        day = date.getDate();
        month = date.getMonth();
        year = date.getFullYear();
        // Hier folgen weitere Aktionen, die mit den Informationen was Sinnvolles machen (sollten)...
      });
      // Datepicker auf aktuellen Tag setzen. Weitere Interaktionen sind z.B. im database Plugin zu finden.
      $('#datepicker').datepicker('update', '{% if language == "en" %}{{ now.strftime('%m/%d/%Y') }}{% else %}{{ now.strftime('%d.%m.%Y') }}{% endif %}');
    </script>
  {% endblock pluginscripts %}
  {% block content -%}
    <div id="datepicker"></div>
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
