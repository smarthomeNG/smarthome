
.. index:: Items; Standard-Attribute
.. index:: Standard-Attribute; Übersicht

.. index:: Standard-Attribute; cache
.. index:: cache
.. index:: Standard-Attribute; initial_value
.. index:: initial_value
.. index:: Standard-Attribute; value
.. index:: value
.. index:: Standard-Attribute; log_change
.. index:: log_change
.. index:: Standard-Attribute; name
.. index:: name
.. index:: Standard-Attribute; remark
.. index:: remark
.. index:: Standard-Attribute; threshold
.. index:: threshold


.. role:: bluesup

Standard Attribute
==================


In SmartHomeNG werden eine Reihe von Standard Attributen unterstützt. Diese sind in der folgenden
Liste aufgeführt. Die Bedeutung und Verwendung der Attribute wird auf den folgenden Seiten beschrieben.

Zusätzlich können Plugins eigene Attribute definieren. Die Bedeutung und Verwendung dieser zusätzlichen
plugin-spezifischen Attribute ist in der Dokumentation des jeweiligen Plugins nachzulesen.

+-----------------+----------------------------------------------------------------------------------------+
| **Attribut**    | **Beschreibung**                                                                       |
+=================+========================================================================================+
| autotimer       | setzt den Wert des Items nach einer Zeitspanne auf einen bestimmten Wert.              |
|                 | **Ab SmartHomeNG v1.3** werden die Konfigurationsmöglichkeiten erweitert               |
|                 | (siehe :doc:`autotimer <./autotimer>`).                                                |
+-----------------+----------------------------------------------------------------------------------------+
| cache           | Wenn 'Yes', dann wird der Wert des Items zwischengespeichert und beim                  |
|                 | erneuten Start von SmartHomeNG wird der alte Wert aus dem Zwischenspeicher             |
|                 | geladen (vergleichbar mit dem Permanentspeicher vom HS)                                |
+-----------------+----------------------------------------------------------------------------------------+
| crontab         | Die Evaluierung des Items findet zu angegebenen Zeitpunkten statt (siehe               |
|                 | Beschreibung unten)                                                                    |
+-----------------+----------------------------------------------------------------------------------------+
| cycle           | Definiert ein regelmäßiges Aufrufen des Items (und damit der verknüpften               |
|                 | Logik oder Eval-Funktion). **Ab SmartHomeNG v1.3** werden die                          |
|                 | Konfigurationsmöglichkeiten erweitert (siehe Beschreibung unten).                      |
+-----------------+----------------------------------------------------------------------------------------+
| enforce_updates | Wenn das Attribut auf **True** gesetzt wird, führt jede Wertzuweisung ans Item         |
|                 | dazu, das abhängige Logiken und item Evaluationen getriggert werden, auch              |
|                 | wenn sich der Wert des Items bei der Zuweisung nicht ändert.                           |
+-----------------+----------------------------------------------------------------------------------------+
| enforce_change  | Wenn das Attribut auf **True** gesetzt wird, führt jede Wertzuweisung ans Item         |
|                 | dazu, dass ein Update (keine Wertänderung) wie ein Change verarbeitet wird. Es werden  |
|                 | die Attribute *changed_by*, *last_change*, etc. aktualisiert.                          |
+-----------------+----------------------------------------------------------------------------------------+
| eval            | eval legt einen Ausdruck fest, nach dem der Wert des Items berechnet wird. Mit         |
|                 | eval_trigger wird festgelegt, wann eine (Neu)berechnung erfolgt (siehe Beschreibung    |
|                 | unten)                                                                                 |
+-----------------+----------------------------------------------------------------------------------------+
| eval_trigger    | Liste von Items, bei deren Veränderung eine Neuberechnung der in eval                  |
|                 | definierten Formel erfolgen soll (siehe Beschreibung unten)                            |
+-----------------+----------------------------------------------------------------------------------------+
| initial_value,  | Ein optionaler Startwert für dieses Item. Es wird empfohlen **initial_value**          |
| value           | anstelle des bisherigen Attributnamens **value** zu verwenden.                         |
|                 |                                                                                        |
|                 | **Achtung**: Wenn in den Item Definitionen ein Wertzuweisung zu einem Item             |
|                 | vom Typ **dict** erfolgen soll, muss unbedingt darauf geachtet werden, dass            |
|                 | der angegebene Wert in Anführungszeichen gesetzt wird, damit yaml nicht den            |
|                 | Wert nicht als Datenstruktur interpretiert.                                            |
|                 | (Also folgendermaßen: **initial_value**: "{'k1': 'v1', 'k2': 'v2'}" )                  |
+-----------------+----------------------------------------------------------------------------------------+
| log_change      | Ermöglicht das Loggen jeder Veränderung des Item-Wertes. **log_change** muss           |
|                 | dazu den Namen des zu verwendeten Loggers enthalten. In **logging.yaml**               |
|                 | muss der Logger als **items.<Name>** konfiguriert sein. Wertänderungen des             |
|                 | Items werden dann mit dem Level INFO geloggt. **Ab SmartHomeNG v1.5**                  |
+-----------------+----------------------------------------------------------------------------------------+
| name            | ein optionaler Name für das Item                                                       |
+-----------------+----------------------------------------------------------------------------------------+
| on_update       | Ermöglicht das setzen des Wertes anderer Items, wenn das aktuelle Item ein             |
|                 | Update erhält (auch wenn sich der Wert des aktuellen Items dabei nicht                 |
|                 | ändert). **Ab SmartHomeNG v1.4**                                                       |
+-----------------+----------------------------------------------------------------------------------------+
| on_change       | Ermöglicht das Setzen des Wertes anderer Items, wenn der Wert des aktuellen            |
|                 | Items verändert wird. **Ab SmartHomeNG v1.4**                                          |
+-----------------+----------------------------------------------------------------------------------------+
| remark          | ein optionaler Kommentar für das Item. Es ist sinnvoll Kommentare zu einem             |
|                 | Item als **remark** Attribut zu erfassen und nicht als Kommentar ( **#** )             |
|                 | in die Konfigurationsdatei zu schreiben. Dadurch können Kommentare in einer            |
|                 | später kommenden graphischen Konfigurationsoberfläche angezeigt und gepflegt           |
|                 | werden.                                                                                |
+-----------------+----------------------------------------------------------------------------------------+
| struct          | Mit dem Attribut **struct** kann ein Template für eine Itemstruktur statt              |
|                 | eines einzelnen Items in den Item-Tree eingefügt werden. **struct** kann ein           |
|                 | String oder eine Liste von Strings sein. Wenn eine Liste angegeben wird,               |
|                 | werden die Template Strukturen in der Reihenfolge angewendet, in der sie in            |
|                 | der Liste angegeben wurden. **Ab SmartHomeNG v1.6**                                    |
+-----------------+----------------------------------------------------------------------------------------+
| threshold       | legt einen Schwellwert oder einen Schwellwertbereich fest. Wenn der Wert               |
|                 | diesen Wert über- bzw. unterschreitet oder der Wert Bereich verlässt oder              |
|                 | wieder betritt, kann durch dieses Item eine Logik oder die Berechnung anderer          |
|                 | Items getriggert werden.                                                               |
|                 | Die Angabe des Bereichs erfolgt in Form von zwei numerischen Werten,                   |
|                 | die durch einen Doppelpunkt getrennt werden. (z.B. 21.4:25.0)                          |
|                 | ist. Es kann auch ein einzelner Wert notiert werden.                                   |
+-----------------+----------------------------------------------------------------------------------------+
| type            | Um Werte zu speichern, muss ein Typ vorgegeben werden. Unterstützte Typen              |
|                 | sind bool, num, str, list, dict, foo, scene                                            |
+-----------------+----------------------------------------------------------------------------------------+


.. toctree::
   :maxdepth: 5
   :hidden:

   autotimer
   crontab
   cycle
   enforce_updates
   enforce_change
   eval
   on_update
   struct
   type

