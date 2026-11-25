.. index:: Plugins; eta_pu
.. index:: eta_pu

======
eta_pu
======

Anbindung der REST-Schnittstelle von ETA-Heizungen (ETA Pellet Unit PU, http://www.eta.co.at).


Voraussetzungen
================

Die ETA Pellet Unit muss den Fernzugriff aktiviert haben. Dafür stehen drei Modi zur Verfügung:
keiner, nur lesend oder lesend/schreibend.


Konfiguration
=============

Die Informationen zur Konfiguration des Plugins sind unter :doc:`/plugins_doc/config/eta_pu` beschrieben.

Item-Attribute
--------------

Die ETA Pellet Unit organisiert ihre Daten über sogenannte **uri** (Unified Resource Identifier).
Jede uri ist lesbar, manche auch schreibbar, und entspricht einer CAN-Bus-Id einer internen
Komponente der Pellet Unit. Eine Antwort auf eine uri-Anfrage sieht z.B. so aus::

    <value uri="/user/var/112/10021/0/0/12162" strValue="26" unit="°C" decPlaces="0" scaleFactor="10" advTextOffset="0">262</value>

Mit **eta_pu_uri** wird die CAN-Bus-Id an einem Item hinterlegt. Alle Ids mit Beschreibung liefert
die Pellet Unit unter ``http://<ip>/user/menu``. Mit **eta_pu_type** wird festgelegt, welcher Teil
der Antwort in das Item eingelesen wird (``strValue``, ``unit``, ``decPlaces``, ``scaleFactor``,
``advTextOffset``). Der zusätzliche Typ ``calc`` berechnet den Wert aus den Rohdaten::

    data = value * scaleFactor + advTextOffset

Für schreibende Zugriffe muss der Typ ``calc`` verwendet werden, das Plugin berechnet daraus den
zu schreibenden Rohwert. Nicht jede uri ist schreibbar - grundsätzlich lässt sich alles schreiben,
was auch über das Touch-Display der Pellet Unit (Benutzermodus) verändert werden kann.

Mit **eta_pu_error** wird ein Item auf ``yes`` gesetzt, um Fehlermeldungen der Pellet Unit
einzulesen.


Beispiele
=========

Die Attribute **eta_pu_uri** und **eta_pu_type** wirken zusammen: das übergeordnete Item trägt die
uri, die Kind-Items lesen jeweils ein Feld der Antwort aus::

    eta_unit:

        boiler:

            emission_temperature:
                eta_pu_uri: 112/10021/0/0/12162
                type: str

                Value:
                    eta_pu_type: calc
                    type: num

                unit:
                    eta_pu_type: unit
                    type: str

        warmwater:

            state:
                eta_pu_uri: 112/10111/0/0/12129

                text:
                    visu_acl: ro
                    type: str
                    eta_pu_type: strValue

            extra_loading_button:
                eta_pu_uri: 112/10111/0/0/12134

                number:
                    visu_acl: rw
                    type: num
                    eta_pu_type: calc

        error:
            eta_pu_error: 'yes'
            type: str
