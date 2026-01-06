
.. index:: Admin GUI; System
.. index:: System; Admin GUI

######
System
######


====================
System Eigenschaften
====================

.. index:: Systeminformation; Übersicht

Übersicht
=========

Die Übersichtsseite zeigt eine Reihe von Informationen über die SmartHomeNG Installation und das System an, auf dem
SmartHomeNG läuft.

.. image:: assets/system-info.jpg
   :class: screenshot



.. index:: Ressource Graphen
.. index:: Systemeigenschaften; Ressource Graphen

Ressource Graphen
=================

Das Tab mit den Resource Graphen zeigt Graphen über System Load, Anzahl Threads, Speicherbelegung und Plattennutzung an.
Drei dieser Graphen sind bereits aus der Konfigurationsseite der smartVISU bekannt.

.. image:: assets/system-ressource-graphs.jpg
   :class: screenshot


.. index:: PyPI Check
.. index:: Systemeigenschaften; PyPI Check

PyPI Check
==========

Das Tab PyPI Check zeigt Informationen über die Versionsstände von benötigten und installierten Python Packages an.
Dabei werden im ersten Block Informationen über Packages angezeigt, die vom Core benötigt werden. Im zweiten Block
werden Informationen über Packages gezeigt, die von Plugins benötigt werden.

Der letzte Block zeigt Informationen über weitere installierte Packages an.

.. image:: assets/system-pypi-check.jpg
   :class: screenshot

Zu jedem Package werden vier Spalten mit Versionsummern angezeigt. Die erste Spalte zeigt die **minimale Version** eines
Packages, die von SmartHomeNG bzw. den Plugins benötigt wird.

Die zweite Spalte zeigt die aktuell **installierte Version** des Packages an, gefolgt von einem Haken, falls diese Version
von SmartHomeNG bzw. den nutzenden Plugins unterstützt wird. Falls die installierte Version die neueste verfügbare Version
oder die maximal unterstützte Version ist, wird der Eintrag in grün dargestellt.

Die dritte Spalte zeigt die **maximale Version** an, die von SmartHomeNG unterstützt wird. Ein **Stern (Asterix)** zeigt
an, dass es keine definierte maximale Version gibt, dass also die neueste Version genutzt werden kann.

Die vierte Spalte zeigt die **Neueste Version** an, die von pypi.org bezogen werden kann. Wenn die neueste Version für die
SmartHomeNG Installation genutzt werden kann, wird neben der Versionsnummer ein Haken angzeigt. Falls sie installierte
Version nicht der neuesten Version entspricht, wird die neueste Version in grün dargestellt, um darauf hinzuweisen, dass
auf diese Version aktualisiert werden kann. Falls die neueste Version nicht genutzt werden kann, wenn sie also kleiner
als eine angegebene Maximalversion ist, wird die Versionsnummer in rot angezeigt.


.. index:: Urheberrechtshinweise
.. index:: Systemeigenschaften; Urheberrechtshinweise

Urheberrechtshinweise
=====================

Auf diesem Tab werden die Urheberrechtshinweise für die Komponenten angezeigt, die zur Erstellung der Administrationsoberfläche
genutzt wurden.

.. image:: assets/system-copyright.jpg
   :class: screenshot



.. index:: System Konfiguration

====================
System Konfiguration
====================

In der System Konfiguration können der Core und die Core Module konfiguriert werden.


.. index:: Konfiguraton; System, allgemein

Allgemein
=========

In diesem Tab werden die allgemeinen Einstellungen für SmartHomeNG konfiguriert. Es handelt sich hierbei um die Einstellungen,
die in der Konfigurationsdatei ../etc/smarthome.yaml abgelegt sind.

.. image:: assets/system-common.jpg
   :class: screenshot

Der Button ```Core neu starten``` wir erst aktiv, wenn geänderte Einstellungen gesichert wurden.


.. index:: Konfiguration; http Modul
.. index:: http Modul; Konfiguration (Admin GUI)

Http Modul
==========

Im Tab für das http Modul werden die Einstellungen für das http Modul konfiguriert. Die Anmeldeinformation wird sowohl
vom http Modul (Basic Auth), als auch vom Admin Modul (JWT Token) genutzt. Passworte werden hierbei nur als Hash in die
Konfiguration geschrieben und NICHT im Klartext. Ein vergessenes Passwort kann daher nicht wieder sichtbar gemacht werden.
Es handelt sich hierbei um die Einstellungen, die in der Konfigurationsdatei ../etc/module.yaml im Abschnitt http: abgelegt
sind.

.. image:: assets/system-http.jpg
   :class: screenshot


.. index:: Konfiguration; admin Modul
.. index:: admin Modul; Konfiguration

Admin Modul
===========

In diesem Tab werden die Einstellungen für das Admin Modul konfiguriert. Es handelt sich hierbei um die Einstellungen,
die in der Konfigurationsdatei ../etc/module.yaml im Abschnitt ``admin:`` abgelegt sind.

.. image:: assets/system-admin.jpg
   :class: screenshot

Falls ein Username und ein Password konfiguriert sind, steuern die folgenden zwei Parameter die Gültigkeitsdauer der
Anmeldung. Die Anmeldung wird über ein Token gesteuert, welches auch bei Beendigung des Browsers erhalen bleibt. Es
wird bei Klick auf den Abmelden Button gelöscht oder es verfällt nach Ablauf der Gültigkeitsdauer.

Der Parameter **login_experiation** legt die Gültigkeitsdauer (in Stunden) des bei der Anmeldung ausgestellten Tokens
fest. Falls eine kurze Gültigkeit gewünscht ist, können auch Werte kleiner 1 angegeben werden. (0.5 bedeutet z.B. eine
Gültigkeit von 30 Minuten).

Der Parameter **login_autorenew** legt fest, ob bei Nutzung des Administrations-Interfaces die Gültigkeit des Tokens
verlängert wird oder nicht. Wenn **login_autorenew** auf **true** gesetzt ist, wird bei einer Nutzung des
Administrations-Interfaces nach Ablauf der halben Gültigkeits-Dauer das Token erneuert, so dass es wieder die volle
mit **login_experiation** festgelegte Dauer gültig ist.


.. index:: Konfiguration; mqtt Modul
.. index:: mqtt Modul; Konfiguration

MQTT Modul
==========

In diesem Tab werden die Einstellungen für Nutzung des MQTT Protokolls konfiguriert. Es handelt sich hierbei um die
Einstellungen, die in der Konfigurationsdatei ../etc/module.yaml im Abschnitt ``mqtt:`` abgelegt sind.

.. image:: assets/system-mqtt.jpg
   :class: screenshot

