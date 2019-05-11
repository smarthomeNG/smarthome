
.. index:: Items; enforce_updates
.. index:: Standard-Attribute; enforce_updates
.. index:: enforce_updates


.. role:: bluesup

enforce_updates
===============

Die Wirkungsweise von *enforce_updates* erschließt sich nicht sofort. Zum Verständnis was *enforce_updates* bewirkt, ist es
wichtig erstmal "in **Items** zu denken" und Plugins oder Logiken für einen Moment zu vergessen.

Wenn sich der Wert eines Items ändert, löst das eine Reihe von Aktionen aus:

    - *eval* Statements in anderen Items werden getriggert, wenn in anderen in den Items ein *eval_trigger* auf das geänderte Item verweist.
    - *on_change* Definitionen des Items werden ausgewertet
    - *on_update* Definitionen des Items werden ausgewertet
    - Logiken werden getriggert, wenn der Trigger der Logik (in ../etc/logic.yaml) auf das geänderte Item verweist.
    - Plugins, die mit diesem Item verbunden sind, erhalten eine Info über den neuen Wert


Wenn ein Item ein Update erhält, welches identisch zu dem bisherigen Wert ist, passiert nur folgendes;

    - *on_update* Definitionen des Items werden ausgewertet

Wenn jetzt in SmartHomeNG ein Item z.B. den Wert **True** erhält (und vorher **False** war), passiert genau das im ersten Fall beschriebene.

Wenn das Item danach erneut den Wert **True** erhält (und ja vorher schon **True** war), passiert das im zweiten Fall beschriebene.
Plugins und Logiken erhalten in diesem Fall also keine Info, dass das Item ein Update mit dem selben Wert erfahren hat.
Erst wenn das Item auf **False** wechselt, werden die Plugins und Logiken über den Wechsel des Wertes informiert.

Wenn jetzt aber ein Item immer wieder nacheinander auf **True** gesetzt wird, ohne dass irgendwoher das Item
zwischendurch auf **False** gesetzt wurde, und man möchte z.B. über das KNX Plugin bei jedem Update ein Telegram verschicken,
so kann durch setzen von *enforce_updates* auf **True** erzwungen werden, dass alle im ersten Fall beschriebenen Aktivitäten
ausgelöst werden, auch wenn sich beim Update des Items der Wert nicht ändert.


