
.. index:: Items; plugin-spezifische Attribute
.. index:: plugin-spezifische Attribute

.. role:: redsup
.. role:: bluesup

Plugin-spezifische Attribute
============================


In SmartHomeNG werden außer den Standard Attributen weiter Attribute unterstützt, die von Plugins
implementiert werden. Wenn das Plugin, welches diese Attribute implementiert nicht geladen ist,
haben die konfigurierten Werte keine Auswirkung auf die Funktion von SmartHomeNG.

Um diese Attribute leichter den Plugins zuordnen zu können, beginnen die
Attributnamen normalerweise mit einem Kürzel, welches das Plugin kennzeichnet, gefolgt von einem
Unterstrich ('_').

Beispiele für Kürzel, die kennzeichnen zu welchem Plugin die jeweiligen Attribute gehören sind:

+-----------------+------------------+-----------------------------------------------------------+
| **Kürzel**      | **Plugin**       | **Attribut-Beispiele**                                    |
+=================+==================+===========================================================+
| knx\_           | knx              | knx_dpt, knx_cache, knx_listen, knx_send                  |
+-----------------+------------------+-----------------------------------------------------------+
| hm\_            | homematic        | hm_address, hm_function                                   |
+-----------------+------------------+-----------------------------------------------------------+
| sv\_            | visu_smartvisu   | sv_page, sv_img, sv_nav_aside, sv_nav_aside2, sv_widget   |
+-----------------+------------------+-----------------------------------------------------------+
| hue\_           | hue              | hue_lamp_id, hue_lamp_type, hue_listen, hue_send          |
+-----------------+------------------+-----------------------------------------------------------+
| avm\_           | avm              | avm_data_type, avm_identifier                             |
+-----------------+------------------+-----------------------------------------------------------+
| enigma2\_       | enigma2          | enigma2_data_type, enigma2_page                           |
+-----------------+------------------+-----------------------------------------------------------+


.. index:: Vererbung von Attributen
.. index:: Items; Vererbung von Attributen

Vererbung von Attributen :bluesup:`update`
------------------------------------------

Bei einigen Plugins ist es notwendig, bei jedem Item einen Identifier anzugeben. Beispiele sind das
homematic Plugin und das hue Plugin. Hier ist es hilfreich, den Identifier (z.B. die **hm_address**
oder die **hue_lamp_id**) nur an einer Stelle konfigurieren zu müssen.

Das hue Plugin hat eine Vererbung der hue_lamp_id von übergeordneten Items im Plugin implementiert,
indem das Plugin immer prüft, ob das Attribut in übergeordneten Items definiert wurde.

Ab der Version 1.5 von SmartHomeNG gibt es einen Standardmechanismus der es möglich macht, selektiv
den Wert aus einem übergeordneten Item zu erben. Dieser Mechanismus funktioniert **nur** bei
plugin-spezifischen Attributen. Hierbei kann ein Attribut mit dem Wert eines Attributes eines
übergeordneten Items belegt werden.

Es kann der Wert eines Attributes aus einer übergeordneten Ebene (Eltern / Großeltern / Urgroßeltern)
überommen (geerbt) werden. Dazu wird für das erbende Attribut ein Wert im Format :code:`<Ebene>:<Attribut>`
angegeben.

.. attention::

   Zwischen Ebene und Doppelpunkt, sowie zwischen Doppelpunkt und Attribut dürfen keine Leerzeichen angegeben werden.

Die :code:`<Ebene>` kann die Werte :code:`..` (für das Parent-Item), :code:`...` (für das Grandparent-Item) sowie
:code:`....` (für das Great-Grandparent-Item) annehmen.

Für :code:`<Attribut>` wird ein :code:`.` angegeben, um aus der übergeordneten Ebene das Attribut mit dem
gleichen Namen zu referenzieren.

Um den Wert eines Attributes vom übergeordnetem Item (Parent-Item) zu erben, muss dementsprechend in der
Konfiguration das Attribut mit dem Wert :code:`..:.` konfiguriert werden:

.. code-block:: yaml

   fenstergriff_kueche:
       type: num
       hm_address: OEQ1234567

       sabotage:
          type: bool
          hm_address: ..:.
          hm_function: SABOTAGE

       low_battery:
          type: bool
          hm_address: ..:.
          hm_function: LOW_BAT


In diesem Beispiel sieht man, dass die HomeMatic Adresse des Devices (hm_address) nur einmal angegeben werden
muss. Der Vorteil wird besonders sichtbar, wenn man mehrere Fenstergriffe hat. Dann kann man diesen Block
einfach kopieren und muss nur dem Item einen neuen Namen geben (z.B. fenstergriff_bad) und die
**hm_adress** an einer Stelle abzuändern. Die Vererbung ist auch bei der Erstellung von structs hilfreich, weil
es die spätere Konfiguration des entstehenden Item-Teilbaums vereinfacht.

Um direkt den Wert eines Attributes von dem übergeordnetem Item des Parent-Items (Grandparent-Item)
zu erben, kann in der Konfiguration das Attribut mit dem Wert :code:`...:.` konfiguriert werden.

Die Vererbung ist so implementiert, dass der Attribut Wert während der Initialisierung der Items beim
Start von SmartHomeNG kopiert wird. Im Backend wird in den Item Details des Child-Items also nicht
:code:`..:.` oder :code:`...:.` angezeigt, sondern der kopierte Wert.


.. index:: Zugriff auf Attribute anderer Items
.. index:: Items; Zugriff auf Attribute anderer Items

Zugriff auf Attribute anderer Items :redsup:`neu`
-------------------------------------------------

Der Zugriff auf Attribute anderer Items ist als Erweiterung der Vererbung von Attributen implementiert.
Hierzu muss im aktuellen Item ein Attribut definiert werden, welches den Wert aufnimmt. Es ist hierbei
(wie bei der Vererbung) ist nur ein Zugriff auf Items oberhalb in der Item Hirarchie möglich.

Der Unterschied liegt darin, dass ein Attributname angegeben werden kann.

Um den Wert eines Attributes vom übergeordnetem Item (Parent-Item) zu übernehmen, muss dementsprechend in
der Konfiguration statt dem :code:`.` (für das aktuelle Attribut), ein Attributname angegeben werden
(:code:`<Ebene>:<Attribut>`).

Es ist auch möglich, auf Attribute des aktuellen Items zuzugreifen. Dazu wird für die :code:`<Ebene>` nur
ein :code:`.` (für das aktuelle Item) angegeben (:code:`.:<Attribut>`).


.. index:: Platzhalter in Attributwerten
.. index:: Items; Platzhalter in Attributwerten

Platzhalter in Attributwerten :redsup:`neu`
-------------------------------------------

Ab SmartHomeNG v1.10 ist es möglich in Attributwerten Platzhalter zu verwenden. Diese Platzhalter referenzieren
ein anderes Attribut und werden beim Start von SmartHomeNG durch den entsprechenden Wert ersetzt.

Die Platzhalter sind Attribut-Referenzen, wie sie in den zwei vorangegangenen Abschnitten beschrieben wurden.
Diese Attribut-Referenzen werden in geschweifte Klammern eingeschlossen (:code:`{<Ebene>:<Attribut>}`).

Damit keine Probleme bei Attributwerten entstehen, die zwar geschweifte Klammern enthalten, aber keine Platzhalter,
findet standardmäßig keine Prüfung auf (und die Ersetzung von) Platzhalter(n) statt. Um die Ersetzung zu
aktivieren, muss an den Namen des Attributes ein Unterstrich angefügt werden. Es muss also z.B. statt in
der Konfigurationsdatei :code:`my_attribute: "Text"` zu schreiben, :code:`my_attribute_: "Text {..:my_value}"`
angegeben werden. Im Zuge des Ladens wird beim Ersetzen der Platzhalter der Unterstrich entfernt. Das Attribut
hal zur Laufzeit also den Namen **my_attribute** und nicht (wie man denken könnte) **my_attribute_**.

...

