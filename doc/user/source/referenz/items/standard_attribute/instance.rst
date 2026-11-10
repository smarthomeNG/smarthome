
.. index:: Standard-Attribute; instance
.. index:: instance
.. index:: Items; instance
.. index:: Plugins; Instanz eines Items

instance
--------

Das Attribut **instance** legt fest, zu welcher Instanz eines mehrfach eingebundenen Plugins die plugin-spezifischen
Attribute eines Items gehören. Als Wert wird der Name des Abschnitts in der ``etc/plugin.yaml`` angegeben, oder eine
Liste solcher Namen. Das Attribut gilt für das Item und für alle Items darunter, solange diese kein eigenes
**instance** setzen.

.. code-block:: yaml

    wan:
        instance: fb7490
        connection_status:
            type: str
            avm_data_type: wan_connection_status    # gilt als avm_data_type@fb7490

Regeln:

- Ein Attribut ohne ``@<instance>`` gehört zu dem Plugin, dessen Abschnitt in **instance** genannt wird, und nicht zur
  Standard-Instanz. Attribute von Plugins, zu denen **instance** keinen Abschnitt nennt, bleiben unverändert.
- ``instance: default`` wählt wieder die Standard-Instanz.
- ``instance: [fb7490, broker1]`` wählt für jedes Plugin den Abschnitt, der in der Liste vorkommt.
- Attribute mit ``@<instance>`` oder ``@*`` haben Vorrang. Ein Attribut mit ``@<abschnittsname>`` gilt immer für den
  Abschnitt dieses Namens, auch wenn er die Standard-Instanz ist.
- Nennt **instance** keinen Abschnitt der ``plugin.yaml``, wird beim Laden des Items eine Warnung ausgegeben.
- In **structs** wird der Platzhalter ``@instance`` durch den Namen ersetzt (siehe :doc:`struct <./struct>`).
- Mit ``legacy_instances: true`` in der ``etc/smarthome.yaml`` wird **instance** nur beim Einsetzen von structs
  ausgewertet.

Siehe auch :doc:`Plugins </konfiguration/plugins>`.
