
Änderungen ab v1.8
==================

Ab SmartHomeNG v1.8 sind für die vollständige smartVISU Unterstützung das **websocket** Modul und
das **smartvisu** Plugins zu konfigurieren.

.. code-block:: yaml
   :caption: Ausschnitt aus ``etc/module.yaml``

   websocket:
       module_name: websocket
   #    ip: 0.0.0.0
   #    port: 2424
   #    tls_port: 2425
   #    use_tls: True
   #    tls_cert: shng.cer
   #    tls_key: shng.key


.. code-block:: yaml
   :caption: Ausschnitt aus ``etc/plugin.yaml``

   smartvisu:
       plugin_name: smartvisu
   #    smartvisu_dir: /var/www/smartvisu
   #    generate_pages: False
   #    overwrite_templates: True
   #    visu_style: std
   #    default_acl: rw
   #    handle_widgets: True
   #    create_masteritem_file: True
   #    list_deprecated_warnings: False

Für die vollständige Dokumentation der Parameter bitte in der Dokumentation des Websocket Moduls und des
smartVISU Plugins auf den folgenden Seiten dieser Dokumentation nachlesen:

- für das **websocket** Modul unter :doc:`../konfiguration/module/module_websocket`
- für das **smartvisu** Plugin unter :doc:`../plugins/smartvisu/user_doc`
