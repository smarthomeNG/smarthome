
Beschreibung der Schlüssel im Abschnitt für einen Parameter bzw. ein Attribut:

- ``type:`` Beschreibt den Datatyp des Parameters bzw. Attributes. Gültige Datentypen sind:

   Einfache Datentypen:
    - ``bool`` - ein boolscher Wert
    - ``int`` - ein ganzzahliger Wert
    - ``scene`` - ein ganzzahliger Wert im Bereich von 0 bis 63, der eine Szenen Nummer repräsentiert
    - ``float`` - ein numerischer Wert der Nachkommastellen enthalten darf
    - ``num`` - das Equivalent zum Typ ```float``
    - ``str`` - ein String`
    - ``ip`` - ein String, der einen Hostnamen, eine ipv4-Adresse oder eine ipv6-Adresse repräsentiert
    - ``ipv4`` - ein String, der eine ipv4-Adresse repräsentiert
    - ``ipv6`` - ein String, der eine ipv6-Adresse repräsentiert
    - ``mac`` - ein String, der eine MAC Adresse repräsentiert
    - ``knx_ga`` - ein string, der eine KNX Gruppen Adresse (z.B..: 31/7/255) repräsentiert
    - ``foo`` - der universelle Datatyp

   Komplexe Datentypen:
    - ``dict`` - ein Dictionary
    - ``list`` - eine Liste bei der jedes Element vom Datentyp ``foo`` ist
    - ``list(len)`` - eine Liste fester Länge bei der jedes Element vom Datentyp ``foo`` ist und deren Anzahl Elemente **len** ist
    - ``list(subtype)`` - eine Liste bei der jedes Element vom Datentyp **subtype** ist :sup:`1` (z.B.: ``list(int)``
      or ``list(ipv4)``)
    - ``list(subtype, subtype, ...)`` - eine Liste bei der jedes Element von einem angegebenen  Datentyp ist.
      Falls die Liste länger ist als die Anzahl angegebener subtypes :sup:`1`, wird der letzte angegebene subtype
      für alle weiteren Elemente verwendet.
    - ``list(len,subtype, subtype, ...)`` - eine Liste fester Länge bei der bei der für jedes Element ein subtype
      angegeben wird. Falls die Liste länger ist als die Anzahl angegebener subtypes :sup:`1`, wird der letzte
      angegebene subtype für alle weiteren Elemente verwendet.

    :sup:`1` *subtype* kann nur ein einfacher Datentyp sein

- ``gui_type:`` Optional: Spezifiziert genauer, wie der Parameter in der Admin GUI shngadmin behandelt werden soll.
  Die Handhabung der Parameter in der Admin GUI wird durch den Parameter ``type`` bestimmt. ``type`` ist jedoch
  auf die Datentypen beschränkt, die SmartHomeNG kennt. Für das Editieren kann es jedoch wünschenswert sein,
  unterschiedlche Feld-Editoren für den selben Datentyp zu verwenden.

  Bisher werden nur zwei Werte für ``gui_type`` unterstützt:

  - ``wide_str`` wird benutzt, um ein breiteres Editor Feld zu verwenden (z.B. für Strings die einen längeren Inhalt
    haben können/sollen.
  - ``readonly`` wird benutzt, wenn der Parameter nicht in der GUI konfiguriert werden soll, z.B. wenn das Webinterface
    des Plugins diesen Parameter konfiguriert.

- ``default:`` Optional: Gibt einen Standardwert vor, der verwendet wird, falls bei der Konfiguration des
  Parameters in ``../etc/plugin.yaml`` bzw. ``../etc/module.yaml`` kein Wert angegeben wird.

- ``description:`` Mehrsprachiger Text, der die Funktion das Plugins beschreibt. Die Beschreibung wird bei der
  Generierung des Dokumentations-Seiten des Plugins verwendet - Die Texte in den verschiedenen Sprachen werden
  als Unter-Einträge in der Form <Sprache>: <Text> erfasst. Zur Identifikation der Sprache werden die 2-stelligen
  Länder-Kürzel verwendet (``de``, ``en``, ``fr``, ``pl``, ...)

  ``de`` und ``en`` müssen angegeben werden. Weitere Sprachen sind optional

- ``valid_list:`` Optional: Liste der erlaubten Werte für den Parameter (case sensitive)

- ``valid_list_ci:`` Optional: Liste der erlaubten Werte für den Parameter (nicht case sensitive)
  Der Wert wird dem Plugin/Modul in lower case übergeben.
  Falls ``valid_list_ci`` angegeben ist, wird eine evtl spezifizierte ``valid_list`` ignoriert.

- ``valid_list_description:`` Optional: Beschreibung der Werte, die in ``valid_list:`` bzw. ``valid_list_ci:``
  spezifiziert sind.
  Falls definiert, muss ``valid_list_description:`` Sub-Keys haben, um die Beschreibung in mehreren Sprachen
  (``de``, ``en``, ``fr``, ``pl``, ...) anzugeben.

  Jeder Sprach-Sub-Key muss eine Liste sein, die für jeden Eintrag in ``valid_list`` eine Beschreibung enthält.

- ``valid_min:`` Optional: Für die Datentypen ``int``, ``pint``, ``float``, ``pfloat``, ``num`` und  ``scene`` kann
  hier ein minimal Wert angegeben werden

- ``valid_max`` Optional: Für die Datentypen ``int``, ``pint``, ``float``, ``pfloat``, ``num`` und  ``scene`` kann
  hier ein maximal Wert angegeben werden

- ``mandatory:`` Optional: Falls auf ``True`` gesetzt, muss dieser Wert konfiguriert werden, damit das Plugin/Modul
  geladen/initialisiert wird. Diese Einschränkung ist wirkungslos, falls ein Wert für ``default:`` definiert ist.

