#
# This file contains user defined functions for use with SmartHomeNG
#
import logging
_logger = logging.getLogger(__name__)

_VERSION     = '0.1.0'
_DESCRIPTION = 'Per Anhalter durch die Galaxis'

#
# Example functions
#
def zweiundvierzig():

    return 'Die Antwort auf die Frage aller Fragen'

def itemtest(sh):

    return sh.env.location.sun_position.elevation.degrees()

def log_test():

    _logger.warning('Log-Test aus einer Userfunction')

    return
