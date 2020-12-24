
.. index:: Multi-Language Support
.. index:: translations

.. role:: redsup
.. role:: bluesup

=================================================
Unterstützung mehrerer Sprachen :bluesup:`Update`
=================================================

:Note: Diese Dokumentation bezieht sich auf Versionen nach v1.4.2. Sie gilt nicht für Versionen bis inklusive v1.4.2

Wörter oder Phrasen können im Webinterface als mehrsprachig deklariert werden, so dass sie abhängig von der in SmartHomeNG eingestellten Sprache automatisch übersetzt werden.


Text als mehrsprachig kennzeichnen
==================================

1. In Jinja2-Templates
----------------------

Um einen Textteil als mehrsprachig zu deklarieren, muss er Teil eines Jinja2-Ausdrucks sein (sie muss von ``{{ ... }}`` eingeschlossen werden).

Innerhalb des Jinja2-Ausdrucks muss der Textteil von ``_( ... )`` eingeschlossen sein.

Der mehrsprachige Textteil kann als Stringliteral oder aus einer Variable eingebunden werden. Ein Stringliteral muss zusätzlich in Anführungszeichen ``_(' ... ')`` gesetzt werden. 

Das heißt, dass ein Text im Webinterface, wie z.B.

.. code-block:: html
   :caption: Beispiel für `plugin/webif/templates/index.html`

   <td class="py-1"><strong>Service für den KNX Support</strong></td>

durch entsprechende Markierung als mehrsprachig und als Stringliteral deklariert werden kann:

.. code-block:: html
   :caption: Beispiel für mehrsprachiges Markup für `plugin/webif/templates/index.html`

   <td class="py-1"><strong>{{ _('Service für den KNX Support') }}</strong></td>


2. Im Python-Code
-----------------

Um einen Textteil als mehrsprachig zu deklarieren, muss die ``translate``-Methode der Plugin-Klasse aufgerufen werden:

.. code-block:: python

   translated_text = self.translate('text')


Wie Mehrsprachigkeit funktioniert
=================================

Die Übersetzung ist ein mehrstufiger Prozess. Dabei wird an mehreren Stellen nach dem zu übersetzenden Textteil gesucht. Die erste Fundstelle wird verwendet. Die Suchreihenfolge ist wie folgt:

   1. in der Sprachdatei des Plugins (in der gewählten Sprache)
   2. in der globalen Sprachdatei (in der gewählten Sprache)
   3. in der Sprachdatei des Plugins (auf Englisch)
   4. in der globalen Sprachdatei (auf Englisch)

Wenn kein Suchtreffer erfolgt, wird der Text unverändert ausgegeben. Die fehlende Übersetzung wird mit der Dringlichkeit INFO im Log vermerkt-

Die Sprachdatei des Plugins heißt ``locale.yaml`` und befindet sich im Plugin-Verzeichnis.

Die globale Sprachdatei, in der überwiegend Übersetzungen für einzelne Wörter enthalten sind, die vom Core, von Modulen oder in mehreren Plugins verwendet werden, heißt ``locale.yaml`` und befindet sich im ``/bin``-Verzeichnis von SmartHomeNG.


Sprachen und Übersetzungen hinzufügen
=====================================

In den Sprachdateien wird für jeden zu übersetzenden Text ein dict im Abschnitt ``plugin_translations:`` aufgenommen:

.. code-block:: YAML
   :caption: Beispiel einer Übersetzung

   plugin_translations:
       # Translations for the plugin specially for the web interface
       'Schließen':         {'de': '=', 'en': 'Close'}

Das Gleichheitszeichen in der deutschen Übersetzung bedeutet, dass der key **Schließen** schon in der angegebenen Sprache ist und nicht übersetzt werden muss. In dem Fall wird nicht weiter gesucht und kein Log-Eintrag ausgegeben.

Weitere Sprachen können durch Hinzufügen des Sprachcodes und der jeweiligen Übersetzungen definiert werden:

.. code-block:: YAML
   :caption: Beispiel einer Übersetzung

   plugin_translations:
       # Translations for the plugin specially for the web interface
       'Schließen':         {'de': '=', 'en': 'Close', 'fr': 'Fermer'}


Platzhalter in Übersetzungen nutzen :redsup:`Neu`
=================================================

In der aktuellen Version von SmartHomeNG ist es möglich, Platzhalter in Übersetzungen zu verwenden. Das macht es einfache, vollständige Sätze zu übersetzen, da sich die Struktur des Satzes in unterschiedlichen Sprachen unterscheidet. 

Übersetzungen können mehrere Platzhalter enthalten. Diese Platzhalter und ihre Werte müssen als Python-dict definiert werden. Die Schlüssel des dict sind die Namen der Platzhalter, die Werte enthalten die einzufügenden Texte für die jeweiligen Sprachen.

Das folgende Beispiel zeigt Übersetzungen mit Platzhaltern für **item_id**. Der Name des Platzhalters muss von geschweiften Klammern eingeschlossen sein (**ohne** Leerzeichen zwischen Klammer und Namen).

.. code-block:: YAML
   :caption: Beispiel für Übersetzungen mit Platzhaltern

   plugin_translations:
    'Löschauftrag für die Einträge von Item ID {item_id} in der Tabelle "log" wurde erfolgreich initiiert!':
        'de': '='
        'en': 'Deletion of data for the entries of item ID {item_id} in table "log" successfully initiated.'

:Critical: TODO - hier fehlt das Platzhalter-dict {'item_id', item.id()}; wie wird das definiert?

1. Platzhalter in Jinja2-Templates
----------------------------------

Wenn ein mehrsprachiger Ausdruck (wie oben im ersten Beispiel) mit flexiblem Inhalt für den Namen des Service versehen werden soll, ohne dass für jeden Service (z.B. KNX, enOcean, ...) einzelne Übersetzungen definiert werden, kann das wie folgt erreicht werden:

.. code-block:: html

   <td class="py-1"><strong>{{ _('Service für den {service} Support', vars={'service': 'KNX'}) }}</strong></td>


2. Platzhalter im Python-Code
-----------------------------

Wenn ein Platzhalter in der Übersetzung enthalten ist, muss ``self.translate`` mit dem Platzhalter-dict als zweitem Argument aufgerufen werden:

.. code-block:: python

   translated_text = self.translate('text', {'item_id', item.id()})


