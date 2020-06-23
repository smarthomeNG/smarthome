
.. index:: Multi-Language Support
.. index:: translations

.. role:: redsup
.. role:: bluesup

========================================
Multi-Language Support :bluesup:`Update`
========================================

This documentation is valid vor SmartHomeNG versions beyond v1.4.2. It does not work on v1.4.2
and below.

Words or phrases in the webinterface can be marked for translation.


Marking text for translation
============================

1. In Jinja2 templates
----------------------

To mark a word or phrase for translation, it has to be part of a Jinja1 expression
(it has to be included in ``{{ ... }}``).

Within the Jinja2 expression, the word/phrase must be included in ``_( ... )``.

The word/phrase to be translated can be read from a variable or can be specified as a constant text.
A constant text, has to be included in quotes (``'...')``.

So, if you have a a prompt in the web interface like this:

.. code-block:: html
   :caption: Example for `plugin/webif/templates/index.html`

   <td class="py-1"><strong>Service für den KNX Support</strong></td>

you can mark it for translation by marking it as a Jinja2 expression and the string as a
constant string to be translated:

.. code-block:: html
   :caption: Example with translation markup for `plugin/webif/templates/index.html`

   <td class="py-1"><strong>{{ _('Service für den KNX Support') }}</strong></td>


2. In Python code
-----------------

To mark a word or phrase for translation, the function translate of the plugin has to be called:

.. code-block:: python

   translated _text = self.translate('text')


How translation works
=====================

The translation is a multi-step process. The translation of the text (word/phrase) is:

   1. searched for in the working language of SmartHomeNG in the plugins' translation file
   2. If not found, the translation is searched for in the working language in the global translation file
   3. If not found, the translation is searched for in 'English' in the plugins' translation file
   4. If not found, the translation is searched for in 'English' in the global translation file
   5. If not found, the text is returned unaltered. In this case, a log entry of severity INFO is
      created, logging the missing translation.

The plugins' translation file is called **locale.yaml** and is stored in the plugin's directory.

The global translation file, which holds translations (mostly for single words) that are used by the core,
by modules and/or in several plugins,is called **locale.yaml** too and is stored in the **bin** directory
of SmartHomeNG.


Adding translations/languages
=============================

In the translation files, for each text to be translated a dict structure is defined in the section
``plugin_translations:``:

.. code-block:: YAML
   :caption: Example a translation

   plugin_translations:
       # Translations for the plugin specially for the web interface
       'Schließen':         {'de': '=', 'en': 'Close'}

The equal-sign in the translation for German signals that the key **Wert 2** is the right translation.
It makes the translation process stop looking for translations and prevents the log entry.

Further languages can be added, using the appropriate language code, followed by the translation text:

.. code-block:: YAML
   :caption: Example of a translation

   plugin_translations:
       # Translations for the plugin specially for the web interface
       'Schließen':         {'de': '=', 'en': 'Close', 'fr': 'Fermer'}


Using placeholders in translation strings :redsup:`Neu`
=======================================================

In the actual version of SmartHomeNG it is possible to use placeholders in translation strings. This makes it
easier to translate complete sentences, since the structure of a sentence can differ from language to language.

Translation strings can contain multiple placeholders. The placeholders and its values have to be defined as
a Pyhon dict. The keys are the placeholders names anf the values specifiy the values to be inserted into the
translation string.

The following example shows translation strings that contain a placeholder for the **item_id**. The name of
the placeholder must be surrounded by curly braces (with **no** spaces between the braces and the placeholder's
name).

.. code-block:: YAML
   :caption: Example of a translation with a placeholder

   plugin_translations:
    'Löschauftrag für die Einträge von Item ID {item_id} in der Tabelle "log" wurde erfolgreich initiiert!':
        'de': '='
        'en': 'Deletion of data for the entries of item ID {item_id} in table "log" successfully initiated.'


1. Defining placeholders in Jinja2 templates
--------------------------------------------

If you want a translation string (like in the example above) but you want to be flexible with the service name
and don't want to define a seperate translation string for each service you handle (e.g. KNX, enOcean, ...)
you can do it the following way:

.. code-block:: html

   <td class="py-1"><strong>{{ _('Service für den {service} Support', vars={'service': 'KNX'}) }}</strong></td>


2. Defining placeholders in Python code
---------------------------------------

If a translation text contains placeholders, the self.translate method of a plugin has to be called with a
second parameter, specifying the placeholder dict:

.. code-block:: python

   translated _text = self.translate('text', {'item_id', item.id()})


