#!/usr/bin/env python
#########################################################################
# Copyright 2013 Stefan Kals
#########################################################################
#  ComfoAir-Plugin for SmartHome.py.  http://mknx.github.com/smarthome/
#
#  This plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this plugin. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

controlset = {
    'comfoair350': {
        'PacketStart': 0x07F0,
        'PacketEnd': 0x070F,
        'Acknowledge': 0x07F3,
        'SpecialCharacter': 0x07,
        'ResponseCommandIncrement': 1
    },
    'comfoair500': {
        'PacketStart': 0x07F0,
        'PacketEnd': 0x070F,
        'Acknowledge': 0x07F3,
        'SpecialCharacter': 0x07,
        'ResponseCommandIncrement': -1
    }
}
    
# Mandatory command properties: Command, Type, ValueBytes
# Optional command properties: ResponsePosition (only for Type = Read), ValueTransform
# Remarks:
# Command must contain the command code (2 bytes) and the data length (1 byte) and can be optionally followed by data bytes.
# If ValueBytes is greater than 0, the value of the assigned item is taken, formatted to the number of bytes and added to the telegram.
# The data length byte must already have the correct amount of data bytes (sum of data bytes provided by 'Command' and dynamic data bytes (of 'ValueBytes' length)).
# Read-Commands MUST always have a length of 3 bytes and no data (third command byte = 00)
commandset = {
    'comfoair350': {
        'ReadComfortTemperature':       { 'Command': 0x00D100, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 1, 'ValueBytes': 1, 'ValueTransform': 'Temperature' },
        'ReadFreshAirTemperature':      { 'Command': 0x00D100, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 2, 'ValueBytes': 1, 'ValueTransform': 'Temperature' }, # Frischluft, außen
        'ReadSupplyAirTemperature':     { 'Command': 0x00D100, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 3, 'ValueBytes': 1, 'ValueTransform': 'Temperature' }, # Zuluft, innen
        'ReadExtractAirTemperature':    { 'Command': 0x00D100, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 4, 'ValueBytes': 1, 'ValueTransform': 'Temperature' }, # Abluft, innen
        'ReadExhaustAirTemperature':    { 'Command': 0x00D100, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 5, 'ValueBytes': 1, 'ValueTransform': 'Temperature' }, # Fortluft, außen
        'ReadGroundHeatTemperature':    { 'Command': 0x00D100, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 7, 'ValueBytes': 1, 'ValueTransform': 'Temperature' }, # Erdwärmetauscher
        'ReadPreHeatingTemperature':    { 'Command': 0x00D100, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 8, 'ValueBytes': 1, 'ValueTransform': 'Temperature' }, # Vorheizung
        'ReadSupplyAirPercentage':      { 'Command': 0x000B00, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 1, 'ValueBytes': 1 },
        'ReadExtractAirPercentage':     { 'Command': 0x000B00, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 2, 'ValueBytes': 1 },
        'ReadSupplyAirRPM':             { 'Command': 0x000B00, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 3, 'ValueBytes': 2, 'ValueTransform': 'RPM' },
        'ReadExtractAirRPM':            { 'Command': 0x000B00, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 5, 'ValueBytes': 2, 'ValueTransform': 'RPM' },
        'ReadBypassPercentage':         { 'Command': 0x000D00, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 1, 'ValueBytes': 1 },
        'ReadPreHeatingStatus':         { 'Command': 0x000D00, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 2, 'ValueBytes': 1 },
        'ReadOperatingHoursAway':       { 'Command': 0x00DD00, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 1, 'ValueBytes': 3 },
        'ReadOperatingHoursLow':        { 'Command': 0x00DD00, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 4, 'ValueBytes': 3 },
        'ReadOperatingHoursMedium':     { 'Command': 0x00DD00, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 7, 'ValueBytes': 3 },
        'ReadOperatingHoursAntiFreeze': { 'Command': 0x00DD00, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 10, 'ValueBytes': 2 },
        'ReadOperatingHoursPreHeating': { 'Command': 0x00DD00, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 12, 'ValueBytes': 2 },
        'ReadOperatingHoursBypass':     { 'Command': 0x00DD00, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 14, 'ValueBytes': 2 },
        'ReadOperatingHoursFilter':     { 'Command': 0x00DD00, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 16, 'ValueBytes': 2 },
        'ReadOperatingHoursHigh':       { 'Command': 0x00DD00, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 18, 'ValueBytes': 3 },
        'ReadCurrentVentilationLevel':  { 'Command': 0x00CD00, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 9, 'ValueBytes': 1 },
        'WriteComfortTemperature':      { 'Command': 0x00D301, 'CommandBytes': 3, 'Type': 'Write', 'ValueBytes': 1, 'ValueTransform': 'Temperature' },
        'WriteVentilationLevel':        { 'Command': 0x009901, 'CommandBytes': 3, 'Type': 'Write', 'ValueBytes': 1 },
        'WriteVentilationLevelAway':    { 'Command': 0x00990101, 'CommandBytes': 4, 'Type': 'Write', 'ValueBytes': 0 },
        'WriteVentilationLevelLow':     { 'Command': 0x00990102, 'CommandBytes': 4, 'Type': 'Write', 'ValueBytes': 0 },
        'WriteVentilationLevelMedium':  { 'Command': 0x00990103, 'CommandBytes': 4, 'Type': 'Write', 'ValueBytes': 0 },
        'WriteVentilationLevelHigh':    { 'Command': 0x00990104, 'CommandBytes': 4, 'Type': 'Write', 'ValueBytes': 0 },
        'WriteFilterReset':             { 'Command': 0x00DB0400000001, 'CommandBytes': 7, 'Type': 'Write', 'ValueBytes': 0 },
        'WriteErrorReset':              { 'Command': 0x00DB0401000000, 'CommandBytes': 7, 'Type': 'Write', 'ValueBytes': 0 }
    },
    'comfoair500': {
        'ReadComfortTemperature':       { 'Command': 0x008B00, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 2, 'ValueBytes': 1, 'ValueTransform': 'Temperature' },
        'ReadFreshAirTemperature':      { 'Command': 0x008500, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 4, 'ValueBytes': 1, 'ValueTransform': 'Temperature' }, # Frischluft, außen
        'ReadIntakeAirTemperature':     { 'Command': 0x008500, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 7, 'ValueBytes': 1, 'ValueTransform': 'Temperature' }, # Ansaugluft vor Comfofond (ComfoAir 500 has no Sensor for Supply Air - External Sensor ( e.g. Onewire ) required for full calculation)
        'ReadExtractAirTemperature':    { 'Command': 0x008500, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 5, 'ValueBytes': 1, 'ValueTransform': 'Temperature' }, # Abluft, innen
        'ReadExhaustAirTemperature':    { 'Command': 0x008500, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 6, 'ValueBytes': 1, 'ValueTransform': 'Temperature' }, # Fortluft, außen
        'ReadSupplyAirPercentage':      { 'Command': 0x008700, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 1, 'ValueBytes': 1 },
        'ReadExtractAirPercentage':     { 'Command': 0x008700, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 2, 'ValueBytes': 1 },
        'ReadSupplyAirRPM':             { 'Command': 0x008700, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 3, 'ValueBytes': 1 },
        'ReadExtractAirRPM':            { 'Command': 0x008700, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 4, 'ValueBytes': 1 },
        'ReadBypassPercentage':         { 'Command': 0x008500, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 1, 'ValueBytes': 1 },
        'ReadEnthalpyPercentage':       { 'Command': 0x00C100, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 1, 'ValueBytes': 1 },
        'ReadEnthalpyTemperature':      { 'Command': 0x00C100, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 2, 'ValueBytes': 1, 'ValueTransform': 'Temperature' },
        'WriteVentilationLevel':        { 'Command': 0x00A001, 'CommandBytes': 3, 'Type': 'Write', 'ValueBytes': 1 },
        'ReadEwtPercentage':            { 'Command': 0x008700, 'CommandBytes': 3, 'Type': 'Read', 'ResponsePosition': 5, 'ValueBytes': 1 } # EWT on/off Wobei 49 EWT Pumpe "ein" repräsentiert - und 17 EWT aus.
    }
}
