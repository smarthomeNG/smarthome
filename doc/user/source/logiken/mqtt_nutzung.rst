.. index:: mqtt; Logiken
.. index:: Logiken; mqtt

.. role:: redsup
.. role:: bluesup

=========================================
Nutzung von MQTT in Logiken :redsup:`Neu`
=========================================

Die Nutzung des MQTT Protokolls in Logiken wird durch das mqtt Modul von SmartHomeNG möglich, welches ab Version 1.7
zur Verfügung steht. Zur Nutzung muss das mqtt Modul geladen und konfiguiert sein und der konfigurierte MQTT Broker
muss laufen.

Das mqtt Objekt
===============

Um MQTT in Logiken zu nutzen, steht ein Obkekt **mqtt** zur Verfügung. Falls das mqtt Modul geladen/konfiguriert ist
oder keine Verbindung zum Broker besteht, ist **mqtt** **None**. In Logiken kann folgendermaßen geprüft werden, ob
MQTT Unterstützung besteht:

.. code-block:: python
   :caption: Test ob MQTT Unterstützung besteht

    if mqtt is None:
        # no MQTT support available
        logger.warning("MQTT module is not loaded or not yet initialized")


Das **mqtt** Objekt stellt folgende Funktionen bereit, um MQTT Messages zu versenden oder zu empfangen:


mqtt.publish_topic()
--------------------

Eine MQTT Message kann versendet werden, indem die Funktion folgendermaßen aufgerufen wird:

.. code-block:: python
   :caption: publish_topic()

   mqtt.publish_topic(source_logic, topic, payload)


+-------------------------+------------------------------------------------------------------------------------------------------+
| Parameter               | Bemerkung                                                                                            |
+=========================+======================================================================================================+
| source_logic            | Name der Logik, welche die Funktion **publish_topic** aufruft. Hier kann einfach die Variable        |
|                         | **logic.name** genutzt werden.                                                                       |
+-------------------------+------------------------------------------------------------------------------------------------------+
| topic                   | Topic der zu veröffentlichenden MQTT Message als **str**.                                            |
+-------------------------+------------------------------------------------------------------------------------------------------+
| payload                 | Payload der zu veröffentlichenden MQTT Message. Die Variable kann jedem Python Datentyp sein.        |
+-------------------------+------------------------------------------------------------------------------------------------------+


mqtt.subscribe_topic()
----------------------

Messages die ein bestimmtes MQTT Topic enthalten, können folgendermaßen aboniert werden:

.. code-block:: python
   :caption: subscribe_topic()

   mqtt.subscribe_topic(source_logic, topic, callback, qos=None, payload_type='str', bool_values=None)


+-------------------------+------------------------------------------------------------------------------------------------------+
| Parameter               | Bemerkung                                                                                            |
+=========================+======================================================================================================+
| source_logic            | Name der Logik, welche die Funktion **subscribe_topic** aufruft. Hier kann einfach die Variable      |
|                         | **logic.name** genutzt werden.                                                                       |
+-------------------------+------------------------------------------------------------------------------------------------------+
| topic                   | Topic welches aboniert werden soll.                                                                  |
+-------------------------+------------------------------------------------------------------------------------------------------+
| callback                | Name der Logik, welche bei Empfang des abonierten Topics getriggert werden soll. Das kann die        |
|                         | aufrufende Logik sein oder eine andere Logik. Wenn die aufrufende Logik getriggert werden soll, kann |
|                         | hier einfach die Variable **logic.name** genutzt werden.                                             |
+-------------------------+------------------------------------------------------------------------------------------------------+
| qos                     | **Optional**: Quality-of-Service, falls ein von der Standardeinstellung abweichender qos genutzt     |
|                         | werden soll. Anderenfalls kann dieser Parameter weggelassen werden.                                  |
+-------------------------+------------------------------------------------------------------------------------------------------+
| payload_type            | **Optional**: Datentyp in welchen die Payload umgewandelt werden soll. Wenn dieser Parameter nicht   |
|                         | angegeben wird, wird der Datentyp **str** verwendet. Angegeben werden können folgende SmartHomeNG    |
|                         | Datentypen: 'str', 'num', 'bool', 'list', 'dict', 'scene' oder 'bytes' - **bytes** bedeutet, dass    |
|                         | keine Typenwandlung vorgenommen wird.                                                                |
+-------------------------+------------------------------------------------------------------------------------------------------+
| bool_values             | **Optional**: Legt fest, welche Werte des Payload als **bool** Values interpretiert werden sollen.   |
|                         | Falls der Parameter angegeben wird, muss eine Liste mit **zwei** Werten angegeben werden, wobei der  |
|                         | erste Wert für **False** steht und der zweiter Wert für **True**                                     |
+-------------------------+------------------------------------------------------------------------------------------------------+

Wenn eine als **callback** angegebene Logik getriggert wird, ist das **trigger** dict mit folgenden Werten belegt:

- **trigger['source']** - 'mqtt' - Konstante
- **trigger['by']** - <topic> - Dadurch kann bestimmt werden, wie die payload zu behandeln ist, falls eine Logik die Callbacks mehrer topics erhält
- **trigger['value']** - <payload>, wobei der Datentyp der payload dem entspricht, was in mqtt.subscribe_topic() als payload_type angegeben wurde

Es können mehrere Logiken das selbe Topic abonieren. Alle Logiken die das Topic aboniert haben, werden beim Eintreffen
einer passenden MQTT Message getriggert.


mqtt.unsubscribe_topic()
------------------------

Ein bestehendes Abonement für Messages die ein bestimmtes MQTT Topic enthalten, kann folgendermaßen beendet werden:

.. code-block:: python
   :caption: unsubscribe_topic()

   mqtt.unsubscribe_topic(source_logic, topic)


+-------------------------+------------------------------------------------------------------------------------------------------+
| Parameter               | Bemerkung                                                                                            |
+=========================+======================================================================================================+
| source_logic            | Name der Logik, welche die Funktion **subscribe_topic()** für den Topic aufgerufen hatte.            |
+-------------------------+------------------------------------------------------------------------------------------------------+
| topic                   | Topic dessen Subscription beendet werden soll.                                                       |
+-------------------------+------------------------------------------------------------------------------------------------------+



Beispiel Logik
==============

Hier ist eine Beispiel Logik, die sowohl Subscriptions ausführt, als auch die Callbacks behandelt:

.. code-block:: python
   :caption: Beispiel Logik **mqtt_demo**

   #!/usr/bin/env python3
   # logics/mqtt_demo.py

   def logic_publish_topic(logger, mqtt, logic, topic, payload):
       logger.info("Function '{}()' - called by '{}()' in logic '{}'".format(inspect.stack()[0][3], inspect.stack()[1][3], logic.name))
       if mqtt.publish_topic(logic.name, topic, payload):
           logger.info("Function '{}()' - test-topic was published".format(inspect.stack()[0][3], inspect.stack()[1][3]))
       else:
           logger.warning("Function '{}()' - test-topic was NOT published".format(inspect.stack()[0][3], inspect.stack()[1][3]))

   def logic_subscribe_topic(logger, mqtt, logic, topic, payload_type='str'):
       logger.info("Function '{}()' - called by '{}()' in logic '{}'".format(inspect.stack()[0][3], inspect.stack()[1][3], logic.name))
       mqtt.subscribe_topic(logic.name, topic, None, payload_type, logic.name)


   # logic main-code starts here
   logger.info("Triggered: trigger['source'] = {}, trigger[by] = {}, trigger[value] = {}".format(trigger['source'], trigger['by'], trigger['value']) )
   if mqtt is None:
       # no MQTT support available
       logger.warning("MQTT module is not loaded or not yet initialized")
   elif trigger['source'] == 'mqtt':
       # callback received
       topic = trigger['by']
       payload = trigger['value']
       logger.info("MQTT received topic '{}': payload = '{}' - type(payload) = {})".format(topic, payload, type(payload)))
   else:
       mydict = {'txt': 'Test payload 2', 'num': 5}
       # logger, mqtt and logic are handed over to functions, because only this way they are accessable in a logic's function
       logic_publish_topic(logger, mqtt, logic, 'test_mqtt/topic', 'Test payload')
       logic_publish_topic(logger, mqtt, logic, 'test_mqtt/topic2', mydict)
       logic_subscribe_topic(logger, mqtt, logic, 'test_mqtt/sub')
       logic_subscribe_topic(logger, mqtt, logic, 'test_mqtt/sub2', 'dict')


.. hint::

   Den **logger** müßte man nicht unbedingt an die Funktionen in der Logik übergeben, aber dann würden im Log die
   Einträge aus Funktionen innerhalb der Logik im Logfile als Modul nicht **logics.mqtt_demo** angeben, sondern
   **scheduler**.

