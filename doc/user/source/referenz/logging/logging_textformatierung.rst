
.. index:: Referenz; Logging, Text Formatierung
.. Index:: Logging, Text Formatierung; Referenz

.. role:: bluesup
.. role:: redsup


==============================
Text Formatierung beim Logging
==============================

Bei der Erstellung von Logiken, User Functions oder Plugins ist es sinnvoll bestimmte Vorkommnisse oder Ereignisse
in Logdateien festzuhalten. Die anderen Abschnitte zum Logging in der Referenz befassen sich mit der Konfiguration
des Loggings. Hier folgen einige Vorschläge zum Vorgehen bei der Formatierung der eigentlichen Log Message.

Die Log Message muss dem Logger als **ein** String übergeben werden. Direkt im Log Aufruf kann man den String zwar
in der folgenden Weise zusammen bauen, das ist jedoch nicht zu empfehlen:

.. code-block:: python

    menge = 24
    preis = 19.98
    logger.info("Artikelmenge: "+str(menge) + ", Preis: " + str(preis) + ", Gesamt: " + str(menge * preis))


In älteren Python Versionen waren unterschiedliche Methoden zur Formatierung üblich. Die veraltete Methode im
Stil von **printf** und **sprintf**:

.. code-block:: python

    menge = 24
    preis = 19.98
    logger.info("Artikelmenge: %3d, Preis: %6.2f, Gesamt: %8.2f" % (menge, preis, menge * preis))


Der "pythonische Weg" war in **älteren** Python Versionen die Nutzung von "**format**":

.. code-block:: python

    menge = 24
    preis = 19.98
    logger.info("Artikelmenge: {}, Preis: {}, Gesamt: {}".format(menge, preis, menge * preis))

Auch hier war eine Formatierung der Variableninhalte möglich:


.. code-block:: python

    menge = 24
    preis = 19.98
    logger.info("Artikelmenge: {:3d}, Preis: {:6.2f}, Gesamt: {:8.2f}".format(menge, preis, menge * preis))


Seit Python 3.6 gibt es eine neue Möglichkeit der Formatierung, die sogenannten **f-Strings**. Diese Methode erhöht
die Lesbarkeit des Python Codes deutlich, besonders bei Verwendung vieler Variablen in einer Message.

.. tip::

    Da inzwischen die von SmartHomeNG unterstützte Python Version >= 3.6 ist, können **f-Strings** uneingeschränkt in
    SmartHomeNG genutzt werden.

    Diese Art der Formatierung wird ausdrücklich empfohlen. Es ist jedoch nicht notwendig, in älterem Code alle
    älteren Formatierungs-Optionen zu ersetzen.

.. code-block:: python

    menge = 24
    preis = 19.98
    logger.info(f"Artikelmenge: {menge}, Preis: {preis}, Gesamt: {menge * preis}")


Auch hier ist die Formatierung der Variableninhalte möglich:

.. code-block:: python

    menge = 24
    preis = 19.98
    logger.info(f"Artikelmenge: {menge:3d}, Preis: {preis:6.2f}, Gesamt: {menge * preis:8.2f}")

