
.. index:: Konfiguration; Feiertage
.. index:: Feiertage

Feiertage
=========

Feiertage werden im Reiter **Allgemein** der Systemkonfiguration konfiguriert. Hierzu stehen die Felder

- holidays_country
- holidays_province
- holidays_state

zur Verfügung.

Weiterhin können benutzerdefinierte Feiertage definiert werden. Hierzu stehen fünf Felder **holidays_custom**? zur
Verfügung in denen die entsprechenden Regeln hinterlegt werden können. Die Regeln werden in json formuliert (das Format
entspricht weitestgehend der Definition eines Python **dict**).

Die Definition darf folgende Keys enthalten:

- day
- month
- year
- name
- dow
- dow_week
- dow_start_week




location:
    country: Germany
    #province: HH       # for DE
    #state: FL          # state is only used for United States and Brazil

#custom:
#    # custom holidays without a specified year repeat every year
#    - '{"dow": 5, "dow_week": "last", "month": 7, "name": "Sysadmin day"}'           # last friday in July
#    - {"day": 2, "month": 8, "name": "Jon Doe's birthday"}
#    - {"day": 22, "month": 11, "name: "Jane Doe's birthday"}
#    - {"day": 2, "month": 8, "year": 2020, "name": "Jon Doe's 100th birthday"}
#    - {"dow": 5, "dow_week": "last", "month": 7, "name": "Sysadmin day"}         # last friday in July
#    - {"dow": 2, "dow_week": 2, "month": 7, "name": "second tuesday in July"}
#    - {"dow": 2, "dow_week": 2, "month": 7, "year": 2019, "name": "second tuesday in July '19"}
#    - {"dow": 3, "dow_week": 2, "year": 2021, "name": "Every second wednesday in 2021"}
#    - {"dow": 3, "dow_week": 2, "dow_start_week": 1, "year": 2021, "name": "Every second wednesday in 2021, starting on 1st wednesday"}

custom:
    - '{"dow": 5, "dow_week": "last", "month": 7, "name": "Sysadmin day"}'           # last friday in July


