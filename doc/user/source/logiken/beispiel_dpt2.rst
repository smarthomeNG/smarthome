Darstellung von DPT 2 Werten
============================

Ziel
----

Items mit dem KNX DPT 2 (Zwangswert/Priorität) können in der Visu oder
CLI Plugin nicht korrekt ausgegeben werden. Ziel ist die Darstellung
dieser Werte.

Logik
-----

Diese Logik löst das Problem mit Hilfe eines Hilfsitems und dieser
Logik:

/usr/local/smarthome/logics/prio.py.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   #!/usr/bin/env python3
   # prio.py

   logger.info(trigger)

   source_item = sh.return_item(trigger['source'])
   prio = trigger['value']
   logger.debug("Trigger Item for Priority Logic: {0}, Value: {1}".format(source_item,prio))

   has_zwang = False

   search_id = source_item.id()+".zwangsstellung"
   for child in source_item.return_children():
       if child.id() == search_id:
           has_zwang = True

   if has_zwang:
       if prio == 0:
           source_item.zwangsstellung([0,0]) 
       elif prio == 1:
           source_item.zwangsstellung([0,1])
       elif prio == 2:
           source_item.zwangsstellung([1,0])
       elif prio == 3:
           source_item.zwangsstellung([1,1])
   else:
       logger.debug("Kein Zwangsstellungsitem.")


/usr/local/smarthome/etc/logic.yaml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   Prio:
       filename: prio.py
       watch_item: '*.zwangvalue'
       visu_acl: rw


Items
-----

/usr/local/smarthome/items/prio.yaml
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

       licht:
           zwangvalue:
               type: num
               knx_dpt: 5
               visu_acl: rw
               enforce_updates: no
               cache: yes
               zwangsstellung:
                   type: list
                   knx_send: 3/0/9
                   knx_dpt: 2
                   visu_acl: rw
                   knx_cache: 3/0/9
                   cache: False
                   enforce_updates: yes

