
.. index:: Plugins; webpush
.. index:: webpush

=======
webpush
=======

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left

Plugin zum Versenden von web push Nachrichten an Browser Clients.

Anforderungen
=============
Auf Client Seite wird ein Browser benötigt der web push Nachrichten unterstützt. Dies ist bei nahezu allen Browsern der
Fall. Lediglich bei einigen mobilen Android Geräten unterstützt der Standardbrowser diese Funktionalität nicht, wie
z.B. der MiBrowser auf Xiaomi Android Geräten. Für den größten Funktionsumfang von web push Nachrichten wird jedoch
der Chrome Browser empfohlen.

**Der web push Dienst erfordert SSL Verschlüsselung.** Auch selbst signierte Zertifikate werden bei manchen
Browsern wie z.B. dem Chrome nicht akzeptiert, Firefox hingegen funktioniert mit https über selbst signierte
Zertifikate.

ACHTUNG:
Der Firefox Browser auf Android enthält einen Bug, weshalb web push Nachrichten nicht immer zugestellt werden. Dazu
gibt es jedoch schon seit einiger Zeit ein Issue (https://github.com/mozilla-mobile/fenix/issues/19152).


Notwendige Software
-------------------

Für die Kommunikation wird die Python-Bibliothek pywebpush benötigt. Des weiteren wird py-vapid für die Schlüssel
Verwaltung benutzt.

Diese werden bei der ersten Verwendung des Plugins automatisch zu SmarthomeNG hinzugefügt.

|

Konfiguration
=============

Die Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
unter :doc:`/plugins_doc/config/webpush` beschrieben.

plugin.yaml
-----------

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.

.. code-block:: yaml

    webpush:
        plugin_name: webpush
        grouplist:
            - alarm
            - info

Items
-----

Für die Kommunikation und die Übertragung der Einstellungen vom Plugin an die Visu des Clients müssen die Items aus dem
webpush.basic Struct in der Konfiguration enthalten sein, ohne diese startet das Plugin nicht. Weiters sind diese
drei Items auch die notwendigen Parameter für das webpush.config Widget.

.. code-block:: yaml

    System:
        webpush:
            struct: webpush.basic

Funktionen
----------

Logik Funktion zum senden einer Nachricht an eine Gruppe:

**sh.webpush.sendPushNotification** (msg, group, title="", url="", requireInteraction=True, icon="", badge="", image="",
silent=False, vibrate=[], ttl=604800, highpriority=True, returnval=True, timestamp=True)

Die Funktion kann aber auch in einem eval oder on_change bzw. on_update Ausdruck verwendet werden, dazu ist der
returnval Parameter hilfreich z.B.:

.. code-block:: yaml

    TestBool:
        type: bool
        eval: sh.webpush.sendPushNotification("Test Bool" + str(value), "info", "INFO Bool", returnval=value)
    TestNum:
        type: num
        eval: sh.webpush.sendPushNotification("Test Num = 100", "alarm", "ALARM Num", returnval=value) if int(value)==100 else value

    TestBoolUpdate:
        type: bool
        on_update:
            - sh.webpush.sendPushNotification("Test Bool", "info", "INFO Bool", returnval=None) if int(value)==1 else None
    TestNumChange:
        type: num
        on_change:
            - sh.webpush.sendPushNotification("Test Num = 50", "alarm", "ALARM Num", returnval=None) if int(value)==50 else None
            - sh.webpush.sendPushNotification("Test Num = 100", "alarm", "ALARM Num", returnval=None) if int(value)==100 else None

Für eine genaue Beschreibung aller Parameter, bitte die aus der plugin.yaml erzeugte Dokumentation beachten.

Infos zum web push Standard sind unter folgenden Links zu finden:

[1] https://www.rfc-editor.org/rfc/rfc8030.txt

[2] https://developer.mozilla.org/en-US/docs/Web/API/ServiceWorkerRegistration/showNotification

[3] https://developer.mozilla.org/en-US/docs/Web/API/Push_API

Weitere Infos (aus [1] Seite 12) zum highpriority Parameter der die Urgency von normal auf high stellt:

.. list-table:: Urgency Parameter
   :widths: 15 45 40
   :header-rows: 1

   * - Urgency
     - Device State
     - Example Application Scenario
   * - very-low
     - On power and Wi-Fi
     - Advertisements
   * - low
     - On either power or Wi-Fi
     - Topic updates
   * - normal
     - On neither power nor Wi-Fi
     - Chat or Calendar Message
   * - high
     - Low battery
     - Incoming phone call or time-sensitive alert

|

SV Widget
=========

Nachfolgend sind die Parameter für das Widget aufgelistet.

.. code-block:: html

    {{ webpush.config(id, grouplist, publickey, fromclient, buttontext) }}

Eine Beispielhafte Verwendung könnte dabei so aussehen:

.. code-block:: html

    {{ webpush.config('', 'System.webpush.config.grouplist', 'System.webpush.config.publickey', 'System.webpush.comunication.fromclient', 'Übernehmen') }}

|

Web Interface
=============

Im Webinterface werden die Grundlegenden Parameter des Plugins angezeigt. Weiters ist dort eine Auflistung der Anzahl an
Abonnenten pro Gruppe gezeigt. Über einen Button kann die Datenbank geleert werden. Achtung dadurch werden alle
Abonnenten gelöscht und können nicht wiederhergestellt werden, jeder Client muss sich erneut zu Nachrichten Gruppen
anmelden.


Credits
=======

* SmartHome NG Team
* WebPush libraries Team (https://github.com/web-push-libs) and their [pywebpush](https://github.com/web-push-libs/pywebpush) and [py-vapid](https://github.com/web-push-libs/vapid) projects)
