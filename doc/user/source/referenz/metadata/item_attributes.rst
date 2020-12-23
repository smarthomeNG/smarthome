
.. role:: redsup
.. role:: bluesup

.. index:: item_attributes; Plugin Metadaten
.. index:: Plugin Metadaten; item_attributes

``item_attributes``
-------------------

Der Abschnitt ``item_attributes:`` hat für jedes definierte Item Attribut einen Unter-Abschnitt, der das Attribut genauer
beschreibt. Der Schlüssel des Unter-Abschnitts ist der Name des Attributes. Attributnamen sollten keine
Großbuchstaben und Sonderzeichen enthalten. Sie dürfen nicht mit einer Ziffer beginnen.

Die Definitionen im Abschnitt ``item_attributes:``  werden für die Gültigkeitsprüfung der konfigurierten Werte in den
Konfigurationsdateien im Verzeichnis ``../items``, sowie zur Dokumentation und in der Zukunft zur Konfiguration
in der Admin GUI benutzt.

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


Plugins ohne item-attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Falls ein Plugin keine Item Attribute hat, wird das durch den folgenden Eintrag in der
Datei ``plugin.yaml`` angezeigt:

.. code:: yaml

    item_attributes: NONE

.. hint::

    Bitte beachten, dass hier ``NONE`` vollständig in Großbuchstaben geschrieben werden muss.

