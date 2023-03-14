.. index:: Web Interface; Automatische Updates

.. role:: redsup
.. role:: bluesup



Automatische Updates der Daten im Webinterface :redsup:`new`
============================================================

Um die Daten im Webinterface zu aktualisieren, sendet die Webseite periodische AJAX-Anfragen
an das Plugin und verarbeitet die zurückgelieferten Informationen,
indem die neuen Daten in die DOM-Elemente der Webseite eingetragen werden.

Um automatische Updates zu implementieren, müssen die folgenden Elemente hinzugefügt werden:

  - In der Klasse ``WebInterface`` des Plugins muss die Methode ``get_data_html()`` implementiert bzw. erweitert werden, um die gewünschten Daten zu liefern.
  - Die DOM-Elemente (z.B. <td>-Elemente im ``headtable``-Block oder in den ``bodytab?``-Blöcken), welche die aktualisierten Daten erhalten sollen, müssen jeweils eine eindeutige ID erhalten.
  - Im HTML-Template muss die JavaScript-Funktion ``handleUpdatedData()`` implementiert bzw. erweitert werden.
  - Die Template-Variable ``update_interval`` muss auf das gewünschte Update-Intervall (in Millisekunden) gesetzt werden.


Erweitern der Python-Methode get_data_html()
--------------------------------------------

Die Klasse ``WebInterface`` im Plugin Code muss so erweitert werden, dass sie die für das Update erforderlichen Daten zusammenstellt und als Dictionary zurückgibt:

.. code-block:: PYTHON

    class WebInterface(SmartPluginWebIf):

        def __init__(self, webif_dir, plugin):

            ...

        @cherrypy.expose
        def index(self, scan=None, test=None, reload=None):

            ...

        @cherrypy.expose
        def get_data_html(self, dataSet=None):
            """
            Return data to update the webpage

            For the standard update mechanism of the web interface, the dataSet to return the data for is None

            :param dataSet: Dataset for which the data should be returned (standard: None)
            :return: dict with the data needed to update the web page.
            """
            if dataSet == 'overview':
                # get the new data from a variable _webdata
                data = self.plugin._webdata
                try:
                    data = json.dumps(data)
                    return data
                except Exception as e:
                    self.logger.error(f"get_data_html exception: {e}")
            if dataSet is None:
                # get the new data
                data = {}
                data['fromip'] = 'fromip': self.plugin.fromip)

                data['item'] = {}
                for i in self.plugin.items:
                    data['item'][i]['value'] = self.plugin.getitemvalue(i)

                # return it as json the the web page
                try:
                    return json.dumps(data)
                except Exception as e:
                    self.logger.error(f"get_data_html exception: {e}")

            return {}


Die optionale Möglichkeit ein ``dataSet`` kann genutzt werden, z.B. Daten in unterschiedlichen
Zyklen zu aktualisieren (z.B. für Daten, deren Ermittlung eine längere Zeit in Anspruch nimmt)
oder nur bestimmte Daten anzufordern. Dieses Feature ist im database Plugin implementiert und
kann dort im Detail angesehen werden.


IDs an DOM-Elemente zuweisen
----------------------------

Normalerweise sieht das ``headtable`` wie folgt aus:

.. code-block:: html+jinja

    {% block headtable %}
        <table class="table table-striped table-hover" style="min-width:600px;">
            <tbody>
                <tr>
                    <td class="py-1"><strong>Scanne von IP</strong></td>
                    <td class="py-1">{{ p.fromip }}</td>
                    ...
                </tr>

                ...

            </tbody>
        </table>
    {% endblock headtable %}

Bei Tabellen im bodytab werden die einzelnen Datenzeilen beim Rendern durch die for-Schleife befüllt:

.. code-block:: html+jinja

    {% block **bodytab1** %}
        <div class="container-fluid m-2 table-resize">
            <table id="maintable">
                <thead>
                    <tr>
                        <th></th>
                        <th>{{ _('Item') }}</th>
                        <th>{{ _('Typ') }}</th>
                        <th>{{ _('knx_dpt') }}</th>
                        <th>{{ _('Wert') }}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in items %}
                        <tr>
                            <td></td>
                            <td class="py-1">{{ item._path }}</td>
                            <td class="py-1">{{ item._type }}</td>
                            <td class="py-1">{{ item.conf['knx_dpt'] }}</td>
                            <td class="py-1">{{ item._value }}</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% endblock **bodytab1** %}


Um die Werte in die <td>-Elemente schreiben zu können, nachdem die Webseite erstellt wurde,
müssen die <td>-Elemente jeweils mit einer ID ergänzt werden. Um sicherzustellen,
dass die ID in Wertetabellen eindeutig sind, wird die for-Schleifenvariable (hier: der Item Name) verwendet. Es ist wichtig, bei Datentabellen (nicht bei normalen Tabellen!)
pro Zeile eine leere Zelle einzufügen! Bei headtables sollten leere Spalten vermieden werden.

.. code-block:: html+jinja

    {% block headtable %}
        <table class="table table-striped table-hover" style="min-width:600px;">
            <tbody>
                <tr>
                    <td class="py-1"><strong>Scanne von IP</strong></td>
                    <td id="fromip" class="py-1">{{ p.fromip }}</td>
                    ...
                </tr>
                ...
            </tbody>
        </table>
    {% endblock headtable %}

    ...

    {% block **bodytab1** %}
        <div class="container-fluid m-2 table-resize">
            <table id="maintable">
                <thead>
                    <tr>
                        <th></th>
                        ...
                        <th class="value">{{ _('Wert') }}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in items %}
                        <tr>
                            <td></td>
                            ...
                            <td id="{{ item }}_value" class="py-1">{{ item._value }}</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% endblock **bodytab1** %}

Jetzt können die DOM-Elemente über die IDs ``fromip`` und ``<item>_value`` angesprochen werden.

.. warning::

    Damit die Anzeige und Adaption der Datatables einwandfrei funktioniert, ist es elementar, den
    Aufbau sauber und exakt aus dem Sampleplugin zu übernehmen. So muss beispielsweise die Tabelle
    selbst in ein div gepackt werden, dem die Klasse ``table-resize`` zugewiesen ist. Außerdem
    müssen leere Zellen am Anfang jeder Zeile eingefügt werden. Ein Angabe von Klassen ist nicht nötig,
    da dies automatisch passiert.


Erweitern der JavaScript-Funktion handleUpdatedData()
-----------------------------------------------------

Das Webinterface ruft regelmäßig eine Methode des Plugins auf, um aktualisierte Daten zu erhalten.
Wenn die Daten empfangen wurden, werden sie an die JavaScript-Funktion ``handleUpdatedData()``
der Webseite übergeben. Diese Funktion weist dann die neuen Daten den jeweiligen DOM-Elementen zu.

Die Funktion ``handleUpdatedData()`` ist im Block ``pluginscripts`` des HTML-Templates definiert.
Das folgende Beispiel weist die neuen Daten dem oben vorgestellten <td>-Element des ``headtable`` zu:

.. code-block:: html+jinja

    {% block pluginscripts %}
    <script>
        function handleUpdatedData(response, dataSet=null) {
            if (dataSet === 'devices_info' || dataSet === null) {
                var objResponse = JSON.parse(response);

                shngInsertText('fromip', objResponse['fromip']);
            }
        }
    </script>
    {% endblock pluginscripts %}


Das nächste Beispiel befüllt dazu analog die <td>-Elemente der Zeilen in der Tabelle im ``bodytab?``.
Die Parameter der shngInsertText-Funktion sind dabei wie folgt:

#. (obligatorisch) ID des HTML Elements, z.B. der Tabellenzelle

#. (obligatorisch) zu schreibender Wert, wird aus dem objResponse dict gelesen

#. (optional) Wenn das Element aus Parameter 0 in einer dataTable ist, muss die ID der Tabelle mitgegeben werden

#. (optional) Möchte man beim Ändern eines Werts einen Highlight-Effekt, kann die Dauer in Sekunden angegeben werden


.. code-block:: html+jinja

    {% block pluginscripts %}
    <script>
        function handleUpdatedData(response, dataSet=null) {
            if (dataSet === 'devices_info' || dataSet === null) {
                var objResponse = JSON.parse(response);

                for (var item in objResponse) {
                    shngInsertText(item+'_value', objResponse['item'][item]['value'], null, 2);
                    // bei Tabellen mit datatables Funktion sollte die Zeile lauten (ID ersetzen!):
                    // shngInsertText(item+'_value', objResponse['item'][item]['value'], 'maintable', 2);
                }
                // Bei Datatables sollte nach der Schleife die gesamte Tabelle ein Mal aktualisert werden
                // $('#maintable').DataTable().draw(false); // ID entsprechend ersetzen
            }
        }
    </script>
    {% endblock pluginscripts %}


Sortierbare Tabellen
--------------------

Wie erwähnt muss für das Aktivieren von sortier- und durchsuchbaren Tabellen der entsprechende Script-Block
wie in :doc:`Das Webinterface mit Inhalt füllen </entwicklung/plugins/webinterface_filling_webinterface>`
unter Punkt 3 beschrieben eingefügt werden. Dabei ist auch zu beachten, dass der zu sortierenden
Tabelle eine entsprechende ID gegeben wird (im Beispiel oben ``maintable``).

Damit die neuen Daten auch von datatables.js erkannt und korrekt sortiert werden, ist es wichtig,
dem Aufruf ``shngInsertText`` die Tabellen-ID als dritten Parameter mitzugeben (im Beispiel 'maintable').

Standardmäßig werden die Spalten automatisch so skaliert, dass sie sich den Inhalten anpassen. Dies kann
va. in Kombination mit dem ``responsive`` Modul der Datatables zu
unerwünschten Ergebnissen führen. Insofern ist es empfehlenswert,
bestimmten Spalten eine konkrete Breite vorzugeben. Dazu sollte im Block ``pluginstyles`` entsprechender
Code eingefügt werden.


.. code-block:: css+jinja

    {% block pluginstyles %}
    <style>
      table th.dpt {
        width: 40px;
      }
      table th.value {
        width: 100px;
      }
    </style>
    {% endblock pluginstyles %}


Außerdem ist den Spalten die entsprechende Klasse zuzuweisen. Dies ist
durch Angabe mittels class-Attribut in den ``<th>`` Tags möglich. Alternativ - und der bessere Ansatz -
ist es, die Klassen bei der Initialisierung der Tabelle zuzuweisen.
Sollte der Inhalt einer Spalte erwartungsgemäß sehr breit sein, kann die Spalte stattdessen auch
durch Zuweisen der Klasse "none" als ausklappbare Informationszeile konfiguriert werden.
Die Deklaration der Tabelle im pluginscripts
Block hat dabei wie folgt auszusehen, wobei bei ``targets`` die interne Nummerierung der Spalten
anzugeben ist (0 wäre die erste Tabellenspalte, 1 die zweite, etc.).

.. code-block:: html+jinja

    table = $('#maintable').DataTable( {
      "pageLength": webif_pagelength,
      "pageResize": resize,
      "columnDefs": [{ "targets": 1, "className": "none"}].concat($.fn.dataTable.defaults.columnDefs)
    } );


Hinzufügen von Tabellenzeilen
-----------------------------

In manchen Fällen kann es notwendig sein, neue Zeilen einer Tabelle dynamisch hinzuzufügen;
beispielsweise, wenn die letzten durchgeführten Commandos oder Logeinträge ergänzt werden sollen.
Hierzu ist es nötig, die Funktion ``handleUpdatedData`` entsprechend anzupassen.

In der ersten if-Abfrage wird evaluiert, ob bereits ein Element mit entsprechender ID existiert.
Falls nicht, wird die Zeile neu angelegt und sanft eingeblendet. Im unten stehenden Code wird zuerst gecheckt,
ob es eine Datentabelle mit der ID "maintable" gibt.
In der Zeile ``if ( $.fn.dataTable.isDataTable('#maintable') )`` sowie in der darauf folgenden
Zeile muss '#maintable' durch die tatsächliche ID der zu aktualisierenden Tabelle ersetzt werden.
Falls nun eine entsprechende Tabelle auf der Seite gefunden wurde, wird diese
als "table_to_update" definiert (was später für das Hinzufügen einer Zeile mittels row.add genutzt wird).

Durch die Einträge in der Liste ``table_to_update.row.add( [ item, '' ] )`` wird festgelegt, welchen Inhalt
die Spalten bekommen sollen. Im Beispielfall wird also der Itemname in die erste Spalte und
ein leerer Wert in die zweite Spalte eingetragen.
Anschließend wird der zweiten Spalte die relevante ID hinzugefügt, um zukünftig den Wert
aktualisieren zu können. Möchte man weiteren Spalten ebenfalls
eine ID zuweisen, ist die Codezeile zu kopieren und die Zahl beim Eintrag ``td:eq(1)`` entsprechend
zu ändern (0 = erste Spalte, 1 = zweite Spalte, etc.). Abschließend wird der leere Wert schließlich
mittels ``shngInsertText`` aktualisiert und dank Angabe einer Zahl als 4. Parameter x Sekunden lang farblich markiert. Nach der for-Schleife sollte die Tabelle neu gezeichnet werden (siehe Beispiel).


.. code-block:: html+jinja

    {% block pluginscripts %}
    <script>
        function handleUpdatedData(response, dataSet=null) {
            if (dataSet === 'devices_info' || dataSet === null) {
                var objResponse = JSON.parse(response);
                for (var item in objResponse) {
                    if (!document.getElementById(item+'_value')) {
                        if ( $.fn.dataTable.isDataTable('#maintable') ) {
                            table_to_update = $('#maintable').DataTable();
                            let newRow = table_to_update.row.add( [ item, '' ] ).draw(false).node();
                            newRow.id = objResponse['item'][item]+"_row";
                            $('td:eq(1)', newRow).attr('id', objResponse['item'][item]+'_value');
                            shngInsertText(item+'_value', objResponse['item'][item]['value'], 'maintable', 5);
                        }
                    }
                    else
                    {
                      shngInsertText(item+'_value', objResponse['item'][item]['value'], 'maintable', 2);
                    }

                }
                $('#maintable').DataTable().draw(false);
            }
        }
    </script>
    {% endblock pluginscripts %}


Hervorheben von Änderungen
--------------------------

Wird über ``shngInsertText`` der Inhalt eines HTML Elements aktualisiert, kann dies optional durch einen
farbigen Hintergrund hervorgehoben werden. Der jquery UI Effekt ``switchClass`` wechselt dabei sanft
von einer CSS Klasse zur anderen. Die Dauer des Effekts kann im letzten Parameter des Aufrufs von
``shngInsertText`` in Sekunden angegeben werden. Eine Dauer von 0 oder keine Angabe sorgen dafür,
dass kein Highlight Effekt ausgeführt wird. Außerdem wird der Effekt auch nicht aktiviert, wenn der vorige
Wert ``...`` war (z.B. beim Initialisieren der Tabelle, bevor aktualisierte Werte vom Plugin kommen).
Die beiden Klassen sind bereits hinterlegt, können aber in der index.html des Plugin webif
im Block ``pluginStyles`` bei Bedarf überschrieben werden.

.. code-block:: css+jinja

    {% block pluginstyles %}
    <style>
        .shng_effect_highlight {
          background-color: #FFFFE0;
        }
        .shng_effect_standard {
          background-color: none;
        }
    </style>
    {% endblock pluginstyles %}


Festlegen von Aktualisierungsintervall, dataSets und weiteren Parametern
------------------------------------------------------------------------

Zu Beginn der Templatedatei ``webif/templates/index.html`` finden sich die folgenden Zeilen:

.. code-block:: css+jinja

   {% set update_interval = 0 %}
   {% set update_active = false %}
   {% set dataSet = 'item_details' %}
   {% set update_params = item_id %}
   {% set buttons = True %}
   {% set autorefresh_buttons = true %}
   {% set reload_button = true %}
   {% set close_button = true %}
   {% set row_count = false %}
   {% set initial_update = true %}

Das Intervall wird via ``update_interval`` auf den gewünschten Wert in Millisekunden gesetzt. Dabei muss sichergestellt sein, dass das gewählte Intervall lang genug ist, dass die Python-Methode ``get_data_html()`` des Plugins die Daten liefern kann, bevor das Intervall abläuft. Wenn nur Daten zurückgegeben werden, die von anderen Routinen und Threads des Plugins bereits bereitgestellt wurden, kann ein Update-Intervall von ca. 1000 ms gewählt werden. Wenn die Python-Methode ``get_data_html()`` selbst noch weitere Routinen ausführen muss, sollte das Update-Intervall wahrscheinlich nicht kleiner als 5000 ms sein.

.. warning::

    Das Intervall darf nicht zu klein sein. Die Dauer **MUSS** länger sein als die notwendige Zeit zur Ausführung der Python-Methode ``get_data_html()``. Bei datenintensiven Plugins macht es u.U. Sinn,
    das Intervall abhängig von der Anzahl an Datensätzen festzulegen.

Durch ``update_active`` wird festgelegt, ob die automatische Aktualisierung zum Start aktiviert oder deaktiviert sein soll. Dies
kann hilfreich sein, um z.B. ein optimales Updateintervall anzugeben, aber dem User zu überlassen, die automatische Aktualisierung
einzuschalten. Im Kopfbereich des Web Interfaces ist dazu neben dem "Aktualisieren"-Button sowohl eine Checkbox zum (De)Aktivieren,
als auch ein Feld für die Adaptierung des Intervalls vorgesehen.

Möchte man verschiedene dataSets nutzen, kann durch den entsprechenden Parameter ``dataSet`` ein entsprechender Name angegeben werden.
Außerdem ist es möglich, zusätzliche Parameter zu definieren, die der Methode zur Verfügung gestellt werden soll.
Dazu sollte die Methode get_data_html in der webif __init__.py entsprechend angepasst werden. Das vereinfachte Beispiel ist dem
Database Plugin entnommen, das zwei Tabs mit verschiedenen Daten anzeigt, die eben auch unterschiedliche Rückmeldungen aus dem
Plugin erhalten.

Die Angaben zu den Buttons sind optional und können
genutzt werden, um die Schalter und Auto-Refresh Funktionen im Header zu verstecken, wenn sie nicht
gebraucht werden.

Durch Definieren der ``row_count`` Variable wird beim Anzeigen einer Tabelle automatisch die Anzahl
an Datenreihen ermittelt und in die Variable ``window.row_count`` gespeichert. Auf diesen Wert kann
in einem eigenen Javascript zugegriffen werden. Wird diese Funktion nicht gebraucht, sollte die entsprechende
Zeile gelöscht bzw. nicht gesetzt werden.

Wenn ``initial_update`` auf "true" gesetzt ist, werden automatisch beim Laden jeder Seite die Daten mittels
get_data_html abgefragt. Dies ist insbesondere dann sinnvoll, wenn anfangs die Tabelle mit Dummy-Daten
oder ohne Inhalt befüllt wurde.


.. code-block:: python

    @cherrypy.expose
    def get_data_html(self, dataSet=None, params=None):
        """
        Return data to update the webpage

        For the standard update mechanism of the web interface, the dataSet to return the data for is None

        :param dataSet: Dataset for which the data should be returned (standard: None)
        :return: dict with the data needed to update the web page.
        """
        self.logger.debug("Page Refresh for Dataset: {}, params: {}".format(dataSet, params))
        if dataSet == 'overview':
            # get the new data
            data = self.plugin._webdata
            try:
                data = json.dumps(data)
                return data
            except Exception as e:
                self.logger.error(f"get_data_html exception: {e}")
        if dataSet == "item_details":
            item_id = params
            if item_id is not None:
                rows = self.plugin.readLogs(item_id, time_start=time_start, time_end=time_end)
            else:
                rows = []
            try:
                data = json.dumps(rows)
                if data:
                    return data
                else:
                    return None
            except Exception as e:
                self.logger.error(f"get_data_html exception: {e}")

        return {}

Dynamische Anpassung von Aktualisierungsintervall, dataSets und weiteren Parametern
-----------------------------------------------------------------------------------

Unter Umständen ist es sinnvoll, diverse Parameter der automatischen Aktualisierung durch ein Script (oder einen Button)
anzupassen. Die Parameter werden dabei durch Aufruf von ``window.refresh.update({});`` in Form eines Dictionary aktualisiert.
Die möglichen Schlüsselwörter des Dictionaries sind dabei:

- dataSet: zur Angabe der Inhalte, die vom Plugin angefordert werden sollen
- update_params: etwaige zusätzliche Parameter für die get_data_html Methode
- update_interval: das Updateintervall in Millisekunden
- update_active: Aktivieren oder Deaktivieren der automatischen Aktualisierung

Das folgende fiktive Beispiel zeigt einen Script Block, bei dem die Aktualisierung ausgeschaltet wird,
wenn wir den 12.12.2022 haben (was vermutlich wenig Sinn macht und daher angepasst werden sollte).

.. code-block:: html+jinja

    <!--
    This is an example on how to update the page refresh method. You can set the dataSet, update interval, special parameters or (de)activate the auto refresh
    In the example the update is deactivated on the 12th of December 2022 (what might make no sense at all)
    -->
    <script>
      var today = new Date();
      var today_date = String(today.getDate()) + String(today.getMonth() + 1) + today.getFullYear();
      let test_date = "12122022";
      if (today_date === test_date)
          window.refresh.update({dataSet:'test', update_params:'specialitem', update_interval:2000, update_active:false});
    </script>
