.. index:: Web Interface

.. role:: redsup
.. role:: bluesup


Das Webinterface mit Inhalt füllen
----------------------------------

Die folgenden Schritte dienen dazu, das Webinterface mit Leben zu füllen:

   1. Die Methode ``index`` der Klasse ``WebInterface`` wird zur Übergabe der gewünschten Daten an das Template modifiziert (im folgenden Beispiel ist das eine Liste von Items, die das Attribut ``knx_dpt`` besitzen).

      Der Beispielcode wird wie folgt verändert von:

      .. code-block:: PYTHON

         @cherrypy.expose
         def index(self, reload=None):
             """
             Build index.html for cherrypy

             Render the template and return the html file to be delivered to the browser

             :return: contents of the template after beeing rendered
             """
             # add values to be passed to the Jinja2 template eg: tmpl.render(p=self.plugin, interface=interface, ...)
             tmpl = self.tplenv.get_template('index.html')
             return tmpl.render(p=self.plugin)

      zu:

      .. code-block:: python

        @cherrypy.expose
        def index(self, reload=None):
            """
            Build index.html for cherrypy

            Render the template and return the html file to be delivered to the browser

            :return: contents of the template after beeing rendered
            """
            pagelength = self.plugin.get_parameter_value('webif_pagelength')
            tmpl = self.tplenv.get_template('index.html')
            # add values to be passed to the Jinja2 template eg: tmpl.render(p=self.plugin, interface=interface, ...)
            return tmpl.render(webif_pagelength=pagelength, p=self.plugin)

            # get list of items with the attribute knx_dpt
            plgitems = []
            for item in self.items.return_items():
                if 'knx_dpt' in item.conf:
                    plgitems.append(item)

            # additionally hand over the list of items, sorted by item-path
            tmpl = self.tplenv.get_template('index.html')
            return tmpl.render(p=self.plugin,
                               webif_pagelength=pagelength,
                               items=sorted(plgitems, key=lambda k: str.lower(k['_path'])),
                              )


   2. Die Variable ``webif_pagelength`` wird genutzt, um die Anzahl an Einträgen
      pro Seite im Web Interface über die plugin.yaml konfigurierbar zu machen.
      Diese Variable kann vom User global im http-Modul gesetzt, aber auch individuell pro Plugin
      überschrieben werden. Bei der Entwicklung eines Plugins ist dabei nichts Weiteres zu
      beachten, da der Parameter automatisch jedem Plugin hinzugefügt wird.


   3. Im Template ``webif/templates/index.html`` werden Anzahl und Titel der Tabs sowie der Starttab konfiguriert.

      * ``{% set tabcount = 4 %}`` definiert die Anzahl an Tabs. Erfolgt keine Angabe, werden automatisch 4 Tabs angezeigt.
      * ``{% set start_tab = 2 %}`` definiert, dass Tab 2 zu Beginn aktiv ist.
      * ``{% set tab1title = "<strong>" ~ p.get_shortname() ~ " Items</strong> (" ~ item_count ~ ")" %}`` sorgt dafür, dass der erste Tab die Überschrift "<Pluginname> Items (<Anzahl>)" erhält. Setzt man den Titel auf "hidden", wird der Tab nicht angezeigt. Dies ist beispielsweise dann sinnvoll, wenn gar keine Inhalte für den Tab vorhanden sind, weil das Plugin vom User entsprechend konfiguriert wurde.

      .. code-block:: HTML

        {% if item_count > 0 %}
            {% set tab1title = "<strong>" ~ p.get_shortname() ~ " Items</strong> (" ~ item_count ~ ")" %}
        {% else %}
            {% set tab1title = "hidden" %}
        {% endif %}


   4. Das Template ``webif/templates/index.html`` wird zur Anzeige der gewünschten Daten angepasst.
      Um im ersten Tab des Webinterface die Items anzuzeigen, die der obige Beispielcode zusammengestellt hat, wird der folgende Code zwischen ``{% block bodytab1 %}`` und ``{% endblock bodytab1 %}`` eingefügt. Es ist sicherzustellen, dass korrekter HTML Code
      für die Tabellen genutzt wird, ua. durch Nutzen der Tags ``<thead>`` und ``<tbody>``
      sowie der jeweiligen End-Tags. Außerdem muss jeder Tabelle eine einzigartige ID vergeben werden.
      Sowohl im Tablehead als auch Tablebody ist eine leere erste Spalte einzufügen, die für das responsive
      Feature der Datatables genutzt wird.
      Die Klasse``table-resize`` ist zwingend dem ``<div>`` Tag, in dem sich die Tabelle befindet, hinzuzufügen,
      um die automatische Anpassung der Datentabelle an die Fensterhöhe zu ermöglichen
      (siehe auch index.html im Example-Plugin). Sollen ober- oder unterhalb der Tabelle zusätzliche Informationen
      angezeigt werden, müssen diese in einem ``<div class="mb-2">`` Tag stehen.

      .. code-block:: html+jinja

        <div class="container-fluid m-2 table-resize">
           <div class="mb-2">
               Informationen oberhalb der Tabelle
           </div>
           <table id="maintable">
               <thead>
                   <tr>
                       <th></th>
                       <th class="item">{{ _('Item') }}</th>
                       <th class="typ">{{ _('Typ') }}</th>
                       <th class="knx_dpt">{{ _('knx_dpt') }}</th>
                   </tr>
               </thead>
               <tbody>
                   {% for item in items %}
                       <tr>
                           <td></td>
                           <td class="py-1" id="{{ item._path }}_path">{{ item._path }}</td>
                           <td class="py-1" id="{{ item._path }}_type">{{ item._type }}</td>
                           <td class="py-1" id="{{ item._path }}_knx_dpt">{{ item.conf['knx_dpt'] }}</td>
                       </tr>
                   {% endfor %}
               </tbody>
           </table>
           <div class="mb-2">
               Informationen unterhalb der Tabelle
           </div>
        </div>



   5. Folgender Scriptcode muss zwischen ``{% block pluginscripts %}`` und
      ``{% endblock pluginscripts %}`` eingefügt werden, um ein Filtern und Sortieren
      der Tabellen zu ermöglichen.
      Der Code ``$('#maintable').DataTable( {} );``
      muss für jede Tabelle, für die Filtern/Sortieren ermöglicht werden soll, kopiert werden.
      Dabei ist sicher zu stellen, dass die ID (#maintable) jeweils richtig angepasst wird.
      Die aktuellste Variante des nötigen Codeteils ist dem Sample-Plugin zu entnehmen, dort sind noch
      weitere relevante Anpassungen zu finden.

      .. code-block:: html+jinja

        <script>
          $(document).ready( function () {
            $(window).trigger('datatables_defaults'); // loading default behaviour
            {% if webif_pagelength is defined %}webif_pagelength = {{ webif_pagelength|int }};{% endif %}
            if (isNaN(parseFloat(webif_pagelength)) || webif_pagelength == 0) {
              resize = true;
              webif_pagelength = -1;
            }
            else {
              resize = false;
            }
            console.log("Using page length from http module/plugin " + webif_pagelength + ", pageResize: " + resize);
            try {
              maintable = $('#maintable').DataTable( {pageLength: webif_pagelength, pageResize: resize} ); // put more options into {} if needed
              <table_xx> = $('#<table_id>').DataTable( {} ); // delete or change name of table and id
            }
            catch (e) {
              console.log("Datatable JS not loaded, showing standard table without reorder option " + e);
            }
          });
        </script>


   6. Das Logo oben links auf der Seite wird automatisch durch das Logo des konfigurierten Plugin-Typs ersetzt. Wenn das Webinterface ein eigenes Logo mitbringen soll, muss das entsprechende Bild im Verzeichnis ``webif/static/img`` mit dem Namen ``plugin_logo`` abgelegt sein. Die zulässigen Dateiformate sind **.png**, **.jpg** oder **.svg**. Dabei sollte die Größe der Bilddatei die Größe des angezeigten Logos (derzeit ca. 180x150 Pixel) nicht überschreiten, um unnötige Datenübertragungen zu vermeiden.
