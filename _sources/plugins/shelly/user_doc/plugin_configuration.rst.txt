
Konfiguration des Plugins
=========================

...

Backward-Compatibility Mode
---------------------------

Zurzeit werden folgende Shelly Devices mit Gen1 API im **Backward-Compatibility Mode** unterstützt:

- Shelly1/pm
- Shelly2
- Shelly2.5
- Shelly4Pro
- Shelly Plug
- Shelly PlugS
- Shelly H&T
- Shelly Flood
- Shelly Door/Window 2

Diese Devices werden konfiguriert, wie es bis zur Version 1.2.0 des shelly Plugins üblich war (durch Angabe der
Attribute ``shelly_id``, ``shelly_type`` und ``shelly_attr``). So konfigurierte Items sind im internen Handling
kompatibel zur alten Version des Plugins.

Es werden dabei alle Relays eines Shelly Devices (bis zu 4) unterstützt. Weiterhin werden die folgenden
Attribute/Parameter der Devices unterstützt, soweit die Devices selbst diese unterstützen:

- humidity
- state
- tilt
- vibration
- lux
- illumination
- flood
- battery
- power
- energy
- temperature
- temperature_f

sowie der online-Status.

|

Aktueller Konfigurations Modus
------------------------------

Weitere Gen1 Devices werden unterstützt, wenn sie analog zu Gen2 Devices konfiguriert werden. Dieser Modus ist
für Gen1 Devices noch experimentell.

Devices mit dem Gen2 und Gen3 API werden **ohne** Angabe von ``shelly_type`` konfiguriert. Die Information über den Typ des
Devices erhält das Plugin vom Device.

Es wird eine große Anzahl von Shelly Devices mit Gen3 API unterstützt. Getestet wurden bisher
folgenden Gen3 Devices:

- Shelly Mini1G3

Es wird eine große Anzahl von Shelly Devices mit Gen2 API unterstützt. Getestet wurden bisher
folgenden Gen2 Devices:

- Shelly Plus Plug S
- Shelly Plus H&T
- Shelly Plus 2PM
- Shelly Plus Add-On (getestet am Shelly Plus 2PM)

Es wird Anzahl von Shelly Devices mit Gen1 API im experimentellen Modus (konfiguriert analog zu Gen2 Devices)
unterstützt. Getestet wurden bisher folgenden Gen1 Devices:

- Shelly Plug S
- Shelly Button1
- Shelly Door/Window2


Unterschiede zwischen Plugin Modi
---------------------------------

Das Attribut ``online`` wird durch das Plugin im Modus für Gen2 Devices nicht durchgehend unterstützt. Das Attribut ist
auf den verschiedenen Shelly Devices zu unterschiedlich implementiert, als dass es sinnvoll genutzt werden könnte.
Einige batteriebetriebene Devices melden ``online`` = False bevor sie sich schlafen legen, andere lassen den Status
auf True. Andere Devices hingegen haben den ``online`` Status gar nicht implementiert.

Im **Backward-Compatibility Mode** für Gen1 Devices steht das ``online`` Attribut (falls es im Plugin
v1.20 implementiert war) weiterhin zur Verfügung.


Konfiguration im Kompatibilitäts-Modus
--------------------------------------

Shelly Devices mit Gen1 API können im (experimentellen) neuen Modus konfiguriert werden, oder im Kompatibilitäts-Modus,
der jedoch nur Devices und Attribute unterstützt, die bereits von der Plugin Version 1.2.0 unterstützt wurden.
Im neuen Modus werden zusätzliche Devices und zusätzliche Attribute zu den bereits unterstützten Devices
unterstützt. Die Konfiguration erfolgt dann analog zur Konfiguration von Gen2 Devices.


Konfiguration für Gen2 Devices
------------------------------

Shelly Devices mit Gen2 API und Devicess mit Gen1 API, die nicht im **Backward-Compatibility Mode** unterstützt werden,
können konfiguriert werden, wie im folgenden beschrieben wird.

Für die Devices werden die Attribute

  - ``shelly_id``: Mac Adresse des Devices, mindestens jedoch die letzten 6 Stellen der Mac Adresse
  - ``shelly_attr``: Name des Attributes, welches eingelesen werden soll. (Wenn der Name des Attributes nicht
    bekannt ist, können die von dem Shelly Device unterstützten Attribute, wie im folgenden beschrieben, ermittelt
    werden).
  - und evtl. ``shelly_group``: Optional: Name der Gruppe, zu der dieses Attribut gehört (z.B. "switch:0")

angegeben. Das Attribut ``shelly_type`` darf **NICHT** angegeben werden.


Ermitteln der unterstützten Status Attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Um die Attribute zu ermitteln, die ein Shelly Device sendet (also Attribute, die einen Status des Devices übermitteln),
muss folgendermaßen vorgegangen werden:

- Ein Item konfigurieren, welches nur die folgenden zwei Attribute besitzt:

.. code-block:: yaml

    test_item:
        shelly_id:<MAC Adresse>
        shelly_list_attrs: True

Außerdem muß der Logger **plugins.shelly** auf den Level INFO konfiguriert werden. Anschließend werden dann die
Attribute, wenn sie vom Shelly Device gesendet werden, in das **smarthome-details.log** geschrieben.
Die Logeinträge enthalten den Namen des Attributes, optional den Namen der Gruppe und den Typ, den das SmartHomeNG Item
haben muß. Falls der Typ **num** ist, wird als Zusatzinfo geloggt, ob der vom Device gelieferte Wert ein Integer oder
ein Float Wert ist.

Das kann einige Zeit in Anspruch nehmen, da die Devices nicht ständig alle Attribute senden und einige batteriebetriebene
Devices zum Teil mehrere Stunden schweigen (z.B.Shelly Plus H&T), oder wie der Shelly Button1 nur senden,
wenn der Button gedrückt wird.

Einige Devices senden den Status eines Attributes auch nur bei einer Änderung des Zustandes
(z.B. das ADD-ON zum ShellyPlus 2 PM).

Im Log finden sich dann Einträge, die wie die folgenden aussehen:

.. code-block:: text

    2023-08-20  16:33:45 INFO     plugins.shelly         list_attrs '80646fe38450': shelly_attr='output' shelly_group='switch:0' type='bool'
    2023-08-20  16:33:45 INFO     plugins.shelly         list_attrs '80646fe38450': shelly_attr='apower' shelly_group='switch:0:0' type='num' (float)
    2023-08-20  16:33:45 INFO     plugins.shelly         list_attrs '80646fe38450': shelly_attr='voltage' shelly_group='switch:0' type='num' (float)
    2023-08-20  16:33:45 INFO     plugins.shelly         list_attrs '80646fe38450': shelly_attr='current' shelly_group='switch:0' type='num' (float)
    2023-08-20  16:33:45 INFO     plugins.shelly         list_attrs '80646fe38450': shelly_attr='energy' shelly_group='switch:0' type='num' (float)
    2023-08-20  16:33:45 INFO     plugins.shelly         list_attrs '80646fe38450': shelly_attr='energy_by_minute' shelly_group='switch:0' type='num' (float)
    2023-08-20  16:33:45 INFO     plugins.shelly         list_attrs '80646fe38450': shelly_attr='temp' type='num' (float)
    2023-08-20  16:33:45 INFO     plugins.shelly         list_attrs '80646fe38450': shelly_attr='temp_f' type='num' (float)

    2023-08-20  16:42:51 INFO     plugins.shelly         list_attrs '485519db1e1d': shelly_attr='battery' shelly_group='sensor' type='num' (int)
    2023-08-20  16:42:51 INFO     plugins.shelly         list_attrs '485519db1e1d': shelly_attr='voltage' shelly_group='sensor' type='num' (float)
    2023-08-20  16:42:51 INFO     plugins.shelly         list_attrs '485519db1e1d': shelly_attr='charger' shelly_group='sensor' type='bool'
    2023-08-20  16:42:51 INFO     plugins.shelly         list_attrs '485519db1e1d': shelly_attr='error' shelly_group='sensor' type='num' (int)
    2023-08-20  16:42:51 INFO     plugins.shelly         list_attrs '485519db1e1d': shelly_attr='act_reasons' shelly_group='sensor' type='list'
    2023-08-20  16:42:51 INFO     plugins.shelly         list_attrs '485519db1e1d': shelly_attr='event' shelly_group='input_event:0' type='str'

Mit diesen Informationen können die entsprechenden Items in SmartHomeNG konfiguriert werden. (Nicht vergessen das
test_item wieder zu löschen)

Die Namen der Attribute entsprechen zum großen Teil den Bezeichnern, die das Shelly Device sendet. Einige Attribut Namen
werden vom Plugin jedoch angepasst, da die unterschiedlichen Shelly Devices gleiche Informationen zum Teil unter
unterschidlichen Bezeichnern publizieren. Eine solche Vereinheitlichung ist zum Beispiel der Attribut Name **temp**.
Die Temperatur (in °C) wird von den verschiedenen Devices z.B. als **temp**, **temperature**, **tC** oder auch als dict
**temperature['tC']** publiziert. Zur Vereinfachung, ist für alle diese Bezeichner der Attribut Name **temp**


Nicht unterstützte Status Attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Es kann vorkommen, dass für ein Shelly Device Attribute oder Gruppen bisher nicht unterstützt werden. In diesem Fall
erfolgt folgender Eintrag im **smarthome-warnings.log**:

.. code-block:: text

    2023-08-20  18:02:04 NOTICE   plugins.shelly         Unbekannter Status empfangen von 'shellyplusht-80646fcbb6c8' - Loglevel des Plugin-Loggers auf INFO setzen und das Details-Log beobachten

Dann muß man man den Logger **plugins.shelly** auf den Level INFO konfigurieren. Anschließend werden dann die
Informationen zu den bisher nicht unterstützten Attributen in das **smarthome-details.log** geschrieben.

Ein Eintrag zu einem bisher nicht unterstützen Attribut sieht z.B. so aus:

.. code-block:: text

    2023-08-20  18:02:04 INFO     plugins.shelly         Unbehandelter Gen2 Status für shellyplusht-80646fcbb6c8:
     - Model='SNSN-0013A'
     - API: Gen2
     - App=PlusHT
     - Client_ID=shellyplusht-80646fcbb6c8
     - Parameter: 'battery'={'V': 6.03, 'percent': 100}
     - Group='devicepower:0'
     - Params={'id': 0, 'battery': {'V': 6.03, 'percent': 100}, 'external': {'present': False}}
     - Calling method=handle_gen2_device_status (pos='*ds1')

Wenn diese Information im Forum im Support Thread für das shelly Plugin oder als Issue auf Github gepostet wird,
kann mit diesen Informationen das Attribut bzw. die Gruppe Gruppen zeitnah in das Plugin integriert werden.

Diese nicht unterstützten Attribute werden werden bei gesetztem ``shelly_list_attrs`` Attribut nicht geloggt.
Ein Logging bei ``shelly_list_attrs`` erfolgt nur für bereits unterstützte Attribute.

|

Attribute um ein Device zu steuern
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Aktuell wird nur zum steuern eines Shelly Devices nur das Attribt ``output`` unterstützt. Es kann in den
Gruppen ``switch:0`` bis ``switch:3`` genutzt werden.

|

Item structs
------------

Zur Vereinfachung der Einrichtung von Items sind für folgende Shelly Devices Item-structs vordefiniert:

- shellyplug
- shellyplug_s
- shellyht
- shellyflood
- shellyplusplug_s

Unter Verwendung der entsprechenden Vorlage kann die Einrichtung einfach durch Angabe der shally_id des
entsprechenden Devices erfolgen:

.. code:: yaml

    plug1:
        name: Mein erster Shellyplug-S
        type: bool
        shelly_id: '040BD0'
        struct: shelly.shellyplug_s


Damit werden außer dem Schalter selbst, Unteritems für Leistung, Energieverbrauch und Temperatur
des Devices (in °C und °F) angelegt.


weitere Informationen
---------------------

Informationen zur Konfiguration und die vollständige Beschreibung der Item-Attribute sind
unter :doc:`/plugins_doc/config/shelly` zu finden.

