
.. index:: Tipps & Tricks; Plugins: Ein Plugin aus develop installieren

.. _Plugin_aus_develop:

Ein Plugin aus develop installieren :greensup:`Update`
======================================================

Falls in Probleme mit einem Plugin auftreten, kann es hilfreich sein eine neuere Version des Plugins aus dem develop
Branch auf GitHub zu installieren, ohne deshalb die eigene Installation vollständig auf die (nicht notwendigerweise
stabile) develop Version von SmartHomeNG zu wechseln.

Dazu gibt es im Prinzip drei Wege, das Plugin zu installieren:

- ein Skript im tools-Verzeichnis
- das `githubplugin`-Plugin
- die manuelle Installation

.. tabs::

    .. tab:: Skript

        Im tools Verzeichnis gibt es ein Skript, welches ein gewähltes Plugin aus dem develop branch zusätzlich in die
        aktuelle Installation von SmartHomeNG kopiert. Damit kein Namenskonflikt mit einem bestehenden Plugin entsteht,
        wird an den Plugin Namen der String '_dev' angehängt. Ein Plugin mit dem Namen **xyz** wird also mit dem Namen
        **xyz_dev** in die bestehende SmartHomeNG Installation kopiert.

        Das Skript für Installation wird folgendermaßen gestartet:

        .. code-block:: bash

            install_plugin_from_develop xyz

        Nachdem das Skript erfolgreich endet, ist ein zusätzliches Plugin **xyz_dev** in der Installation vorhanden.

    .. tab:: githubplugin

        Das Plugin `githubplugin` ist seit Version 1.11 standardmäßig installiert und kann ohne weitere Konfiguration
        genutzt werden, wenn es in der ``etc/plugin.yaml`` aktiviert wurde. Die Dokumentation des Plugins befindet
        sich in :doc:`Plugins/githubplugin </plugins/githubplugin/user_doc>`.

    .. tab:: manuelle Installation

        Alternativ kann das Plugin manuell installiert werden. Im folgenden wird ein mögliches Vorgehen beschrieben,
        um ein Plugin aus dem develop Branch in eine Release Installation zu installieren. Dazu sind folgende Schritte
        durchzuführen:

        |

        **Plugins Repository aufrufen:**


        Im Browser die Seite http://www.github.com/smarthomeng/plugins aufrufen:

        .. image:: ../assets/plugin_install_1.jpg
           :class: screenshot

        |

        und in den develop Branch wechseln:

        .. image:: ../assets/plugin_install_2.jpg
           :class: screenshot

        |

        **Plugins Repository Download:**


        Anschließend auf den grünen **Code** Button klicken und **Download ZIP** auswählen:

        .. image:: ../assets/plugin_install_3.jpg
           :class: screenshot


        |

        Falls der Browser das ZIP Archiv nicht bereits entpackt hat, das Archiv ``plugins-develop.zip`` entpacken.

        |

        **Gewünschtes Plugin installieren:**

        Um zum Beispiel ein Plugin mit dem Namen **xyz** aus dem develop Branch zu installieren, sollte (falls es existiert)
        zuerst das Verzeichnis **xyz_dev** im ``plugins`` Verzeichnis gelöscht werden, damit keine Seiteneffekte durch
        bestehende Dateien auftreten.

        Anschließend kann das Verzeichnis **xyz** (mit allen Bestandteilen/Unterordnern) aus dem beim Entpacken entstandenen
        Verzeichnis ``plugins-develop`` in das ``plugins`` Verzeichnis der SmartHomeNG Installation unter dem Namen **xyz_dev**
        kopiert werden.

        Nun kann das Archiv ``develop.zip`` und das Verzeichnis ``plugins-develop`` gelöscht werden.

|

Konfiguration anpassen
----------------------

Um das neue Plugin zu aktivieren, muss noch die Plugin Konfiguration in der Datei ``etc/plugin.yaml`` angepasst werden.
Dazu muss im Abschnitt in dem das Plugin konfiguriert ist, der Eintrag ``plugin_name: xyz`` durch
``plugin_name: xyz_dev`` oder den im githubplugin selbst vergebenen Namen ersetzt werden.

Falls ein Logger für das ursprüngliche Plugin **xyz** konfiguriert ist, muss auch noch in ``etc/logging.yaml`` ein
Logger für das Plugin **xyz_dev** konfiguriert werden. Dazu einfach den Abschnitt mit dem Logger ``plugins.xyz``
kopieren und in der Kopie den Namen in ``plugins.xyz_dev`` oder ``plugins.<Namen aus githubplugin>`` ändern.

|

