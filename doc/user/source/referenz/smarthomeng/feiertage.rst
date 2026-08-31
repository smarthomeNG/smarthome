
.. index:: Konfiguration; Feiertage
.. index:: Feiertage

Feiertage
=========

Feiertage werden im Reiter **Allgemein** der Systemkonfiguration konfiguriert. Hierzu stehen die Felder

- holidays_country
- holidays_province
- holidays_state

zur Verfügung.

Weiterhin können benutzerdefinierte Feiertage definiert werden. Hierzu stehen fünf Felder
(**holidays_custom1** bis **holidays_custom5**) zur Verfügung, in denen jeweils eine Regel hinterlegt werden kann.
Die Regeln werden in json formuliert (das Format entspricht weitestgehend der Definition eines Python **dict**).

Die Definition darf folgende Keys enthalten:

- day
- month
- year
- name
- dow
- dow_week
- dow_start_week




.. code-block:: yaml
   :caption: etc/module.yaml (Modul core)

   core:
       holidays_country: DE
       #holidays_province: HH       # for DE
       #holidays_state: FL          # state is only used for United States and Brazil

       # custom holidays without a specified year repeat every year - one rule per field,
       # up to 5 custom rules (holidays_custom1 .. holidays_custom5)
       holidays_custom1: '{"dow": 5, "dow_week": "last", "month": 7, "name": "Sysadmin day"}'           # last friday in July
       holidays_custom2: '{"day": 2, "month": 8, "name": "Jon Does birthday"}'
       holidays_custom3: '{"day": 22, "month": 11, "name": "Jane Does birthday"}'
       holidays_custom4: '{"day": 2, "month": 8, "year": 2020, "name": "Jon Does 100th birthday"}'
       holidays_custom5: '{"dow": 3, "dow_week": 2, "dow_start_week": 1, "year": 2021, "name": "Every second wednesday in 2021, starting on 1st wednesday"}'


