.. index:: Plugins; slack (Slack Benachrichtigungsdienst)
.. index:: slack

=====
slack
=====

Das slack-Plugin sendet Push-Benachrichtigungen an einen oder mehrere Slack-Workspaces.


Voraussetzungen
===============

Im Ziel-Workspace muss ein Incoming Webhook eingerichtet werden. Der dabei erzeugte Token wird für
die Konfiguration des Plugins benötigt:

1. Unter ``https://<team>.slack.com/apps/new/A0F7XDUAZ-incoming-webhooks`` einen neuen Webhook anlegen.
2. Dabei einen Kanal des Workspace auswählen.
3. Den im Webhook enthaltenen Token in ``etc/plugin.yaml`` eintragen.

Ein Token erlaubt das Posten in alle Kanäle des zugehörigen Workspace.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/slack` beschrieben.

Für mehrere Slack-Workspaces oder mehrere Token wird das Plugin mehrfach instanziiert, jeweils mit
eigenem **instance**-Namen und eigenem **token**. Nachrichten werden dann über die jeweilige
Instanz verschickt, z.B. ``sh.SlackInstance_1.notify(...)`` bzw. ``sh.SlackInstance_2.notify(...)``.

Die vom Plugin bereitgestellte Funktion **notify()** ist unter :doc:`/plugins_doc/config/slack`
beschrieben. Zur Formatierung von Nachrichten (fett, unterstrichen, Links, Emojis, mehrzeilig)
siehe die `Slack-Dokumentation <https://api.slack.com/docs/message-formatting>`_.
