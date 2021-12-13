:tocdepth: 4

.. index:: Logiken; Logiken

.. role:: redsup
.. role:: bluesup
.. role:: greensup
.. role:: blacksup


#######
Logiken
#######

Logiken für SmartHomeNG sind Python Skripte. Zur Erstellung von Logiken müssen Sie über
Kenntnisse der Programmiersprache Python verfügen.

Die Logik-Skripte müssen im Verzeichnis **../logics** der SmartHomeNG Installation abgelegt werden.

=====================
Grundlegende Struktur
=====================

Das wichtigste Objekt, das in Logiken verwendet wird, ist **sh**. Dies ist das Smarthome-Objekt.
Es enthält jedes Detail über die laufende SmartHomeNG Instanz. Mit diesem Objekt ist es möglich auf
alle Items, Plugins und Grundfunktionen von SmartHomeNG zuzugreifen. 

Zugriff auf Items und Werte
===========================

Um den Wert eines Items zu erhalten, rufen Sie zum Beispiel den Namen auf: sh.path.item(). 
Um einen neuen Wert zu setzen, geben Sie ihn einfach als Argument an: sh.path.item(neuer_wert).

.. attention::

   Zuweisung von Item-Werten:

   Es ist sehr wichtig, immer mit Klammern **()** auf die Items zuzugreifen! Wenn das Item direkt
   zugewiesen wird, z.B. mit sh.path.item = Wert, dann wird das item-Objekt in SmartHomeNG überschrieben.

   In diesem Fall kann die mitgelieferte Logik **check_items.py** verwendet werden, um auf Vorhandensein
   entsprechend beschädigter Items zu prüfen und diese wiederherzustellen. Alternativ werden die Items nach
   einem Neustart von SmartHomeNG neu erstellt.


Alternativ kann auch über die Item-Properties auf den Wert zugegriffen werden: sh.path.item.propery.value
gibt den Wert zurück, mit sh.path.item.property.value = Wert kann der Wert zugewiesen werden. Diese Variante
lässt sich wie eine normale Variablenzuweisung nutzen.

Beispiel
========

Eine Logik sieht prinzipiell folgendermaßen aus:

.. code-block:: python
   :caption: /usr/local/smarthome/logics/testlogik1.py

   #!/usr/bin/env python3
   # testlogik1.py

   #Code der Logik:

   # Das Deckenlicht im Büro einschalten, falls es nicht eingeschaltet ist
   if not sh.buero.deckenlicht():
       sh.buero.deckenlicht('on')


===============================
Verfügbare Objekte und Methoden
===============================


.. toctree::
   :maxdepth: 3
   :hidden:
   :titlesonly:

   objekteundmethoden_logging
   objekteundmethoden_feiertage_datum_zeit
   objekteundmethoden_sonne_mond
   objekteundmethoden_item_methoden
   objekteundmethoden_scheduler
   objekteundmethoden_tools


Neben dem **sh** Objekt, gibt es andere wichtige vordefinierte Objekte:


Das logic Objekt
================

Dieses Objekt bietet Zugriff auf das aktuelle Logikobjekt. Es ist möglich, während der Laufzeit
logische Attribute (crontab, cycle, ...) abzufragen und ändern. Diese Änderungen gehen nach dem Neustart
von SmartHomeNG verloren.

Definierte Methoden des Logikobjekts:

+-------------------+--------------------------------------------------------------------------------------------------------+
| Methode           | Erläuterung                                                                                            |
+===================+========================================================================================================+
| logic.id()        | Diese Methode liefert dem Namen der Logik wie in **../etc/logic.yaml** angegeben.                      |
+-------------------+--------------------------------------------------------------------------------------------------------+
| logic.last_run()  | Diese Methode liefert den letzten Lauf dieser Logik (vor aktuellen Lauf).                              |
+-------------------+--------------------------------------------------------------------------------------------------------+
| logic.disable()   | Konfigurierte Logiken sind standardmäßig aktiv und werden entsprechend der Konfiguration ausgeführt.   |
|                   | Diese Methode deaktiviert die Logik, sodass deren Ausführung unterbunden wird. (Ab SmartHomeNG v1.3)   |
+-------------------+--------------------------------------------------------------------------------------------------------+
| logic.enable()    | Eine bereits deaktivierte Logik kann mit dieser Methode wieder aktiviert werden. (Ab SmartHomeNG v1.3) |
+-------------------+--------------------------------------------------------------------------------------------------------+


Vordefinierte Attribute des Logikobjekts:

+---------------------------+--------------------------------------------------------------------------------------------------------+
| Attribut                  | Erläuterung                                                                                            |
+===========================+========================================================================================================+
| trigger[]                 | Ein Python-Dictionary, welches im Folgenden beschreiben wird.                                          |
+---------------------------+--------------------------------------------------------------------------------------------------------+
| logic.name                | Das Attribut logic.name liefert das selbe Ergebnis wie die Methode logic.id()                          |
+---------------------------+--------------------------------------------------------------------------------------------------------+
| logic.crontab             | Das Attribut liefert das aktuelle **crontab** Setting dieser Logik.                                    |
+---------------------------+--------------------------------------------------------------------------------------------------------+
| logic.cycle               | Das Attribut liefert das aktuelle **cycle** Setting dieser Logik.                                      |
+---------------------------+--------------------------------------------------------------------------------------------------------+
| logic.prio                | Das Attribut liefert das aktuelle **prio** Setting dieser Logik.                                       |
+---------------------------+--------------------------------------------------------------------------------------------------------+
| logic.filename            | Das Attribut liefert den Dateinamen des Python Skripts dieser Logik.                                   |
+---------------------------+--------------------------------------------------------------------------------------------------------+
| logic.<parameter>         | Liefert den konfigurierten Parameter <parameter> oder den Wert einer in einem vorherigen Lauf dieser   |
|                           | Logik persistieren Variablen.                                                                          |
+---------------------------+--------------------------------------------------------------------------------------------------------+


trigger Dict
============

trigger ist ein Python-Dictionary, welches als Laufzeitumgebung einige Informationen über das
Ereignis liefert, das die Logik ausgelöst hat.

Das Dictionary enthält folgende Informationen:

+---------------------------+--------------------------------------------------------------------------------------------------------+
| Attribut/Funktion         | Erläuterung                                                                                            |
+===========================+========================================================================================================+
| trigger['by']             | Auslöser ('Scheduler', Item', etc.)                                                                    |
+---------------------------+--------------------------------------------------------------------------------------------------------+
| trigger['source']         | enthält den Pfad des Items, welches die Logik getriggert hat.                                          |
+---------------------------+--------------------------------------------------------------------------------------------------------+
| trigger['source_details'] | Falls eine Logik aus einem Item heraus getriggert wurde (also trigger['by'] == Item ist), enthält      |
|                           | trigger['source_details'] weitere Details zum Auslöser (Beispiel: 'knx:1.1.241:ga=3/3/5')              |
+---------------------------+--------------------------------------------------------------------------------------------------------+
| trigger['dest']           |                                                                                                        |
+---------------------------+--------------------------------------------------------------------------------------------------------+
| trigger['value']          | enthält den Wert des Items, dass die Logik getriggert hat.                                             |
+---------------------------+--------------------------------------------------------------------------------------------------------+


Das logics Objekt
=================

Zugriff auf das Logics-API über das logics Objekt:

+---------------------------------+---------------------------------------------------------------------------------------------------------+
| Methode                         | Erläuterung                                                                                             |
+=================================+=========================================================================================================+
| logics.<method>                 | ermöglicht den Zugriff auf das Logics API, welches in der Developer Dokumentation beschrieben ist.      |
|                                 | Im folgenden sind einige Beispiele aufgeführt:                                                          |
+---------------------------------+---------------------------------------------------------------------------------------------------------+
| logics.scheduler_add()          | Hinzufügen eines Scheduler Eintrages für den logics-Namensraum. Der Syntax entspricht der               |
|                                 | scheduler.add() Methode.                                                                                |
+---------------------------------+---------------------------------------------------------------------------------------------------------+
| logics.scheduler_change()       | Ändern eines Scheduler Eintrages im logics-Namensraum. Der Syntax entspricht der scheduler.change()     |
|                                 | Methode.                                                                                                |
+---------------------------------+---------------------------------------------------------------------------------------------------------+
| logics.scheduler_remove()       | Löschen eines Scheduler Eintrages im logics-Namensraum. Der Syntax entspricht der scheduler_remove()    |
+---------------------------------+---------------------------------------------------------------------------------------------------------+
| logics.trigger_logic()          | Triggern einer im Logik                                                                                 |
+---------------------------------+---------------------------------------------------------------------------------------------------------+
| logics.set_config_section_key() | Setzt den Wert eines Schlüssels für eine angegebene Logik (Abschnitt) permanent in ../etc/logic.yaml    |
+---------------------------------+---------------------------------------------------------------------------------------------------------+

Der vollständige Syntax der Methoden kann der `Entwickler Dokumentation <https://www.smarthomeng.de/developer/lib/logic.html#>`_ entnommen werden.


Geladene Python Module
======================

Im Logik Environment sind diverse Python Module bereits geladen:

- sys
- os
- time
- datetime
- ephem
- random
- Queue
- subprocess


=============
Konfiguration
=============

Details zur Konfiguration von Logiken finden sich :doc:`hier <../konfiguration/logiken>` .


.. index:: Logiken; Persistente Variablen

=====================
Persistente Variablen
=====================

Normale Variablen innerhalb von Logiken sind nur für den jeweiligen Lauf gültig. Es ist jedoch
in einigen Fällen notwendig, Werte zwischen verschiedenen Läufen einer Logik zu übergeben.

Solche persistente Variablen sind in Logiken von SmartHomeNG möglich, es sind jedoch einige
Dinge zu beachten:

- Diese Variablen sind über mehrere Läufe von Logiken persistent. Allerdings gilt das nur während
  des Laufs von SmartHomeNG. Bei einem Neustart von SmartHomeNG gehen diese Werte verloren.
  Der Wert einer solchen Variablen geht auch verloren, wenn die Logik über das Backend während
  der Laufzeit von SmartHomeNG gespeichert und neu geladen wird.
- Beim 1. Lauf einer Logik nach dem Start von SmartHomeNG existieren diese Variablen nicht. Der
  erste Zugriff innerhalb einer Logik muss deshalb in einen **if not hasattr():** Ausdruck
  eingebunden werden.
- Diese Variablen sind **lokal zur Logik**. Sie stehen außerhalb der Logik, die sie definiert hat,
  nicht zur Verfügung. Wenn die Daten auch außerhalb der Logik verwendet werden, müssen sie in
  Items abgelegt werden. (Ein Sonderfall sind Werte, die zwar außerhalb der definierenden Logik
  verwendet werden sollen, aber nur in Logiken. Hier gibt es eine weitere Möglichkeit, die
  weiter unten beschrieben wird).
- Es dürfen einige Namen nicht verwendet werden, da sie interne Variablen des Logik Objektes
  überschreiben würden.

Die Persistenz dieser Variablen gilt nur während des Laufs von SmartHomeNG. Mit der Beendigung von
SmartHomeNG gehen die gespeicherten Werte verloren.


Einrichtung
===========

Normale Variablen sind lokal zum Lauf der der Logik. Eine Variable **myvar** die während eines
Laufes der Logik einen Wert zugewiesen bekommt, ist beim Beginn des nächsten Laufes nicht
definiert.

Um eine Variable so zu definieren, dass sie die Zeit bis zum nächsten Lauf der Logik überdauert,
muss sie als Attribut zur Logik definiert werden. Also statt:

.. code-block:: python

   myvar = 'my Value'

muss die Variable folgendermaßen definiert werden:

.. code-block:: python

   logic.myvar = 'my Value'


Die Variable **logic.myvar** übersteht die Zeit bis zum nächsten Lauf der Logik und sie steht
nur in der Logik zur Verfügung, die sie auch definiert hat.


Existenz einer Variablen sicherstellen
======================================

Wenn auf eine Variable zugegriffen wird bevor sie definiert wird, führt das zu einer Exception
und der Rest der Logik wird nicht ausgeführt. Beim ersten Lauf einer Logik nach einem Neustart
von SmartHomeNG existiert jedoch keine Variable aus vorangegangenen Läufen. Sie muss erstmal
definiert werden. Das kann zum Beispiel in der folgenden Form erfolgen, in der die Variable
**logic.myvar** mit dem Wert **None** initialisiert wird, falls sie nicht existiert

.. code-block:: python
   :caption: Sicherstellen, dass die Variable existiert

   if not hasattr(logic, 'myvar'):
       logic.myvar = None


Nutzung selbst definierter Parameter
====================================

Es ist möglich eigene Parameter in der Datei **../etc/logic.yaml** zu definieren. Diese Parameter
stehen in der Logik unter **logic.<Parameter>** zur Verfügung. Diese Parameter können als
eine bereits initialisierte Variable verstanden/genutzt werden. Sie können in der Logik nicht
nur gelesen, sondern auch verändert werden. Diese Änderung geht wie beschrieben bei einem
Neustart von SmartHomeNG verloren.


.. attention::

   Einschränkungen bei Variablennamen:

   Variablennamen dürfen nicht gleich einem Namen der Attribute sein, die im Abschnitt
   **Verfügbare Objekte und Methoden** beschrieben sind.


Einrichtung (Logik übergreifend)
================================

Statt eine persistende lokale Variable einzurichten:

.. code-block:: python

   :caption: persistent, lokal zu definierenden Logik

   logic.myvar = 'my Value'


kann eine Variable Logik-übergreifend eingerichtet werden. Dann ist als Präfix statt *logic.*
der Präfix *logics.* zu verwenden:

.. code-block:: python

   :caption: persistent, für alle Logiken zugreifbar

   logics.myvar = 'my Value'


Analog zur lokalen persistenten Variable muss die Existenz folgendermaßen sichergestellt werden:

.. code-block:: python
   :caption: Sicherstellen, dass die Variable existiert

   if not hasattr(logics, 'myvar'):
       logics.myvar = None


Unterschiede zu lokalen persistenten Variablen
----------------------------------------------

Eine einmal initialisierte Logik-übergreifende persistente Variable behält ihren Wert bis
zum Neustart von SmartHomeNG.

.. attention::

   Da die Logik-übergreifende Variable ihren Wert auch behält, wenn die Logik die sie initialisiert hat
   neu geladen wird, kann es zu unerwarteten Ergebnissen kommen, da sich die Logik nun evtl. bei einem
   Neustart der Logik anders verhält, als beim Neustart von SmartHomeNG!



.. index:: Funktionen; Logiken
.. index:: Logiken; Funktionen

======================
Nutzung von Funktionen
======================

Bei der Nutzung von Funktionen in Logiken ist eine Besonderheit zu beachten:

Eine Logik verhält sich nicht wie ein Python Modul! Variablen und Funktionen die auf Ebene der Logik definiert werden,
sind keine globalen Objekte. Sie stehen in Funktionen die innerhalb der Logik definiert werden nicht zur Verfügung.
Daher müssen Variablen und Funktionen die innerhalb von Funktionen genutzt werden, der Funktion explizit bekannt gemacht
werden.

Dafür müssen Funktionen und Variablen der Funktion als Parameter übergeben werden. Das kann geschehen, indem die
Übergabe für jede Variable/Funktion einzeln erfolgt oder sie können in einem Objekt übergeben werden (was die zu
bevorzugende Methode ist.

Dazu kann das Objekt **logic** genutzt werden, welches SmartHomeNG zur Verfüfung stellt um Variablen zu implementieren,
die den Lauf der Logik "überleben" und beim nächsten Lauf dieser Logik wieder zur Verfügung stehen. Das **logic**
Objekt ist privat. Das bedeutet, jede Logik hat ihr eigenes **logic** Objekt.

Funktionen müssen dazu in der Definition den zusätzlichen Parameter **logic** enthalten. Das sollte zur besseren
Handhabung der letzte Parameter sein. Da dieser Parameter innerhalb der Logik immer mit dem selben Wert übergeben wird,
kann der Wert auch gleich als Standard-Wert in der Funktionsdefinition mit angegeben werden. Dann braucht er in den
Aufrufen der Funktion nicht angegeben zu werden.

Das folgende Beispiel verdeutlicht das Vorgehen:

.. code-block:: python

    # Variablen, die in Funktionen genutzt werden sollen, müssen dem logic Objekt zugewiesen werden
    logic.sh = sh
    logic.myvar1 = 5
    logic.myvar2 = False

    # Funktionen definieren und anschließend dem logic Objekt zuweisen
    def func1(wert, logic=logic):
        logger.warning("Funktion 1: wert = {}".format(wert))
    logic.func1 = func1

    def func2(logic=logic):
        logger.warning("Funktion 2")
        logic.func1(2)
    logic.func2 = func2


    # Main Routine der Logik
    logic.func1(1)
    logic.func2()

Um aus Funktionen heraus auf das **sh** Objekt zugreifen zu können, sollte auch dieses (wie im obigen Beispiel) als
Variable im **logic** Objekt abgelegt werden.


.. index:: Logiken; Klassen

================================
Klassen in Logiken :redsup:`Neu`
================================

In Logiken können auch Klassen definiert werden. Damit diese Klassen in Funktionen zur Verfügung stehen,
muss auch hier (wie bei Funktionen) die Klasse dem Logik Objekt zugewiesen werden (letzte Zeile im folgenden Beispiel):

.. code-block:: python

    class triggervalue():

        def __init__(self, init_value=None, trigger_item=None, logic=None):
            self.trigger_item = trigger_item
            self.value = init_value
            self.changed = False
            self._last_value = init_value
            if self.trigger_item is not None:
                self.value = logic.items.return_item(trigger_item)()
                self.changed = (logic.trigger_dict['source'] == trigger_item)
                self._last_value = None

        def set(self, newvalue):
            if self.trigger_item is None:
                self._last_value = self.value
                self.value = newvalue
                self.changed = self.value != self._last_value
                return self.changed
            return self.changed
    logic.triggervalue = triggervalue

Wenn in einer Klasse auf Elemente des **logic** Objektes zugegriffen werden soll (wie in dem obigen Beispiel),
muss **logic** beim Erstellen einer Instanz mit übergeben werden:

.. code-block:: python

        logic.freigabe_sued = logic.triggervalue(trigger_item='beschattung.beschattungsautomatik.sued', logic=logic)




.. index:: mqtt; Logiken
.. index:: Logiken; mqtt

===========================
Nutzung von MQTT in Logiken
===========================

Die Nutzung des MQTT Protokolls in Logiken wird durch das mqtt Modul von SmartHomeNG möglich, welches ab Version 1.7
zur Verfügung steht. Zur Nutzung muss das mqtt Modul geladen und konfiguriert sein und der konfigurierte MQTT Broker
muss laufen.


Das mqtt Objekt
===============

Um MQTT in Logiken zu nutzen, steht ein Objekt **mqtt** zur Verfügung. Falls das mqtt Modul geladen/konfiguriert ist
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

Messages die ein bestimmtes MQTT Topic enthalten, können folgendermaßen abonniert werden:

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
| callback                | Name der Logik, welche bei Empfang des abonnierten Topics getriggert werden soll. Das kann die       |
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

Es können mehrere Logiken das selbe Topic abonnieren. Alle Logiken die das Topic abonniert haben, werden beim Eintreffen
einer passenden MQTT Message getriggert.


mqtt.unsubscribe_topic()
------------------------

Ein bestehendes Abonnement für Messages die ein bestimmtes MQTT Topic enthalten, kann folgendermaßen beendet werden:

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

   Den **logger** müsste man nicht unbedingt an die Funktionen in der Logik übergeben, aber dann würden im Log die
   Einträge aus Funktionen innerhalb der Logik im Logfile als Modul nicht **logics.mqtt_demo** angeben, sondern
   **scheduler**.

