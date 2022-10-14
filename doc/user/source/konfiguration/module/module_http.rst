
.. index:: http; Modul
.. index:: Module; http
.. index:: http; Konfiguration

.. index:: Webinterfaces; Konfiguration
.. index:: Webservices; Konfiguration

.. role:: redsup
.. role:: bluesup

===========
Module http
===========

Der vom Module http zur Verfügung gestellte Webserver wird genutzt um die Admin GUI zur Verfügung zu stellen.

Weiterhin erlaubt es dieses Modul in Plugins eine Webschnittstelle zu implementieren. Die API wird weiter
unten beschrieben. Es implementiert auch die Basisauthentifizierung für den Zugriff auf Webinterfaces und Webservices.

Über Webinterfaces können Plugins Webseiten zur Verfügung stellen, um bei Befarf eine GUI für
bestimmte Features anzubieten.

Über Webservices können Plugins Dienste zu Verfügung stellen, welche die Kommunikation mit anderen
Anwendungen ermöglichen (z.B. ein REST Interface).


.. index:: Konfigurationsdateien; /etc/module.yaml (http)

Konfiguration
=============

--------------------------
Datei *../etc/module.yaml*
--------------------------

.. code-block:: yaml
   :caption: ../etc/module.yaml

   # etc/module.yaml
   http:
       module_name: http
   #    starturl: backend
   #    threads: 8
   #    showtraceback: False
   #    showpluginlist: True

   #    port: 8383
   #    user: admin
   #    password: geheim
   #    hashed_password: 1245a9633edf47b7091f37c4d294b5be5a9936c81c5359b16d1c4833729965663f1943ef240959c53803fedef7ac19bd59c66ad7e7092d7dbf155ce45884607d

   #    servicesport: 8384
   #    service_user: serviceuser
   #    service_password: geheim
   #    service_hashed_password: 1245a9633edf47b7091f37c4d294b5be5a9936c81c5359b16d1c4833729965663f1943ef240959c53803fedef7ac19bd59c66ad7e7092d7dbf155ce45884607d


.. note::

    Die Konfigurationsparameter des http Modules, die in dieser Datei konfiguriert werden, können auch über das graphische
    Administrations-Interface geändert werden.



+-------------------------+------------------------------------------------------------------------------------------------------+
| Parameter               | Bemerkung                                                                                            |
+=========================+======================================================================================================+
| starturl                | **Optional**: Wenn **starturl** auf den Namen eines geladenen Plugins gesetzt ist, wird beim Aufruf  |
|                         | von http://smarthomeNG.local:8383/ auf dieses Plugin weitergeleitet, statt auf die Übersichtsseite.  |
|                         | Wenn z.B. standardmäßig das Backend Plugin aufgerufen werden soll, muss ``starturl: backend``        |
|                         | gesetzt werden. Die Übersichtsseite ist weiterhin unter http://smarthomeNG.local:8383/plugins/       |
|                         | erreichbar.                                                                                          |
+-------------------------+------------------------------------------------------------------------------------------------------+
| threads                 | **Optional**: Die Anzahl der Threads, die CherryPy für jeden Port startet, auf dem es lauscht.       |
|                         | Default ist 8, was für leistungsschwächere CPUs zu viel sein kann                                    |
+-------------------------+------------------------------------------------------------------------------------------------------+
| showtraceback           | **Optional**: Falls dieser Parameter auf  **True** gesetzt wird, zeigen Fehlerseiten (außer Fehler   |
|                         | bei 404) einen Python Fehler-Trace an. Normalerweise wird dieser Trace nur im **smarthome.log**      |
|                         | aufgezeichnet.                                                                                       |
+-------------------------+------------------------------------------------------------------------------------------------------+
| showpluginlist          | **Optional**: Falls der Parameter auf **False** gesetzt wird, wird unter                             |
|                         | **http://smarthomeNG.local:8383/plugins** keine Liste der geladenen Plugins mit Web Interface        |
|                         | gezeigt. Dann ist der Zugriff auf die Webinterfaces nur direkt über die jeweilige Url oder über die  |
|                         | Seite **Plugins** im Backend möglich. **showpluginlist** ist standardmäßig **True**.                 |
+-------------------------+------------------------------------------------------------------------------------------------------+
| port                    | **Optional**: Der Port auf welchem das html Interface lauscht. Dieser Port wird für Webinterfaces    |
|                         | wie z.B. das Backend Plugin genutzt- Standard Port ist **8383** .                                    |
+-------------------------+------------------------------------------------------------------------------------------------------+
| user                    | **Optional**: Der Benutzername mit dem man sich zur Nutzung der Webinterfaces authentifizieren muss. |
|                         | Der Standardwert ist **admin**                                                                       |
+-------------------------+------------------------------------------------------------------------------------------------------+
| password                | **Optional**: Das Passwort mit dem man sich zur Nutzung der Webinterfaces authentifizieren muss im   |
|                         | Klartext. Standardmäßig ist kein Passwort gesetzt. Wenn kein Passwort (oder Hashed-Passwort) gesetzt |
|                         | ist, ist der Zugriff auf die Webinterfaces ohne Anmeldung möglich.                                   |
+-------------------------+------------------------------------------------------------------------------------------------------+
| hashed_password         | **Optional**: Das Passwort für die Basis-Authentifizierung an Webinterfaces als Hash-Wert. Kann      |
|                         | anstelle von**password** verwendet werden, wenn kein Klartext-Passwort in der                        |
|                         | Konfigurationsdatei haben möchten. Wenn weder **password** als auch **hashed_password** angegeben    |
|                         | werden, ist die Basisauthentifizierung deaktiviert. Derzeit ist **hashed_password** der              |
|                         | SHA-512-Hash-Wert des Passworts. Um den Hash für das Passwort zu erstellen, kann die Funktion        |
|                         | **Passwort-Hash erzeugen** auf der Seite **Dienste** im Backend verwendet werden.                    |
+-------------------------+------------------------------------------------------------------------------------------------------+
| serviceport             | **Optional**: Der Port auf welchem das html Interface lauscht. Dieser Port wird für den Zugriff      |
|                         | auf Webservices genutzt, wie ihn z.B. das Plugin Webservices zur Verfügung stellt. Standard Port     |
|                         | ist **8384** .                                                                                       |
+-------------------------+------------------------------------------------------------------------------------------------------+
| service_user            | **Optional**: Der Benutzername mit dem man sich zur Nutzung der Webservices authentifizieren muss.   |
|                         | Der Standardwert ist **serviceuser**                                                                 |
+-------------------------+------------------------------------------------------------------------------------------------------+
| service_password        | **Optional**: Das Passwort mit dem man sich zur Nutzung der Webservices authentifizieren muss im     |
|                         | Klartext. Standardmäßig ist kein Passwort gesetzt. Wenn kein Service-Passwort (oder                  |
|                         | Hashed-Service-Passwort) gesetzt ist,ist der Zugriff auf die Webservices ohne Anmeldung möglich.     |
+-------------------------+------------------------------------------------------------------------------------------------------+
| service_hashed_password | **Optional**: Das Passwort für die Basis-Authentifizierung an Webservices als Hash-Wert. Kann        |
|                         | anstelle von**service_password** verwendet werden, wenn kein Klartext-Passwort in der                |
|                         | Konfigurationsdatei haben möchten. Wenn weder **service_password** als auch                          |
|                         | **service_hashed_password** angegeben werden, ist die Basisauthentifizierung deaktiviert. Derzeit    |
|                         | ist **service_hashed_password** der SHA-512-Hash-Wert des Service-Passworts. Um den Hash für         |
|                         | das Passwort zu erstellen, kann die Funktion **Passwort-Hash erzeugen** auf der Seite                |
|                         | **Dienste** im Backend verwendet werden.                                                             |
+-------------------------+------------------------------------------------------------------------------------------------------+


.. note::

   Wenn über den Parameter **starturl** die Weiterleitung auf ein spezifisches Plugin aktiviert ist,
   kann trotzdem die Übersichtsseite mit der Liste aller geledenen Plugins, die ein Webinterface registriert
   haben über **http://smarthomeNG.local:8383/plugins** angezeigt werden. Außer, man hat über
   ``showpluginlist: False`` diese Übersichtsseite deaktiviert.


