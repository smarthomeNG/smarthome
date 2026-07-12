.. index:: Web Interface; Drittanbieterkomponenten

.. role:: redsup
.. role:: bluesup



Komponenten von Drittanbietern für Webinterfaces
------------------------------------------------

SmartHomeNG liefert eine Reihe von Drittanbieterkomponenten mit dem http-Modul aus, welche für erweiterte und komplexere Webinterfaces wie folgt eingebunden werden können:

   * JQuery 4.0.0

     * JS: <script src="/gstatic/js/jquery-4.0.0.min.js"></script>
   * JQuery UI Core and Effects 1.14.2:

     * CSS: <link rel="stylesheet" href="/gstatic/css/jquery-ui.min.css" type="text/css"/>
     * JS: <script src="/gstatic/js/jquery-ui.min.js"></script>
   * Datatables 2.3.7 incl. some plugins and extensions:

     * CSS: <link rel="stylesheet" href="/gstatic/datatables/datatables.min.css" type="text/css"/>
     * JS:

       * <script src="/gstatic/datatables/datatables.min.js"></script>
       * <script src="/gstatic/datatables/datatables.defaults.js"></script>
       * <script src="/gstatic/datatables/dataTables.pageResize.min.js"></script>
       * <script src="/gstatic/datatables/datetime-moment.min.js"></script>
       * <script src="/gstatic/datatables/moment.min.js"></script>
   * Bootstrap 5.3.8:

     * CSS: <link rel="stylesheet" href="/gstatic/bootstrap/css/bootstrap.min.css" type="text/css"/>
     * JS: <script src="/gstatic/bootstrap/js/bootstrap.min.js"></script>
   * Bootstrap Tree View 1.2.1:

      * CSS: <link rel="stylesheet" href="/gstatic/bootstrap-treeview/bootstrap-treeview.css" type="text/css"/>
      * JS: <script src="/gstatic/bootstrap-treeview/bootstrap-treeview.min.js"></script>
   * Bootstrap Datepicker v1.10.0:

      * CSS: <link rel="stylesheet" href="/gstatic/bootstrap-datepicker/dist/css/bootstrap-datepicker.min.css" type="text/css"/>
      * JS:

        * <script src="/gstatic/bootstrap-datepicker/dist/js/bootstrap-datepicker.min.js"></script>
        * <script src="/gstatic/bootstrap-datepicker/dist/locales/bootstrap-datepicker.de.min.js"></script>
   * Popper 2.11.8 (Tooltips):

      * CSS: <link rel="stylesheet" href="/gstatic/popper.js/popper.css"/>
      * JS:

        * <script src="/gstatic/popper.js/popper.min.js"></script>
        * <script src="/gstatic/popper.js/popper_functions.js"></script>
   * CodeMirror 5.65.21:

      * CSS: <link rel="stylesheet" href="/gstatic/codemirror/lib/codemirror.css"/>
      * JS: <script src="/gstatic/codemirror/lib/codemirror.js"></script>
   * Font Awesome 7.1.0:

      * CSS: <link rel="stylesheet" href="/gstatic/fontawesome/css/all.css" type="text/css"/>

Erweiterungen usw., die mit den Komponenten ausgeliefert wurden, finden sich im Ordner ``/modules/http/webif/gstatic``.

Für Vorschläge weiterer "globaler" Komponenten sind wir jederzeit offen.
Ansonsten können diese natürlich jederzeit im eigenen Plugin eingebunden und mitgeliefert werden,
solange die Open Source-Lizenz der jeweiligen Komponente das erlaubt.
