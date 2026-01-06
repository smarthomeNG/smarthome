.. index:: New; Web Interface

.. role:: redsup
.. role:: bluesup


Unterstützung mehrerer Sprachen :redsup:`new`
=============================================

Text kann im Template ``webif/templates/index.html`` als mehrsprachig deklariert werden, so dass die Webseite sich der in der Konfiguration gewählten Sprache anpasst.

Im Beispiel des Abschnitts **Webinterface mit Inhalt füllen**

      .. code-block:: HTML

        <div class="container-fluid m-2 table-resize">
           <table id="maintable" class="table table-striped table-hover pluginList dataTableAdditional">
               <thead>
                   <tr>
                       <th>{{ _('Item') }}</th>
                       <th>{{ _('Typ') }}</th>
                       <th>{{ _('knx_dpt') }}</th>
                   </tr>
               </thead>
               <tbody>
                   {% for item in items %}
                       <tr>
                           <td class="py-1">{{ item._path }}</td>
                           <td class="py-1">{{ item._type }}</td>
                           <td class="py-1">{{ item.conf['knx_dpt'] }}</td>
                       </tr>
                   {% endfor %}
               </tbody>
           </table>
         </div>

sind die drei Spaltenüberschriften als mehrsprachig deklariert. Üblicherweise würden diese Überschriften wie folgt aussehen:

      .. code-block:: HTML

         <th>Item</th>
         <th>Typ</th>
         <th>knx_dpt</th>

Um als mehrsprachig deklariert zu werden, muss der Text sowohl als Argument der Funktion ``_( ... )`` als auch in der Markierung für die Template-Engine ``{{ ... }}`` einschlossen sein. So wird aus 'Text' dann ``{{ _('Text') }}``.

      .. code-block:: HTML

         <th>{{ _('Item') }}</th>
         <th>{{ _('Typ') }}</th>
         <th>{{ _('knx_dpt') }}</th>

Mehrsprachigkeit ist detailliert auf der Seite :doc:`Multi-Language Support <multilanguage>` beschrieben.
