.. index:: Logiken; Persistente Variablen

Persistente Variablen in Logiken
================================

Normale Variablen innerhalb von Logiken sind zur für den jeweiligen Lauf gültig. Es ist jedoch 
in einigen Fällen notwendig, Werte zwischen verschiedenen Läufen einer Logik zu übergeben.

Solche persistente Variablen sind in in Logiken von SmartHomeNG möglich, es sind jedoch einige
Dinge zu beachten:

- Diese Variablen sind über mehrere Läufe von Logiken persistent. Allerdings gilt das nur während 
  des Laufs von SmartHomeNG. Bei einem Neustart von SmartHomeNG gehen diese Werte vrloren. 
- Beim 1. Lauf einer Logik nach dem Start von SmartHomeNG existieren diese Variablen nicht. Der 
  erste Zugriff innerhalb einer Logik muss deshalb in einen **if not hasattr():** Ausdruck 
  eingebunden werden.
- Diese Variablen sind lokal zur Logik. Sie stehen außerhalb nicht zur Verfügung. Wenn die Daten
  auch außerhalb der Logik verwendet werden, müssen sie in Items abgelegt werden.
- Es dürfen einige Namen nicht verwendet werden, da sie interne Variablen des Logik Objektes
  überschreiben würden.
  

Einrichten einer persistenten Variablen
---------------------------------------

Normale Variablen sind lokal zum Lauf der der Logik. Eine Variable **myvar** die während eines
Laufes der Logik einen Wert zugewiesen bekommt, ist beim Beginn des nächsten Laufes nicht
definiert.

Um eine Variable so zu definieren, dass sie die Zeit bis zum nächsten Lauf der Logik überdauert,
muss sie als Attribut zur Logik definiert werden. Also statt:

.. code-block:: python
   :caption: nicht persistent
   
   myvar = 'my Value'

muss die Variable folgendermaßen definert werden:

.. code-block:: python
   :caption: persistent
   
   logics.myvar = 'my Value'


Die Variable **logics.myvar** übersteht die Zeit bis zum nächsten Lauf der Logik und sie steht
nur in der Logik zur Verfügung, die sie auch definiert hat.


Existenz einer Variable sicherstellen
-------------------------------------

Wenn auf eine Variable zugegriffen wird bevor sie definiert wird, führt das zu einer Exception
und der Rest der Logik wird nicht ausgeführt. Beim ersten Lauf einer Logik nach einem Neustart 
von SmartHomeNG existiert jedoch keine Variable aus vorangegangenen Läufen. Sie muss erstmal
definiert werden. Das kann zum Beispiel in der folgenden Form erfolgen, in der die Variable
**logics.myvar** mit dem Wert **None** initialisiert wird, falls sie nicht existiert

.. code-block:: python
   :caption: Sicherstellen, dass die Variable existiert
   
   if not hasattr(logic, 'myvar'):
       logics.myvar = None


Nutzung selbst definierter Parameter
------------------------------------

Es ist möglich eigene Parameter in der Datei **../etc/logic.yaml** zu definieren. Diese Parameter
stehen in der Logik under **logics.<Parameter>** zur Verfügung. Diese Parameter können als
eine bereits initialisierte Variable verstanden/genutzt werden. Sie können in der Logiik nicht
nur gelesen, sondern auch verändert werden. Diese Änderung geht wie beschrieben bei einem
Neustart von SmartHomeNG verloren.


.. attention::

   Einschränkungen bei Variablennamen:

   Variablennamen dürfen nicht gleich einem Namen der Attribute sein, die auf der Seite 
   :doc:`./objekteundmethoden` beschrieben sind.


