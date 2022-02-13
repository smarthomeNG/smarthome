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
                    self.logger.error("get_data_html exception: {}".format(e))

            return {}


Die optionale Möglichkeit einen ``dataSet`` anzugeben, ist für zukünftige Erweiterungen vorgesehen.
Darüber soll es möglich werden, Daten in unterschiedlichen Zyklen zu aktualisieren
(z.B. für Daten, deren Ermittlung eine längere Zeit in Anspruch nimmt).


IDs an DOM-Elemente zuweisen
----------------------------

Normalerweise sieht das ``headtable`` wie folgt aus:

.. code-block:: html+jinja

    {% block headtable %}
        <table class="table table-striped table-hover">
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

Bei Tabellen werden die einzelnen Datenzeilen beim Rendern durch die for-Schleife befüllt:

.. code-block:: html+jinja

    {% block **bodytab1** %}
        <div class="table-responsive" style="margin-left: 3px; margin-right: 3px;" class="row">
            <div class="col-sm-12">
                <table id="#maintable" class="table table-striped table-hover pluginList display">
                    <thead>
                        <tr>
                            <th>{{ _('Item') }}</th>
                            <th>{{ _('Typ') }}</th>
                            <th>{{ _('knx_dpt') }}</th>
                            <th>{{ _('Wert') }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in items %}
                            <tr>
                                <td class="py-1">{{ item._path }}</td>
                                <td class="py-1">{{ item._type }}</td>
                                <td class="py-1">{{ item.conf['knx_dpt'] }}</td>
                                <td class="py-1">{{ item._value }}</td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    {% endblock **bodytab1** %}


Um die Werte in die <td>-Elemente schreiben zu können, nachdem die Webseite erstellt wurde,
müssen die <td>-Elemente jeweils mit einer ID ergänzt werden. Um sicherzustellen,
dass die ID in Wertetabellen eindeutig sind, wird die for-Schleifenvariable (hier: der Item Name) verwendet:

.. code-block:: html+jinja

    {% block headtable %}
        <table class="table table-striped table-hover">
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
        <div class="table-responsive" style="margin-left: 3px; margin-right: 3px;" class="row">
            <div class="col-sm-12">
                <table id="#maintable" class="table table-striped table-hover pluginList display">
                    <thead>
                        <tr>
                            <th class="item">{{ _('Item') }}</th>
                            <th class="typ">{{ _('Typ') }}</th>
                            <th class="dpt">{{ _('knx_dpt') }}</th>
                            <th class="value">{{ _('Wert') }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in items %}
                            <tr>
                                <td class="py-1">{{ item._path }}</td>
                                <td class="py-1">{{ item._type }}</td>
                                <td class="py-1">{{ item.conf['knx_dpt'] }}</td>
                                <td id="{{ item }}_value" class="py-1">{{ item._value }}</td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    {% endblock **bodytab1** %}

Jetzt können die DOM-Elemente über die IDs ``fromip`` und ``<item>_value`` angesprochen werden.


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


Das nächste Beispiel befüllt dazu analog die <td>-Elemente der Zeilen in der Tabelle im ``bodytab?``:

.. code-block:: html+jinja

    {% block pluginscripts %}
    <script>
        function handleUpdatedData(response, dataSet=null) {
            if (dataSet === 'devices_info' || dataSet === null) {
                var objResponse = JSON.parse(response);

                for (var item in objResponse) {
                    shngInsertText(item+'_value', objResponse['item'][item]['value']);
                    // bei Tabellen mit datatables Funktion sollte die Zeile lauten:
                    // shngInsertText(item+'_value', objResponse['item'][item]['value'], 'maintable');
                }
            }
        }
    </script>
    {% endblock pluginscripts %}


Sortierbare Tabellen
--------------------

Wie erwähnt muss für das Aktivieren von sortier- und durchsuchbaren Tabellen der entsprechende Script-Block
wie in :doc:`Das Webinterface mit Inhalt füllen </entwicklung/plugins/webinterface_filling_webinterface>`
unter Punkt 3 beschrieben eingefügt werden. Dabei ist auch zu beachten, dass der zu sortierenden
Tabelle eine entsprechende ID gegeben wird (im Beispiel oben ``#maintable``) und die Klasse ``display``
ergänzt wird.

Damit die neuen Daten auch von datatables.js erkannt und korrekt sortiert werden, ist es wichtig,
dem Aufruf ``shngInsertText`` die Tabellen-ID als dritten Parameter mitzugeben (im Beispiel 'maintable').

Standardmäßig werden die Spalten automatisch so skaliert, dass sich den Inhalten anpassen. Möchte man
bestimmten Spalten eine konkrete Breite vorgeben, sollte im Block ``pluginstyles`` entsprechender
Code eingefügt werden. Außerdem sind die ``<th>`` Tags natürlich mit den entsprechenden Klassen zu bestücken.
Zusätzlich/alternativ kann die Tabelle auch mit dem css Style ``table-layout: fixed;`` versehen werden,
um die dynamische Anpassung der Spaltenbreite gänzlich zu unterbinden.

.. code-block:: css+jinja

    {% block pluginstyles %}
    <style>
      table th.dpt {
        width: 40px;
      }
      table th.value {
        width: 100px;
      }
      #maintable {
         display: none;
      }
    </style>
    {% endblock pluginstyles %}


Sollte der Inhalt einer Spalte erwartungsgemäß sehr breit sein, kann die Spalte stattdessen auch
als ausklappbare Informationszeile konfiguriert werden. Dann empfiehlt es sich auf jeden Fall,
wie oben angegeben, die Tabelle per CSS unsichtbar zu machen. Die datatables.js defaults sorgen dafür,
dass die Tabelle nach der kompletten Inititalisierung angezeigt wird. Dadurch wird ein
mögliches Flackern der Seite beim Aufbau verhindert. Die Deklaration der Tabelle im pluginscripts
Block hat dabei wie folgt auszusehen, wobei bei ``targets`` die interne Nummerierung der Spalten
anzugeben ist (0 wäre die erste Tabellenspalte, 2 die zweite, etc.).

.. code-block:: html+jinja

    table = $('#maintable').DataTable( {
      "columnDefs": [{ "targets": 0, "className": "none"}].concat($.fn.dataTable.defaults.columnDefs)
    } );


Festlegen des Aktualisierungsintervalls
---------------------------------------

Zu Beginn der Templatedatei ``webif/templates/index.html`` findet sich die folgende Zeile:

.. code-block:: css+jinja

   {% set update_interval = 0 %}

Diese wird auf den gewünschten Wert in Millisekunden gesetzt. Dabei muss sichergestellt sein, dass das gewählte Intervall lang genug ist, dass die Python-Methode ``get_data_html()`` des Plugins die Daten liefern kann, bevor das Intervall abläuft. Wenn nur Daten zurückgegeben werden, die von anderen Routinen und Threads des Plugins bereits bereitgestellt wurden, kann ein Update-Intervall von ca. 1000 ms gewählt werden. Wenn die Python-Methode ``get_data_html()`` selbst noch weitere Routinen ausführen muss, sollte das Update-Intervall wahrscheinlich nicht kleiner als 5000 ms sein.

.. warning::

    Das Intervall darf nicht zu klein sein. Die Dauer **MUSS** länger sein als die notwendige Zeit zur Ausführung der Python-Methode ``get_data_html()``.
