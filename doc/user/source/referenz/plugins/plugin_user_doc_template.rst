
.. code-block:: rst

    .. index:: Plugins; <Pluginname in Kleinbuchstaben>
    .. index:: <Pluginname in Kleinbuchstaben>


    ===============================
    <Pluginname in Kleinbuchstaben>
    ===============================


    .. image:: webif/static/img/plugin_logo.<png, jpg oder svg>
       :alt: plugin logo
       :width: 300px
       :height: 300px
       :scale: 50 %
       :align: left

    <Hier erfolgt die allgemeine Beschreibung des Zwecks des Plugins>


    Anforderungen
    =============

    ...

    Notwendige Software
    -------------------

    <Hier wird weitere benötigte Software beschrieben. Falls keine weitere Software benötigt wird, kann dieser
    Abschnitt entfallen.>

    Unterstützte Geräte
    -------------------

    <Hier werden unterstützte Geräte beschrieben. Falls keine keine speziell zu beschreibenden Geräte unterstützt
    werden, kann dieser Abschnitt entfallen.>


    Konfiguration
    =============

    Die Plugin Parameter und die Informationen zur Item-spezifischen Konfiguration des Plugins sind
    unter :doc:`/plugins_doc/config/<Pluginname in Kleinbuchstaben>` beschrieben.


    plugin.yaml
    -----------

    Zu den Informationen, welche Parameter in der ../etc/plugin.yaml konfiguriert werden können bzw. müssen, bitte
    bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/<Pluginname in Kleinbuchstaben>>` lesen, die aus
    den Metadaten der plugin.yaml erzeugt wurde (siehe oben).

    <Hier können bei Bedarf ausführliche Beschreibungen zu den Parametern dokumentiert werden.>

    items.yaml
    ----------

    Zu den Informationen, welche Attribute in der Item Konfiguration verwendet werden können bzw. müssen, bitte
    bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/<Pluginname in Kleinbuchstaben>>` lesen, die aus
    den Metadaten der plugin.yaml erzeugt wurde (siehe oben).

    <Hier können bei Bedarf ausführliche Beschreibungen zu den Attributen dokumentiert werden.>

    logic.yaml
    ----------

    Zu den Informationen, welche Konfigurationsmöglichkeiten für Logiken bestehen, bitte
    bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/<Pluginname in Kleinbuchstaben>>` lesen, die aus
    den Metadaten der plugin.yaml erzeugt wurde (siehe oben).

    Funktionen
    ----------

    Zu den Informationen, welche Funktionen das Plugin bereitstellt (z.B. zur Nutzung in Logiken), bitte
    bitte die Dokumentation :doc:`Dokumentation </plugins_doc/config/<Pluginname in Kleinbuchstaben>>` lesen, die aus
    den Metadaten der plugin.yaml erzeugt wurde (siehe oben).

    <Hier können bei Bedarf ausführliche Beschreibungen zu den Funktionen dokumentiert werden.>

    |

    Beispiele
    =========

    Hier können bei Bedarf Konfigurationsbeispiele dokumentiert werden.

    |

    Web Interface
    =============

    <Hier erfolgt die Beschreibung des Web Interfaces>

    Tab 1: <Name des Tabs>
    ----------------------

    <Hier wird der Inhalt und die Funktionalität des Tabs beschrieben.>

    .. image:: assets/webif_tab1.jpg
       :class: screenshot

    <Zu dem Tab ist ein Screenshot im Unterverzeichnis ``assets`` des Plugins abzulegen.

    |

Die Datei ``dev/sample_plugin/webif/templates/index.html`` sollte als Grundlage für Webinterfaces genutzt werden.
Um Tabelleninhalte nach Spalten filtern und sortieren zu können, muss der entsprechende Code Block mit Referenz
auf die relevante Table ID eingefügt werden (siehe Doku).

SmartHomeNG liefert eine Reihe Komponenten von Drittherstellern mit, die für die Gestaltung des Webinterfaces
genutzt werden können. Erweiterungen dieser Komponenten usw. finden sich im Ordner ``/modules/http/webif/gstatic``.

Wenn das Plugin darüber hinaus noch Komponenten benötigt, werden diese im Ordner ``webif/static`` des Plugins abgelegt.



    Version History
    ===============

    <In diesem Abschnitt kann die Versionshistorie dokumentiert werden, falls der Plugin Autor dieses möchte.
    Diese Abschnitt ist optional.>


