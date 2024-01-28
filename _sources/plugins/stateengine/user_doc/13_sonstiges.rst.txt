
.. index:: Stateengine; Sonstiges
.. _Sonstiges:

=========
Sonstiges
=========

Einbinden anderer Zustände
--------------------------

**se_use (optional):**
*Einbinden einer weiteren Zustandskonfiguration*

.. code-block:: yaml

    se_use: <Zustandsitem> # z.B. stateengine_defaults.state_suspend.rules.suspend

Seit Version 1.8 wird se_use gleich behandelt wie andere Plugin spezifische Attribute mit Wertzuweisung.
Dadurch ist es nicht nur möglich, eine Liste von einzubindenden Zuständen zu deklarieren,
sondern auch auf die verschiedenen Schlüsselwörter zurückzugreifen:

- item:<Itempfad> liest den Wert aus gegebenem Item aus und nutzt diesen als Zustandserweiterung. Es ist möglich,
  mehrere Zustände als Liste im Item zu deklarieren, indem entweder ein Item mit Typ "list" referenziert wird
  oder mehrere Einträge in einem "str" Item durch ein Komma getrennt angegeben werden.
- eval:<Ausdruck> ermöglicht das dynamische Erweitern des Zustands, z.B. abhängig von einem vorigen Zustand, etc.
- value:<Itempfad> sucht das angegebene Item und bindet dieses ein. Der Wert kann auch als
  relativer Pfad angegeben werden. Hierbei ist zu beachten, dass die relative Adressierung
  vom StateEngine Item selbst aus, also vom rules-Item gesucht wird! Daher reicht in der Regel
  ein einzelner Punkt vor dem Namen des Zustands.
- struct:<structname> ermögicht den Zugriff auf Structs, die entweder selbst oder durch irgendein Plugin bereit gestellt werden

Wird se_use über ein Item oder einen Eval-Ausdruck definiert, wird bei jedem Durchlauf der Zustand neu eingelesen bzw.
neu aufgebaut. So können Zustände dynamisch zur Laufzeit erweitert und geändert werden.

Beinhaltet ein verknüpfter State ebenfalls ein se_use Attribut, werden auch die weiteren Zustände mit eingebunden.
Je "tiefer" eine Deklaration steckt, desto geringer ist ihre Priorität.
Heißt, etwaige Zustandseinstellungen im eigentlichen Item erweitern und
überschreiben Einstellungen, die mit se_use eingebunden wurden.

Weitere Details sind unter :ref:`Zustand-Templates` zu finden.


Neukonfiguration der Hierarchie
-------------------------------

**se_stateorder (optional):**
*Festlegen der Reihenfolge eines Status in der Hierarchiefolge*

Dieses Attribut ermöglicht es, die hierarchische Reihenfolge, die sich ursprünglich
aus der YAML Datei ergibt, anzupassen. Dies kann durch folgende Schlüsselwörter geschehen:

- item:<Itempfad> liest den Wert aus gegebenem Item aus. Das Item sollte einen integer Wert beinhalten.
- eval:<Ausdruck> ermöglicht die hierarchische Neuordnung mittels Eval-Ausdruck
- value:<Itempfad> Angabe der hierarchischen Position durch Angabe eines Integer-Werts (min. 0)


Auflösen von Zuständen
----------------------

**se_releasedby (optional):**
*Definieren von Zuständen, die den aktuellen Zustand auflösen können, auch wenn sie untergeordnet sind*

Das Attribut ermöglicht es, andere untergeordnete Zustände
zu definieren, die den Zustand auflösen, sobald jene
eingenommen werden könnten. Gewünscht wird dies normalerweise beim
Suspendzustand, allerdings kann das Attribut bei jedem
beliebigem Zustand genutzt werden. Seit Version 2.0 wird se_released_by gleich
behandelt wie andere Plugin spezifische Attribute mit Wertzuweisung, es können
also alle gültigen Schlüsselwörter und auch Listenangaben in Items genutzt werden.
Außerdem wurde in der Pluginversion 2.0 das released_by Feature komplett überarbeitet,
sodass es nun zuverlässig funktionieren sollte ;)

Ein Zustand mit diesem Attribut wird aufgelöst, also
(vorerst) nicht mehr eingenommen, sobald ein mit dem
Attribut angegebener Zustand eingenommen werden könnte.
Befindet sich in der Hierarchie noch ein weiterer übergeordneter Zustand,
dessen Bedingungen erfüllt werden, wird eben dieser Zustand
eingenommen - auch wenn er den ursprünglichen Zustand nicht aufgelöst hat.

Bei einer relativen Angabe eines Zustands/Items ist
darauf zu achten, dass hier nicht relativ vom rules
Item aus gesucht wird (wie sonst üblich), sondern relativ
zum Zustandsitem. Es reicht also ein einzelner Punkt vor dem Namen des Zustandes.

Ein Beispiel:
Der in der Hierarchie ganz oben (unter lock und release)
angesiedelte Suspendmodus hat das Attribut definiert:

.. code-block:: yaml

    struct: stateengine.state_suspend

    rules:
      suspend:
        se_releasedby: .Nacht

      Nacht:
        enter:
          <Bedingungen>

Angenommen, aktuell ist der Zustand "Nacht" aktiv. Es wird nun ein
Schalter betätigt, der den übergeordneten Suspendzustand aktiviert.
Die Stateengine wechselt nun in den Suspendmodus.

Und bleibt auch dort, selbst wenn es noch Nacht ist.
Werden beim nächsten Check die Bedingungen für den
Nachzustand nicht mehr erfüllt, passiert nach wie vor
nichts, da ja der Suspendzustand ohnehin übergeordnet
ist. Intern wird der Zustand allerdings nach einer Aktualisierung
der released_by Einträge (z.B. wenn sie durch Items oder evals definiert
sind) eine Position über den "Suspend" Zustand kopiert.

Sind bei einem späteren Check der Zustände
die Bedingungen aus einem Bedingungsset für "Nacht" alle wahr,
wird der Suspendmodus aufgelöst. Die Leave-Aktionen werden ausgeführt,
der intern kopierte Zustand und alle anderen released_by Zustände werden
aus der Hierarchie gelöscht und der nächste mögliche Zustand in der Hierarchie
wird nach einer neuen Evaluierung eingenommen.
Im obigen Beispiel wäre das der Nacht-Zustand.

Zustandsnamen
-------------

**name (optional):**
*Name des Zustands*

Der Name des Zustands wird im Protokoll sowie als Wert für das
über ``se_laststate_item_name`` angegebene Item verwendet. Wenn
kein Name angegeben ist, wird hier die Id des
Zustands-Items verwendet.

**se_name:**
*Überschreiben des Namens des Zustands*

Über das Attribut ``se_name`` kann der im Attribut ``name`` angegebene Wert
überschrieben werden, beispielsweise mittels ``eval:sh.eine_funktion()``.
Dies kann beispielsweise nützlich sein, um den Namen abhängig von einer Bedingungsgruppe
zu ändern. Ist also z.B. der Zustand auf Grund der Temperatur eingenommen worden,
könnte der Name auf "Zustand (Temp)" geändert werden. Ist der Zustand aufgrund
der Helligkeitsbedingung aktiv, könnte der Name auf "Zustand (Hell)" geändert werden.

CLI
---

Im CLI Plugin können folgende zwei Befehle zu Debuggingzwecken eingesetzt werden:

**se_list**
*Zeigt eine Liste der Regelwerk-Items, für die das stateengine-Plugin aktiv ist*

**se_detail <Id eines Regelwerk-Items>**
*Zeigt Details zum Objekt Item*
