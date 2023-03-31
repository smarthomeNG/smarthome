# mieleathome

## Version 1.0.0

Das Plugin ermöglicht den Zugriff auf die Miele@Home API. Es werden Stati abgefragt und 
im Rahmen der Möglichkeiten der API können Geräte gesteuert werden.
Es wird das Pollen von Informationen sowie das Event-gestütze Empfangen von Daten unterstützt.
Für das Event-Listening wird ein Stream-request zum Miele-Server aufgebaut. Falls durch den Trennung der 
Internet-Verbindung der Stream abreisst wird dies durch das Plugin erkannt und eine neuer Stream
aufgebaut.


## table of content

1. [Change Log](#changelog)
2. [Aktivierung des Zugriffs für 3rd party-Apps](#activate)
3. [Einstellungen in der plugin.yaml](#plugin_yaml)
4. [Ermittln der Device-ID´s](#device_id)
5. [Items definieren](#create_items)
6. [Darstellung in der VISU](#visu)
7. [known issues](#issues)

## ChangeLog<a name="changelog"/>

### 2021-11-21
- Version 1.0.0
- first Commit für Tests
- Bedienen und Überwachen von Trocknern und Gefrierschränken ist implementiert
- Folgende Funktionen sind realisiert

    - Status
    - programPhase
    - programType
    - remainingTime
    - targetTemperature
    - temperature
    - signalInfo
    - signalFailure
    - signalDoor
    - dryingStep
    - elapsedTime
    - ecoFeedback
    - batteryLevel
    - processAction ( start / stop / pause / start_superfreezing / stop_superfreezing / start_supercooling / stop_supercooling / PowerOn / PowerOff)


### Todo in Version 1.0.0

- Verarbeitung von "Programmen"
- Verarbeitung von "ambientLight", "light", "ventilationStep", "colors"
- Verarbeiten von "modes"

## Aktivierung des Zugriffs für 3rd party-Apps<a name="changelog"/>
 

Eine App unter https://www.miele.com/f/com/en/register_api.aspx registrieren. Nach Erhalt der Freischalt-Mail die Seite aufrufen und das Client-Secret und die Client-ID kopieren und merken (speichern).
Dann einmalig über das Swagger-UI der API (https://www.miele.com/developer/swagger-ui/swagger.html) mittels Client-ID und Client-Secret über den Button "Authorize" (in grün, auf der rechten Seite) Zugriff erteilen. Wenn man Client-Id und Client-Secret eingetragen hat wird man einmalig aufgefordert mittels mail-Adresse, Passwort und Land der App-Zugriff zu erteilen.

Die erhaltenen Daten für Client-ID und Client-Secret in der ./etc/plugin.yaml wie unten beschrieben eintragen.

##Settings für die /etc/plugin.yaml<a name="plugin_yaml"/>

<pre><code>
mieleathome:
    plugin_name: mieleathome
    class_path: plugins.mieleathome
    miele_cycle: 120
    miele_client_id: ''
    miele_client_secret: ''
    miele_client_country: 'de-DE'
    miele_user: ''      # email-Adress
    miele_pwd: ''       # Miele-PWD
</code></pre>

## Ermitteln der benötigten Device-ID´s<a name="device_id"/>

Das Plugin kann ohne item-Definitionen gestartet werden. Sofern gültige Zugangsdaten vorliegen
werden die registrierten Mielegeräte abgerufen. Die jeweiligen Device-Id´s können im WEB-IF auf dem
zweiten Tab eingesehen werden.

## Anlegen der Items<a name="create_items"/>

Es wird eine vorgefertigtes "Struct" für alle Geräte mitgeliefert. Es muss lediglich die Miele-"DeviceID" beim jweiligen Gerät
erfasst werden. Um die Miele-"DeviceID" zu ermitteln kann das Plugin ohne Items eingebunden und gestartet werden. Es werden im Web-IF
des Plugins alle registrierten Geräte mit der jeweiligen DeviceID angezeigt.
Führende Nullen der DeviceID sind zu übernehmen

<pre>
<code>
%YAML 1.1
---
MieleDevices:
    Freezer:
        type: str
        miele_deviceid: 'XXXXXXXXXXX'
        struct: mieleathome.child
    Dryer:
        type: str
        miele_deviceid: 'YYYYYYYYYYY'
        struct: mieleathome.child        

</code>
</pre>



## Darstellung in der VISU<a name="visu"/>

Es gibt eine vorgefertigte miele.html im Plugin-Ordner. Hier kann man die jeweiligen Optionen herauslesen und nach
den eigenen Anforderungen anpassen und in den eigenen Seiten verwenden.

## known issues<a name="issues"/>
### Trockner :
Ein Trockner kann nur im Modus "SmartStart" gestartet werden.
Es muss der SmartGrid-Modus aktiv sein und das Gerät auf "SmartStart" eingestellt werden.
Der Trockner kann dann via API/Plugin gestartet werden bzw. es kann eine Startzeit via API/Plugin gesetzt werden  
