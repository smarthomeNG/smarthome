helios_tcp
==========

Das helios_tcp-Plugin erlaubt die Abfrage von neuern Lüftungsanlagen der Firma Helios.


Voraussetzungen
---------------
Die Lüftungsanlage ...
- ... ist mit Helios easyControls ausgestattet
- ... läuft mindestens unter Firmware-Version 2.01
- ... ist mit dem lokalen Netzwerk verbunden
- ... hat "Modbus" unter Konfiguration --> Gerät aktiviert

  
Einrichtung
-----------
pymodbus3 muss installiert sein. Weiterhin ist das Plugin in der plugin.yml zu aktivieren::

  helios_tcp:
      class_name: HeliosTCP
      class_path: plugins.helios_tcp
      helios_ip: < IP-Adresse des Lüftungsgeräts >
      update_cycle: < Abstand in Sekunden, nachdem die Werte aktualisiert werden sollen >


Verknüpfung von Items
---------------------

Ein Item wird mit dem entsprechenden Werte der Lüftungsanlage gefüllt, indem die Eigenschaft ``helios_tcp`` auf
den Namen der entsprechenden Variable gesetzt wird. Beispiel::

  Zulufttemperatur:
      type: num
      helios_tcp: incoming_temp

Variablen
---------

Die folgenden Variablen stehen zur Verfügung und können abgefragt werden.

Einige Werte stehen je nach Systemkonfiguration nicht in jeder Lüftungsanlage zur Verfügung.

======================== ============================================== ========    ==========  =====   =====
Variable                 Beschreibung                                   Datentyp    Schreibbar  Min     Max    
======================== ============================================== ========    ==========  =====   =====
outside_temp             Temperatur Außenluft                           float    
exhaust_temp             Temperatur Abluft                              float    
inside_temp              Temperatur Fortluft                            float    
incoming_temp            Temperatur Zuluft                              float    
pre_heating_temp         VHZ Kanalfüler (-Außenluft- T5)                float    
post_heating_temp        NHZ Kanalfühler (-Zuluft- T6)                  float    
post_heating_reflux_temp NHZ Rücklauffühler (-Warmwasser-Register- T7)  float    
error_count              Anzahl der Fehler                              int      
warning_count            Anzahl der Warnungenint                        int      
info_count               Anzahl der Infos                               int      
fan_in_rpm               Zuluft rpm                                     int      
fan_out_rpm              Abluft rpm                                     int      
internal_humidity        Interner Luftfeuchtigkeitsfühler               int      
sensor1_humidity         Externer Fühler KWL-FTF Feuchte 1              int      
sensor2_humidity         Externer Fühler KWL-FTF Feuchte 2              int      
sensor3_humidity         Externer Fühler KWL-FTF Feuchte 3              int      
sensor4_humidity         Externer Fühler KWL-FTF Feuchte 4              int      
sensor5_humidity         Externer Fühler KWL-FTF Feuchte 5              int      
sensor6_humidity         Externer Fühler KWL-FTF Feuchte 6              int      
sensor7_humidity         Externer Fühler KWL-FTF Feuchte 7              int      
sensor8_humidity         Externer Fühler KWL-FTF Feuchte 8              int      
sensor1_temperature      Externer Fühler KWL-FTF Temp 1                 float    
sensor2_temperature      Externer Fühler KWL-FTF Temp 2                 float    
sensor3_temperature      Externer Fühler KWL-FTF Temp 3                 float    
sensor4_temperature      Externer Fühler KWL-FTF Temp 4                 float    
sensor5_temperature      Externer Fühler KWL-FTF Temp 5                 float    
sensor6_temperature      Externer Fühler KWL-FTF Temp 6                 float    
sensor7_temperature      Externer Fühler KWL-FTF Temp 7                 float    
sensor8_temperature      Externer Fühler KWL-FTF Temp 8                 float    
sensor1_co2              Externer Fühler KWL-CO2 1                      float    
sensor2_co2              Externer Fühler KWL-CO2 2                      float    
sensor3_co2              Externer Fühler KWL-CO2 3                      float    
sensor4_co2              Externer Fühler KWL-CO2 4                      float    
sensor5_co2              Externer Fühler KWL-CO2 5                      float    
sensor6_co2              Externer Fühler KWL-CO2 6                      float    
sensor7_co2              Externer Fühler KWL-CO2 7                      float    
sensor8_co2              Externer Fühler KWL-CO2 8                      float    
sensor1_voc              Externer Fühler KWL-VOC 1                      float    
sensor2_voc              Externer Fühler KWL-VOC 2                      float    
sensor3_voc              Externer Fühler KWL-VOC 3                      float    
sensor4_voc              Externer Fühler KWL-VOC 4                      float    
sensor5_voc              Externer Fühler KWL-VOC 5                      float    
sensor6_voc              Externer Fühler KWL-VOC 6                      float    
sensor7_voc              Externer Fühler KWL-VOC 7                      float    
sensor8_voc              Externer Fühler KWL-VOC 8                      float    
filter_remaining         Restlaufzeit                                   int      
boost_remaining          Partybetrieb Restzeit                          int      
sleep_remaining          Ruhebetrieb Restzeit                           int      
fan_level_percent        Prozentuale Lüfterstufe                        int      
bypass_open              Bypass geöffnet                                bool     
humidity_control_status  Feuchte-Steuerung Status                       int         X           0       2
humidity_control_target  Feuchte-Steuerung Sollwert                     int         X           20      80
co2_control_status       CO2-Steuerung Status                           int         X           0       2
co2_control_target       CO2-Steuerung Sollwert                         int         X           300     2000
voc_control_status       VOC-Steuerung Status                           int         X           0       2
voc_control_target       VOC-Steuerung Sollwert                         int         X           300     2000
comfort_temperature      Behaglichkeitstemperatur                       float       X           10      25
fan_in_voltage_level1    Spannung Lüfterstufe 1 Zuluft                  float       X           1.6     10
fan_out_voltage_level1   Spannung Lüfterstufe 1 Abluft                  float       X           1.6     10
fan_in_voltage_level2    Spannung Lüfterstufe 2 Zuluft                  float       X           1.6     10
fan_out_voltage_level2   Spannung Lüfterstufe 2 Abluft                  float       X           1.6     10
fan_in_voltage_level3    Spannung Lüfterstufe 3 Zuluft                  float       X           1.6     10
fan_out_voltage_level3   Spannung Lüfterstufe 3 Abluft                  float       X           1.6     10
fan_in_voltage_level4    Spannung Lüfterstufe 4 Zuluft                  float       X           1.6     10
fan_out_voltage_level4   Spannung Lüfterstufe 4 Abluft                  float       X           1.6     10
manual_mode              Betriebsart (1 = Handbetrieb)                  bool        X           0       1
filter_change            Filterwechselbool                              bool        X           0       1
filter_changeinterval    Wechselintervall in Monaten                    int         X           0       12
bypass_roomtemperature   Bypass Raumtemperatur                          int         X           10      40
bypass_minoutsidetemp    Bypass minimale Außentemperatur                int         X           5       20
fan_level                Lüfterstufe                                    int         X           0       4
fan_in_level             Lüfterstufe Zuluft                             int         X           0       4
fan_out_level            Lüfterstufe Abluft                             int         X           0       4
boost_duration           Partybetrieb Dauer                             int         X           5       180
boost_level              Partybetrieb Lüfterstufe                       int         X           0       4
boost_on                 Partybetrieb aktivieren / abbrechen            bool        X           0       1
sleep_duration           Ruhebetrieb Dauer                              int         X           5       180
sleep_level              Ruhebetrieb Lüfterstufe                        int         X           0       4
sleep_on                 Ruhebetrieb aktivieren / abbrechen             bool        X           0       1
preheating_status        Vorheizung Status                              bool        X           0       1
======================== ============================================== ========    ==========  =====   =====

Über die Modbus-Schnittstelle stellt die Lüftungsanlage noch weitere Attribute zur Verfügung, die aktuell
nicht durch das Plugin abrufbar sind. Im Dokument "Modbus Gateway TCP/IP" von Helios (auffindbar durch Google oder auf der Helios-Website)
sind diese dokumentiert. Sollte noch ein weiteres Attribut benötigt werden, kann dieses einfach in die __init__.py des Plugins aufgenommen werden,
indem die Variable ``VARLIST`` entsprechend ergänzt wird. Außerdem ist das Attribut dann in der plugin.yml in der valid_list der
item_attributes aufzunehmen.
