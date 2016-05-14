import logging
import re

from plugin import SiriPlugin

logger = logging.getLogger('')

class SmartHomeSiriPlugin(SiriPlugin):

    def __init__(self, smarthome):
        self._sh = smarthome

    def set_bool(self, phrase, match, item):
        logger.debug('set state for item {0}'.format(item))
        d = match.groupdict()
        item(d.has_key('True') and d['True'] is not None)
        self.respond('OK')
        self.complete()
    
    def set_num(self, phrase, match, item):
        logger.debug('set value for item {0}'.format(item))
        d = match.groupdict()
        if d.has_key('Num') and d['Num'] is not None:
            item(d['Num'])
        self.respond('OK')
        self.complete()

    def trigger_logic(self, phrase, match_groups, logic):
        logger.debug('trigger logic {0}'.format(logic))
        logic()
        response = 'OK'
        self.respond(response)
        self.complete()
