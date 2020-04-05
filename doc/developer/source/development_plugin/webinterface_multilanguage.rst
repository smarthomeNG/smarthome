.. index:: New; Web Interface

.. role:: redsup
.. role:: bluesup


Multi-Language Support :redsup:`new`
====================================

In the template **webif/templates/index.html** text can be marked to be translated, if the used language of the
admin interface is changed.

In the example in the section **Filling the webinterface with content**

      .. code-block:: HTML

         <div class="table-responsive" style="margin-left: 3px; margin-right: 3px;" class="row">
             <div class="col-sm-12">
                 <table class="table table-striped table-hover pluginList">
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
         </div>

three column headings are marked as text to be translated if necessary. Usually the headings would look like this:

      .. code-block:: HTML

         <th>Item</th>
         <th>Typ</th>
         <th>knx_dpt</th>

To be translated the Text has to be included as stings in the function ``_( )``. For the function to be executed it has
to be declared a variable for the templating engine by including it in ``{{  }}``. So you end up with ``{{ _('text') }}``.

      .. code-block:: HTML

         <th>{{ _('Item') }}</th>
         <th>{{ _('Typ') }}</th>
         <th>{{ _('knx_dpt') }}</th>

Translations are covered in more detail on the page :doc:`Multi-Language Support </development_plugin/multilanguage>`

