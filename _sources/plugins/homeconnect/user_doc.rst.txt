.. index:: Plugins; homeconnect
.. index:: homeconnect

===========
homeconnect
===========

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Das Plugin bindet Hausgeräte an, die über die
`BSH/Siemens HomeConnect-Schnittstelle <https://www.home-connect.com/>`_ verwaltet werden. Der
Zugriff erfolgt per OAuth2.

Voraussetzungen
================

Für den Zugriff wird neben einem regulären HomeConnect-Konto eine Registrierung als Entwickler
unter `developer.home-connect.com <https://developer.home-connect.com/>`_ benötigt, um eine
**Client ID** und ein **Client Secret** zu erhalten.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/homeconnect`
beschrieben.

Web Interface
=============

Über das Webinterface wird der OAuth2-Autorisierungsprozess gestartet und der aktuelle
Token-Status angezeigt.

.. important::

   Ohne eine erfolgreiche OAuth2-Autorisierung über das Webinterface liefert das Plugin keine
   Daten. War die SmartHomeNG-Instanz zu lange offline, läuft der gespeicherte Token ab; der
   Autorisierungsprozess muss dann über das Webinterface wiederholt werden. Fehler werden in
   diesem Fall im Log vermerkt.

Der Tab **OAuth2 Data** enthält den Link zum Start der Autorisierung sowie Ablaufzeit, Scope und
Refresh Token des aktuellen Tokens.

Der Tab **Plugin-API** listet die vom Plugin bereitgestellten, aus Logiken aufrufbaren Funktionen
mit Beschreibung und Parametern auf.

Der Tab **Appliances** zeigt die über HomeConnect registrierten Geräte, einschließlich der
**haId**, die für die Item-Attribute **ha_id** benötigt wird.
