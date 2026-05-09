
:tocdepth: 5

=================================
Funktionen und Klassen in Logiken
=================================


.. index:: Funktionen; Logiken
.. index:: Logiken; Funktionen

Funktionen in Logiken
=====================

Funktionen und Variablen müssen der Funktion als Parameter übergeben werden. Das kann geschehen, indem die
Übergabe für jede Variable/Funktion einzeln erfolgt oder sie können in einem Objekt übergeben werden (was die zu
bevorzugende Methode ist.

Dazu kann das Objekt **logic** genutzt werden, welches SmartHomeNG zur Verfüfung stellt, um Variablen zu implementieren,
die den Lauf der Logik "überleben" und beim nächsten Lauf dieser Logik wieder zur Verfügung stehen. Das **logic**
Objekt ist privat. Das bedeutet, jede Logik hat ihr eigenes **logic** Objekt.

Funktionen müssen dazu in der Definition den zusätzlichen Parameter **logic** enthalten. Das sollte zur besseren
Handhabung der letzte Parameter sein. Da dieser Parameter innerhalb der Logik immer mit dem selben Wert übergeben wird,
kann der Wert auch gleich als Standard-Wert in der Funktionsdefinition mit angegeben werden. Dann braucht er in den
Aufrufen der Funktion nicht angegeben zu werden.

Das folgende Beispiel verdeutlicht das Vorgehen:

.. code-block:: python

    # Funktionen definieren und anschließend dem logic Objekt zuweisen
    def func1(wert):
        logger.warning("Funktion 1: wert = {}".format(wert))

    def func2(logic=logic):
        logger.warning("Funktion 2")
        func1(2)


    # Main Routine der Logik
    func1(1)
    func2()


.. index:: Klassen; Logiken
.. index:: Logiken; Klassen


Klassen in Logiken
==================

In Logiken können auch Klassen definiert werden. Damit diese Klassen in Funktionen zur Verfügung stehen,
muss auch hier (wie bei Funktionen) die Klasse dem Logik Objekt zugewiesen werden (letzte Zeile im folgenden Beispiel):

.. code-block:: python

    class triggervalue():

        def __init__(self, init_value=None, trigger_item=None):
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

Wenn in einer Klasse auf Elemente des **logic** Objektes zugegriffen werden soll (wie in dem obigen Beispiel),
muss **logic** beim Erstellen einer Instanz mit übergeben werden:

.. code-block:: python

        freigabe_sued = triggervalue(trigger_item='beschattung.beschattungsautomatik.sued')

Zu beachten ist hierbei, dass das Weglassen der Zeile

.. code-block:: python

    logic.triggervalue = triggervalue

und das Ansprechen der Objektes ohne den Präfix ``logic.`` dazu führt, dass das Objekt nur während des Laufed
der Logik existiert. Wird hingegen das Objekt im logic Objekt abgelegt, existert das Objekt mis zum Neustart
von SmartHomeNG (Siehe dazu auch **Persistente Variablen**).
