#!/usr/bin/env python
#
# Configuration file with the speech parser commands:

""" Hier folgt die Definition der Listen mit den zu suchenden Begriffen """

""" Der Aufbau ist wie folgt:

    Name der Liste  suchbegriff1 wird in die Antwort eingesetzt
          |          Rückgabewert         |               Weitere Suchbegriffe
    varBeispiel = [       |               |                |               |
                     ['rueckgabe', ['suchbegriff1', 'suchbegriff2', 'suchbegriff3']],
                     [ ... ]
                   ]

    Der Rückgabewert kann z.B. ein Teil des Items sein oder ein Wert der zurückgegeben wird.
    Wird als Rückgabewert %status% definiert, dann wird der Wert des Items abgefragt und zurückgegeben (siehe Beispiel Temperatur)
    Wichtig: Alle Suchbegriffe in Kleinschreibung!
"""

varSchalten = [
                [1, ['eingeschaltet', 'einschalten', '1', 'anschalten', 'aktivieren', 'an', 'ein']],
                [0, ['ausgeschaltet', 'ausschalten', '0', 'abschalten', 'deaktivieren', 'aus']]
              ]

varRaum = [
                ['eg.kueche', ['küchenbereich', 'kochbereich', 'küche', 'kochen']],
                ['eg.essen', ['esszimmer', 'essen', 'essbereich']],
                ['eg.wohnen', ['wohnzimmer', 'stube', 'wohnen', 'wohnbereich']],
                ['eg.buero', ['büro von xy', 'büro', 'xy', 'arbeitszimmer']],
                ['eg.diele', ['flur unten', 'diele', 'eingangsbereich']],
                ['eg.gaeste_wc', ['gäste wc', 'wc', 'toilette', 'klo']],
                ['eg.hwr', ['hauswirtschaftsraum', 'hwr']],
                ['dg.bad_eltern', ['eltern badezimmer', 'elternbadezimmer', 'elternbad', 'eltern bad', 'bad', 'badezimmer', 'dusche', 'badewanne']],
                ['dg.schlafen', ['schlafzimmer', 'schlafen', 'eltern']],
                ['dg.gast', ['büro von yz', 'yz', 'büro oben', 'oberes büro', 'gast', 'gästezimmer']],
                ['dg.kind1', ['zimmer von max', 'mahx', 'maxs', 'maxszimmer']],
                ['dg.kind2', ['zimmer von moritz', 'moritz', 'moritzs', 'moritzszimmer']],
                ['dg.kinderbad', ['kinderbad', 'bad kinder', 'kinder']],
                ['dg.flur', ['flur', 'flur oben']],
                ['dg.dachboden', ['dachboden', 'spitzboden']],
                ['aussen.terrasse', ['terrassenbereich', 'terrasse']]
          ]

varFahren = [
                [0, ['hochgefahren', 'hochfahren', 'auffahren', 'nachoben', 'auf', 'hoch', 'öffnen', 'oben' ]],
                [1, ['zugefahren', 'abfahren', 'runterfahren', 'zufahren', 'zu', 'ab', 'runter', 'schließen', 'unten', 'unter']]
            ]

varDimmen = [
                [1, ['heller']],
                [0, ['dunkler']]
            ]

varRollladen = [
                ['rollladen', ['rollladen', 'rolladen', 'rollläden', 'rolläden', 'jalousie', 'rollo', 'behang', 'rollen', 'rolle']]
               ]

varRichtung = [
                ['sued', ['süd', 'Südlich']],
                ['west', ['west', 'Westlich']],
                ['ost', ['ost', 'Östlich']],
                ['nord', ['nord', 'Nördlich']]
              ]

varDimmwert = [
                [80, ['hell']],
                [5, ['dunkel']],
                [100, ['ganz hell']]
              ]

varPosition = [
                [70, ['beschatten']],
                [85, ['lüften', 'schlitze', 'schlitz']]
              ]

varZahl = [
                [1000, ['1000', 'tausend', 'eintausend']], 
                [100, ['100', 'hundert', 'einhundert']], 
                [13, ['13', 'dreizehn']], 
                [14, ['14', 'vierzehn']],  
                [15, ['15', 'fünfzehn']],
                [10, ['10', 'zehn']], 
                [11, ['11', 'elf']], 
                [12, ['12', 'zwölf']], 
                [16, ['16']], 
                [17, ['17']], 
                [18, ['18']], 
                [19, ['19']], 
                [25, ['25', 'fünfundzwanzig']],
                [26, ['26']],
                [27, ['27']],
                [28, ['28']],
                [29, ['29']],
                [20, ['20', 'zwanzig']],
                [21, ['21']],
                [22, ['22']],
                [23, ['23']],
                [24, ['24']],
                [35, ['35', 'fünfunddreizig']],
                [36, ['36']],
                [37, ['37']],
                [38, ['38']],
                [39, ['39']],
                [30, ['30', 'dreizig']],
                [31, ['31']],
                [32, ['32']],
                [33, ['33']],
                [34, ['34']],
                [45, ['45', 'fünfundvierzig']], 
                [46, ['46']],
                [47, ['47']],
                [48, ['48']],
                [49, ['49']],
                [40, ['40', 'vierzig']], 
                [41, ['41']],
                [42, ['42']],
                [43, ['43']],
                [44, ['44']],
                [55, ['55', 'fünfundfünfzig']],
                [56, ['56']],
                [57, ['57']],
                [58, ['58']],
                [59, ['59']], 
                [50, ['50', 'fünfzig']], 
                [51, ['51']],
                [52, ['52']],
                [53, ['53']],
                [54, ['54']],
                [65, ['65', 'fünfundsechzig']],
                [66, ['66']],
                [67, ['67']],
                [68, ['68']],
                [69, ['69']], 
                [60, ['60', 'sechzig']], 
                [61, ['61']],
                [62, ['62']],
                [63, ['63']],
                [64, ['64']],
                [75, ['75', 'fünfundsiebzig']],
                [76, ['76']],
                [77, ['77']],
                [78, ['78']],
                [79, ['79']],
                [70, ['70', 'siebzig']], 
                [71, ['71']],
                [72, ['72']],
                [73, ['73']],
                [74, ['74']],
                [85, ['85', 'fünfundachtzig']],
                [86, ['86']],
                [87, ['87']],
                [88, ['88']],
                [89, ['89']], 
                [80, ['80', 'achtzig']], 
                [81, ['81']],
                [82, ['82']],
                [83, ['83']],
                [84, ['84']],
                [95, ['95', 'fünfundneunzig']],
                [96, ['96']],
                [97, ['97']],
                [98, ['98']],
                [99, ['99']], 
                [90, ['90', 'neunzig']], 
                [91, ['91']],
                [92, ['92']],
                [93, ['93']],
                [94, ['94']],
                [0, ['0', 'null']], 
                [1, ['1', 'eins']], 
                [2, ['2', 'zwei']], 
                [3, ['3', 'drei']], 
                [4, ['4', 'vier']], 
                [5, ['5', 'fünf']], 
                [6, ['6', 'sechs']], 
                [7, ['7', 'sieben']], 
                [8, ['8', 'acht']], 
                [9, ['9', 'neun']]
          ]

varLueftung = [
                [0, ['aus', 'ausschalten', 'stufe 0']],
                [1, ['nachtbetrieb', 'nacht', 'stufe 1' ]],
                [2, ['tagbetrieb', 'tag', 'stufe 2' ]],
                [3, ['party', 'maximal', 'stufe 3', 'partybetrieb', 'maximum' ]]
            ]

varLicht = [
                ['beleuchtung', ['licht', 'lampe', 'lampen', 'beleuchtung', 'leuchten', 'leuchte']]
           ]
           

varStopp = [
                [1, ['gestoppt', 'stoppen', 'stopp', 'stop', 'anhalten']]
           ]

varTemperatur = [
                ['%status%', ['temperatur', 'lufttemperatur', 'raumtemperatur', 'wie warm', 'wie kalt']]
                ]

varSzene = [
                ['eg.szenen.kueche_essen_wohnen', ['beleuchtungsszene', 'szenen', 'szene', 'lichtstimmung']]
           ]

varSzeneValue = [
                [9, ['fernsehen']],
                [10, ['essen']],
                [11, ['kochen']],
                [12, ['party']],
                [13, ['alles aus']]
                ]

varRadio = [
                ['egal', ['mp3 player', 'radio', 'kassettenrekorder', 'kassettenrecorder', 'rekorder', 'recorder', 'mp3', 'radiorecorder', 'radiorekorder', 'hardy']]
           ]
           
varMoritz = [
                ['moritz', ['moritz', 'moritzs' ]]
         ]

""" Hier folgt die Definition der Regeln unter Einbeziehung der vorhergehenden Variablen/Listen """

""" Der Aufbau ist wie folgt:

    Name der Liste                                  Rückgabewert                              Antwort die zurückgemeldet wird
          |     Item- oder Logik-Name mit Platzhalter     | Suchmuster mit Wörtern und Variablen             |     Optional: Typangabe "item" (default) oder "logic"
    varParse = [                  |                       |                   |           |                  |                    |
                     ["%x%.beleuchtung.buero.schalten", "%y%", [varXYZ, 'suchbegriff1', varWXY], "OK, Befehl wird ausgeführt", 'logic'],
                     [ ... ]
               ]

    Die Reihenfolge bestimmt die Priorität, d.h. nur die erste Regel die zutrifft wird ausgeführt, alle weiteren nicht mehr.
    Die Platzhalternummerierung (%x%) entspricht der Reihenfolge der Listen/Wörter beginnend mit Null,
       Beispiel: [varLicht, varRaum, varSchalten] dann wird der Platzhalter %0% vom Rückgabewert varLicht ersetzt, %1% von varRaum und %2% von varSchalten.
    Wenn kein Typ angegeben ist, wird Item angenommen, soll eine Logik getriggert werden, dann muss 'logic' angegeben werden.
    varParse muss so heißen und NACH den übrigen Listen eingetragen werden.
"""
varParse = [
                ["%1%.beleuchtung.decke.schalten", "%2%", [varLicht, varRaum, varSchalten], "OK, Licht im %1% %2%." ],
                ["%0%.beleuchtung.decke.dimmen", "%1%", [varRaum, varDimmen], "OK, Licht im %0% %1%." ],
                ["%1%.beleuchtung.decke.dimmen", "%0%", [varDimmen, varRaum], "OK, Licht im %0% %1%." ],
                ["%0%.beleuchtung.decke.dimmwert", "%2%", [varRaum, varLicht, varZahl, 'prozent'], "OK, dimme %0% auf %2% Prozent." ],
                ["%0%.beleuchtung.decke.schalten", "%2%", [varRaum, varLicht, varSchalten], "OK, Licht im %0% %2%." ],
                ["%1%.beleuchtung.decke.dimmwert", "%2%", [varLicht, varRaum, varZahl, 'prozent'], "OK, dimme %1% auf %2% Prozent." ],
                ["%2%.beleuchtung.decke.dimmwert", "%0%", [varZahl, 'prozent', varRaum], "OK, Licht im %2% %0%." ],
                ["zentral.haus.rollladen.dg.fahren", "%2%", ['dachgeschoss', varRollladen, varFahren], "OK, Rollläden im Dachgeschoss %2%." ],
                ["zentral.haus.rollladen.dg.fahren", "%2%", [varRollladen, 'dachgeschoss', varFahren], "OK, Rollläden im Dachgeschoss %2%." ],
                ["zentral.haus.rollladen.eg.fahren", "%2%", ['erdgeschoss', varRollladen, varFahren], "OK, Rollläden im Erdgeschoss %2%." ],
                ["zentral.haus.rollladen.eg.fahren", "%2%", [varRollladen, 'erdgeschoss', varFahren], "OK, Rollläden im Erdgeschoss %2%." ],
                ["%2%.rollladen.%1%.position", "%3%", [varRollladen, varRichtung, varRaum, varZahl, 'Prozent'], "OK, fahre den Rollladen %1% im %2% auf %3% Prozent." ],
                ["%0%.rollladen.%3%.position", "%3%", [varRaum, varRollladen, varRichtung, varZahl, 'Prozent'], "OK, fahre den Rollladen %2% im %0% auf %3% Prozent." ],
                ["%2%.rollladen.%1%.fahren", "%3%", [varRollladen, varRichtung, varRaum, varFahren], "OK, Rollladen %1% im %2% %3%." ],
                ["%0%.rollladen.%3%.fahren", "%3%", [varRaum, varRollladen, varRichtung, varFahren], "OK, Rollladen %2% im %0% %3%." ],
                ["%2%.rollladen.fahren", "%2%", [varRollladen, varRaum, varFahren], "OK, Rollladen im %1% %2%." ],
                ["%0%.rollladen.fahren", "%2%", [varRaum, varRollladen, varFahren], "OK, Rollladen im %0% %2%." ],
                ["%1%.rollladen.position", "%2%", [varRollladen, varRaum, varZahl, 'Prozent'], "OK, fahre den Rollladen im %1% auf %2% Prozent." ],              
                ["%0%.rollladen.position", "%2%", [varRaum, varRollladen, varZahl, 'Prozent'], "OK, fahre den Rollladen im %0% auf %2% Prozent." ],
                ["%2%.rollladen.%1%.stopp", "%3%", [varRollladen, varRichtung, varRaum, varStopp], "OK, Rollladen %1% im %2% %3%." ],
                ["%0%.rollladen.%3%.stopp", "%3%", [varRaum, varRollladen, varRichtung, varStopp], "OK, Rollladen %2% im %0% %3%." ],
                ["%2%.rollladen.stopp", "%2%", [varRollladen, varRaum, varStopp], "OK, Rollladen im %1% %2%." ],
                ["%0%.rollladen.stopp", "%2%", [varRaum, varRollladen, varStopp], "OK, Rollladen im %0% %2%." ],
                ["eg.wohnen.steckdose.subwoofer.schalten", "%1%", ['subwoofer', varSchalten], "OK, Subwoofer %1%." ],
                ["eg.wohnen.steckdose.fernseher.schalten", "%1%", ['fernseher|tv', varSchalten], "OK, Fernseher %1%." ],
                ["%1%.temperatur.luft", "%0%", [varTemperatur, varRaum], "Die Lufttemperatur im %1% beträgt %0% Grad." ],
                ["%0%.temperatur.luft", "%1%", [varRaum, varTemperatur], "Die Lufttemperatur im %0% beträgt %1% Grad." ],
                ["%0%", "%1%", [varSzene, varSzeneValue], "Die Szene %1% wurde aufgerufen." ],
                ["dg.kind2.steckdose.nord.schalten", "%2%", [varRadio, varMoritz, varSchalten], "Der %0% wurde %2%." ],
                ["dg.kind2.steckdose.nord.schalten", "%2%", [varMoritz, varRadio, varSchalten], "Der %1% wurde %2%." ],
                ["test", "nichts", ['logik'], "Logik test wurde getriggert.", 'logic' ]
              ]

dictError = {
                'error': 'Es ist ein Fehler aufgetreten, der Befehl wurde nicht ausgeführt!',
                'unknown_command': 'Der Befehl wurde nicht erkannt! Bitte wiederholen.',
                'status_error': 'Es tut mir leid, der Status konnte nicht ermittelt werden!',
                'rights_error': 'Lesen und schreiben ist bei dem Objekt nicht erlaubt!'
           }
