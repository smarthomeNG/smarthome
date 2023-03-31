
.. index:: Plugins; avm
.. index:: avm

===
avm
===

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Allgemeine Informationen
------------------------

Im Plugin wird das TR-064 Protokoll und das AHA Protokoll verwendet.

Links zur Definition des TR-064 Protokolls:
    https://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/X_contactSCPD.pdf
    http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/hostsSCPD.pdf
    http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/wanipconnSCPD.pdf
    http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/x_voipSCPD.pdf


Links zur Definition des AHA Protokolls:
    https://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/AHA-HTTP-Interface.pdf


Unterstützung erhält man im Forum unter: https://knx-user-forum.de/forum/supportforen/smarthome-py/934835-avm-plugin


Konfiguration der Fritz!Box
---------------------------

Für die Nutzung der Informationen über Telefonereignisse muss der CallMonitor aktiviert werden. Dazu muss auf
einem direkt an die Fritz!Box angeschlossenen Telefon (Analog, ISDN S0 oder DECT) \*96#5# eingegeben werden.

Bei neueren Firmware Versionen (ab Fritz!OS v7) Muss die Anmeldung an der Box von "nur mit Kennwort" auf "Benutzername
und Kennwort umgestellt werden" und es sollte ein eigener User für das AVM Plugin auf der Fritz!Box eingerichtet werden.


Konfiguration des Plugins
---------------------------

Diese Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/avm` beschrieben.

.. note:: Kürzere Updatezyklen können abhängig vom Fritzdevice aufgrund hoher CPU Auslastung zu Problemen (u.a.
zu Nichterreichbarkeit des Webservice) führen. Wird ein kürzerer Updatezyklus benötigt, sollte das shNG Log beobachtet
werden. Dort werden entsprechende Fehlermeldungen hinterlegt.


item_structs
------------
Zur Vereinfachung der Einrichtung von Items sind für folgende Item-structs vordefiniert:

Fritz!Box // Fritz!Repeater mit TR-064
    - ``info``  -  Allgemeine Information zur Fritz!Box oder Fritz!Repeater
    - ``monitor``  -  Call Monitor (nur Fritz!Box)
    - ``tam``  -  Anrufbeantworter (nur Fritz!Box)
    - ``deflection``  -  Rufumleitung (nur Fritz!Box)
    - ``wan``  -  WAN Verbindung (nur Fritz!Box)
    - ``wlan``  -  WLAN Verbimdungen (Fritz!Box und Fritz!Repeater)
    - ``device``  -  Information zu einem bestimmten mit der Fritz!Box oder dem Fritz!Repeater verbundenen Netzwerkgerät (Fritz!Box und Fritz!Repeater)


Fritz!DECT mit AHA (FRITZ!DECT 100, FRITZ!DECT 200, FRITZ!DECT 210, FRITZ!DECT 300, FRITZ!DECT 440, FRITZ!DECT 500, Comet DECT)
    - ``aha_general``  -  Allgemeine Informationen eines AVM HomeAutomation Devices (alle)
    - ``aha_thermostat``  -  spezifische Informationen eines AVM HomeAutomation Thermostat Devices (thermostat)
    - ``aha_temperature_sensor``  -  spezifische Informationen eines AVM HomeAutomation Devices mit Temperatursensor (temperature_sensor)
    - ``aha_humidity_sensor``  -  spezifische Informationen eines AVM HomeAutomation Devices mit Feuchtigkeitssensor (bspw. FRITZ!DECT 440) (humidity_sensor)
    - ``aha_alert``  -  spezifische Informationen eines AVM HomeAutomation Devices mit Alarmfunktion (alarm)
    - ``aha_switch``  -  spezifische Informationen eines AVM HomeAutomation Devices mit Schalter (switch)
    - ``aha_powermeter``  -  spezifische Informationen eines AVM HomeAutomation Devices mit Strommessung (powermeter)
    - ``aha_level``  -  spezifische Informationen eines AVM HomeAutomation Devices mit Dimmfunktion oder Höhenverstellung (dimmable_device)
    - ``aha_blind``  -  spezifische Informationen eines AVM HomeAutomation Devices mit Blind / Rollo (blind)
    - ``aha_on_off``  -  spezifische Informationen eines AVM HomeAutomation Devices mit An/Aus (on_off_device)
    - ``aha_button``  -  spezifische Informationen eines AVM HomeAutomation Devices mit Button (bspw. FRITZ!DECT 440) (button)
    - ``aha_color``  -  spezifische Informationen eines AVM HomeAutomation Devices mit Color (bspw. FRITZ!DECT 500) (color_device)

Welche Funktionen Euer spezifisches Gerät unterstützt, könnt ihr im WebIF im Reiter "AVM AHA Devices" im "Device Details (dict)" unter "device_functions" sehen.


Item Beispiel mit Verwendung der structs ohne Instanz
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    avm:
        fritzbox:
            info:
                struct:
                  - avm.info
            reboot:
                type: bool
                visu_acl: rw
                enforce_updates: yes
            monitor:
                struct:
                  - avm.monitor
            tam:
                struct:
                  - avm.tam
            rufumleitung:
                rufumleitung_1:
                    struct:
                      - avm.deflection
                rufumleitung_2:
                    avm_deflection_index: 2
                    struct:
                      - avm.deflection
            wan:
                struct:
                  - avm.wan
            wlan:
                struct:
                  - avm.wlan
            connected_devices:
                mobile_1:
                    avm_mac: xx:xx:xx:xx:xx:xx
                    struct:
                      - avm.device
                mobile_2:
                    avm_mac: xx:xx:xx:xx:xx:xx
                    struct:
                      - avm.device
        smarthome:
            hkr_og_bad:
                type: foo
                avm_ain: 'xxxxx xxxxxxx'
                struct:
                  - avm.aha_general
                  - avm.aha_thermostat
                  - avm.aha_temperature_sensor


Item Beispiel mit Verwendung der structs mit Instanz
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    smarthome:
        socket_3D_Drucker:
            type: foo
            ain@fritzbox_1: 'xxxxx xxxxxxx'
            instance: fritzbox_1
            struct:
              - avm.aha_general
              - avm.aha_switch
              - avm.aha_powermeter
              - avm.aha_temperature_sensor
            temperature:
                database: 'yes'
            power:
                database: 'yes'

Hier wird zusätzlich das Item "smarthome.socket_3D_Drucker.temperature", welches durch das struct erstellt wird, um das
Attribut "database" ergänzt, um den Wert in die Datenbank zuschreiben.


Plugin Funktionen
-----------------

cancel_call
~~~~~~~~~~~

Beendet einen aktiven Anruf.

get_call_origin
~~~~~~~~~~~~~~~

Gib den Namen des Telefons zurück, das aktuell als 'call origin' gesetzt ist.

.. code-block:: python

    phone_name = sh.fritzbox_7490.get_call_origin()


CURL for this function:

.. code-block:: bash

    curl --anyauth -u user:password "https://fritz.box:49443/upnp/control/x_voip" -H "Content-Type: text/xml; charset="utf-8"" -H "SoapAction:urn:dslforum-org:service:X_VoIP:1#X_AVM-DE_DialGetConfig" -d "<?xml version='1.0' encoding='utf-8'?><s:Envelope s:encodingStyle='http://schemas.xmlsoap.org/soap/encoding/' xmlns:s='http://schemas.xmlsoap.org/soap/envelope/'><s:Body><u:X_AVM-DE_DialGetConfig xmlns:u='urn:dslforum-org:service:X_VoIP:1' /></s:Body></s:Envelope>" -s -k

get_calllist
~~~~~~~~~~~~
Ermittelt ein Array mit dicts aller Einträge der Anrufliste (Attribute 'Id', 'Type', 'Caller', 'Called', 'CalledNumber', 'Name', 'Numbertype', 'Device', 'Port', 'Date',' Duration' (einige optional)).

get_contact_name_by_phone_number(phone_number)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Durchsucht das Telefonbuch mit einer (vollständigen) Telefonnummer nach Kontakten. Falls kein Name gefunden wird, wird die Telefonnummer zurückgeliefert.

get_device_log_from_lua
~~~~~~~~~~~~~~~~~~~~~~~
Ermittelt die Logeinträge auf dem Gerät über die LUA Schnittstelle /query.lua?mq_log=logger:status/log.

get_device_log_from_tr064
~~~~~~~~~~~~~~~~~~~~~~~~~
Ermittelt die Logeinträge auf dem Gerät über die TR-064 Schnittstelle.

get_host_details
~~~~~~~~~~~~~~~~
Ermittelt die Informationen zu einem Host an einem angegebenen Index.
dict keys: name, interface_type, ip_address, mac_address, is_active, lease_time_remaining

get_hosts
~~~~~~~~~
Ermittelt ein Array mit den Details aller verbundenen Hosts. Verwendet wird die Funktion "get_host_details"

Beispiel einer Logik, die die Host von 3 verbundenen Geräten in eine Liste zusammenführt und in ein Item schreibt.
'avm.devices.device_list'

.. code-block:: python

    hosts = sh.fritzbox_7490.get_hosts(True)
    hosts_300 = sh.wlan_repeater_300.get_hosts(True)
    hosts_1750 = sh.wlan_repeater_1750.get_hosts(True)

    for host_300 in hosts_300:
        new = True
        for host in hosts:
            if host_300['mac_address'] == host['mac_address']:
                new = False
        if new:
            hosts.append(host_300)
    for host_1750 in hosts_1750:
        new = True
        for host in hosts:
            if host_1750['mac_address'] == host['mac_address']:
                new = False
        if new:
            hosts.append(host_1750)

    string = '<ul>'
    for host in hosts:
        device_string = '<li><strong>'+host['name']+':</strong> '+host['ip_address']+', '+host['mac_address']+'</li>'
        string += device_string

    string += '</ul>'
    sh.avm.devices.device_list(string)

get_phone_name
~~~~~~~~~~~~~~
Gibt den Namen eines Telefons an einem Index zurück. Der zurückgegebene Wert kann in 'set_call_origin' verwendet werden.

.. code-block:: python

    phone_name = sh.fb1.get_phone_name(1)

get_phone_numbers_by_name(name)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Durchsucht das Telefonbuch mit einem Namen nach nach Kontakten und liefert die zugehörigen Telefonnummern.

.. code-block:: python

    result_numbers = sh.fritzbox_7490.get_phone_numbers_by_name('Mustermann')
    result_string = ''
    keys = {'work': 'Geschäftlich', 'home': 'Privat', 'mobile': 'Mobil', 'fax_work': 'Fax', 'intern': 'Intern'}
    for contact in result_numbers:
        result_string += '<p><h2>'+contact+'</h2>'
        i = 0
        result_string += '<table>'
        while i < len(result_numbers[contact]):
            number = result_numbers[contact][i]['number']
            type_number = keys[result_numbers[contact][i]['type']]
            result_string += '<tr><td>' + type_number + ':</td><td><a href="tel:' + number + '" style="font-weight: normal;">' + number + '</a></td></tr>'
            i += 1
        result_string += '</table></p>'
    sh.general_items.number_search_results(result_string)

is_host_active
~~~~~~~~~~~~~~
Prüft, ob eine MAC Adresse auf dem Gerät aktiv ist. Das kann bspw. für die Umsetzung einer Präsenzerkennung genutzt
werden.

CURL for this function:

.. code-block:: bash

    curl --anyauth -u user:password "https://fritz.box:49443/upnp/control/hosts" -H "Content-Type: text/xml; charset="utf-8"" -H "SoapAction:urn:dslforum-org:service:Hosts:1#GetSpecificHostEntry" -d "<?xml version='1.0' encoding='utf-8'?><s:Envelope s:encodingStyle='http://schemas.xmlsoap.org/soap/encoding/' xmlns:s='http://schemas.xmlsoap.org/soap/envelope/'><s:Body><u:GetSpecificHostEntry xmlns:u='urn:dslforum-org:service:Hosts:1'><s:NewMACAddress>XX:XX:XX:XX:XX:XX</s:NewMACAddress></u:GetSpecificHostEntry></s:Body></s:Envelope>" -s -k

reboot
~~~~~~
Startet das Gerät neu.

reconnect
~~~~~~~~~
Verbindet das Gerät neu mit dem WAN (Wide Area Network).

set_call_origin
~~~~~~~~~~~~~~~
Setzt den 'call origin', bspw. vor dem Aufruf von 'start_call'. Typischerweise genutzt vor der Verwendung von "start_call".
Der Origin kann auch mit direkt am Fritzdevice eingerichtet werden: "Telefonie -> Anrufe -> Wählhilfe verwenden ->
Verbindung mit dem Telefon".

.. code-block:: python

    sh.fb1.set_call_origin("<phone_name>")

start_call
~~~~~~~~~~
Startet einen Anruf an eine übergebene Telefonnummer (intern oder extern).

.. code-block:: python

    sh.fb1.start_call('0891234567')
    sh.fb1.start_call('**9')

wol(mac_address)
~~~~~~~~~~~~~~~~
Sendet einen WOL (WakeOnLAN) Befehl an eine MAC Adresse.

get_number_of_deflections
~~~~~~~~~~~~~~~~~~~~~~~~~
Liefert die Anzahl der Rufumleitungen zurück.

get_deflection
~~~~~~~~~~~~~~
Liefert die Details der Rufumleitung der angegebenen ID zurück (Default-ID = 0)

get_deflections
~~~~~~~~~~~~~~~
Liefert die Details aller Rufumleitungen zurück.

set_deflection_enable
~~~~~~~~~~~~~~~~~~~~~
Schaltet die Rufumleitung mit angegebener ID an oder aus.


Web Interface
-------------

Das avm Plugin verfügt über ein Webinterface, mit dessen Hilfe die Items die das Plugin nutzen
übersichtlich dargestellt werden.

.. important::

   Das Webinterface des Plugins kann mit SmartHomeNG v1.4.2 und davor **nicht** genutzt werden.
   Es wird dann nicht geladen. Diese Einschränkung gilt nur für das Webinterface. Ansonsten gilt
   für das Plugin die in den Metadaten angegebene minimale SmartHomeNG Version.


Aufruf des Webinterfaces
~~~~~~~~~~~~~~~~~~~~~~~~

Das Plugin kann aus dem Admin-IF aufgerufen werden. Dazu auf der Seite Plugins in der entsprechenden
Zeile das Icon in der Spalte **Web Interface** anklicken.

Es werden nur die Tabs angezeigt, deren Funktionen im Plugin aktiviert sind bzw. die von Fritzdevice unterstützt werden.

Im WebIF stehen folgende Reiter zur Verfügung:

AVM AVM TR-064 Items
~~~~~~~~~~~~~~~~~~~~

Tabellarische Auflistung aller Items, die mit dem TR-064 Protokoll ausgelesen werden

.. image:: user_doc/assets/webif_tab1.jpg
   :class: screenshot

AVM AHA Items
~~~~~~~~~~~~~
Tabellarische Auflistung aller Items, die mit dem AHA Protokoll ausgelesen werden (Items der AVM HomeAutomation Geräte)

.. image:: user_doc/assets/webif_tab2.jpg
   :class: screenshot

AVM AHA Devices
~~~~~~~~~~~~~~~

Auflistung der mit der Fritzbox verbundenen AVM HomeAutomation Geräte

.. image:: user_doc/assets/webif_tab3.jpg
   :class: screenshot

AVM Call Monitor Items
~~~~~~~~~~~~~~~~~~

Tabellarische Auflistung des Anrufmonitors (nur wenn dieser konfiguriert ist)

.. image:: user_doc/assets/webif_tab4.jpg
   :class: screenshot

AVM Log-Einträge
~~~~~~~~~~~~

Listung der Logeinträge der Fritzbox

.. image:: user_doc/assets/webif_tab5.jpg
   :class: screenshot

AVM Plugin-API
~~~~~~~~~~

Beschreibung der Plugin-API

.. image:: user_doc/assets/webif_tab6.jpg
   :class: screenshot
