#!/usr/bin/env python3
# logics/example_persistance.py

# Diese Beispiel-Logik zeigt, Variablen definiert werden müssen, um den Lauf einer Logik zu überdauern
#
# Dazu:
# - Diese Logik triggern
# - die Einträge in ../var/log/smarthome-details.log prüfen
#
# - Diese Logik erneut triggern
# - die Einträge in ../var/log/smarthome-details.log prüfen

if not hasattr(logic, 'mycounter'):
    logic.mycounter = 0

logic.mycounter += 1

logger.info("Logik '{}' (filename '{}'): mycounter = {}".format(logic.name, logic.filename, logic.mycounter))

