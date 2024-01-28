.. index:: Plugins; mailrcv
.. index:: mailrcv

=======
mailrcv
=======

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 400px
   :height: 308px
   :scale: 50 %
   :align: left

Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/mailrcv` beschrieben.

plugin.yaml
-----------

.. code:: yaml

   imap:
       plugin_name: mailrcv
       host: mail.example.com
       username: smarthome
       password: secret
       # tls: False
       # port: default
       # cycle: 300

Logiken
=======

Wenn eine Logik durch dieses Plugin ausgelöst wird, setzt es den Trigger
``source`` auf die Absenderadresse und der ``value`` enthält ein `Email
Objekt <https://docs.python.org/3.9/library/email.message.html>`_.

Sie können die folgenden Schlüsselwörter einer Logik zuordnen. Die Reihenfolge der Zuordnung
ist wie aufgeführt:

mail_subject
------------

Wenn der Betreff der eingehenden E-Mail mit dem Wert dieses Schlüssels übereinstimmt,
wird die Logik ausgelöst.

mail_to
-------

Wenn die E-Mail an die angegebene Adresse gesendet wird, wird die Logik ausgelöst.

Wenn gmail verwendet wird, können Sie mehrere Logiken mit einem Konto auslösen -
Erweitern Sie einfach die E-Mail Adresse mit dem `+ Zeichen <https://gmail.googleblog.com/2008/03/2-hidden-ways-to-get-more-from-your.html>`__
(z.B. benutzen Sie ``myaccount+logicname@gmail.com`` um ``logicname`` auszulösen)

Aus Sicherheitsgründen sollten Sie nur ein spezielles gmail-Konto mit diesem Plugin verwenden
und filtern Sie Nachrichten von unbekannten Absendern herausfiltern (z.B. erstellen Sie den Filter
``from:(-my_trusted_mail@example.com)`` mit Aktion archivieren oder löschen)

mail
----

Ein allgemeines Flag, um die Logik beim Empfang einer Mail auszulösen.

.. important::

      Es kann nur eine Logik pro Mail aufgerufen werden. Wenn eine Mail von einer Logik verarbeitet wird, wird sie gelöscht (in den Ordner "Gelöscht" verschoben).

Es gibt keine E-Mail-Sicherheit. Sie müssen eine Infrastruktur verwenden, die Sicherheit bietet
(z.B. ein eigener Mailserver, der nur authentifizierte Nachrichten für den Posteingang akzeptiert).

.. code-block:: yaml

   sauna:
       filename: sauna.py
       mail_to: sauna@example.com

   mailbox:
       filename: mailbox.py
       mail: 'yes'

Eine Mail an ``sauna@example.com`` wird nur die Logik 'Sauna' auslösen.
Alle anderen Mails werden von der Logik "Mailbox" verarbeitet.

Web Interface
=============

Das Plugin stellt kein Web Interface zur Verfügung.
