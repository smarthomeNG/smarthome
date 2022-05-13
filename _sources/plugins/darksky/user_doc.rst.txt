
.. index:: Plugins; darksky (darksky.net / forecast.io Wetterdaten)
.. index:: darksky
.. index:: Wetter; darksky
.. index:: struct; darksky

=======
darksky
=======

Wetterdaten von `darksky.net <https://darksky.net>`_ lesen. 

Darksky.net wurde am 31. März 2020 von Apple gekauft. Als Folge davon werden keine weiteren API Schlüssel vergeben 
und das API ist auch nur noch bis Ende 2021 zugänglich.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/darksky` beschrieben.


Web Interface
=============

Das darksky Plugin verfügt über ein Webinterface, mit dessen Hilfe die Items die das Plugin nutzen
übersichtlich dargestellt werden.

.. important::

   Das Webinterface des Plugins kann mit SmartHomeNG v1.4.2 und davor **nicht** genutzt werden.
   Es wird dann nicht geladen. Diese Einschränkung gilt nur für das Webinterface. Ansonsten gilt
   für das Plugin die in den Metadaten angegebene minimale SmartHomeNG Version.

   Die Nutzung des Item Templates funktionert erst ab SmartHomeNG v1.6.


Item Konfiguration
------------------

Eine sehr einfache Möglichkeit die benötigten Items das Plugins zu definieren, ist die Nutzung des mit dem
Plugin mitgelieferten struct-Templates.

Hierzu kann einfach ein Item (hier wetter_darksky) angelegt und als ``struct`` vom Typ ``darksky.weather`` definiert
werden. Standardmäßig sind unter hourly die nächsten 12 Stunden implementiert.

.. code-block:: yaml

   ...

    wetter_darksky:
        struct: darksky.weather


Besonderheiten
--------------

Zeiten werden bei darky als Epoch Time angegeben, diese Zeit ist in den struct als ``time_epoch`` hinterlegt. 
In den ``time`` Items wird sie durch folgende Konvertierung umformatiert. 
Wer möchte, kann dieses Muster für die anderen Zeitangaben (Sonnenauf/untergang, etc.) nutzen. 
Das unten definierte ``eval`` Attribut kann überschrieben bzw. bei den relevanten Items hinzugefügt werden. 
Unabhängig davon haben alle Items auch einen ``weekday`` und ``date`` Eintrag, die direkt abgefragt werden können.

.. code-block:: yaml

    time:
        type: str
        eval: datetime.datetime.fromtimestamp(value).strftime('%HH:%MM')


Die Originalantwort der Darksky Webseite wird vom Plugin entsprechend aufgedröselt.
Informationen, die unter daily/data und hourly/data angegeben sind, sind nun direkt als 
day0, day1, etc. sowie hour0, hour1, etc. abrufbar. 
Der ursprüngliche data Eintrag wird aus dem JSON Objekt gelöscht, um die Übersichtlichkeit zu bewahren. 
Die stündlichen Informationen werden neben den relativen Angaben 
(hour0 = aktuelle Stunde, hour1, kommende Stunde, etc.) auch in den passenden Tagen direkt als Uhrzeit gelistet. 
Diese Information ist als Dictionary in den Items day0/hours, day1/hours und day2/hours hinterlegt. 
Es empfiehlt sich, das Web Interface zu nutzen, um die vorhandenen Informationen zu erforschen. 
Um diese Daten zu nutzen, sind entsprechende Logiken notwendig.


Die relevantesten Berechnungen zu den stundenweisen Vorhersagen sind aber bereits im Plugin implementiert. 
Und zwar sind unter den Items bzw. ds_matchstring mit den Namen 
``precipProbability_mean``, ``precipIntensity_mean`` und ``temperature_mean`` die durchschnittlichen
Regen- und Temperaturvorhersagen abrufbar.
Hierbei werden die entsprechenden stündlichen Einzelwerte herangezogen, um den Mittelwert zu erstellen.
Auf diese Weise ist es z.B. möglich, die Regenwahrscheinlichkeit für den restlichen heutigen Tag abzufragen.


Instanzen
---------

Wenn mehrere Instanzen des Plugins konfiguriert sind, kann das struct-Template auch mehrfach eingebunden werden.
Hierbei muss bei der eingebundenen struct-Template angegeben werden, für welche Instanz des Plugins sie verwendet
werden soll:

.. code-block:: yaml

   ...

   wetter_ham:
       struct: darksky.weather
       instance: ham

   wetter_bos:
       struct: darksky.weather
       instance: bos


Aufruf des Webinterfaces
------------------------

Das Plugin kann aus dem backend aufgerufen werden. Dazu auf der Seite Plugins in der entsprechenden
Zeile das Icon in der Spalte **Web Interface** anklicken.

Außerdem kann das Webinterface direkt über ``http://smarthome.local:8383/darksky`` bzw.
``http://smarthome.local:8383/darksky_<Instanz>`` aufgerufen werden.


Beispiele
---------

Folgende Informationen können im Webinterface angezeigt werden:

Oben rechts werden allgemeine Parameter zum Plugin angezeigt.

Im ersten Tab werden die Items angezeigt, die das darksky Plugin nutzen:

.. image:: assets/webif1.jpg
   :class: screenshot

Im zweiten Tab werden die darksky Rohdaten (JSON Format) angezeigt:

.. image:: assets/webif2.jpg
   :class: screenshot
