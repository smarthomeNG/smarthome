.. index:: Web Interface; Drittanbieterkomponenten

.. role:: redsup
.. role:: bluesup



Komponenten von Drittanbietern für Webinterfaces
------------------------------------------------

SmartHomeNG liefert eine Reihe von Drittanbieterkomponenten mit dem http-Modul aus, welche für erweiterte und komplexere Webinterfaces wie folgt eingebunden werden können:

   * JQuery 3.4.1:

     * JS: <script src="/gstatic/js/jquery-3.4.1.min.js"></script>
   * Bootstrap :

     * CSS: <link rel="stylesheet" href="/gstatic/bootstrap/css/bootstrap.min.css" type="text/css"/>
     * JS: <script src="/gstatic/bootstrap/js/bootstrap.min.js"></script>
   * Bootstrap Tree View:

      * CSS: <link rel="stylesheet" href="/gstatic/bootstrap-treeview/bootstrap-treeview.css" type="text/css"/>
      * JS: <script src="/gstatic/bootstrap-treeview/bootstrap-treeview.min.js"></script>
   * Bootstrap Datepicker v1.8.0:

      * CSS: <link rel="stylesheet" href="/gstatic/bootstrap-datepicker/dist/css/bootstrap-datepicker.min.css" type="text/css"/>
      * JS:
         * <script src="/gstatic/bootstrap-datepicker/dist/js/bootstrap-datepicker.min.js"></script>
         * <script src="/gstatic/bootstrap-datepicker/dist/locales/bootstrap-datepicker.de.min.js"></script>
   * popper.js:

      * JS: <script src="/gstatic/popper.js/popper.min.js"></script>
   * CodeMirror 5.46.0:

      * CSS: <link rel="stylesheet" href="/gstatic/codemirror/lib/codemirror.css"/>
      * JS: <script src="/gstatic/codemirror/lib/codemirror.js"></script>
   * Font Awesome 5.8.1:

      * CSS: <link rel="stylesheet" href="/gstatic/fontawesome/css/all.css" type="text/css"/>

Erweiterungen usw., die mit den Komponenten ausgeliefert wurden, finden sich im Ordner ``/modules/http/webif/gstatic``.

Für Vorschläge weiterer "globaler" Komponenten sind wir jederzeit offen. 
Ansonsten können diese natürlich jederzeit im eigenen Plugin eingebunden und mitgeliefert werden, 
solange die Open Source-Lizenz der jeweiligen Komponente das erlaubt.
