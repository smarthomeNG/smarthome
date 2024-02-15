#!/usr/bin/env python3
# logics/example_logging.py

# Beispiel-Logik welche zeigt, wie Logeinträge verschiedener Levels in die Logdateien eingetragen werden.
#
# Dazu:
# - Diese Logik triggern
# - die Einträge in ../var/log/smarthome-warnings.log und ../var/log/smarthome-details.log prüfen

logger.warning(f"Logik '{logic.name}' (filename '{logic.filename}') wurde getriggert (WARNING)")
logger.notice(f"Logik '{logic.name}' (filename '{logic.filename}') wurde getriggert (NOTICE)")
logger.info(f"Logik '{logic.name}' (filename '{logic.filename}') wurde getriggert (INFO)")
logger.debug(f"Logik '{logic.name}' (filename '{logic.filename}') wurde getriggert (DEBUG)")

