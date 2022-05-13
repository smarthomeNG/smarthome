text_display
============

Das Plugin dient dazu Nachrichten auf Displays (z.B. KNX-Taster) anzuzeigen.

* Es gibt Nachrichten**senken**, das sind die jeweiligen Anzeigegeräte, die die Nachrichten anzeigen sollen.
* Nachrichten werden in den Nachrichten**ringen** verwaltet. Auf jedem Ring gibt es eine feste Anzahl an Slots, für die geprüft wird, ob die Nachricht relevant ist. Die Anzahl wird natürlich aus der Menge der möglichen Nachrichtenquellen automatisch definiert.
* Ein Nachrichtenring hat **Slots** in denen die Nachrichten**quellen** verankert sind. Jeder Slot hat zwei Zuordnungen, einen Boolean-Wert, der bestimmt ob die Nachricht gerade relevant ist, und einen Textwert.
* Nachrichten eines Rings haben die gleiche Priorität. Auf einer Senke lassen sich mehrere Ringe registrieren, die in absteigender Priorität abgearbeitet werden.
* Für eine Senke kann ein oder mehrere Ringe definiert werden, die die Standardringe erzwungenermaßen verdecken, z.B. für die Anzeige von Anrufen oder Alarmen.
* Eine Senke kann einen default-Wert haben, auf den zurückgesetzt wird, wenn keine Nachricht gültig ist.

Anforderungen
-------------
Das Plugin funktioniert ab Python 3.6, ansonsten existieren keine Anforderungen

Notwendige Software
~~~~~~~~~~~~~~~~~~~

Keine Abhängigkeiten

Unterstützte Geräte
~~~~~~~~~~~~~~~~~~~

Im Prinzip funktioniert das Plugin Hardwareunabhängig. Die Anzeige des einen Texts kann zum Beispiel auch in der Visu erfolgen. Zu beachten wäre, dass KNX-Taster nur 13 Zeichen anzeigen können. Es werden nur die ersten 13 Zeichen verschickt, wenn man den knx_dpt: "16.001" verwendet, der Rest wird "verschluckt".


Konfiguration
-------------

Die Konfiguration erfolgt (abgesehen von der Instantiierung) ausschließlich über Items. Es gibt keine durch Logik auslösbaren Funktionen oder Verknüpfungen mit Logiken.

plugin.yaml
~~~~~~~~~~~

Das Plugin muss nur einmal instantiiert werden. Es ist nicht nötig/möglich mehrere Instanzen zu verwalten.

.. code-block:: yaml
   :linenos:

    text_display:
        plugin_name: text_display


items.yaml
~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde. Bzw. das Beispiel unten verstehen...


Beispiele
---------

Die Folgenden Anforderungen werden im nachfolgenden Beispiel umgesetzt:

* Alle KNX-Taster im Haus sollen die gleichen Texte anzeigen (a.k.a die Meldungen gehen über EINE KNX-GA, es gibt also nur eine Senke).
* Wenn ein Fenster auf ist, soll die Raum-Innentemperatur des Raumes mit seinem Namen angezeigt werden. (Nachrichtenring "fenster")
* Wenn ein Fenster auf ist, soll die Außentemperatur angezeigt werden, aber nur einmal, egal wieviele Fenster auf sind. (Nachrichtenring "fenster")
* Wenn eine neue Nachricht auf dem Fritzbox Anrufbeantworter vorliegt, soll die Nachricht "AB prüfen" angezeigt werden. (Nachrichtenring "wichtiger_als_fenster")
* Wenn jemand anruft, soll "T: <Name>" bzw. "T: <Nummer>" auf den Displays angezeigt werden, die Anruflogik liegt dabei im AVM-Plugin. (Nachrichtenring "anruf")

Relevant sind letztlich nur die text_display_... Attribute. Letzten Endes werden mit den ganzen Konstruktionen außen herum nur einfache Booleanwerte erzeugt, die aussagen, ob die Nachricht angezeigt werden sollte oder nicht. Damit die Nachrichten noch etwas mehr Informationsgehalt haben, sind einige Nachrichtentexte mit Informationen von anderen Items angereichert worden.

Nachrichtensenke
~~~~~~~~~~~~~~~~

In diesem Beispiel werden die Nachrichten auf die KNX-GA a/b/c geschickt. Liegt keine Nachricht vor, wird ein Leerzeichen als Text geschickt, damit z.B. auf den MDT Glastastern keine alten Nachrichten stehen bleiben. Lässt man die Default-Konfiguration einfach weg, wird kein Wert gesendet. Auf den MDT-RTR ist das der einfachste Weg, die Nachricht verschwinden zu lassen.

.. code:: yaml

   meldung:
        knx_dpt: "16.001"
        knx_send: a/b/c
        knx_reply: a/b/c
        enforce_updates: "yes"
        text_display_default_message: ' '
        text_display_sink_for_rings:
            - "wichtiger_als_fenster"
            - "fenster"
        text_display_sink_rings_with_prio:
            - "anruf"


"Fenster auf" Nachrichtenquelle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dies ist die Struktur für einen Raum, das muss dann für jeden Raum wiederholt werden.

.. code:: yaml

    schlafzimmer:
        temperatur_im_schlafzimmer:
            type: num
            knx_cache: x/y/z

            anzeige_string:
                type: str
                eval: >
                    f"SchlaZi: {sh...():.1f}°C"
                eval_trigger: ..

                display_is_relevant:
                    type: bool
                    eval: or
                    eval_trigger:
                        - .,..irgendein_fenster_im_schlafzimmer_offen
                    text_display_target_ring: 'fenster'
                    text_display_content_source_item: ..

        irgendein_fenster_im_schlafzimmer_offen:
            type: bool
            eval: or
            eval_trigger:
                - .fenster_zur_strasse
                - .fenster_zum_garten

            fenster_zur_strasse:
                type: bool
                knx_dpt: 1
                knx_cache: x/y/z
            fenster_zur_strasse:
                type: bool
                knx_dpt: 1
                knx_cache: x/y/z


Außentemperatur abhängig von Fensterstatus:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: yaml

    wetter:
        luft_temperatur:
            type: num
            remark: wo auch immer der Wert herkommt (OpenWeatherMap ;-) / Wetterstation)

            message_string:
                type: str
                eval: >
                    f"Außen: {sh...():.1f}°C"
                eval_trigger: ..
                display_is_relevant:
                    type: bool
                    eval: or
                    eval_trigger:
                        - schlafzimmer.fenster
                        - kinderzimmer.fenster
                        - buero.fenster
                        - og_bad.fenster
                        - eg_bad.fenster
                        - wohnzimmer.fenster
                    text_display_target_ring: 'fenster'
                    text_display_content_source_item: ..


AB Prüfen Nachrichtenquelle:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Die Anzahl der neuen Nachrichten auf dem Anrufbeantworter muss über 0 sein, damit immer der gleiche "AB prüfen" Text angezeigt wird.

.. code:: yaml

    fritzbox:
        tam:
            index: 1
            type: bool
            avm_data_type@fritzbox: tam
            new_message_present:
                type: bool
                visu_acl: ro
                eval: sh.fritzbox.tam.message_number_new() > 0
                eval_trigger:
                    - fritzbox.tam.message_number_new
                text_display_target_ring: 'wichtiger_als_fenster'
                text_display_content_source_item: .ab_pruefen_text

                ab_pruefen_text:
                    type: str
                    remark: Klar kann man hier auch die Nachricht dynamisch bauen, z.B. "'AB: {} Nachr.'.format(sh.fritzbox.tam.message_number_new())"
                    initial_value: "AB prüfen"

            message_number_new:
                type: num
                visu_acl: ro
                avm_data_type@fritzbox: tam_new_message_number


Anrufer-Meldungen
~~~~~~~~~~~~~~~~~

.. code:: yaml

    fritzbox:
        monitor:
            message:
                type: bool
                eval: sh.fritzbox.monitor.incoming.event() == 'ring' and sh.fritzbox.monitor.incoming.is_call_incoming() == True
                eval_trigger:
                    - ..incoming.is_call_incoming
                    - ..incoming.event
                text_display_target_ring: 'anruf'
                text_display_content_source_item: .message_text
                message_text:
                    type: str
                    eval: "'T:{}'.format(sh.fritzbox.monitor.incoming.last_caller())"
                    eval_trigger: fritzbox.monitor.incoming.last_caller
            incoming:
                is_call_incoming:
                    type: bool
                    avm_data_type@fritzbox: is_call_incoming
                last_caller:
                    type: str
                    avm_data_type@fritzbox: last_caller_incoming
                event:
                    type: str
                    avm_data_type@fritzbox: call_event_incoming


Web Interface
-------------

Das Plugin liefert ein WebInterface in dem sich die Nachrichtenringe, mit den gesetzten Slots nachvollziehen lassen. Darüberhinaus werden dort auch die Senken angezeigt. Die Darstellung ist sicher noch Verbesserungsfähig, funktioniert aber fürs Debuggen.
