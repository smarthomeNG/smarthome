
Änderungen ab v1.8
==================

Ab SmartHomeNG v1.8 sind für die vollständige smartVISU Unterstützung das **websocket** Modul und
das **smartvisu** Plugins zu konfigurieren.

.. code-block:: yaml
   :caption: Ausschnitt aus **../etc/module.yaml**

   websocket:
       module_name: websocket
   #    ip: 0.0.0.0
   #    port: 2424
   #    tls_port: 2425
   #    use_tls: True
   #    tls_cert: shng.cer
   #    tls_key: shng.key


.. code-block:: yaml
   :caption: Ausschnitt aus **../etc/plugin.yaml**

   smartvisu:
       plugin_name: smartvisu
   #    smartvisu_dir: /var/www/smartvisu
   #    generate_pages: True
   #    overwrite_templates: Yes
   #    visu_style: blk
   #    default_acl: rw
   #    handle_widgets: True
   #    list_deprecated_warnings: False


Für die vollständige Dokumentation der Parameter bitte in der Dokumentation des Websocket Moduls und des
smartVISU Plugins auf den folgenden Seiten dieser Dokumentation nachlesen:

- für das **websocket** unter :doc:`../konfiguration/module/module_websocket`
- für das **smartvisu** unter :doc:`../plugins/smartvisu/user_doc`

Falls die Funktionalitäten zur automatischen Generierung von smartVISU Seiten und zur Installation
von Widgets in die smartVISU nicht benötigt werden, ist es hinreichend das Modul **websocket**
zu konfigurieren.

