import logging

logger = logging.getLogger('EnOcean')

class EEP_Parser():

    def __init__(self):
        logger.info('enocean: eep-parser instantiated')

    def CanParse(self, eep):
        found = callable(getattr(self, "_parse_eep_" + eep, None))
        if (not found):
            logger.error("eep-parser: missing parser for eep {} - there should be a _parse_eep_{}-function!".format(eep, eep))
        return found

    def Parse(self, eep, payload, status):
        #logger.debug('enocean: parser called with eep={} / payload={} / status={}'.format(eep, payload, status))
        results = getattr(self, "_parse_eep_" + eep)(payload, status)
        #logger.info('enocean: parser returns {}'.format(results))
        return results

    def _parse_eep_A5_02_01(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 40.0) - 40.0}

    def _parse_eep_A5_02_02(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 40.0) - 30.0}

    def _parse_eep_A5_02_03(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 40.0) - 20.0}

    def _parse_eep_A5_02_04(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 40.0) - 10.0}

    def _parse_eep_A5_02_05(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 40.0)}

    def _parse_eep_A5_02_06(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 40.0) + 10.0}

    def _parse_eep_A5_02_07(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 40.0) + 20.0}

    def _parse_eep_A5_02_08(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 40.0) + 30.0}

    def _parse_eep_A5_02_09(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 40.0) + 40.0}

    def _parse_eep_A5_02_0A(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 40.0) + 50.0}

    def _parse_eep_A5_02_0B(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 40.0) + 60.0}

    def _parse_eep_A5_02_10(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 80.0) - 60.0}

    def _parse_eep_A5_02_11(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 80.0) - 50.0}

    def _parse_eep_A5_02_12(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 80.0) - 40.0}

    def _parse_eep_A5_02_13(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 80.0) - 30.0}

    def _parse_eep_A5_02_14(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 80.0) - 20.0}

    def _parse_eep_A5_02_15(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 80.0) - 10.0}

    def _parse_eep_A5_02_16(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 80.0)}

    def _parse_eep_A5_02_17(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 80.0) + 10.0}

    def _parse_eep_A5_02_18(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 80.0) + 20.0}

    def _parse_eep_A5_02_19(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 80.0) + 30.0}

    def _parse_eep_A5_02_1A(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 80.0) + 40.0}

    def _parse_eep_A5_02_1B(self, payload, status):
        return {'TMP': (payload[2] / 255.0 * 80.0) + 50.0}

    def _parse_eep_A5_02_20(self, payload, status):
        return {'TMP': (((payload[1] & 0x03) * 256.0 + payload[2]) / 20.0) - 10.0}

    def _parse_eep_A5_02_30(self, payload, status):
        return {'TMP': (((payload[1] & 0x03) * 256.0 + payload[2]) / 10.0) - 40.0}

    def _parse_eep_A5_11_04(self, payload, status):
        #4 Byte communication (4BS) Telegramm, RORG = A5 = ORG = 0x07
        # For example dim status feedback from eltako FSUD-230 actor.
        #Data_byte3 = 0x02
        #Data_byte2 = Dimmwert in % von 0-100 dez.
        #Data_byte1 = 0x00
        #Data_byte0 = 0x08 = Dimmer aus, 0x09 = Dimmer an
        logger.debug("enocean: processing A5_11_04: Dimmer Status on/off")
        results = {}
        #if !( (payload[0] == 0x02) and (payload[2] == 0x00)):
        #    logger.error("enocean: error in processing A5_11_04: static byte missmatch")
        #    return results
        results['D'] = payload[1]
        if (payload[3] == 0x08):               # Dimmer is off
            results['STAT'] = 0
        elif (payload[3] == 0x09):             # Dimmer is on
            results['STAT'] = 1
        return results

    def _parse_eep_A5_12_01(self, payload, status):
        # Status command from switche actor with powermeter, for example eltako FSVA-230, RORG = 0x07
        logger.debug("enocean: processing A5_12_01")
        results = {}
        status = payload[3]
        value = (payload[0] << 16) + (payload[1] << 8) + payload[2]
        results['VALUE'] = value
        return results

    def _parse_eep_A5_38_08(self, payload, status):
        results = {}
        if (payload[1] == 2):  # Dimming
            results['EDIM'] = payload[2]
            results['RMP'] = payload[3]
            results['LRNB'] = ((payload[4] & 1 << 3) == 1 << 3)
            results['EDIM_R'] = ((payload[4] & 1 << 2) == 1 << 2)
            results['STR'] = ((payload[4] & 1 << 1) == 1 << 1)
            results['SW'] = ((payload[4] & 1 << 0) == 1 << 0)
        return results

    def _parse_eep_A5_3F_7F(self, payload, status):
        #logger.debug("enocean: processing A5_3F_7F")
        results = {'DI_3': (payload[3] & 1 << 3) == 1 << 3, 'DI_2': (payload[3] & 1 << 2) == 1 << 2, 'DI_1': (payload[3] & 1 << 1) == 1 << 1, 'DI_0': (payload[3] & 1 << 0) == 1 << 0}
        results['AD_0'] = (((payload[1] & 0x03) << 8) + payload[2]) * 1.8 / pow(2, 10)
        results['AD_1'] = (payload[1] >> 2) * 1.8 / pow(2, 6)
        results['AD_2'] = payload[0] * 1.8 / pow(2, 8)
        return results

    def _parse_eep_D5_00_01(self, payload, status):
        #ORG = 0x06
        #Window/Door Contact Sensor, for example Eltako FTK, FTKB
        logger.debug("enocean: processing D5_00_01: Door contact")
        return {'STATUS': (payload[0] & 0x01) == 0x01}

    def _parse_eep_F6_02_01(self, payload, status):
        logger.debug("enocean: processing F6_02_01: Rocker Switch, 2 Rocker, Light and Blind Control - Application Style 1")
        results = {}
        R1 = (payload[0] & 0xE0) >> 5
        EB = (payload[0] & (1<<4) == (1<<4))
        R2 = (payload[0] & 0x0E) >> 1
        SA = (payload[0] & (1<<0) == (1<<0))
        NU = (status & (1<<4) == (1<<4))

        if (NU):
            results['AI'] = (R1 == 0) or (SA and (R2 == 0))
            results['AO'] = (R1 == 1) or (SA and (R2 == 1))
            results['BI'] = (R1 == 2) or (SA and (R2 == 2))
            results['BO'] = (R1 == 3) or (SA and (R2 == 3))
        elif (not NU) and (payload[0] == 0x00):
            results = {'AI': False, 'AO': False, 'BI': False, 'BO': False}
        else:
            logger.error("enocean: parser detected invalid state encoding - check your switch!")
        return results

    def _parse_eep_F6_02_02(self, payload, status):
        logger.debug("enocean: processing F6_02_02: Rocker Switch, 2 Rocker, Light and Blind Control - Application Style 2")
        return self._parse_eep_F6_02_01(payload, status)

    def _parse_eep_F6_02_03(self, payload, status):
        #Repeated switch communication(RPS) Telegramm, RORG = F6 = ORG = 0x05
        # Status command from bidirectional actors, for example eltako FSUD-230, FSVA-230V or switches (for example Gira)
        logger.debug("enocean: processing F6_02_03: Rocker Switch, 2 Rocker")
        results = {}
        #Button A1: Dimm light down
        results['AI'] = (payload[0]) == 0x10
        #Button A0: Dimm light up
        results['AO'] = (payload[0]) == 0x30
        #Button B1: Dimm light down
        results['BI'] = (payload[0]) == 0x50
        #Button B0: Dimm light up
        results['BO'] = (payload[0]) == 0x70
        if (payload[0] == 0x70):
            results['B'] = True
        elif (payload[0] == 0x50):
            results['B'] = False
        elif (payload[0] == 0x30):
            results['A'] = True
        elif (payload[0] == 0x10):
            results['A'] = False
        return results

    def _parse_eep_F6_10_00(self, payload, status):
        logger.debug("enocean: processing F6_10_00: Mechanical Handle")
        results = {}
        if (payload[0] == 0xF0):
            results['STATUS'] = 0
        elif ((payload[0]) == 0xE0) or ((payload[0]) == 0xC0):
            results['STATUS'] = 1
        # Typo error in Eltako Datasheet for 0x0D instead of the right 0xD0
        elif (payload[0] == 0xD0):
            results['STATUS'] = 2
        else:
            logger.error("enocean: error in F6_10_00 handle status")
        return results
