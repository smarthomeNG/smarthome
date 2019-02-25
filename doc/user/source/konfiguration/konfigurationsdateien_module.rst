.. index:: module

module.yaml
###########

Module sind eine Erweiterung des Cores und stellen den Plugins zusätzliche Funktionalitäten 
zur Verfügung. Sie bilden also eine erweiterte API für Plugin-Entwickler.

Da diese Funktionalitäten einen größeren Ressourcenbedarf haben, sind sie nicht fest in den
Programmcode des Cores aufgenommen worden, sondern als ladbare Module ausgeführt. Dadurch ist 
es möglich SmartHomeNG auch auf leistungsschwachen Systemen einzusetzen. Man muss nur auf den 
Einsatz der ladbaren Module verzichten.

Die ladbaren Module werden in der Datei **../etc/module.yaml** konfiguriert.

Details bitte dem Abschnitt **Konfiguration/Module** dieser Dokumentation entnehmen.

