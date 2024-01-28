.. index:: Plugins; influxdb
.. index:: influxdb

========
influxdb
========

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/influxdb` beschrieben.

/etc/influxdb/influxdb.conf
---------------------------

Wenn UDP verwendet wird, muss der UDP-Endpunkt explizit in influxdb aktiviert werden.
Der UDP-Endpunkt ist nicht auth-geschützt und ist an eine bestimmte Datenbank gebunden.

.. code-block:: yaml

   [[udp]]
     enabled = true
     bind-address = ":8089"
     database = "smarthome"
     # retention-policy = ""

Wenn Sie den HTTP-Zugang verwenden möchten, ist keine zusätzliche Konfiguration erforderlich, da der
HTTP-Zugriff auf die influxdb standardmäßig aktiviert ist.

plugin.yaml
-----------

Es können globale Tags und Felder angegeben werden:

.. code-block:: yaml

   influxdb:
       plugin_name: influxdb
       # host: localhost
       # udp_port: 8089
       # keyword: influxdb
       # value_field: value
       # write_http: True
       # http_port: 8086
       tags: '{"key": "value", "foo": "bar"}'
       fields: '{"key": "value", "foo": "bar"}'

items.yaml
----------

Logging in eine Messung namens ``root.some_item``, Standard-Tags und
Tags/Felder wie in plugin.yaml angegeben

.. code-block:: yaml

  root:
      some_item:
          influxdb: 'true'

Wenn ``keyword`` in der plugin.yaml auf ``sqlite`` gesetzt wird, kann dies auch
als Ersatz für sqlite verwendet werden.

.. code-block:: yaml

  root:
      some_item:
          sqlite: 'true'

*empfohlen*: Loggen der Messung ``temp`` mit einem zusätzlichen
Tag ``room`` und Standard-Tags (einschließlich ``item: root.dining_temp``) und
Tags/Felder wie in plugin.yaml angegeben

.. code-block:: yaml

  root:
      dining_temp:
          influxdb_name: temp
          influxdb_tags: '{"room": "dining"}'


In InfluxDB über UDP oder HTTP loggen
=====================================

Protokollierung von Elementen in der Zeitseriendatenbank
`InfluxDB <https://www.influxdata.com/time-series-platform/>`_

Dieses Plugin ist ein Fork von ``influxdata`` mit den folgenden
Erweiterungen:

- korrekte Namensgebung
- Angabe eines Namens für die Messung statt auf die ID des Elements zurückzugreifen
- zusätzliche Tags oder Felder global (plugin.yaml) und/oder pro Element

Die speziellen smarthomeNG Attribute ``caller``, ``source`` und ``dest``
werden immer als Tags protokolliert.

Nur wenn ein Messungsname angegeben wird, wird automatisch auch die ID des Elements
mitprotokolliert (Tag ``item``) - wenn Sie keinen Messungsnamen angeben,
wird der Name auf die ID des Items zurückgreifen, was den Item-Tag
überflüssig macht

Korrektes Logging
=================

Bitte lesen Sie die `Key Konzepte <https://docs.influxdata.com/influxdb/v1.8/concepts/key_concepts/>`_
und `Schema Design <https://docs.influxdata.com/influxdb/v1.8/concepts/schema_and_data_layout/>`_

Insbesondere diese:

- `Metadaten kodieren in Tags <https://docs.influxdata.com/influxdb/v1.8/concepts/schema_and_data_layout/#encode-meta-data-in-tags>`_
- `Vermeiden Sie die Kodierung von Daten in Messnamen <https://docs.influxdata.com/influxdb/v1.8/concepts/schema_and_data_layout/#avoid-encoding-data-in-measurement-names>`_
- Vermeiden Sie mehr als eine Information in einem Tag <https://docs.influxdata.com/influxdb/v1.8/concepts/schema_and_data_layout/#avoid-putting-more-than-one-piece-of-information-in-one-tag>`_

Daten aus dem Database Plugin transferieren
===========================================

Diese Anleitung wurde unter influxdb2 getestet und muss eventuell für influxdb1 adaptiert werden.

1. Pandas und influxdb_client Module für Python installieren
2. CSV-Dump aus dem Webinterface des Datenbank-Plugins herunterladen
3. Anpassen der Zugriffsparameter im unten stehenden Skript
4. Anpassen des Pfads zur CVS-Datei
5. Ausführen des Skripts
6. Abhängig von der Größe der Datenbank ist Geduld gefragt.


.. code-block:: python

    from influxdb_client import InfluxDBClient
    from influxdb_client.client.write_api import SYNCHRONOUS
    import pandas as pd


    # ----------------------------------------------
    ip = "localhost"
    port = 8086
    token = "******************"
    org = "smarthomeng"
    bucket = "shng"
    value_field = "value"
    str_value_field = "str_value"

    csvfile = "smarthomeng_dump.csv"
    # ----------------------------------------------


    client = InfluxDBClient(url=f"http://{ip}:{port}", token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    df = pd.read_csv(csvfile, sep=';', header=0)
    df = df.reset_index()

    num_rows = len(df.index)
    last_progress_percent = -1

    for index, row in df.iterrows():
      progress_percent = int((index/num_rows)*100)
      if last_progress_percent != progress_percent:
          print(f"{progress_percent}%")
          last_progress_percent = progress_percent

      p = {'measurement': row['item_name'], 'time': int(row['time']) * 1000000,
           'tags': {'item': row['item_name']},
           'fields': {value_field: row['val_num'], str_value_field: row['val_str']}
           }
      write_api.write(bucket=bucket, record=p)

    client.close()


Web Interface
=============

Das Plugin stellt kein Web Interface zur Verfügung.
