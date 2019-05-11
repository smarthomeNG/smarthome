
.. role:: bluesup

###########################################
Samba installieren :bluesup:`update`
###########################################

Wer mit einem Windows-Rechner auf die Dateien von SmartHomeNG und
SmartVISU zugreifen möchte, *kann* dazu **Samba** installieren:

.. code-block:: bash

   sudo apt-get install samba

Dann die smb.conf sichern und editieren:

.. code-block:: bash

   sudo mv /etc/samba/smb.conf /etc/samba/smb.conf.bak
   sudo nano /etc/samba/smb.conf

In die Datei folgendes einfügen:

.. code-block:: ini

   [global]
   workgroup = WORKGROUP
   server string = SmartHome
   domain master = no
   syslog only = no
   syslog = 10
   panic action = /usr/share/samba/panic-action %d
   encrypt passwords = true
   passdb backend = tdbsam
   obey pam restrictions = yes
   unix password sync = yes
   unix extensions = no
   passwd program = /usr/bin/passwd %u
   passwd chat = *Enter\snew\s*\spassword:* %n\n *Retype\snew\s*\spassword:* %n\n *password\supdated\ssuccessfully* .
   pam password change = yes
   map to guest = bad user
   invalid users = root
   guest ok = no
   usershare allow guests = no
   # disable printing
   load printers = no
   printing = bsd
   printcap name = /dev/null
   disable spoolss = yes
   # do not use old protocol versions due to security reasons
   server min protocol = SMB2_10
   #   client max protocol = SMB3
   #   client min protocol = SMB2_10

   # keep access to your local network
   hosts deny = ALL
   hosts allow = 192.168.20.0/24

   [SmartHomeNG]
   path = /usr/local/smarthome
   comment = SmartHomeNG Directories
   available = yes
   browseable = yes
   writable = yes
   force user = smarthome
   force group = smarthome
   create mask = 0664
   directory mask = 0775

   [smartVISU]
   path = /var/www/html/smartVISU
   comment = smartVISU Directories
   available = yes
   browseable = yes
   writable = yes
   force user = www-data
   force group = www-data
   create mask = 0775
   directory mask = 0775

Die Zeile ``hosts allow = 192.168.20.0/24`` muss vor dem Speichern noch auf den lokalen IP-Bereich
angepaßt werden.
Auch die Zeile ``server min protocol = SMB2_10`` die besagt, das nur Rechner mit SMB2 (ab Windows 7)
auf die Freigaben zugreifen können kann von der Version her höher gesetzt werden z.B. ``SMB3_11``.
Näheres dazu
`hier <https://www.samba.org/samba/docs/man/manpages-3/smb.conf.5.html>`__

Nun muß der User smarthome noch bekannt gemacht werden mit
``sudo smbpasswd -a smarthome``.

Im Windows Explorer sollten nun via
``\\<IP des Rechners oder hostname>`` zwei Freigaben angezeigt
werden.
