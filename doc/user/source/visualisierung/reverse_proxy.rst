:tocdepth: 1

.. index:: NGINX als ReverseProxy

NGINX als ReverseProxy
======================

Um einen sicheren Zugriff auf SmartHomeNG und die smartVISU von außen
(ohne VPN) zu ermöglichen, empfiehlt es sich einen ReverseProxy mit
Basic Authentication oder Clientzertifikaten zu nutzen. Die folgende
Dokumentation beschreibt eine Installation von NGINX als ReverseProxy
auf eigenständiger Hardware unter Raspberry OS. Dieser ist
bspw. auch für das Alexa Plugin oder die Nutzung von SmartHomeNG mit
**EgiGeoZone** / **Geofency** notwendig.

Annahmen
--------

Diese Anleitung hat folgende Annahmen:

* NGINX wird auf einem frisch aufgesetzten Raspberry Pi mit
  **Raspberry OS Debian Stretch oder Buster Lite** installiert.
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
Risikoländern blockieren. Hinweis: Die GeoIP Datenbank von Maxmind wird nicht mehr
weiter gepflegt, ist aber noch über eine alternative URL (siehe unten) abrufbar.

.. code-block:: bash

   sudo apt-get install geoip-database libgeoip1
   cd /usr/share/GeoIP/
   sudo wget https://dl.miyuru.lk/geoip/maxmind/country/maxmind4.dat.gz
   sudo gunzip maxmind4.dat.gz
   sudo wget https://dl.miyuru.lk/geoip/maxmind/country/maxmind6.dat.gz
   sudo gunzip maxmind6.dat.gz
   mv /usr/share/GeoIP/maxmind4.dat /usr/share/GeoIP/GeoIP.dat
   mv /usr/share/GeoIP/maxmind6.dat /usr/share/GeoIP/GeoIPv6.dat

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

   sudo systemctl restart nginx

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

NGINX mit ``sudo systemctl restart nginx`` neu starten.


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

       # Zugriff auf die SmartVISU mit Basic Auth
       location /smartVISU {
                  auth_basic "Restricted Area: smartVISU";
                  auth_basic_user_file /etc/nginx/.smartvisu;
                  try_files /wartung.html @loc_smartvisu;
       }

       # Alexa Plugin Weiterleitung
       location /alexa {
           auth_basic "Restricted Area: Alexa";
           auth_basic_user_file /etc/nginx/.alexa;
           try_files /wartung.html @loc_alexa;
       }

       # Network Plugin Weiterleitung
       location /shng {
           auth_basic "Restricted Area: SmartHomeNG";
           auth_basic_user_file /etc/nginx/.shng;
           try_files /wartung.html @loc_shng;
       }

       location @loc_websocket {
               proxy_pass http://websocket;
               include /etc/nginx/headers.conf;
       }

       location @loc_smartvisu {
               proxy_pass http://<SmartHomeNG LAN IP>/$request_uri;
               include /etc/nginx/headers.conf;
       }

       location @loc_alexa {
           proxy_pass http://<SmartHomeNG LAN IP>:<Alexa Plugin Port>/;
           include /etc/nginx/headers.conf;
       }

       location @loc_shng {
           proxy_pass http://<SmartHomeNG LAN IP>:<Network Plugin Port>/;
           include /etc/nginx/headers.conf;
       }
   }

Die Datei ``/etc/nginx/headers.conf`` muss nun entsprechend angelegt werden:

.. code-block:: cfg

  add_header Strict-Transport-Security "max-age=31536000; includeSubdomains" always;
  add_header X-Cache $upstream_cache_status;
  add_header X-Frame-Options "SAMEORIGIN" always;
  add_header X-Xss-Protection "1; mode=block" always;
  add_header X-Content-Type-Options "nosniff" always;
  add_header X-Proxy-Cache $upstream_cache_status;

Außerdem sollten zumindest folgende Zeilen in die Datei ``/etc/nginx/proxy_params``
eingetragen werden:

.. code-block:: cfg

  proxy_http_version      1.1;
  proxy_set_header        Host            $host;
  proxy_set_header        X-Real-IP       $remote_addr;
  proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header        Upgrade $http_upgrade;
  proxy_set_header        Connection $connection_upgrade;
  proxy_set_header        X-Forwarded-Proto $scheme;
  proxy_set_header        X-SSL-CERT $ssl_client_escaped_cert;


Im Anschluss muss nginx neu gestartet werden:

.. code-block:: bash

   sudo systemctl restart nginx


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

Danach den NGINX neu starten.

Client Zertifikate erstellen (optional)
---------------------------------------

Clientzertifikate können mittels openssl manuell erstellt werden. Etwas komfortabler
läuft das über easy-rsa von https://github.com/OpenVPN/easy-rsa/releases
Im Folgenden wird der Weg ohne dieses Tool beschrieben.

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
   default_crl_days= 365
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

Erweiterung: LUA Script für Apple Geräte
----------------------------------------

Apple Geräte wie MacBook oder iPhone kommen mit der oben skizzierten Konfiguration
leider nicht klar, sobald Websockets (die für die SmartVISU zwingend nötig sind)
im Spiel sind. Daher ist hier auf ein spezielles LUA Script zurückzugreifen.

.. code-block:: bash

  sudo apt-get install lua5.1 luarocks liblua5.1-dev libnginx-mod-http-lua
  git clone https://github.com/evanlabs/luacrypto.git && cd luacrypto
  luarocks install ./rockspecs/luacrypto-git-1.rockspec
  mkdir /usr/local/lib/lua/5.1/
  ln -s /usr/local/lib/lua/crypto.so /usr/local/lib/lua/5.1/crypto.so

Das LUA Script selbst wird in einer neuen Datei namens ``/etc/nginx/scripts/hass_access.lua``
erstellt. In der ersten Zeile ist dabei das Passwort anzugeben, mit dem die Zertifikate
verschlüsselt wurden.

.. code-block:: lua

  local HMAC_SECRET = "<SECRETKEY from OPENSSL>"
  local crypto = require "crypto"

  function ComputeHmac(msg, expires)
    return crypto.hmac.digest("sha256", string.format("%s%d", msg, expires), HMAC_SECRET)
  end

  verify_status = ngx.var.ssl_client_verify

  if verify_status == "SUCCESS" then
    client = crypto.digest("sha256", ngx.var.ssl_client_cert)
    expires = ngx.time() + 3600

    ngx.header["Set-Cookie"] = {
      string.format("AccessToken=%s; path=/", ComputeHmac(client, expires)),
      string.format("ClientId=%s; path=/", client),
      string.format("AccessExpires=%d; path=/", expires)
    }
    return
  elseif verify_status == "NONE" then
    client = ngx.var.cookie_ClientId
    client_hmac = ngx.var.cookie_AccessToken
    access_expires = ngx.var.cookie_AccessExpires

    if client ~= nil and client_hmac ~= nil and access_expires ~= nil then
      hmac = ComputeHmac(client, access_expires)

      if hmac ~= "" and hmac == client_hmac and tonumber(access_expires) > ngx.time() then
        return
      end
    end
  end

  ngx.exit(ngx.HTTP_FORBIDDEN)

Schließlich muss noch folgende Zeile in der Datei /etc/nginx/conf.d/\<mydomain\>.\<myds\>.\<me\>.conf
bei jeder Location eingetragen werden:

.. code-block:: nginx

  access_by_lua_file /etc/nginx/scripts/hass_access.lua;


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
   sudo systemctl restart nginx

Die Sicherheit der eigenen https-Domain kann nun unter
https://www.ssllabs.com/ssltest/ getestet werden. Mit den oben genannten
Maßnahmen sollte ein A+ erreicht werden.

Der versiertere Nutzer kann sich unter
https://mozilla.github.io/server-side-tls/ssl-config-generator/ auch
gleich eine eigene Konfiguration generieren lassen.

Wartung: Zertifikat nach 3 Monaten erneuern
-------------------------------------------

Nach 3 Monaten muss das Let’s Encrypt Serverzertifikat erneuert werden.
Dies sollte prinzipiell automatisiert geschehen, da certbot einen entsprechenden
cron Job erstellt.

Damit das Erneuerungs-Skript funktioniert, muss Port 80 im NGINX
freigegeben, oder (wie oben dokumentiert) auf HTTPS umgeleitet sein. Außerdem
kann/soll das ini File wie folgt adaptiert werden, um nginx nach der Aktualisierung
automatisch neu zu starten oder vorher/nachher ein Skript (z.B. zum Weiterleiten
von Ports auf der Fritzbox oder An/Ausschalten einer Firewall) auszuführen:

.. code-block:: ini

  # Manage Firewall
  #pre-hook = ufw allow http
  #post-hook = ufw deny http

  # Restart Postfix & Dovecot
  renew-hook = systemctl restart nginx.service

Eine manuelle Erneuerung geht wie folgendermaßen:

.. code-block:: bash

   sudo certbot certonly --agree-tos --rsa-key-size 4096 --webroot -w /var/www/letsencrypt -d <mydomain>.<myds>.<me>

Danach NGINX neu starten.

.. code-block:: bash

   sudo systemctl restart nginx

Der Test über https://www.ssllabs.com/ssltest/ gibt nun Aufschluß über
die Laufzeit des verlängerten Zertifikats.
