Nachdimmen von Leuchten
=======================

Ziel
----

Nachdimmen von Leuchten auf einen bestimmten Wert um das Licht nachts
gedimmt einzuschalten, obwohl es über einen Schalter mit voller
Helligkeit eingeschaltet wurde.

Logik
-----

Die Logik prüft ob globale oder lokale Voraussetzungen für das
Nachdimmen gegeben sind. Wenn ja wird gedimmt, ansonsten wird nichts
gemacht.

Das lokale Item überschreibt dabei das globale Item, somit lassen sich
Leuchten einzeln auf Uhrzeiten etc. konfigurieren, alle zentral oder
auch gemischt nachdimmen.

Nur wenn beim Item das “nachdimm_wert” Attribut konfiguriert ist, wird
durch die Logik nachgedimmt.

/usr/local/smarthome/logics/nachdimmen.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   #!/usr/bin/env python3
   # nachdimmen.py

   logger.info("Nachdimmen Logik gestartet")

   itemname = trigger['source']
   item = sh.return_item(itemname)

   if trigger['value'] == True:

       active = False
       has_local = False

       #schauen ob es ein lokales Steueritem gibt
       search_id = item.id()+".nachdimmen"
       for child in item.return_children():
            if child.id() == search_id:
                   has_local = True

       if has_local:
           if item.nachdimmen:
              logger.info("local active")
              active = True
       else:
           if sh.zentral.nachdimmen:
                logger.info("zentral active")
                active = True
       # Leuchte auf Wert aus 'nachdimm_wert: xx' dimmen
       if active:
           item.helligkeit(item.conf['nachdimm_wert'])
       else:
           logger.info("Nachdimmen Logik: Nachdimmen weder beim Objekt noch zentral aktiviert")

   else:
       logger.info("Nachdimmen Logik: Licht wird ausgeschaltet")


Die Logik aktiviert man unter ``etc/logics.yaml`` mit dem Eintrag von:

/usr/local/smarthome/etc/logics.yaml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   nachdimmen:
       filename: nachdimmen.py
       watch_item: '*:nachdimm_wert'


Items
-----

/usr/local/smarthome/items/zentral.yaml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   zentral:
       nachdimmen:
           type = bool
           knx_dpt: 1
           visu_acl: rw
           knx_send: 1/0/3
           knx_cache: 1/0/3
           uzsu:
               type: dict
               uzsu_item: zentral.nachdimmen
               cache: True
               visu_acl: rw


/usr/local/smarthome/items/nachdimm_test.yaml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   test:
       testlichtB:
           type: bool
           knx_dpt: 1
           visu_acl: rw
           knx_send: 7/7/5
           knx_cache: 7/7/5
           nachdimm_wert: 20
           helligkeit:
               type: num
               visu_acl: rw
               knx_dpt: 5
               knx_cache: 7/7/95
               enforce_updates: yes
               knx_send: 7/7/93

       testlicht:
           type: bool
           knx_dpt: 1
           visu_acl: rw
           knx_send: 7/7/1
           knx_cache: 7/7/2
           nachdimm_wert: 45
           nachdimmen:
               type: bool
               visu_acl: rw
           helligkeit:
               type: num
               visu_acl: rw
               knx_dpt: 5
               knx_cache: 7/7/85
               enforce_updates: yes
               knx_send: 7/7/83

           uszu:
               type: dict
               uzsu_item: test.testlicht.nachdimmen
               cache: True
               visu_acl: rw
