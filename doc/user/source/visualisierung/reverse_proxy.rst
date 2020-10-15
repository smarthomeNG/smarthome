:tocdepth: 1

.. index:: NGINX als ReverseProxy

NGINX als ReverseProxy
======================

Um einen sicheren Zugriff auf SmartHomeNG und die smartVISU von außen
(ohne VPN) zu ermöglichen, empfiehlt es sich einen ReverseProxy mit
Basic Authentication oder Clientzertifikaten zu nutzen. Die folgende
Dokumentation beschreibt eine Installation von NGINX als ReverseProxy
auf eigenständiger Hardware unter Raspbian Stretch Lite. Dieser ist
bspw. auch für das Alexa Plugin oder die Nutzung von SmartHomeNG mit
**EgiGeoZone** / **Geofency** notwendig.

Annahmen
--------

Diese Anleitung hat folgende Annahmen:

* NGINX wird auf einem frisch aufgesetzten Raspberry Pi mit
  **Raspbian Stretch Lite** installiert.
* Der Raspberry Pi dient ausschliesslich der Funktion als ReverseProxy
* Der Standarduser heißt weiterhin **pi**
* Eine DynDNS (o.ä.) Domain ist vorhanden und leitet auf die aktuelle Internet IP
* SmartHomeNG und SmartVISU sind auf einem separaten Rechner im gleichen LAN installiert.

Basiskonfiguration
------------------

-  Deutsches Keyboard festlegen: ``/etc/default/keyboard`` editieren und in
   der Zeile ``XKBLAYOUT="..."`` ein **de** eintragen. Danach
   ``sudo reboot now`` eingeben, um neu zu starten.
-  Aus Sicherheitsgründen das Standard-Passwort für **pi** ändern: Als
   User **pi** mit Standard-Passwort einloggen und mit ``passwd`` ein
   neues Passwort setzen.

NGINX installieren:
-------------------

.. code-block:: bash

   sudo apt-get update
   sudo apt-get install nginx-full

GeoIP installieren:
-------------------

Über GeoIP kann mittels der anfragenden IP herausgefunden werden, aus
welchem Land eine Anfrage kommt. Darüber lassen sich bspw. Requests aus
Risikoländern blockieren.

.. code-block:: bash

   sudo apt-get install geoip-database libgeoip1
   cd /usr/share/GeoIP/
   sudo wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz
   sudo gunzip GeoIP.dat.gz

Let’s Encrypt Server-Zertifikate
--------------------------------

(nach
https://goneuland.de/debian-9-stretch-lets-encrypt-zertifikate-mit-certbot-erstellen/)

Über Let’s Encrypt lassen sich kostenlos SSL Zertifikate, bspw. für
dyndns-Domains, ausstellen.

Certbot installieren:

.. code-block:: bash

   sudo apt-get install certbot

Nun die Datei ``/etc/nginx/snippets/letsencrypt.conf`` bearbeiten:

.. code-block:: bash

   sudo nano /etc/nginx/snippets/letsencrypt.conf

Dort folgenden Inhalt einfügen, damit certbot die Identität überprüfen
kann.:

.. code-block:: nginx

   location ^~ /.well-known/acme-challenge/ {
    default_type "text/plain";
    root /var/www/letsencrypt;
   }

.. code-block:: bash

   sudo mkdir -p /var/www/letsencrypt/.well-known/acme-challenge

.. code-block:: bash

   sudo nano /etc/nginx/sites-available/default

Dort unterhalb von ``listen [::]:80 default_server;`` die Zeile
``include /etc/nginx/snippets/letsencrypt.conf;`` einhängen:

.. code-block:: nginx

   server {
           listen 80 default_server;
           listen [::]:80 default_server;
           include /etc/nginx/snippets/letsencrypt.conf;
   [...]

.. code-block:: bash

   sudo service nginx restart

Port 80 und Port 443 im Router jeweils auf den identischen Port am
ReverseProxy-RaspberryPi mappen!

.. code-block:: bash

   sudo certbot certonly --rsa-key-size 4096 --webroot -w /var/www/letsencrypt -d <mydomain>.<myds>.<me>

Nachdem man seine E-Mail eingegeben hat, sollte die Generierung
erfolgreich durchlaufen und mit

.. code-block:: bash

   Generating key (4096 bits): /etc/letsencrypt/keys/0000_key-certbot.pem
   Creating CSR: /etc/letsencrypt/csr/0000_csr-certbot.pem

enden.

NGINX Konfiguration
-------------------

``/etc/nginx/nginx.conf`` bearbeiten und direkt im **http** Block die GeoIP
Einstellungen hinzufügen. Unter der Konfiguration der **virtual hosts**
noch einen Block als Schutz gegen Denial of Service Angriffe ergänzen:

.. code-block::  nginx

   http {
       ##
       # GeoIP Settings
       # Nur Länder aus erlaubten IP Bereichen dürfen den ReverseProxy
       # passieren!
       # https://www.howtoforge.de/anleitung/nginx-besucher-mit-dem-geoip-modul-nach-landern-blocken-debianubuntu/
       ##
       geoip_country /usr/share/GeoIP/GeoIP.dat;
       map $geoip_country_code $allowed_country {
           default yes;
           BY no;
           BR no;
           KP no;
           KR no;
           RS no;
           RO no;
           RU no;
           CN no;
           CD no;
           NE no;
           GH no;
           IQ no;
           IR no;
           SY no;
           UA no;
       }
       ##
       # websocket for shng
       ##
       upstream websocket {
         server 127.0.0.1:2424;
       }

       ##
       # Basic Settings
       ##
       map $http_upgrade $connection_upgrade {
         default Upgrade;
         '' close;
      }
      
      sendfile on;
      tcp_nopush on;
      tcp_nodelay on;
      keepalive_timeout 65;
      types_hash_max_size 2048;
      server_tokens off;
   [...]
       ##
       # Virtual Host Configs
       ##

       include /etc/nginx/conf.d/*.conf;
       include /etc/nginx/sites-enabled/*;

       ##
       # Harden nginx against DDOS
       ##

       client_header_timeout 10;
       client_body_timeout   10;
   }

NGINX mit ``sudo service nginx restart`` neu starten.

/etc/nginx/conf.d/<mydomain>.<myds>.<me>.conf erstellen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block::  nginx

   server {

       ## Blocken, wenn Zugriff aus einem nicht erlaubten Land erfolgt ##
       if ($allowed_country = no) {
           return 403;
       }

       # https://www.cyberciti.biz/tips/linux-unix-bsd-nginx-webserver-security.html
       ## Block download agents ##
       if ($http_user_agent ~* LWP::Simple|BBBike|wget) {
           return 403;
       }

       ## Block some robots ##
       if ($http_user_agent ~* msnbot|scrapbot) {
           return 403;
       }

       ## Deny certain Referers ##
       if ( $http_referer ~* (babes|forsale|girl|jewelry|love|nudit|organic|poker|porn|sex|teen) )
       {
           return 403;
       }

       listen 443 ssl default_server;
       server_name <mydomain>.<myds>.<me>;

       ##
       # SSL
       ##

       ## Activate SSL, setze SERVER Zertifikat Informationen ##
       # Generiert via Let's Encrypt!
       ssl on;
       ssl_certificate /etc/letsencrypt/live/<mydomain>.<myds>.<me>/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/<mydomain>.<myds>.<me>/privkey.pem;
       ssl_session_cache builtin:1000 shared:SSL:10m;
       ssl_prefer_server_ciphers on;
       # unsichere SSL Ciphers deaktivieren!
       ssl_ciphers    HIGH:!aNULL:!eNULL:!LOW:!3DES:!MD5:!RC4;

       ##
       # HSTS
       ##

       add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

       ##
       # global
       ##

       root /var/www/<mydomain>.<myds>.<me>;
       index index.php index.htm index.html;

       # Weiterleitung zu SmartHomeNG (Websocket Schnittstelle) mit Basic Auth
       location / {
               if ($http_upgrade != websocket) {
                      return 404;
               }
               try_files /wartung.html @loc_websocket;
       }

       location @loc_websocket {
               proxy_pass http://websocket;
               proxy_http_version 1.1;
               proxy_set_header Upgrade $http_upgrade;
               proxy_set_header Connection $connection_upgrade;
               proxy_set_header Host $host;
       }

       # Zugriff auf die SmartVISU mit Basic Auth
       location /smartVISU {
                  auth_basic "Restricted Area: smartVISU";
                  auth_basic_user_file /etc/nginx/.smartvisu;
                  try_files /wartung.html @loc_smartvisu;
       }

       location @loc_smartvisu {
               proxy_pass http://<SmartHomeNG LAN IP>/$request_uri;
               proxy_set_header Host $host;
               proxy_set_header X-Real-IP $remote_addr;
               proxy_set_header X_Forwarded-For $proxy_add_x_forwarded_for;
               proxy_set_header X_Forwarded-Proto $scheme;
       }

       # Alexa Plugin Weiterleitung
       location /alexa {
           auth_basic "Restricted Area: Alexa";
           auth_basic_user_file /etc/nginx/.alexa;
           try_files /wartung.html @loc_alexa;
       }

       location @loc_alexa {
           proxy_pass http://<SmartHomeNG LAN IP>:<Alexa Plugin Port>/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       # Network Plugin Weiterleitung
       location /shng {
           auth_basic "Restricted Area: SmartHomeNG";
           auth_basic_user_file /etc/nginx/.shng;
           try_files /wartung.html @loc_shng;
       }

       location @loc_shng {
           proxy_pass http://<SmartHomeNG LAN IP>:<Network Plugin Port>/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }

NGINX reloaden:
~~~~~~~~~~~~~~~

.. code-block:: bash

   /etc/init.d/nginx reload

Passwort-Files für unterschiedliche User für smartVISU, Alexa, Network Plugin erstellen
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sudo apt-get install apache2-utils

   sudo htpasswd -c /etc/nginx/.smartvisu <username>
   sudo htpasswd -c /etc/nginx/.alexa <username>
   sudo htpasswd -c /etc/nginx/.shng <username>

Dann ein Passwort vergeben.

Der Zugriff auf https://../smartVISU sollte nun klappen.

Nacharbeiten: Port 80 in NGINX deaktivieren
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Da NGINX im LAN aktuell noch auf Port 80 konfiguriert ist, sollte man in
der /etc/nginx/sites-available/default noch ein ``return 403`` ergänzen
und NGINX neu starten:

.. code-block:: nginx

   server {
           listen 80 default_server;
           listen [::]:80 default_server;

           return 403;

           include /etc/nginx/snippets/letsencrypt.conf;

Alternativ kann auch eine Weiterleitung von der HTTP (Port 80) auf die
HTTPS (Port 443) URL gesetzt werden. Das ist insbesondere beim Erneuern
von Zertifikaten von Vorteil, da hier eine Anfrage gegen Port 80 gemacht
wird:

.. code-block:: nginx

   server {
           listen 80 default_server;
           listen [::]:80 default_server;

           server_name _;
           return 301 https://$host$request_uri;

           include /etc/nginx/snippets/letsencrypt.conf;

Danach den NGINX neu starten:

.. code-block:: bash

   /etc/init.d/nginx reload

Client Zertifikate erstellen (optional)
---------------------------------------

openssl.cnf editieren
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sudo nano /etc/ssl/openssl.cnf

Folgende Zeilen anpassen:

.. code-block:: ini

   dir = /etc/ssl/ca                       # Directory where everything is kept
   [...]
   ew_certs_dir = $dir/certs               # default place for new certs.
   [...]
   certificate = $dir/ca.crt               # The CA certificate
   [...]
   crl = $dir/crl.pem                      # The current CRL
   private_key = $dir/private/ca.key       # The private key
   [...]
   default_md = sha1 # use public key default MD

Drei neue Verzeichnisse und drei Dateien anlegen:

.. code-block:: bash

   sudo mkdir -p /etc/ssl/ca/certs/users
   sudo mkdir -p /etc/ssl/ca/crl
   sudo mkdir -p /etc/ssl/ca/private

   sudo touch /etc/ssl/ca/index.txt
   sudo touch /etc/ssl/ca/index.txt.attr

In der Datei crlnumber den Wert “01” eintragen und speichern.

.. code-block:: bash

   sudo nano /etc/ssl/ca/crlnumber

Zertifikat für Certification Authority (CA) erstellen, Passwort für die
CA wählen und eigene Daten eingeben:

.. code-block:: bash

   sudo openssl genrsa -des3 -out /etc/ssl/ca/private/ca.key 4096
   sudo openssl req -new -x509 -days 1095 -key /etc/ssl/ca/private/ca.key -out /etc/ssl/ca/certs/ca.crt
   sudo openssl ca -name CA_default -gencrl -keyfile /etc/ssl/ca/private/ca.key -cert /etc/ssl/ca/certs/ca.crt -out /etc/ssl/ca/private/ca.crl -crldays 1095

Client Zertifikat für einen User erstellen und ein Passwort für das
Client Zertifikat vergeben:

.. code-block:: bash

   sudo openssl genrsa -des3 -out /etc/ssl/ca/certs/users/<USERNAME>.key 1024
   sudo openssl req -new -key /etc/ssl/ca/certs/users/<USERNAME>.key -out /etc/ssl/ca/certs/users/<USERNAME>.csr

Bei folgendem Schritt das Passwort für die CA eingeben:

.. code-block:: bash

   sudo openssl x509 -req -days 1095 -in /etc/ssl/ca/certs/users/<USERNAME>.csr -CA /etc/ssl/ca/certs/ca.crt -CAkey /etc/ssl/ca/private/ca.key -CAserial /etc/ssl/ca/serial -CAcreateserial -out /etc/ssl/ca/certs/users/<USERNAME>.crt

Bei folgendem Schritt mit dem Passwort für das Client Zertifikat
bestätigen und ein Export Passwort wählen:

.. code-block:: bash

   sudo openssl pkcs12 -export -clcerts -in /etc/ssl/ca/certs/users/<USERNAME>.crt -inkey /etc/ssl/ca/certs/users/<USERNAME>.key -out /etc/ssl/ca/certs/users/<USERNAME>.p12

<USERNAME>.p12 File herunterladen:

.. code-block:: bash

   sudo cp /etc/ssl/ca/certs/users/<USERNAME>.p12 /home/pi
   cd /home/pi/
   sudo chown pi <USERNAME>.p12

Bspw. nun via SFTP ziehen und aufs Datei aufs Android Handy übertragen
und ausführen oder im Browser unter “Zertifikate” importieren. Dabei
muss es mit Export Passwort bestätigt werden.

Client Zertifikate in NGINX nutzen (optional)
---------------------------------------------

Anleitung nach
https://arcweb.co/securing-websites-nginx-and-client-side-certificate-authentication-linux/

/etc/nginx/conf.d/<mydomain>.<myds>.<me>.conf bearbeiten und die Zeilen
im SSL Block ergänzen (“ab Client Zertifikat spezifisch”)

.. code-block::  nginx

       ##
       # SSL
       ##

       ## Activate SSL, setze SERVER Zertifikat Informationen ##
       # Generiert via Let's Encrypt!
       ssl on;
       ssl_certificate /etc/letsencrypt/live/<mydomain>.<myds>.<me>/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/<mydomain>.<myds>.<me>/privkey.pem;
       ssl_session_cache builtin:1000 shared:SSL:10m;
       ssl_prefer_server_ciphers on;
       # unsichere SSL Ciphers deaktivieren!
       ssl_ciphers    HIGH:!aNULL:!eNULL:!LOW:!3DES:!MD5:!RC4;

       # Client Zertifikat spezifisch
       ssl_client_certificate /etc/ssl/ca/certs/ca.crt;
       ssl_crl /etc/ssl/ca/private/ca.crl;
       ssl_verify_client optional;
       ssl_session_timeout 5m;

Die smartVISU relevanten Teile könnten jetzt folgendermaßen über
Clientzertifikate geschützt werden:

.. code-block::  nginx

       # Weiterleitung zu SmartHomeNG (Websocket Schnittstelle) mit Clientzertifikat
       location / {
           # Clientzertifikat gültig?
           if ($ssl_client_verify != SUCCESS) {
                   return 403;
           }

           # Zugreifendes Land erlaubt?
           if ($allowed_country = no) {
                   return 403;
           }

           # Nur Websocket Verbindungen gegen "/" durchlassen!
           if ($http_upgrade = websocket) {
                   proxy_pass http://<SmartHomeNG LAN IP>:<Websocket Port>;
           }
           if ($http_upgrade != websocket) {
                   return 403;
           }
       }

       # Zugriff auf die SmartVISU mit Clientzertifikat
       location /smartVISU {
           # Clientzertifikat gültig?
           if ($ssl_client_verify != SUCCESS) {
                   return 403;
           }

           # Zugreifendes Land erlaubt?
           if ($allowed_country = no)  {
                   return 403;
           }

           proxy_pass http://<SmartVISU Server LAN IP>/smartVISU;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

Wer es doppelt sicher haben möchte, kann die Basic Auth in den jew.
Blöcken auch beibehalten.

Testbar ist das Ganze, wenn es im Browser ohne Zertifikat einen 403er
Fehler gibt und mit Zertifikat die smartVISU aufbaut.

Erweiterung: Stärkere Diffie-Hellman-Parameter
----------------------------------------------

Damit die Sicherheit “perfekt” wird, sollten stärkere
Diffie-Hellman-Schlüssel verwendet werden. Dazu muss ein neues .pem File
generiert werden. Es empfiehlt sich, die Erzeugung dieses Files nicht
direkt auf den Raspi sondern auf einem PC mit stärker er CPU
durchzuführen. Ein Test auf einem Raspi3 dauerte 24 Stunden (!). Ein
Intel 4790k brauchte hingegen nur 30 Minuten.

Folgendes ist zu tun:

.. code-block:: bash

   cd /etc/ssl/certs
   sudo openssl dhparam -out dhparam.pem 4096

Alternativ kann das File auch einfach unter /etc/ssl/certs reinkopiert
werden.

Danach ist in der SSL Konfiguration von NGINX folgende Zeile zu ergänzen
und NGINX neu zu starten:

.. code-block:: bash

   # Konfiguration editieren
   sudo nano /etc/nginx/conf.d/\<mydomain\>.\<myds\>.\<me\>.conf

.. code-block:: nginx

   ## Dort folgende Zeile im Block SSL einfügen:

   ##
   # SSL
   ##
   [...]
   ssl_dhparam /etc/ssl/certs/dhparam.pem;
   [...]

.. code-block:: bash

   ## NGINX neu starten
   sudo service nginx restart

Die Sicherheit der eigenen https-Domain kann nun unter
https://www.ssllabs.com/ssltest/ getestet werden. Mit den oben genannten
Maßnahmen sollte ein A+ erreicht werden.

Der versiertere Nutzer kann sich unter
https://mozilla.github.io/server-side-tls/ssl-config-generator/ auch
gleich eine eigene Konfiguration generieren lassen.

Wartung: Zertifikat nach 3 Monaten erneuern
-------------------------------------------

Nach 3 Monaten muss das Let’s Encrypt Serverzertifikat erneuert werden.
Damit das Erneuerungs-Skript funktioniert, muss Port 80 im NGINX
freigegeben, oder (wie oben dokumentiert) auf HTTPS umgeleitet sein.

Die Erneuerung geht dann wie folgendermaßen:

.. code-block:: bash

   sudo certbot certonly --rsa-key-size 4096 --webroot -w /var/www/letsencrypt -d <mydomain>.<myds>.<me>

Im nun folgenden Dialog Option 2 (2: Renew & replace the cert (limit ~5
per 7 days)) auswählen. Danach NGINX neu starten.

.. code-block:: bash

   sudo service nginx restart

Der Test über https://www.ssllabs.com/ssltest/ gibt nun Aufschluß über
die Laufzeit des verlängerten Zertifikats.
