.. index:: Web Interface; Automatich Updates

.. role:: redsup
.. role:: bluesup



Automatic Updates of Webinterface data :redsup:`new`
====================================================

To update data in the web interface, the web page periodically sends AJAX requests to the plugin and processes the
result by incorporating the new data in the DOM of the web page.

To implement automatic updates, the following has to be added to the web interface:

  - In the class **WebInterface** of the plugin, the method **get_data_html()** has to be implemented/extended to deliver
    the needed data
  - The DOM elements (e.g. <td> elements in the **headtable** block or in the **bodytab?** blocks that are to be updated,
    have to have an id assigned to them
  - int the html template, the javascript function **handleUpdatedData()** has to be implemented/extended
  - The template variable **update_interval** has to be set to the desired interval (in milli-seconds)


Extending the Python method get_data_html()
-------------------------------------------

The class **WebInterface** in the plugin code has to be extended to collect the data that is needed to update the web page
and to return it as a dict:

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


Die optionale Möglichkeit einen **dataSet** anzugeben, ist für zukünftige Erweiterungen vorgesehen. Darüber soll es
möglich werden, Daten in unteeschiedlichen Zyklen zu aktualisieren (z.B. für Daten deren Ermittlung eine längere
Zeit in Anspruch nimmt).


Assign IDs to the DOM elements
------------------------------

Usually the **headtable** looks like this:

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

For tables, it is essential to have an individual id for the <td> elements in every row of the table that is
filled through the for loop during rendering:

.. code-block:: html+jinja

    {% block **bodytab1** %}
        <div class="table-responsive" style="margin-left: 3px; margin-right: 3px;" class="row">
            <div class="col-sm-12">
                <table class="table table-striped table-hover pluginList">
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


To enable setting the values of the <td> elements while the page is displayed, the td elements have to be extended
with an id. To ensure individual ids in data tables, the id has to include the variable (named item) from the for loop:

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
                <table class="table table-striped table-hover pluginList">
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
                                <td id="{{ item }}_value" class="py-1">{{ item._value }}</td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    {% endblock **bodytab1** %}

Now the DOM element can be accessed through the ids **fromip** and **<item>_value**.


Extending the Javascript function handleUpdatedData()
-----------------------------------------------------

The web interface calls the plugin periodically to get updated data. When new data is received, the javascript
function **handleUpdatedData()** of the web page is called. This function has to assign the updated data to the
right DOM elements.

The function **handleUpdatedData()** is defined in the block **pluginscripts** of the html template of the web interface.
The following example fills the data to the <td> element of **headdata** that has been mentioned above:

.. code-block:: html+jinja

    {% block pluginscripts %}
    <script>
        function handleUpdatedData(response, dataSet=null) {
            if (dataSet === 'devices_info' || dataSet === null) {
                var objResponse = JSON.parse(response);

                shngInsertText('fromip', objResponse['fromip'])
            }
        }
    </script>
    {% endblock pluginscripts %}


The following example fills the data to the <td> elements of all rows of **bodytab?** that has been mentioned above:

.. code-block:: html+jinja

    {% block pluginscripts %}
    <script>
        function handleUpdatedData(response, dataSet=null) {
            if (dataSet === 'devices_info' || dataSet === null) {
                var objResponse = JSON.parse(response);

                for (var item in objResponse) {
                    shngInsertText(item+'_value', objResponse['item'][item]['value'])
                }
            }
        }
    </script>
    {% endblock pluginscripts %}


Setting the update interval
---------------------------

At the top of the template file **webif/templates/index.html** you find the following line

.. code-block:: css+jinja

   {% set update_interval = 0 %}

Change it to the desired update interval in milli-seconds. Make sure, that the interval is longer than the time needed
to execute the Python method **get_data_html()**. If the method only returns data that has been updated/collected by
other Python threads, you can go down to about 1000 msec. If the Python method **get_data_html()** needs to collect
the data when beeing called, you probably should set the update interval not below 5000 msec.

.. warning::

    Make sure, that the interval is not too short. It HAS TO BE be longer than the time needed to execute
    the Python method **get_data_html()**.

