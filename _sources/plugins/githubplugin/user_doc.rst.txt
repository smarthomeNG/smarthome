
.. index:: Plugins; githubplugin
.. index:: githubplugin


============
githubplugin
============

.. image:: webif/static/img/plugin_logo.png
   :alt: plugin logo
   :width: 300px
   :height: 300px
   :scale: 50 %
   :align: left


Beschreibung
============

Wenn man das Plugin eines anderen Autors ausprobieren oder testen möchte, muss es aus einem fremden Repository von GitHub in die eigene Installation eingebunden werden.

Dieses Plugin ermöglicht es komfortabel, fremde Plugins von GitHub zu installieren und wieder zu deinstallieren. 

Die Bedienung des Plugins und die Übersicht über installierte Plugins erfolgt über das Web-Interface, das über die Admin-UI von SmartHomeNG zugänglich ist.

Dort können Plugins angezeigt, installiert und entfernt  sowie durch einen pull aktualisiert werden. Das Aktualisieren oder Löschen von installierten Plugins ist nur möglich, wenn deren git-Verzeichnisse keine veränderten, gelöschten oder hinzugefügten Dateien enthalten und alle neuen mögliche Commits zu GitHub hochgeladen wurden (push).

Das Plugin legt im Verzeichnis `plugins` das Unterverzeichnis `priv_repos` an, in dem die heruntergeladenen Daten abgelegt werden. Für jedes Plugin werden die folgenden Dateien bzw. Verzeichnisse benötigt:

- ein Repository ("git clone") in `plugins/priv_repos/<Autor>/`; dieser Ordner kann durch mehrere Plugins genutzt werden,
- ein Ordner mit Worktree-Daten für den jeweiligen Branch in `plugins/priv_repos/<Autor>_wt_<Branch>/`,
- eine Verknüpfung/Symlink `plugins/priv_<Name>`, die auf den Plugin-Ordner im Worktree verlinkt.

Dabei ist Name ein Bezeichner, der vom Nutzer selbst festgelegt werden kann. Dieser wird dann in der Form `priv_<Name>` auch in der `etc/plugin.yaml` als Bezeichner für das Plugin verwendet.

Im Status-Bereich zeigt das Web-If an, wieviele Zugriffe in der aktuellen Konfiguration pro Stunde möglich und wieviele noch verfügbar sind. Wenn die Zugriffe verbraucht sind, wird die Zeit bis zum nächsten Rücksetzzeitpunkt angezeigt und alle 10 Sekunden aktualisiert.

Anforderungen
=============

Notwendige Software
-------------------

Das Plugin benötigt die Python-Pakete GitPython und PyGithub.

Konfiguration
=============

Das Plugin benötigt keine Konfiguration.

Ohne weiteres Zutun sind 60 Zugriffe pro Stunde möglich. Für normale Nutzer, die gelegentlich neue Plugins zum Testen oder Ausprobieren installieren, reicht das völlig aus. Wenn mehr Zugriffe benötigt werden, kann auf der Seite `GitHub App-Tokens <https://github.com/settings/tokens>` ein Token registriert und in der Plugin-Konfiguration hinterlegt werden. Damit sind bis zu 5000 Zugriffe pro Stunde möglich.

Die Plugin-Parameter sind unter :doc:`/plugins_doc/config/githubplugin` beschrieben.

