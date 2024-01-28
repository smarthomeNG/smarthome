.. index:: Plugins; asterisk
.. index:: asterisk


========
asterisk
========


.. image:: webif/static/img/plugin_logo.svg
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Ansteuerung einer **Asterisk** Telefonanlage 


Anforderungen
=============

...

Notwendige Software
-------------------

Für den Betrieb wird vorausgesetzt das eine Version von Asterisk installiert ist und der entsprechende Daemon läuft.
Es ist ebenfalls notwendig, das das Asterisk Manager Interface (AMI) installiert und funktionell ist.
In der ``manager.config`` muss mindestens
``read = system,call,user,cdr`` und ``write = system,call,orginate``
eingerichtet sein.

Unterstützte Geräte
-------------------

<Hier werden unterstützte Geräte beschrieben. Falls keine keine speziell zu beschreibenden Geräte unterstützt
werden, kann dieser Abschnitt entfallen.>


Konfiguration
=============

Die Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/asterisk` beschrieben.


plugin.yaml
-----------

Zu den Informationen, welche Parameter in der ../etc/plugin.yaml konfiguriert werden können bzw. müssen, bitte
bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/asterisk>` lesen, die aus
den Metadaten der plugin.yaml erzeugt wurde (siehe oben).

<Hier können bei Bedarf ausführliche Beschreibungen zu den Parametern dokumentiert werden.>

items.yaml
----------

Zu den Informationen, welche Attribute in der Item Konfiguration verwendet werden können bzw. müssen, bitte
bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/asterisk>` lesen, die aus
den Metadaten der plugin.yaml erzeugt wurde (siehe oben).

.. code:: yaml

    buero:
        telefon:
            type: bool
            ast_dev: 2222
            ast_db: active/buero

            box:
                type: num
                ast_box: 22


Bei einem Anruf bei ``2222`` von einem SIP client oder 
bei Anruf von dem entsprechenden Gerät wird das Item ``buero.telefon`` auf ``True`` gesetzt.
Wird der Anruf beendet, so wird das Item ``buero.telefon`` auf ``False`` gesetzt.

ast_dev
~~~~~~~

Dieses keyword kann bei einem Item mit Typ Bool verwendet werden.
Der Parameter für dieses keyword ist ein String, der identisch zu einer Gerätebenennung in der sip.conf ist.
Im unteren Beispiel also ``device22``:

.. code:: ini

    [device22]
    secret=very
    context=internal

ast_db
~~~~~~

Gibt den Databank Eintrag an der bei einer Item Änderung aktualisiert wird

ast_box
~~~~~~~

Hier wird die Mailbox Nummer des Telefones eingegeben. Die Anzahl der neuen Nachrichten wird dann an dieses Item übermittelt
logic.yaml
----------

Zu den Informationen, welche Konfigurationsmöglichkeiten für Logiken bestehen, bitte
bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/asterisk>` lesen, die aus
den Metadaten der plugin.yaml erzeugt wurde (siehe oben).

Beispiel für eine Logik:

..code:: yaml

    logic1:
        ast_userevent: Call

    logic2:
        ast_userevent: Action

Für jede Logik kann in der ``logic.yaml`` das keyword ``ast_userevent`` angegeben werden.

In der Asterisk ``extensions.conf`` muss dann  angegeben werden
``exten => _X.,n,UserEvent(Call,Source: ${CALLERID(num)},Value: ${CALLERID(name)})`` 

Damit würde die ``logic1`` jedesmal getriggert, wenn das UserEvent geschickt wird.

A specified destination for the logic will be triggered e.g. 
``exten => _X.,n,UserEvent(Call,Source: ${CALLERID(num)},Destination: Office,Value: ${CALLERID(name)})``


Funktionen
----------

Zu den Informationen, welche Funktionen das Plugin bereitstellt (z.B. zur Nutzung in Logiken), bitte
bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/asterisk>` lesen, die aus
den Metadaten der plugin.yaml erzeugt wurde (siehe oben).

call(source, dest, context, callerid=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``sh.ast.call('SIP/200', '240', 'door')`` 
würde einen Anruf von der SIP extension ``200`` zur extention ``240`` starten mit dem ``door`` context.
Optional kann eine callerid mit angegeben werden


db_write(key, value)
~~~~~~~~~~~~~~~~~~~~

``sh.ast.db_write('dnd/office', 1)``  würde den Asterisk Datenbank Eintrag ``dnd/office`` auf ``1`` setzen

db_read(key)
~~~~~~~~~~~~

``dnd = sh.ast.db_read('dnd/office')`` würde ``dnd`` auf den Wert des Asterisk Datenbank Eintrages ``dnd/office`` setzen.

mailbox_count(mailbox, context='default')
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``mbc = sh.ast.mailbox_count('2222')`` würde ``mbc`` auf ein Wertetupel ``(old_messages, new_messages)`` setzen.

hangup(device)
~~~~~~~~~~~~~~

``sh.ast.hangup('30')`` would close all connections from or to the device ``30``.


..  todo ist noch die Implementation des
    Web Interface
    =============

    Das Plugin hat aktuell kein Webinterface

    Tab 1: <Name des Tabs>
    ----------------------

    <Hier wird der Inhalt und die Funktionalität des Tabs beschrieben.>

    .. image:: assets/webif_tab1.jpg
       :class: screenshot

    <Zu dem Tab ist ein Screenshot im Unterverzeichnis ``assets`` des Plugins abzulegen.

