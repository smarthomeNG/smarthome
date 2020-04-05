.. index:: Logiken; Persistente Variablen

.. role:: bluesup

=======================================
Persistente Variablen :bluesup:`update`
=======================================

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


Einrichten einer persistenten Variablen
=======================================

Normale Variablen sind lokal zum Lauf der der Logik. Eine Variable **myvar** die während eines
Laufes der Logik einen Wert zugewiesen bekommt, ist beim Beginn des nächsten Laufes nicht
definiert.

Um eine Variable so zu definieren, dass sie die Zeit bis zum nächsten Lauf der Logik überdauert,
muss sie als Attribut zur Logik definiert werden. Also statt:

.. code-block:: python
   :caption: nicht persistent

   myvar = 'my Value'

muss die Variable folgendermaßen definiert werden:

.. code-block:: python
   :caption: persistent

   logic.myvar = 'my Value'


Die Variable **logic.myvar** übersteht die Zeit bis zum nächsten Lauf der Logik und sie steht
nur in der Logik zur Verfügung, die sie auch definiert hat.


Existenz einer Variable sicherstellen
=====================================

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

   Variablennamen dürfen nicht gleich einem Namen der Attribute sein, die auf der Seite
   :doc:`./objekteundmethoden` beschrieben sind.


Einrichten einer persistenten Variablen (Logik übergreifend)
============================================================

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

