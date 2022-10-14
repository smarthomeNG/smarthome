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
            try:
                pagelength = self.plugin.webif_pagelength
            except Exception:
                pagelength = 100
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


   2. Die Variable ``webif_pagelength`` sollte genutzt werden, um die Anzahl an Einträgen
      pro Seite im Web Interface über die plugin.yaml konfigurierbar zu machen.
      Hierzu ist es notwendig, das ``__init__.py`` File des Plugins (nicht im webif Ordner!) und ``plugin.yaml`` wie folgt anzupassen.

      .. code-block:: python

        self.webif_pagelength = self.get_parameter_value('webif_pagelength')

      Die plugin.yaml sollte hiermit ergänzt werden:

      .. code-block:: yaml

        webif_pagelength:
          type: int
          default: 100
          description:
            de: 'Anzahl an Items, die standardmäßig in einer Web Interface Tabelle pro Seite angezeigt werden.
                 0 = automatisch, -1 = alle'
            en: 'Amount of items being listed in a web interface table per page by default.
                 0 = automatic, -1 = all'
          description_long:
            de: 'Anzahl an Items, die standardmäßig in einer Web Interface Tabelle pro Seite angezeigt werden.\n
                 Bei 0 wird die Tabelle automatisch an die Höhe des Browserfensters angepasst.\n
                 Bei -1 werden alle Tabelleneinträge auf einer Seite angezeigt.'
            en: 'Amount of items being listed in a web interface table per page by default.\n
                 0 adjusts the table height automatically based on the height of the browser windows.\n
                 -1 shows all table entries on one page.'
          valid_list:
            - -1
            - 0
            - 25
            - 50
            - 100


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
      Die ID ``resize_wrapper`` ist zwingend dem ``<div>`` Tag, in dem sich die Tabelle befindet, hinzuzufügen,
      um die automatische Anpassung der Datentabelle an die Fensterhöhe zu ermöglichen
      (siehe auch index.html im Example-Plugin).

      .. code-block:: html+jinja

        <div class="container-fluid m-2" id="resize_wrapper">
           <table id="maintable" class="table table-striped table-hover pluginList display">
               <thead>
                   <tr>
                       <th class="item">{{ _('Item') }}</th>
                       <th class="typ">{{ _('Typ') }}</th>
                       <th class="knx_dpt">{{ _('knx_dpt') }}</th>
                   </tr>
               </thead>
               <tbody>
                   {% for item in items %}
                       <tr>
                           <td class="py-1" id="{{ item._path }}_path">{{ item._path }}</td>
                           <td class="py-1" id="{{ item._path }}_type">{{ item._type }}</td>
                           <td class="py-1" id="{{ item._path }}_knx_dpt">{{ item.conf['knx_dpt'] }}</td>
                       </tr>
                   {% endfor %}
               </tbody>
           </table>
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
            try {
              /* get pagelength from plugin. Also see hidden span element in bodytab1 block! */
              webif_pagelength = parseInt(document.getElementById('webif_pagelength').innerHTML);
              if (webif_pagelength == 0) {
                resize = true;
                webif_pagelength = -1;
              }
              else {
                resize = false;
              }
            }
            catch (e) {
              webif_pagelength = 100;
              resize = false;
              console.log("Using default values for page length " + webif_pagelength + ", pageResize: " + resize);
            }
            try {
              table = $('#maintable').DataTable( {pageLength: webif_pagelength, pageResize: resize} ); // put more options into {} if needed
              <table_xx> = $('#<table_id>').DataTable( {} ); // delete or change name of table and id
            }
            catch (e) {
              console.log("Datatable JS not loaded, showing standard table without reorder option " + e);
            }
          });
        </script>


    .. code-block:: html+jinja

      <!-- This code has to be implemented in the index.html file either in the headtable or bodytab -->
      {% block headtable %}
      <span id='webif_pagelength' style="display:none">{{ webif_pagelength }}</span>


   6. Das Logo oben links auf der Seite wird automatisch durch das Logo des konfigurierten Plugin-Typs ersetzt. Wenn das Webinterface ein eigenes Logo mitbringen soll, muss das entsprechende Bild im Verzeichnis ``webif/static/img`` mit dem Namen ``plugin_logo`` abgelegt sein. Die zulässigen Dateiformate sind **.png**, **.jpg** oder **.svg**. Dabei sollte die Größe der Bilddatei die Größe des angezeigten Logos (derzeit ca. 180x150 Pixel) nicht überschreiten, um unnötige Datenübertragungen zu vermeiden.
