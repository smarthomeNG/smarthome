prowl
=====

Anforderungen
-------------

Es wird ein Prowl-Konto mit einem API-Key benötigt, um den Dienst nutzen zu können.


Konfiguration
-------------

plugin.yaml
~~~~~~~~~~~

Das Attribut ``apikey`` gibt den API-Key für das Plugin an. Es ist möglich, beim Aufruf der Funktion ``notify()`` einen abweichenden API-Key anzugeben.


items.yaml
~~~~~~~~~~

Die Attribute ``prowl_event`` und ``prowl_text`` geben die Werte für das Ereignis und die Beschreibung des Ereignisses für die Nachricht an. Bei beiden Feldern wird der Text ``VAL`` durch den Wert des Items ersetzt. Ein Beispiel:

..code: yaml

	typ2:
		type: str
		prowl_event: 'Nachricht von shng'
		prowl_text: 'Item typ2 hat jetzt den Wert "VAL"'


Unter ``prowl_values`` kann eine Liste von `Wert: "Text"`-Paaren angegeben werden. Wenn das Item einem der angegebenen Werte entspricht, wird der jeweilige Text gesendet, ggf. statt des Textes aus ``prowl_text``. Ein Beispiel:

..code: yaml

	typ3:
		type: bool
		prowl_event: 'Änderung von typ3'
		prowl_values:

			- true: 'typ3 ist an'
			- false: 'typ3 ist aus'


Wenn der aktuelle Item-Wert nicht in der Liste von ``prowl_values`` erscheint, wird der Text aus ``prowl_text`` gesendet. Falls dieser nicht definiert ist, wird keine Nachricht gesendet.

Damit ist es möglich, Nachrichten nur bei bestimmten Werten zu senden.


Der Parameter ``prowl_swap`` bewirkt, dass die Texte für Ereignis und Beschreibung unmittelbar vor dem Senden vertauscht werden. Alle wertbezogenen Auswahlen und Ersetzungen sind bis dahin schon erfolgt.


Funktionen
~~~~~~~~~~

Die Funktion ``notify()`` kann z.B. in Logiken genutzt werden, um Benachrichtigungen zu senden. Sie wird wie folgt aufgerufen:

..code: yaml

	notify(event='', description='', priority=None, url=None, apikey=None, application='SmartHomeNG')


``event`` gibt den Text für das Ereignis an, ``description`` gibt den Text für die Beschreibung an.

``priority`` gibt die Dringlichkeit an und kann von 0 bis 2 gewählt werden.

``url`` kann eine URL mitgeben, die auf dem Gerät angezeigt wird.

Mit ``apikey`` kann ein API-Key angegeben werden, der von dem abweicht, der in der ``/etc/plugin.yaml`` definiert wurde. Wenn dort kein Standard-API-Key definiert wurde, muss dieser Parameter angegeben werden.

``application`` gibt die sendende Anwendung an und ist standardmäßig mit "SmartHomeNG" vorbelegt.


Beispiele
---------

..code: yaml

	sh.notify('Intrusion', 'Living room window broken', 2, 'http://yourvisu.com/')

	sh.notify('Tumbler', 'finished', apikey='qwerqwer')
