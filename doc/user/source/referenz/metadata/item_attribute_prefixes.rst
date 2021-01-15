
.. role:: redsup
.. role:: bluesup

.. index:: item_attribute_prefixes; Plugin Metadaten
.. index:: Plugin Metadaten; item_attribute_prefixes

``item_attribute_prefixes``
---------------------------

Falls ein Plugin eine Reihe von Items definiert, deren vollständiger Name erst zur Konfigurationszeit bekannt ist,
werden diese Items durch ihren Namens-Anfang (Präfix) definiert. Diese Art von Item Definition (und damit auch dieser
Abschnitt der Metadaten) soll nur genutzt werden, wenn es unbedingt notwendig ist, wie zum Beispiel beim
``stateengine`` Plugin.


Der ``item_attribute_prefixes:`` Abschnitt definiert die Items ansonsten analog zum Abschnitt ``item_attributes``.

Die Definitionen im Abschnitt ``item_attribute_prefixes:``  werden für die Gültigkeitsprüfung der konfigurierten
Werte in den Konfigurationsdateien im Verzeichnis ``../items``, sowie zur Dokumentation und in der Zukunft zur
Konfiguration in der Admin GUI benutzt.

.. code:: yaml

    item_attributes:
        attribute1:
            type: int
            default: 1234
            description:
                de: 'Deutsche Beschreibung des Attributes'
                en: 'English description of the attribute'
            valid_list:
              - 1234
              - 2222
              - 4321

        attribute2:
            type: ...


.. include:: /referenz/metadata/parameter_keys.rst


Plugins ohne Attribut-Präfixe
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Falls ein Plugin keine Item Attribut-Präfixe definiert, wird das durch den folgenden Eintrag in der
Datei ``plugin.yaml`` angezeigt:

.. code:: yaml

    item_attribute_prefixes: NONE

.. hint::

    Bitte beachten, dass hier ``NONE`` vollständig in Großbuchstaben geschrieben werden muss.

