.. index:: Web Interface; Interaktion mit dem Plugin

.. role:: redsup
.. role:: bluesup



Interaktion des Webinterface mit dem Plugin :redsup:`new`
=========================================================

Wenn nicht nur die jeweils aktuellen Daten des Plugins dargestellt werden sollen, sondern auch Aktionen ausgelöst werden und Ergebnisse in das Webinterface übernommen werden sollen, müssen die dafür notwendigen Routinen zum Senden, Empfangen und Verarbeiten von AJAX-Kommandos implementiert werden.

Dazu sind die folgenden Schritte notwendig:

  - In der Klasse ``WebInterface`` des Plugins muss die Methode ``submit()`` implementiert bzw. erweitert werden, um die vorgesehenen Daten zum empfangen, zu verarbeiten und zurückzusenden.
  - Die DOM-Elemente (z.B. <td>-Elemente im ``headtable``-Block oder in den ``bodytab?``-Blöcken), welche die aktualisierten Daten anzeigen sollen, müssen jeweils eine eindeutige IDs erhalten.
  - Im Webinterface müssen die aktiven Elemente wie Buttons und Eingabefelder implementiert werden und jeweils eindeutige IDs erhalten.
  - Im HTML-Template muss (mindestens) eine neue Routine für das Handling der aktiven Elemente und für den Datentransfer innerhalb der Methode für das ``$(document).ready()``-Event implementiert werden.


Die Python-Methode submit() implementieren
------------------------------------------

Die Klasse ``WebInterface`` des Plugins muss eine Schnittstelle bieten, um Daten via AJAX zu empfangen und die verarbeiteten Daten zurückzuliefern.
Dazu dient die Methode ``submit()``:

.. code-block:: PYTHON

    class WebInterface(SmartPluginWebIf):

        def __init__(self, webif_dir, plugin):

            ...

        @cherrypy.expose
        def index(self, scan=None, test=None, reload=None):

            ...

        @cherrypy.expose
        def submit(self, param1=None):
            '''
            Submit handler für Ajax
            '''
            result = None

            if param1 is not None:

                # verarbeite die Daten
                result_dict = self.plugin.tu_was_mit_daten(param1)

            if result_dict is not None:
                # JSON zurücksenden
                cherrypy.response.headers['Content-Type'] = 'application/json'
                return json.dumps(result_dict).encode('utf-8')


Die Anzahl und die Namen der Funktionsparameter (im Beispiel nur ``param1``) müssen dem Bedarf und den Definitionen im Webinterface entsprechen.
Mehrere Variablen können einzeln (dann jeweils als eigener Parameter) oder gesammelt
in einem Dictionary Objekt übergeben werden. Das muss in der weiteren Verarbeitung berücksichtigt sein.

Der Block mit dem Kommentar "verarbeite die Daten" ruft beispielhaft nur eine beliebige Funktion des Plugins auf,
um die Daten zu verarbeiten und einen entsprechenden Rückgabewert zu erhalten.
Hier sind beliebige zusätzliche Verarbeitungen denkbar, wie z.B. Überprüfung der übergebenen
Werte auf Vollständigkeit und Gültigkeit, ggf. Transformation von Daten, auch umfangreichere
Interaktionen mit dem Plugin sind möglich. Weiterhin können die Daten, die zurückgegeben werden sollen,
formatiert und in ein Dictionary gekapselt werden.

Generell empfiehlt sich, als Rückgabewert nur ein Dictionary anzugeben;
zum Einen, weil die Daten für den Transport per JSON verkapselt werden, was Dictionaries nativ übergeben kann,
zum Anderen weil Dictionaries im Javascript der Webseite als Objekte direkt angesprochen werden können.

Das Dictionary

.. code-block:: PYTHON

    result_dict = {
                    "kategorie1": {
                        "attr1": "...",
                        "attr2": "...",
                        "wert": "..."
                    },
                    "kategorie2": {
                        "attr1": "...",
                        "attr2": "...",
                        "wert": "..."
                    }}

kann in der Javascript-Methode dann unmittelbar angesprochen werden, wenn das Dictionary an die Variable ``data`` übergeben wurde:

.. code-block:: JavaScript

    var kat1attr1 = data.kategorie1.attr1
    var kat2 = data.kategorie2
    var wert = kat2.wert


IDs an DOM-Elemente zuweisen
----------------------------

Normalerweise sieht das ``headtable`` wie folgt aus. Die Angabe einer min-width
ist optional, aber empfohlen, um das responsive Design zu optimieren.

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


Tabellen in einem ``bodytab?`` können mit einer Schleife befüllt werden, das ist auf der Seite
:doc:`Webinterface mit Inhalt füllen <webinterface_filling_webinterface>` näher beschrieben:

.. hint::

   Sowohl im thead als auch tbody ist jeweils eine leere Tabellenzelle einzufügen, um das
   Responsive Feature der Datentabellen korrekt anzuzeigen.


.. code-block:: html+jinja

    {% block **bodytab1** %}

        <div class="container-fluid m-2 table-resize">
            <table id="maintable">
                <thead>
                    <tr>
                        <th></th>
                        <th>{{ _('Attribut 1') }}</th>
                        <th>{{ _('Attribut 2') }}</th>
                        <th>{{ _('aktualisieren') }}</th>
                        <th>{{ _('Wert') }}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for elem in data %}
                        <tr>
                            <td></td>
                            <td>{{ data[elem]['attr1'] }}</td>
                            <td>{{ data[elem]['attr2'] }}</td>
                            <td> <!-- leer --> </td>
                            <td>{{ data[elem]['wert']</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% endblock **bodytab1** %}


Um das nachträgliche Zuweisen von Werten an die <td>-Elemente zu ermöglichen,
muss bei diesen eine ID ergänzt werden.
Damit die IDs in den Wertetabellen eindeutig sind, verwenden wir die Variable aus der for-Schleife:


.. code-block:: html+jinja

    {% block headtable %}
        <table id="headtable" class="table table-striped table-hover" style="min-width:600px;">
            <tbody>
                <tr>
                    <td></td>
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
                        <th>{{ _('Attribut 1') }}</th>
                        <th>{{ _('Attribut 2') }}</th>
                        <th>{{ _('aktualisieren') }}</th>
                        <th>{{ _('Wert') }}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for elem in data %}
                        <tr>
                            <td></td>
                            <td>{{ data[elem]['attr1'] }}</td>
                            <td>{{ data[elem]['attr2'] }}</td>
                            <td> <!-- leer --> </td>
                            <td id="{{ elem }}_value">{{ data[elem]['wert']</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% endblock **bodytab1** %}

Jetzt können die DOM-Elemente über die IDs ``fromip`` und ``<elem>_value`` angesprochen werden.
Im Beispiel von oben wäre <elem> jeweils ``kategorie1`` und ``kategorie2``.


Aktive Elemente im WebInterface definieren
------------------------------------------

Einzelne Buttons für generische Aktionen können üblicherweise im Block ``button`` definiert
und unterhalb der Headertabelle angezeigt werden,
wo standardmäßig schon die Buttons "Aktualisieren" und "Schließen" vorhanden sind.

.. code-block:: html+jinja

    {% block buttons %}
            <button id="clear" class="btn btn-shng btn-sm" type="button">Aktion ausführen</button>
    {% endblock %}

Dabei ist wichtig, dass die ID (hier: "clear") vergeben und eindeutig im gesamten Template ist.

Wenn nur ein Button eingefügt werden soll, ist das die einfachste Variante.
Wie weiter unten beschrieben, ist für jeden Button, der auf diese Weise implementiert wird,
eine eigene Handler-Routine erforderlich.

Wenn mehrere Buttons dieser Art vorgesehen sind, oder z.B. in einer Wertetabelle ein Button
in jeder Zeile stehen soll, dann bietet es sich an, statt einzelnen Button-Elementen eine Formularkonstruktion zu nutzen. Um das automatische Skalieren von Tabellen zu gewährleisten,
sollte das ``form`` Element NACH der Tabelle deklariert werden

.. code-block:: html+jinja

    {% block bodytab1 %}
      <div class="container-fluid m-2 table-resize">
          <table id="maintable">
              <thead>
                  <tr>
                      <th></th>
                      <th>{{ _('Attribut 1') }}</th>
                      <th>{{ _('Attribut 2') }}</th>
                      <th>{{ _('aktualisieren') }}</th>
                      <th>{{ _('Wert') }}</th>
                  </tr>
              </thead>
              <tbody>
                  {% for elem in data %}
                      <tr>
                          <td></td>
                          <td>{{ data[elem]['attr1'] }}</td>
                          <td>{{ data[elem]['attr2'] }}</td>
                          <td>
                              <button
                                  class="btn btn-shng btn-sm"
                                  type="button"
                                  onclick="$('#button').val('{{ elem }}');$('#button_pressed').submit();"
                              >lesen
                              </button>
                          </td>
                          <td id="{{ elem }}_value">{{ data[elem]['wert']</td>
                      </tr>
                  {% endfor %}
              </tbody>
          </table>
          <form id="button_pressed" action="" method="post">
              <input type="hidden" id="button" name="button" value="" />
          </form>

      </div>
    {% endblock bodytab1 %}


In der Tabellenspalte mit den Buttons wird in jeder Zeile ein Button eingefügt.
Durch den Ausdruck ``{{ elem }}`` wird jedem Button der entsprechende Zeilenwert
in den Button-Code eingefügt. Um die eindeutige Zuordnung sicher zu stellen,
wird die for-Variable der Tabelle verwendet. Natürlich können auch andere Werte verwendet werden,
z.B. Inhalte aus dem ``data`` Dictionary. Dann muss sicher gestellt sein, dass die Werte eindeutig sind.

Die Definition der aktiven Elemente ist damit abgeschlossen.


Javascript-Funktion zum Handling implementieren
-----------------------------------------------

Normalerweise werden Buttons und Formulare an den Webserver gesendet, welcher daraufhin eine
neue Webseite an den Browser schickt.
Um zu verhindern, dass bei jeder Interaktion eine neue Seite geladen wird,
benötigen die aktiven Elemente sogenannte handler-Methoden.
Gleichzeitig empfangen die handler die Antwortdaten vom Plugin und fügen diese in die entsprechenden DOM-Elemente ein.

Diese handler müssen auf der Webseite im Block ``pluginscripts`` eingefügt werden.
Falls dort noch kein Handler für das ``$(document).ready()``-Event vorhanden ist, wird dieser mit hinzugefügt;
ansonsten werden die neuen Handler in den document.ready-Handler eingefügt.


Der Handler für das document.ready-Event sieht wie folgt aus:

.. code-block:: html+jinja

    {% block pluginscripts %}
    <script type="text/javascript">
        $(document).ready( function () {

            // hier webseitenspezifische Funktionen einfügen
            // diese werden nach dem Rendern der Webseite ausgeführt
        }
    </script>
    {% endblock pluginscripts %}


Dort werden dann die Handler für die aktiven Elemente eingefügt.

.. code-block:: html+jinja

    {% block pluginscripts %}
    <script type="text/javascript">
        $(document).ready( function () {

            // Handler für einfachen Button - das "click"-Element wird abgefangen
            $("#clear").click(function(e) {

                // keine HTML-Aktion ausführen (z.B. Formular senden)
                e.preventDefault();

                // festen Wert per AJAX senden
                $.post('submit', {clear: "true"}, function(data) {

                    // Ergebnis in Feld #fromip schreiben. Der dritte Parameter muss mit der Tabellen-ID identisch sein.
                    shngInsertText('fromip', data.ip, 'maintable')
                });
                return false ;
            });

            // Handler für Formular - das "submit"-Element (Senden) wird abgefangen
            $("#button_pressed").submit(function(e) {

                // keine HTML-Aktion ausführen (z.B. Formular senden)
                e.preventDefault();

                // die Kennung des gedrückten Buttons per AJAX senden
                $.post('submit', {button: $("#button").val()}, function(data) {

                    // Zeile ermitteln
                    var row = $("#button").val()
                    var id = row + "_value"

                    // nur die betroffene Zeile ändern. Der dritte Parameter muss mit der Tabellen-ID identisch sein.
                    shngInserText(id, data.wert, 'maintable')

                    // alternativ kann auch ein ganzes Feld übertragen werden...
                    for (var row in data) {
                            shngInsertText(row + "_value", data.row.wert, 'maintable')
                    }
                });
                return false ;
            });


        }
    </script>
    {% endblock pluginscripts %}


In der Implementation ist zu beachten, dass die Werte vom Plugin so strukturiert sind,
dass sie verarbeitet werden können. Sowohl die gewählte Datenstruktur als auch die davon
abhängige Implementation der Handler können sich in Struktur und Umfang erheblich vom Beispiel unterscheiden.
