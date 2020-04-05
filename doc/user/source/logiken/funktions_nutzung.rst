.. index:: Funktionen; Logiken
.. index:: Logiken; Funktionen

.. role:: redsup
.. role:: bluesup

====================================
Nutzung von Funktionen :redsup:`Neu`
====================================

Bei der Nutzung von Funktionen in Logiken ist eine Besonderheit zu beachten:

Eine Logik verhält sich nicht wie ein Python Modul! Variablen und Funktionen die auf Ebene der Logik definiert werden,
sind keine globalen Objekte. Sie stehen in Funktionen die innerhalb der Logik definiert werden nicht zur Verfügung.
Daher müssen Variablen und Funktionen die innerhalb von Funktionen genutzt werden, der Funktion explizit bekannt gemacht
werden.

Dafür müssen Funktionen und Variablen der Funktion als Parameter übergeben werden. Das kann geschehen, indem die
Übergabe für jede Variable/Funktion einzeln erfolgt oder sie können in einem Objekt übergeben werden (was die zu
bevorzugende Methode ist.

Dazu kann das Objekt **logic** genutzt werden, welches SmartHomeNG zur Verüfung stellt um Variablen zu implementieren,
die den Lauf der Logik "überleben" und beim nächsten Lauf dieser Logik wieder zur Verfügung stehen. Das **logic**
Objekt ist privat. Das bedeutet, jede Logik hat ihr eigenes **logic** Objekt.

Funktionen müssen dazu in der Definition den zusätzlichen Parameter **logic** enthalten. Das sollte zur besseren
Handhabung der letzte Parameter sein. Da dieser Parameter innerhalb der Logik immer mit dem selben Wert übergeben wird,
kann der Wert auch gleich als Standard-Wert in der Funktionsdefinition mit angegeben werden. Dann braucht er in den
Aufrufen der Funktion nicht angegeben zu werden.

Das folgende Beispiel verdeutlicht das Vorgehen:

.. code-block:: python

    # Funktionen definieren
    def func1(wert, logic=logic):
        logger.warning("Funktion 1: wert = {}".format(wert))

    def func2(logic=logic):
        logger.warning("Funktion 2")
        logic.func1(2)

    # Funktionen, welche in Logiken genutzt werden sollen, dem logic Objekt zuweisen
    logic.func1 = func1
    logic.func2 = func2

    # Variablen, die in Logiken genutzt werden sollen, dem logic Objekt zuweisen
    logic.sh = sh
    logic.myvar1 = 5
    logic.myvar2 = False

    # Code der Logik
    func1(1)
    func2()

Um aus Funktionen heraus auf das **sh** Objekt zugreifen zu können, solte auch dieses (wie im obigen Beispiel) als
Variable im **logic** Objekt abgelegt werden.
