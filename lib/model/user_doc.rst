SmartPlugin - Modifikation
==========================

Ziel der Änderungen ist es,

-   das Starten und Stoppen von Plugins,
-   (dazu) das Parsen (binden) und “Unparsen” (lösen) von Items zum
    Plugin

zu ermöglichen. Sofern das Plugin die notwendigen Konventionen einhält,
kann es im Betrieb gestoppt und wieder gestartet werden sowie Items neu
laden bzw. entfernen, die zur Laufzeit angelegt, geändert oder entfernt
wurden.

Überlegungen
------------

Die bisherige Struktur bzw. Implementierung der meisten Plugins ist
nicht darauf ausgerichtet, Plugins nach dem Stoppen wieder zu starten.
Das liegt zum Einen daran, wie Initialisierung und “Aufräumen”
strukturiert sind (teilweise Initialisierung in ``run()``, Anhalten und
Aufräumen sind in ``stop()`` zusammengefasst); zum Anderen daran, dass
Initialisierung möglicherweise erneut durchlaufen werden muss,
spätestens dann, wenn sich Items oder Konfigurationsparameter des
Plugins geändert haben.

Zur vorbereitenden Initialisierung gehören z.B.

-   Lesen der Konfiguration
-   Vorbereiten von Verbindungen (nicht: Herstellen/Öffnen!)
-   Parsen und Binden von Items
-   ggf. Initialisieren von Items / Feldern
-   Einrichten von Schedulern (sofern Einrichten/Starten getrennt möglich
    ist)

Zum Startvorgang gehören z.B.

-   Öffnen von Verbindungen
-   Starten von Schedulern
-   ggf. Starten zusätzlicher Threads

Analog muss auch der Stop-Prozess geteilt werden. Zum Anhalten des
Plugins gehören u.a.

-   Schließen von Verbindungen
-   Stoppen von Schedulern
-   ggf. Stoppen zusätzlicher Threads

Zum Herunterfahren sollten dann noch folgende Aktionen gehören:

-   Unparsen / Lösen von Items
-   Löschen von Schedulern (s.o.)

Die letzten beiden Punkte sind für den bisherigen Betrieb irrelevant, da
shng bzw. Python diese beim Beenden von shng automatisch durchführt bzw.
diese durch das Beenden des Programms nicht erforderlich sind. Wenn aber
ein echter Neustart eines Plugins, z.B. nach dem Neuanlegen oder Ändern
von Items oder ggf. sogar Änderungen am Programmcode gewünscht wird,
dann müssen diese Funktionen getrennt verfügbar und ausführbar gemacht
werden.

Implementierung
~~~~~~~~~~~~~~~

Die vorgeschlagenen Änderungen ermöglichen die Deinitialisierung als
Gegenstück zur Initialisierung in ``__init__()``. Die Methode
``deinit()`` hält - falls noch nicht geschehen - das Plugin an und löst
alle gebundenen Items (s.u.).

Um die Nutzung in - auch bestehenden - Plugins zu vereinfachen, werden
die Änderungen an der Klasse ``smartplugin`` als Basisklasse von Plugins
umgesetzt. Dabei muss darauf geachtet werden, so wenig wie möglich
“breaking changes” zu produzieren.

Anpassung von Plugins
~~~~~~~~~~~~~~~~~~~~~

Sofern die Neuerungen nicht genutzt werden (sollen), sind die Änderungen
im Idealfall rückwärtskompatibel. Durch Anpassung des Plugins an die
Änderungen sollten die Aktivierung/Nutzung der neuen Funktionen mit
vergleichsweise geringem Aufwand möglich werden:

-   ``__init__()`` anpassen und ``deinit()`` überschreiben
-   ``run()`` und ``stop()`` anpassen
-   Plugin auf Nutzung der neuen Felder anpassen

Binden / Lösen von Items
------------------------

Plugins bekommen von der ``items``-Klasse alle Items an ``parse_item()``
übergeben, damit sie prüfen können, ob das jeweilige Item für sie
relevant ist. Falls ja, kann das Item in einer Plugin-internen Liste
gespeichert werden, um darauf zuzugreifen. Wenn Änderungen am Item
automatisch an das Plugin übergeben werden sollen, kann z.B. ein Verweis
auf ``update_item()`` als Update-Trigger zurückgegeben werden. Diesen
Prozess bezeichne ich im Folgenden als “Binden” (sowohl das interne
Speichern als auch das Registrieren in der ``item``-Klasse per
Update-Trigger).

Bisher meist nicht implementiert ist der umgekehrte Prozess des
“Lösens”, das Entfernen aus den internen Listen oder das
“Unregistrieren” des Update-Triggers.

Es ist offensichtlich, dass für dynamisch änderbare Items diese Prozesse
beide zur Laufzeit (ggf. mehrmals) durchlaufen werden können müssen.

.. _implementierung-1:

Implementierung
~~~~~~~~~~~~~~~

Die vorgeschlagenen Änderungen ermöglichen das Lösen/“Unparsing” von
Items als Gegenstück zum Parsen in ``parse_item()``. So wie
``parse_item()`` prüft, ob das Item im Plugin verwendet werden kann/soll
und den Update-Trigger ``update_item()`` zurückgibt, löscht
``unparse_item()`` die Update-Verknüpfung und entfernt das Item aus den
plugin-internen Listen/Feldern.

Konventionen
------------

Um Klarheit und Verständlichkeit zu fördern, werden die folgenden
Konventionen genutzt:

(TODO: Ich hoffe, ich habe sie selber überall eingehalten… prüfen!)

-   ``item`` bezeichnet ein Objekt der ``class Item()``
-   ``item_path`` bezeichnet einen String mit dem Item-Pfad (ehemals
    item_id)
-   ``items`` bezeichnet eine Liste mit ``class Item()``-Objekten
-   ``item_dict`` bezeichnet ein dict, das item_path als Schlüssel
    verwendet

Beschreibung der Änderungen
===========================

Felder
------

-   ``_plg_item_dict``:

    Schon länger gab es im SmartPlugin ein Feld ``_itemlist``, das
    rudimentär von der Plugins-Klasse unterstützt wurde. Dieser Ansatz
    wird ausgebaut:

    Es gibt - neu - im SmartPlugin ein dict ``_plg_item_dict``, in dem
    alle dem Plugin zugeordneten Items und deren (pluginspezifischen)
    Konfiguration vorgehalten werden:

.. code:: python

       self._plg_item_dict[item.path()] = {
           'item': item,               # das Item (Objektreferenz)
           'is_updating': True,        # wurde das Item in shng über update_item registriert?
           'mapping': mapping,         # ggf. "Aktionsbezeichner" für das Item
           'config_data': {}           # dict mit Item-spezifischen Konfigurationsdaten
       }

-   ``_item_lookup_dict``:

    Es gibt weiterhin ein “Rückwärtssuch”-dict ``_item_lookup_dict``, in
    dem die Items nach ihren jeweiligen ``mappings`` gelistet
    werden:

.. code:: python

       self._item_lookup_dict[mapping] = [item1, item2, ...]

    Damit wird ein schneller Zugriff auf die entsprechenden Items
    möglich, wenn ``mapping`` aktiviert wird (üblicherweise über
    ein durch das Plugin verwaltetes Gerät/Netzwerkverbindung).

Methoden
--------

-   ``__init__()``:

    unverändert, muss aber ggf. auf die neuen Felder angepasst werden.

-   ``deinit()``:

    Das neue Gegenstück zu ``__init__()``. Standardmäßig wird - sofern
    noch nicht geschehen - das Plugin per ``stop()`` angehalten. Danach
    werden alle Items aus ``_plg_item_dict`` durch Aufruf von
    ``remove_item(item)`` gelöst.

-   ``add_item()``:

    Ehemals ``_append_to_itemlist``. Das übergebene Item wird in
    ``_plg_item_dict`` eingetragen, und falls ein ``mapping``
    übergeben wurde, wird ``_item_lookup_dict`` ebenfalls ergänzt.

    Diese Methode muss in ``parse_item()`` aufgerufen werden, wenn das
    Item im Plugin genutzt werden soll. (“Muss” nicht, aber sollte, um
    die Konventionen einzuhalten und die neuen Funktionen fehlerfrei
    nutzen zu können…)

    Weiterhin wird diese Methode (erneut) durch das Item selbst
    aufgerufen, wenn ``parse_item`` eine Triggermethode (``update_item``)
    zurückgibt. In dem Fall wird ``register_updating`` aufgerufen, um die
    entsprechenden Eintragungen in ``_plg_item_dict`` vorzunehmen.

-   ``remove_item()``:

    Das Gegenstück zu ``add_item()``, das übergebene Item wird aus den
    internen Listen entfernt. Zusätzlich wird ``unparse_item()``
    aufgerufen, um ggf. gesetzte Update-Trigger zu löschen.

    Diese Methode wird automatisch für alle Items von ``deinit()``
    aufgerufen.

-   ``register_updating()``:

    Setzt im ``_plg_item_dict`` das Flag für Updates (“``is_updating``”).
    Falls das Item noch nicht registriert ist, wird vorher automatisch
    ``add_item(item)`` aufgerufen.

-   ``unparse_item()``:

    Löscht den Update-Trigger im Item-Objekt. Wird durch
    ``remove_item()`` aufgerufen.

-   verschiedene Getter-Methoden (``get_items()``,
    ``get_trigger_items()``, ``get_items_for_mapping()``,
    ``get_item_path_list()``):

    Geben Listen von Items bzw. Item-Pfaden zurück.

    ``get_items()`` und ``get_item_path_list()`` können optional gefiltert werden.
    Das Filtern geschieht über einen anzugebenen filter_key des config_data_dicts und einen anzugebenen filter_value.
    Wenn filter_key und filter_value angegeben sind, wird ein Item nur in die Ergebnisliste eingeschlossen,
    wenn der value im config_data_dict zu dem angegebenen filter_key dem filter_value entspricht.


TODO
====

Die bisher beschriebenen Methoden und Felder sind - nach meinem
Dafürhalten - fertig implementiert, bedürfen aber noch der Überprüfung
und ggf. Anpassung, wenn einzelne Funktionen anders umgesetzt werden
sollen.

Wenn ein Plugin auf Basis der neuen ``SmartPlugin``-Klasse erstellt
wurde, sollte es starten und stoppen können und zusätzlich im Betrieb
Items neu laden (stoppen - deinitialisieren - initialisieren - starten).

Nicht berücksichtigt sind die Fragen,

-   wie Items dynamisch angelegt / geändert werden
-   ob / wie geänderte Items in den Konfigurationsdateien gesichert
    werden (können),
-   ob geänderte Plugin-Konfiguration in den Konfigurationsdateien
    gesichert werden (können),
-   ob man Plugin “inaktiv”/“aktiv” schalten können soll,

Weiteres Vorgehen (meine Idee)
------------------------------

-   Anpassung erster Plugins, Teste, ggf. Korrekturen
-   Anpassung weiterer Plugins, idealerweise durch deren Autoren, Teste,
    ggf. Korrekturen
-   noch mehr Teste
-   Übernahme in master, Release
