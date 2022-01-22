#!/usr/bin/env python3
#
# This file contains a logic for use with SmartHomeNG
#
# Name of the logic: example_logic.py
#

# This logic performs the following function(s):
#
#    ...
#

# The following triggers should be defined in ../etc/logic.yaml:
#
#	watch_item = <item1> | <item2> | ...
#	crontab = init = Init
#   cycle = 600
#

logger.debug(f"Trigger: {trigger}")      # When debug logging is enabled for this logic, the values which
                                         # the logic is called with, are logged
                                         #
                                         # To enable debug logging for the logic, add a logger to your logging
                                         # configuration in ../etc/logging.yaml
                                         # loggers:
                                         #     ...
                                         #         logics:
                                         #             handlers: [shng_details_file]
                                         #             level: WARNING
                                         #
                                         #         logics.example_logic:      # has to be the name of the logic config, not the logic's Python file
                                         #             level: DEBUG
