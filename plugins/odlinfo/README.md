# ODLInfo

Version 0.1

This plugin retrieves the Gamma-Ortsdosisleistung (ODL) in µSv/h from several measuring stations in Germany.
For more information see https://odlinfo.bfs.de.

# Requirements
This plugin requires lib requests. You can install this lib with: 
<pre>
sudo pip3 install requests --upgrade
</pre>

All mappings to items need to be done via your own logic.

Forum thread to the plugin: https://knx-user-forum.de/forum/supportforen/smarthome-py/986480-odlinfo-plugin-f%C3%BCr-strahlungsdaten

The odlinfo id can be retrieved by selecting your station on the map on https://odlinfo.bfs.de and looking in the URL
of the station, e.g. for 86949 Windach: https://odlinfo.bfs.de/DE/aktuelles/messstelle/091811461.html => id = 091811461

Take care not to request the interface too often, e.g. only once every hour (cycle = 3600).
The one hour medians that are retrieved by this plugin are typically updated in odlinfo.bfs.de at 04:30 UTC, 10:30 UTC,
16:30 UTC, and 22:30 UTC.

The data published by ODL can be used freely for registred users. The data provided by odlinfo is
copyrighted by Bundesamt für Strahlenschutz (BfS), Willy-Brandt-Straße 5, 38226 Salzgitter, Deutschland
Do not directly link the data interface / URL of ODLINFO in any context.

# Nutzung der Daten / Terms of Service
(in German only - most recent version see https://odlinfo.bfs.de/DE/service/downloadbereich.html)

Bei der Nutzung der vom Bundesamt für Strahlenschutz erhobenen Daten ist zu beachten:

Das Bundesamt für Strahlenschutz ist Urheber der ODL-Messnetz-Daten soweit diese nicht anders gekennzeichnet sind.
Es wird insbesondere vorsorglich auf den Inhalt der § 62, § 63 des Urheberrechtsgesetz (UrhG) hingewiesen:

Bei der Nutzung der Daten ist es grundsätzlich verboten, sie selbst, ihren Inhalt, ihren Titel oder die
Urheberbezeichnung zu ändern, § 62 Absatz 1 UrhG. Zulässige Änderungen ergeben sich allein aus dem Inhalt des § 62
Absatz 2 und Abs. 3 UrhG.
Bei der Nutzung der Daten oder der auf ihnen beruhenden Applikationen ist in Anerkennung der jeweiligen Urheberschaft
die Quelle deutlich anzugeben, also der Name des jeweiligen Urhebers sowie die Fundstelle, § 63 Absatz 1 UrhG.

Die Nichteinhaltung der Bestimmungen des Urheberrechts stellt eine Rechtsverletzung dar. Für diesen Fall behält sich
das BfS vor, zu ihrer Durchsetzung rechtliche Maßnahmen zu ergreifen. Mit dem Herunterladen und Speichern der Daten
erkennt der Nutzer die Nutzungsbedingungen an.
Im Übrigen wird an dieser Stelle ausdrücklich auf die rechtlichen Hinweise des Internetangebots des Bundesamtes für
Strahlenschutz hingewiesen. Es ist zu beachten, dass das technische Verfahren der Bereitstellung der Daten und das
verwendete Format noch nicht abschließend festgelegt ist, es kann jederzeit und ohne Vorankündigung geändert werden.

Angesichts der Sensibilität des Themas bittet das BfS darum, die Daten der Gamma-Ortsdosisleistung im Rahmen einer
möglichen Veröffentlichung in sachlicher Art und Weise darzustellen. Auf Rückfrage unterstützt sie das BfS gerne bei
fachlichen Erklärungen und wissenschaftlichem Hintergrundwissen.

Daten

Die ODL-Tagesmittelwerte auf dieser Seite sind geprüft und mit einem Schlüssel versehen, der die Originalität der
Daten verifiziert. Tagesmittelwerte werden nur gebildet, wenn die Station den ganzen Tag betriebsbereit war und
mindestens 80 Prozent der Einzelwerte vorhanden und fehlerfrei sind. Unplausible Messwerte und damit Lücken in den
Zeitreihen ergeben sich unter anderem durch:

Qualitätssicherungsmessungen, bei denen eine radioaktive Quelle für 30 Minuten an der Sonde befestigt war
fehlerhafte Komponenten oder externe Störungen (zum Beispiel Schaltvorgänge bei benachbarten Industrieanlagen) die
einzelne Peaks mit sehr hoher Amplitude bewirken können (siehe hierzu Menüpunkt Messwertinterpretation)
langfristige Stromausfälle (mehr als zwei Tage)
Wartungsarbeiten oder Sondentausch

Sprünge in der Zeitreihe, bei denen sich das Niveau langfristig ändert, können durch Erdarbeiten nahe der Sonde oder
durch sonstige Veränderungen der Umgebungsbedingungen verursacht sein. Kleinere Differenzen sind auch sichtbar, wenn
veraltete Sonden erneuert wurden. Im Rahmen der Messnetzpflege kommt es ständig zu Verlegungen von Sondenstandorten.
Dies führt dazu, dass einzelne Zeitreihen abrupt enden.

# Configuration

## plugin.conf
<pre>
[odlinfo]
    class_name = ODLInfo
    class_path = plugins.odlinfo
    user = <your own user>
    password = <your own password>
</pre>

### Attributes
  * `user`: Your own personal user for odlinfo.bfs.de. Instructions see https://odlinfo.bfs.de/DE/service/datenschnittstelle.html
  * `password`: Your own personal password for odlinfo.bfs.de. Instructions see https://odlinfo.bfs.de/DE/service/datenschnittstelle.html

## items.conf

### Example:
<pre>
[outside]
    [[radiation]]
        type = num
</pre>

# Functions

## get_radiation_for_ids(odlinfo_ids):
Gets a list of radiaton values and according stations to an array of internal odlinfo_ids
Dict keys per entry: 'ort', 'kenn', 'plz', 'status', 'kid', 'hoehe', 'lon', 'lat', 'mw'
Description see stamm.json (https://odlinfo.bfs.de/downloads/Datenbereitstellung-2016-04-21.pdf)
<pre>
sh.odlinfo.get_radiation_for_ids(['010620461','091811461']) # station Meddewade and Windach
</pre>

## get_radiation_for_id(odlinfo_id)
Gets a list of radiaton values and according stations to an internal odlinfo_id
Dict keys per entry: 'ort', 'kenn', 'plz', 'status', 'kid', 'hoehe', 'lon', 'lat', 'mw'
Description see stamm.json (https://odlinfo.bfs.de/downloads/Datenbereitstellung-2016-04-21.pdf)
<pre>
sh.odlinfo.get_radiation_for_id('091811461') # station Windach
</pre>

# Logics

## Fill item with radiation data
<pre>
radiation = sh.odlinfo.get_radiation_for_id('091811461') # station Windach
sh.outside.radiation(radiation['mw'])
</pre>
