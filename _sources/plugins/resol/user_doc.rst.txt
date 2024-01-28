.. index:: Plugins; resol (Resol Unterstützung)
.. index:: resol

=====
resol
=====

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Allgemein
=========

Resol plugin, mit Unterstützung für Resol Solar Datenlogger, Frischwasserwärmetauscher und Regler.

`Resol Webseite <http://www.resol.de/index/produktdetail/kategorie/4/id/8/sprache/de>`_
`Cosmo Solarregelung <http://www.cosmo-info.de/fileadmin/user_upload/DL/COSMO-Solarregelung/COSMO-Multi.pdf>`_


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/resol` beschrieben.


Beispiel
========

.. code-block:: yaml

  resol:
    resol_source: '0x7821'
    resol_destination: '0x0010'
    resol_command: '0x0100'

    temperature_soll:
        type: num
        visu_acl: ro
        enforce_updates: 'true'
        resol_offset: 24
        resol_bituse: 7
        resol_factor:
         - '1.0'

    temperatur_2:
        type: num
        visu_acl: ro
        enforce_updates: 'true'
        resol_offset: 2
        resol_bituse: 15
        resol_factor:
         - '0.1'
         - '25.6'

    waermemenge:
        type: num
        visu_acl: ro
        enforce_updates: 'true'
        resol_offset: 28
        resol_bituse: 48
        resol_factor:
         - '1'
         - '256'
         - '1000'
         - '256000'
         - '1000000'
         - '256000000'

    solar:
        resol_source@solar: '0x7721'
        resol_destination@solar: '0x0010'
        resol_command@solar: '0x0100'

        sensordefektmaske:
            type: num
            visu_acl: ro
            resol_offset@solar: 36
            resol_bituse@solar: 16
            resol_factor@solar:
             - '1.0'
             - '256.0'

        temperatur_1:
            name: 'Temperature Kollektor'
            type: num
            visu_acl: ro
            database: init
            database_maxage: 62
            resol_offset@solar: 0
            resol_bituse@solar: 16
            resol_factor@solar:
             - '0.1'
             - '25.6'
            resol_isSigned@solar:
             - False
             - True

Resol Protokoll
===============

Informationen
-------------

Weitere Informationen zu Resol Parametern und Quellen sind hier zu finden:

`Github <https://github.com/danielwippermann/resol-vbus>`_
`Daniel Wippermann <https://danielwippermann.github.io/resol-vbus/#/vsf>`_

Über die Installation der Resol Software Service Center können weitere Offsets und Bitmasken ausgelesen werden.
Diese werden im XML Format von RESOL als Teil der RSC Software (Resol Service Center) bereitgestellt. Hierzu
einfach download, installieren (unter Linux ``wine`` nutzen) und die benötigten XML Dateien von hier beziehen: {Install_dir}/eclipse/plugins/de.resol.servicecenter.vbus.resol_2.0.0/ -

Sync byte zwischen verschiedenen Messages: 0xAA

Message:
=============== =========================================================================
Byte(s)                Inhalt
=============== =========================================================================
0-1               Destination
2-3               Source
4                 Protocol Version,        0x10 -> "PV1", 0x20 -> "PV2", 0x30 -> "PV3"
5-6               Command
7-8               Frame count,             Example 0x1047-> 104 bytes
=============== =========================================================================
