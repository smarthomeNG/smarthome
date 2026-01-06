
.. role:: redsup
.. role:: bluesup

.. index:: Modul Metadaten
.. index:: Metadaten; Modul
.. index:: Modul Metadaten; Globale Metadaten


module
------

Der globale Metadaten Abschnitt ``module:`` kennt die folgenden Schlüsselbegriffe:

.. code:: yaml

    # Metadata for the module
    module:
        # Global module attributes
        classname: Http
        version: 1.4.3
    #    sh_minversion: 1.7          # minimum shNG version to use this module (leave empty if no special requirement)
    #    sh_maxversion:              # maximum shNG version to use this module (leave empty if latest)
    #    py_minversion: 3.6          # minimum Python version needed for this module (leave empty if no special requirement)
    #    py_maxversion:              # maximum Python version to use this module (leave empty if no special requirement)
        description:
            de: 'Modul zur Implementierung von Backend-Webinterfaces für Plugins'
            en: 'Module for implementing a backend-webinterface for plugins'

Beschreibung der Schlüsselbegriffe im Abschnitt ``module:``

    - ``classname:`` Name der Python Klasse die das Modul implementiert un die zum Start des Moduls initialisiert wird
    - ``version:`` VersionsNumber des Moduls. Sie wird beim Laden mit der Versionsnummer die im Code definierert ist verglichen.
    - ``sh_minversion:`` Minimale SmartHomeNG Version mit der das Modul kmpatibel ist. Falls `sh_minversion`` leer ist, nimmt SmartHomeNG an, dass das Modul mit jeder älteren Version von SmartHomeNG kompatibel ist.
    - ``sh_maxversion:`` Maximale SmartHomeNG Version mit der das Modul kmpatibel ist. Falls `sh_maxversion`` leer ist, nimmt SmartHomeNG an, dass das Modul mit jeder neueren Version von SmartHomeNG kompatibel ist.
    - ``py_minversion:`` Minimale Python Version mit der das Modul kmpatibel ist. Falls `py_minversion`` leer ist, nimmt SmartHomeNG an, dass das Modul mit jeder älteren Python Version komatibel ist die von SmartHomeNG unterstützt wird.
    - ``py_maxversion:`` Maximale Python Version mit der das Modul kmpatibel ist. Falls `py_maxversion`` leer ist, nimmt SmartHomeNG an, dass das Modul mit jeder neueren Python Version komatibel ist die von SmartHomeNG unterstützt wird.
    - ``description:`` Mehrsprachiger Text, der die Funktion das Plugins beschreibt. Die Beschreibung wird bei der
      Generierung des Dokumentations-Seiten des Plugins verwendet - Die Texte in den verschiedenen Sprachen werden
      als Unter-Einträge in der Form <Sprache>: <Text> erfasst. Zur Identifikation der Sprache werden die 2-stelligen
      Länder-Kürzel verwendet (``de``, ``en``, ``fr``, ``pl``, ...)

      ``de`` und ``en`` müssen angegeben werden. Weitere Sprachen sind optional.

