.. index:: Plugins; xmpp
.. index:: xmpp

====
xmpp
====

Das Plugin verbindet SmartHomeNG über das Extensible Messaging and Presence Protocol (XMPP) mit
einem Jabber/XMPP-Konto. Es unterstützt aktuell nur das Senden von Nachrichten, empfangene
Nachrichten werden ignoriert.

Voraussetzungen
================

Für verschlüsselte Chats (OTR über XEP-0384) muss zusätzlich
`slixmpp-omemo <https://pypi.org/project/slixmpp-omemo/>`_ manuell installiert werden.

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/xmpp`
beschrieben.

Nachrichten werden aus Logiken heraus über die Funktion **send()** verschickt, siehe
:doc:`/plugins_doc/config/xmpp`::

    sh.xmpp.send("skender@somexmppserver.me", "ALARM: Triggered, Danger.", 'chat')

XMPP als Logging-Handler
=========================

Das Plugin kann auch als Logging-Handler eingebunden werden, um Log-Meldungen von SmartHomeNG per
XMPP an einen Chat- oder Gruppenchat-Kontakt zu senden. Dazu wird in ``etc/logging.yaml`` ein
Handler auf Basis des Plugins definiert::

    handlers:
        xmpp:
            class: plugins.xmpp.XMPPLogHandler
            formatter: shng_simple
            xmpp_plugin: xmpp
            xmpp_receiver: room@conference.example.com
            xmpp_receiver_type: groupchat
    loggers:
        xmpp:
            handlers: [xmpp]
            level: WARN

**xmpp_plugin** verweist auf die Instanz des xmpp-Plugins, über die versendet werden soll.
**xmpp_receiver** und **xmpp_receiver_type** (``chat`` oder ``groupchat``) legen den
Ziel-Kontakt fest.

Auf diese Weise lässt sich z.B. auch ein einzelnes Operationlog gezielt per XMPP versenden::

    loggers:
        plugins.operationlog.alarms:
            handlers: [xmpp]
            level: INFO
