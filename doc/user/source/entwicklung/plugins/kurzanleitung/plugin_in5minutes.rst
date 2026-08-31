
=====================================
In wenigen Minuten zum eigenen Plugin
=====================================


Plugins sind Erweiterungen von SmartHomeNG mit zusätzlichen Funktionen. Sie sind in Python geschrieben.
Um ein neues Plugin hinzuzufügen, wird der Plugin-Code und ein entsprechender Eintrag in der Konfigurationsdatei ``plugin.yaml`` benötigt.

Eine gute Basis für ein eigenes Plugin ist das Beispielplugin, welches komplett
mit allen notwendigen Dateien auf github unter https://github.com/smarthomeng/smarthome im ``dev``-Ordner zur Verfügung steht.


Beschreibung des Plugins
========================

Übersicht
---------

Das Plugin wird in einem eigenen Ordner unterhalb des ``plugins``-Ordner abgelegt. Der Name des Ordners entspricht dem Namen des Plugins in **Kleinschreibung**.

Derzeit besteht ein Plugin mindestens aus drei Dateien, die alle im Plugin Ordner liegen. Dies sind:

  - ``__init__.py``
  - ``plugin.yaml``
  - ``user_doc.rst``

Die Datei ``__init__.py`` enthält den Python-Code des Plugins.

Die Datei ``plugin.yaml`` enthält die Metadaten des Plugins.
Diese geben eine formale Beschreibung des Plugins und werden verwendet, um die Dokumentation
zu erstellen und das Plugin im Admin-GUI verwalten zu können.

Die Datei ``user_doc.rst`` beinhaltet zusätzliche Dokumentation zum Plugin,
ausführlichere Beschreibungen, umfangreichere Beispiele oder Anwendungsmöglichkeiten
über die ``plugin.yaml`` hinaus. Auch diese Datei wird verwendet,
um die Dokumentation von SmartHomeNG zu erstellen.

Optional werden im Unterverzeichnis ``webif`` die Dateien dabgelegt, welche das Webinterface implementieren. Das
Verzeichnis hat folgenden Inhalt:

  - ``__init__.py``
  - Verzeichnis ``static``
  - Verzeichnis ``templates``

Die Datei ``__init__.py`` enthält den Python-Code des Webinterfaces des Plugins.

Im Verzeichnis ``static`` werden Dateien abgelegt, die durch das Webinterface an den Browser ausgeliefert werden.
Es gibt mindestens das Unterverzeichnis ``img``, in dem das Logo des Plugins under dem Namen ``plugin_logo.png``
gespeichert wird. Zulässig als Plugin Logos sind auch ``plugin_logo.jpg`` und ``plugin_logo.svg``

Weiterhin kann es ein Unterverzeichnis ``assets`` geben, in dem weitere Dateien (z.B. zur Dokumentation user_doc)
abgelegt werden.


.. hint::

   Das in früheren Versionen verwendete ``README``-Format für die Dokumentation von Plugins ist veraltet.
   Ein Großteil der Dokumentation ist in die Metadaten-Dokumentation in ``plugin.yaml`` übergegangen.
   Die restliche Dokumentation sollte nur noch im ``user_doc``-Format erfolgen.

   Soweit möglich, sollten bestehende ``README`` im Rahmen von Aktualisierungen in entsprechende ``user_doc`` überführt werden.

Um das Plugin zu laden, muss es in der Konfigurationsdatei ``/etc/plugin.yaml`` eingebunden und konfiguriert werden.


Die Metadaten: plugin.yaml
--------------------------

Diese Datei stellt Metadaten über das Plugin in den folgenden Abschnitten bereit:

* `plugin`  -  globale Attribute des Plugins
* `parameters`  -  Definition der Konfigurationsoptionen in ``etc/plugin.yaml``
* `item_attributes`  -  Definition der Item-Attribute, die durch dieses Plugin genutzt werden
* `item_structs`  -  Vorlagen für Item-Structs (Teilbäume) des Plugins
* `logic_parameters`  -  Definition von Parametern für Logiken, soweit das Plugin diese implementiert
* `plugin_functions`  -  Funktionen, die das Plugin für die Nutzung z.B. in Logiken bereitstellt


Der Typ des Plugins muss aus der folgenden Liste ausgewählt werden:

* gateway
* interface
* protocol
* system
* web


Beispiel einer Metadaten-Datei:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    # meta data for the plugin
    plugin:
        # Global plugin attributes
        type: interface                # plugin type (gateway, interface, protocol, system, web)

    parameters:
        # Definition of parameters to be configured in etc/plugin.yaml

    item_attributes:
        # Definition of item attributes defined by this plugin

    item_structs: NONE

    logic_parameters: NONE

    plugin_functions: NONE




Die Dokumentation: user_doc.rst
-------------------------------

Die Dokumentation beginnt mit dem Titel, der dem Namen des Plugins entspricht.

.. important::

   Die erste Überschrift der Dokumentationsdatei ``user_doc`` MUSS dem Kurznamen des Plugins in Kleinbuchstaben entsprechen.

   Dieser Eintrag wird als Einstiegspunkt für die Navigation in der Dokumentation genutzt.
   Ein anderer Eintrag als Überschrift sorgt für Inkonsistenzen in den Navigationselementen.

Die Datei sollte die folgende Struktur haben.

Die Konfigurationsparameter selbst müssen in der user_doc.rst nicht beschrieben werden. Die Dokumentation der
Konfigurationsparameter und der Item Attribute wird automatisch aus den Metadaten (aus der plugin.yaml) generiert.
Falls gewünscht kann jeweils auf die (automatisch generierte) Seite mit der Konfigurationsdokumentation verwiesen
werden.


.. literalinclude:: /dev/sample_plugin/user_doc.rst
    :caption: user_doc.rst des Sample Plugins

|


Konfigurieren des Plugins in der Systemkonfiguration `/etc/plugin.yaml`
-----------------------------------------------------------------------

Die Konfigurationsdatei ``plugin.yaml`` befindet sich im Unterordner ``etc`` der SmartHomeNG-Installation.
Hier wird SmartHomeNG mitgeteilt, welche Plugins geladen werden sollen, wo sie zu finden sind und welche Optionen sie ggf. benötigen.

Dies ist ein typischer Abschnitt für ein neues Plugin. Wir nehmen an, dass das Plugin ``myplugin`` heißt:

.. code-block:: yaml

    # etc/plugin.yaml
    myplugin_instance:
        plugin_name: myplugin
        parameter1: 42


Werfen wir einen Blick auf die einzelnen Angaben:

``myplugin_instance``:

Das ist der Name der tatsächlich geladenen Instanz des Plugins. Er kann frei gewählt werden.
Wenn mehrere Instanzen eines Plugins geladen werden (z.B. für mehrere Geräte des gleichen Typs),
wird anhand dieses Namens zwischen den Instanzen (und damit den Geräten) unterschieden.

``plugin_name``:

Das ist der Name des Plugin, der auch für den Plugin-Ordner verwendet wurde (wieder in Kleinbuchstaben).

``parameter1``:

Es können mehrere Parameter definiert werden, deren Werte dem Plugin bei der Initialisierung übergeben werden.
Sie können zur Konfiguration verwendet werden.


Der Plugin-Code: `__init__.py`
------------------------------

Das Nächste ist das Plugin selbst. Der Code befindet sich in der Datei ``/plugins/myplugin/__init__.py``.
Alle Plugins haben die gleiche Struktur. Der Einfachheit halber wird das oben verlinkte Beispielplugin als Grundlage verwendet.

Es gibt mehrere Funktionen, die erforderlich sind, damit SmartHomeNG mit dem Plugin korrekt kommunizieren kann.
Die meisten davon werden vom SmartHomeNG-Scheduler aufgerufen.

Zusätzlich werden eigene Funktionen im Plugin definiert, die die eigentlichen Aufgaben ausführen.
Der Scheduler kann angewiesen werden, diese zu bestimmten Zeiten oder in festgelegten Intervallen aufzurufen.
Das ist näher im Abschnitt "Der Scheduler" beschrieben.

.. hint::

   Der folgende Code ist direkt aus dem Beispielplugin (``dev/sample_plugin/__init__.py``) entnommen.
   Im Zweifel gilt immer die dort vorliegende, aktuelle Version als Referenz.

Die Klasse des Plugins erbt von ``SmartPlugin`` (aus ``lib.model.smartplugin``). Der Klassenname muss dem
``classname``-Parameter in der ``plugin.yaml`` entsprechen. Im Folgenden werden die Funktionen beschrieben, die
für ein Plugin benötigt werden bzw. benötigt werden können.


Vordefinierte Funktionen des Plugins
====================================


.. code-block:: python

    def __init__(self, sh=None, **kwargs):


Die ``__init__``-Funktion wird einmal aufgerufen, wenn SmartHomeNG im Rahmen der Initialisierung das Plugin lädt,
bevor die Items geladen sind. Hier wird der Code eingefügt, den das Plugin zur Einrichtung benötigt - zum Beispiel
könnte ein serieller Port zur Verbindung mit einem externen Gerät vorbereitet, Dateien geöffnet oder Variablen
initialisiert werden.

Die eigene ``__init__``-Methode **muss** ``super().__init__()`` aufrufen, damit die von ``SmartPlugin`` intern
benötigten Strukturen (u.a. für die Item-Verwaltung, siehe unten) korrekt pro Instanz angelegt werden - wird das
vergessen, teilen sich versehentlich alle Instanzen des Plugins dieselben Strukturen.

Auf die Parameter aus ``etc/plugin.yaml`` wird über ``self.get_parameter_value(parametername)`` zugegriffen. Für
den (in den meisten Fällen nicht mehr benötigten) direkten Zugriff auf das SmartHomeNG-Objekt steht
``self.get_sh()`` zur Verfügung.

.. literalinclude:: /dev/sample_plugin/__init__.py
    :language: python
    :start-after: def __init__(self, sh=None, **kwargs):
    :end-before: def run(self):


----

.. code-block:: python

    def run(self):


Die ``run``-Funktion wird einmalig aufgerufen, wenn SmartHomeNG startet - zu diesem Zeitpunkt sind die Items bereits
geladen und ``parse_item()`` wurde bereits für jedes Item aufgerufen. Die Variable ``self.alive`` muss hier auf
``True`` gesetzt werden (Ausnahme: bei Nutzung von asyncio wird ``self.alive`` von der Coroutine selbst gesetzt).

.. literalinclude:: /dev/sample_plugin/__init__.py
    :language: python
    :start-after: def run(self):
    :end-before: def stop(self):


----

.. code-block:: python

    def stop(self):


Diese Routine wird aufgerufen, wenn SmartHomeNG beendet wird oder das Plugin neu geladen wird (siehe ``deinit()``
weiter unten). Hier müssen alle Verbindungen und Threads beendet werden, die das Plugin gestartet hat. Die Variable
``self.alive`` muss auf ``False`` gesetzt werden.

Wenn ``self.alive`` auf ``False`` gesetzt ist, sollte das Plugin Änderungen an Items nicht mehr weitergeben und
auch keine Daten empfangen und in Items sichern.

.. literalinclude:: /dev/sample_plugin/__init__.py
    :language: python
    :start-after: def stop(self):
    :end-before: def parse_item(self, item):


----

.. code-block:: python

    def parse_item(self, item):


Diese Funktion wird während des Starts für jedes Item einmal aufgerufen, wenn SmartHomeNG die Item-Konfiguration
liest - und danach jedes Mal, wenn zur Laufzeit ein neues Item angelegt wird (dynamische Item-Verwaltung, siehe
Abschnitt `Item-Verwaltung`_ weiter unten). Hier wird geprüft, ob das Item für dieses Plugin relevant ist,
üblicherweise über ein plugin-eigenes Item-Attribut, das über ``self.has_iattr(item.conf, 'attributname')`` geprüft
wird.

Ist das Item relevant, **muss** es über ``self.add_item(item, ...)`` beim Plugin registriert werden. Soll das
Plugin außerdem über Änderungen des Items informiert werden, wird zusätzlich die Methode ``update_item``
zurückgegeben; diese wird dann von SmartHomeNG jedes Mal aufgerufen, wenn sich der Wert des Items ändert.

.. literalinclude:: /dev/sample_plugin/__init__.py
    :language: python
    :start-after: def parse_item(self, item):
    :end-before: def parse_logic(self, logic):


----

.. code-block:: python

    def parse_logic(self, logic):


Diese Funktion wird beim Systemstart für jede Logik aufgerufen. Hier kann geprüft werden, ob ein plugin-spezifischer
Parameter in der Logik-Konfiguration gesetzt ist. Soll das Plugin über die Ausführung der Logik informiert werden,
wird eine selbst gewählte Callback-Methode zurückgegeben - im Beispiel unten heißt sie ``run_logic``. Das ist
**kein** reservierter Methodenname von ``SmartPlugin``, sondern frei wählbar, genau wie ``update_item`` bei
``parse_item()``. Diese Methode wird dann bei Ausführung der Logik aufgerufen, mit denselben Parametern wie
``update_item()``.

.. literalinclude:: /dev/sample_plugin/__init__.py
    :language: python
    :start-after: def parse_logic(self, logic):
    :end-before: def update_item(self, item, caller=None, source=None, dest=None):


----

.. code-block:: python

    def update_item(self, item, caller=None, source=None, dest=None):


Diese Funktion wird jedes Mal aufgerufen, wenn sich der Wert eines Items ändert, für das der Aufruf in
``parse_item()`` eingerichtet wurde. Sie erhält die folgenden Parameter:

`caller`
    Dieser String gibt an, wer das Item geändert hat, z.B. der Name eines anderen Plugins.

`source`
    Optionale, genauere Angabe zur Quelle der Änderung.

`dest`
    Optionales Ziel der Änderung.

Um eine Rückkopplungsschleife zu vermeiden, sollte der neue Wert nur dann an das Gerät weitergegeben werden, wenn
das Plugin läuft (``self.alive``) und die Änderung nicht von diesem Plugin selbst ausgelöst wurde
(``caller != self.get_fullname()``).

.. literalinclude:: /dev/sample_plugin/__init__.py
    :language: python
    :start-after: def update_item(self, item, caller=None, source=None, dest=None):
    :end-before: def poll_device(self):


----

.. _`Item-Verwaltung`:

Item-Verwaltung: add_item, remove_item, parse_item/unparse_item, init/deinit
------------------------------------------------------------------------------

SmartHomeNG unterstützt dynamische Item-Verwaltung: Items können zur Laufzeit angelegt, geändert oder gelöscht
werden, und Plugins können neu geladen werden, ohne dass SmartHomeNG neu gestartet werden muss. Damit das
funktioniert, muss ein Plugin seine Item-Zuordnungen sauber auf- und wieder abbauen können. Dafür gibt es folgende,
zueinander passende Methodenpaare.

``add_item`` / ``remove_item``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Diese beiden Methoden sind in ``SmartPlugin`` bereits vollständig implementiert und **dürfen nicht überschrieben
werden**. ``add_item(item, config_data_dict=None, mapping=None, updating=False)`` wird aus ``parse_item()`` heraus
aufgerufen, um ein Item mit seinen plugin-spezifischen Konfigurationsdaten zu registrieren - danach ist das Item
z.B. über ``self.get_item_list()`` auffindbar. ``remove_item(item)`` macht das rückgängig; es wird automatisch von
``deinit()`` aufgerufen (siehe unten) und muss **nicht** selbst aufgerufen werden.

``parse_item`` / ``unparse_item``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``unparse_item(item)`` ist das symmetrische Gegenstück zu ``parse_item()`` und wird automatisch von
``remove_item()`` aufgerufen, wenn ein Item entfernt wird (z.B. weil es aus der Konfiguration gelöscht wurde oder
das Plugin neu geladen wird).

Ruft ``parse_item()`` für ein Item **nur** ``self.add_item(...)`` auf (wie im Beispielplugin oben), muss
``unparse_item()`` **nicht** implementiert werden - die Standardimplementierung tut nichts, und die von
``add_item()`` angelegte Buchführung wird bereits automatisch durch ``remove_item()`` aufgeräumt:

.. literalinclude:: /libsrc/model/smartplugin.py
    :language: python
    :start-after: def unparse_item(self, item) -> None:
    :end-before: def get_configname(self) -> str:

Führt ``parse_item()`` darüber hinaus eigene Buchführung durch - z.B. wird das Item zusätzlich in eine eigene
Liste oder ein eigenes Dictionary des Plugins eingetragen - **muss** ``unparse_item()`` überschrieben werden, um
diesen Eintrag beim Entfernen des Items wieder zu löschen.

``__init__`` / ``deinit``
~~~~~~~~~~~~~~~~~~~~~~~~~~

``deinit()`` ist das Gegenstück zu ``__init__()`` bzw. ``run()``/``stop()`` und wird aufgerufen, kurz bevor ein
Plugin entladen wird (z.B. beim Neuladen des Plugins über die AdminUI). Die Standardimplementierung stoppt das
Plugin, falls es noch läuft, und entfernt alle registrierten Items über ``remove_item()``:

.. literalinclude:: /libsrc/model/smartplugin.py
    :language: python
    :start-after: def deinit(self, items: list | None = None) -> None:
    :end-before: ###############################################################################

Reicht diese Standardimplementierung nicht aus - etwa weil ``__init__()`` oder ``run()`` dauerhafte Strukturen
angelegt haben (z.B. eigene Threads, Prozesse oder Verbindungen, die über das hinausgehen, was ``stop()`` bereits
abbaut) - muss ``deinit()`` überschrieben werden, um diese vor dem Entladen sauber zu beenden. Der eigene Code
sollte dann zusätzlich ``super().deinit()`` aufrufen (oder den obigen Code sinngemäß nachbilden), damit
Plugin-Stop und Item-Abmeldung weiterhin passieren.

Das Beispielplugin oben implementiert weder ``unparse_item()`` noch ``deinit()`` - beides ist hier nicht nötig, da
``parse_item()`` nur ``add_item()`` nutzt und ``__init__()``/``run()`` keine über ``stop()`` hinausgehenden
dauerhaften Strukturen anlegen.


----

Erstellung eines Webinterfaces
------------------------------

Die Datei ``dev/sample_plugin/webif/templates/index.html`` sollte als Grundlage für Webinterfaces genutzt werden.
Um Tabelleninhalte nach Spalten filtern und sortieren zu können, muss der entsprechende Code Block mit Referenz
auf die relevante Table ID eingefügt werden (siehe Doku).

SmartHomeNG liefert eine Reihe Komponenten von Drittherstellern mit, die für die Gestaltung des Webinterfaces
genutzt werden können. Erweiterungen dieser Komponenten usw. finden sich im Ordner ``/modules/http/webif/gstatic``.

Wenn das Plugin darüber hinaus noch Komponenten benötigt, werden diese im Ordner ``webif/static`` des Plugins abgelegt.


Neben diesen vordefinierten Funktionen können auch eigene Funktionen erstellt werden, die Funktionen im Plugin ausführen.


Funktionen von SmartHomeNG
==========================


Der Scheduler
-------------

Der Scheduler ist eine der wichtigsten Komponenten von SmartHomeNG.
Es ist die zentrale Uhr, die Funktionen zu bestimmten Zeiten aufruft.
Damit eigene Funktionen ausgeführt werden, müssen diese dem Scheduler bekannt gemacht werden.
Dies erfolgt durch den Aufruf spezieller Funktionen, die ``SmartPlugin`` bereitstellt (``self.scheduler_add()``
usw.) - ein direkter Zugriff auf den Scheduler von SmartHomeNG ist dafür nicht nötig.

Die wichtigste Funktion ist `add`:

`scheduler_add`
~~~~~~~~~~~~~~~

.. code-block:: python

    self.scheduler_add('name',
                       obj,
                       prio=3,
                       cron=None,
                       cycle=None,
                       value=None,
                       offset=None,
                       next=None)


``scheduler_add`` fügt dem Scheduler einen Eintrag hinzu. Es müssen mindestens ``name``,
``object`` und einer der Timing-Parameter übergeben werden.


`name=string`
^^^^^^^^^^^^^
Das ist der Name, der diesem Scheduler-Eintrag gegeben wird. Er wird benötigt, um den Scheduler-Eintrag zu verändern oder zu löschen.


`obj=function`
^^^^^^^^^^^^^^
``obj`` ist eine Funktion, die im Plugin definiert wird (ein sogenannter Callback).
Diese Funktion wird vom Scheduler aufgerufen. Wenn die Funktion Parameter benötigt,
können diese mit ``**kwargs`` übergeben werden (siehe weiter unten in der Beschreibung der Parameter).


`cron=string`
^^^^^^^^^^^^^

Der Parameter für ``cron`` ist ein String im SmartHomeNG spezifischen crontab Format. Siehe :ref:`Dokumentation zu Crontab<crontab>`
Damit wird der Scheduler angewiesen, die Funktion ``obj`` entsprechend oft aufzurufen.

`cycle=int`
^^^^^^^^^^^

``cycle`` ist eine Ganzzahl in Sekunden. Damit wird der Scheduler angewiesen,
die Funktion ``obj`` alle ``cycle`` Sekunden aufzurufen.
Wenn das Intervall auf 60 gesetzt wird, ruft der Scheduler die Funktion alle 60 Sekunden auf, so lange SmartHomeNG läuft.

`next=dateobject`
^^^^^^^^^^^^^^^^^
``next`` fordert die einmalige Ausführung von ``obj`` zu dem Zeitpunkt an, der als Argument übergeben wird.
Das Argument ist ein ``dateobject``, das z.B. mit ``datetime`` erstellt werden kann:

.. code-block:: python

    nd = datetime.strptime('Jan 14 2015 8:09PM','%b %d %Y %I:%M%p').replace(tzinfo=self.shtime.tzinfo())


.. important ::
   Die Zeitzone muss im ``datetime``-Objekt mit angegeben werden, ansonsten kann der Scheduler abstürzen. Im Beispiel wird die Zeitzone von SmartHomeNG benutzt.

`value`
^^^^^^^

Mit dem Parameter ``value`` können Argumente an die Funktion ``obj`` übergeben werden, wenn der Scheduler sie aufruft. Dies ist eine Liste von `keyword=value`-Wertpaaren. Diese können wie folgt definiert werden:

.. code-block:: python

    _bla(self, **kwargs):
        if 'heinz' in kwargs:
            logger.info("found")
            em = kwargs['heinz']


In dem Fall sollte der Scheduler mit einer Werteliste aufgerufen werden:

.. code-block:: python

    self.scheduler_add('name',
                        self._bla,
                        value={'heinz': bla, 'tom': 10},
                        next=_ndate)


..warning::

   Werte können über den Scheduler nur weitergegeben werden, wenn dieser mit dem Parameter ``next`` für eine einmalige Ausführung aufgerufen wird. Für eine periodische Ausführung können keine Argumente übergeben werden.

`offset=int`
^^^^^^^^^^^^
Wenn eine periodische Ausführung mit ``cycle`` angefordert wurde, wird die erste Ausführung um ``offset`` Sekunden verzögert. Wenn z.B. ein `cycle=10` und `offset=20` gesetzt wurde, dann wird die erste Ausführung 20 Sekunden nach Abschluss der Initialisierung erfolgen und jede weitere jeweils 10 Sekunden später.

Wenn ``offset`` nicht definiert oder auf 0 gesetzt wird, legt SmartHomeNG einen Zufallswert zwischen 10 und 15 Sekunden fest.


`scheduler_remove`
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    self.scheduler_remove(name)


Diese Funktion löscht den mit ``name`` bezeichneten Eintrag aus dem Scheduler.

`Name=string`
^^^^^^^^^^^^^
Der Name der Schedulereintrags als String.


Items suchen
------------

.. code-block:: python

    from lib.item import Items
    items = Items.get_instance()

    items.return_item(item_path)


``return_item`` gibt das Item mit dem Pfad ``item_path`` zurück. Innerhalb einer Logik ist das ``items``-Objekt
bereits initialisiert und kann direkt genutzt werden.

`item_path=string`
~~~~~~~~~~~~~~~~~~
Der Pfad des Items, wie er in der Item Konfiguration festgelegt ist, z.B. Ebene1.Raum4.Lampe2
Die Funktion gibt das Item-Objekt zurück, welches aufgerufen werden kann,
um den Wert zu lesen oder zu ändern oder auf andere Eigenschaften zuzugreifen.


Items verändern
---------------

.. code-block:: python

    item(value, caller)


`value`
~~~~~~~

Der Wert, der dem Item zugewiesen werden soll. Für boolesche Items ist dies ``True`` oder ``False``.

`caller=string`
~~~~~~~~~~~~~~~
Ein selbst gewählter Name, der denjenigen identifiziert, der das Item verändert hat. Dieses Argument wird an die Funktion ``update_item`` übergeben.

