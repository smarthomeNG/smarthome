############################
Visualisierung mit smartVISU
############################

Visu Unterstützung ab SmartHomeNG v1.2
======================================

Überblick
---------

Im Release 1.2 wurde die Unterstützung für die smartVISU weiterentwickelt. Dabei wurde das
Visu Plugin durch zwei neue Plugins ersetzt.

In SmartHomeNG v1.2 und v1.3 wurden die smartVISU Versionen v2.7 und v2.8 unterstützt.
In SmartHomeNG v1.4 kommt Unterstützung für smartVISU Versionen v2.9 hinzu.

- Das erste Plugin (**visu_websocket**) implementiert das Websocket Protokoll über das smartVISU
  mit SmartHomeNG kommuniziert.
- Das zweite Plugin (**visu_smartvisu**) implementiert die aus den bisherigen Releases bekannte
  Möglichkeit zur automatischen Generierung von smartVISU Seiten. Diese Funktion wurde stark
  erweitert. Weiterhin ermöglicht dieses Plugin die Installation von Widgets in die smartVISU,
  die die Entwickler von SmartHomeNG Plugins geschrieben und ihren Plugins beigefügt haben.

Das smartVISU Plugin implementiert:

- eine erweiterte Möglichkeit zum automatischen Generieren von smartVISU Seiten
- die Fähigkeit zur Widget Installation in die smartVISU, die es Plugin Entwicklern ermöglicht,
  mit ihrem  Plugin smartVISU Widgets auszuliefern.


Änderungen in der Konfiguration ab SmartHomeNG v1.2
---------------------------------------------------

In den bisherigen Releases von smarthome bzw. SmartHomeNG wurde die Visualisierungsunterstützung
in der Datei **../etc/plugin.yaml** folgendermaßen konfiguriert:

.. code-block:: yaml
   :caption: Ausschnitt aus **../etc/plugin.yaml**

   visu:
       class_name: WebSocket
       class_path: plugins.visu
   #    ip: 0.0.0.0
   #    port: 2424
       smartvisu_dir: /var/www/smartvisu
   #    acl: rw
   

Ab v1.2 sind für die vollständige smartVISU Unterstützung zwei Plugins an Stelle des bisherigen
visu Plugins zu konfigurieren.

.. code-block:: yaml
   :caption: Ausschnitt aus **../etc/plugin.yaml**

   websocket:
       class_name: WebSocket
       class_path: plugins.visu_websocket
   #    ip: 0.0.0.0
   #    port: 2424
   #    tls: no
   #    wsproto: 4
       acl: rw

   smartvisu:
       class_name: SmartVisu
       class_path: plugins.visu_smartvisu
       smartvisu_dir: /var/www/smartvisu
   #    generate_pages: True
   #    handle_widgets: True
   #    overwrite_templates: Yes
   #    visu_style: blk


Für die vollständige Dokumentation der Parameter bitte in den README Dateien der beiden Plugins
oder auf den folgenden Seiten dieser Dokumentation nachlesen:

- für das **visu_websocket** unter :doc:`../plugins/visu_websocket/README`
- für das **visu_smartvisu** unter :doc:`../plugins/visu_smartvisu/README`

Falls die Funktionalitäten zur automatischen Generierung von smartVISU Seiten und zur Installation
von Widgets in die smartVISU nicht benötigt werden, ist es hinreichend das Plugin **visu_websocket**
zu konfigurieren.


.. toctree::
   :maxdepth: 4
   :hidden:
   :titlesonly:

   visualisierung_kommunikation
   visualisierung_autogenerierung
   visualisierung_widgets
