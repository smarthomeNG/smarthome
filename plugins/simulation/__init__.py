#1!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2013 KNX-User-Forum e.V.            http://knx-user-forum.de/
#########################################################################
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
# 
#  ToDo
#  Fehlermeldung wenn Datei nicht geschrieben werden kann
#  Language Settings
#  Day is out of range for Month...  
#  Replay simulation from beginning when end of file is reached
#
#  Releases:
#  0.1  initial
#  0.2  fixed bug when play is pushed while recording
#       removed rest of state 3 (hold)
#  0.3  changed most logger.info to logger.debug
#       Added release version to init message
#  0.4  Changed logging style
#       corrected serious bug in compare entry with NextDay
#
#x#########################################################################

import logging
from datetime import datetime, timedelta
from lib.model.smartplugin import SmartPlugin

class Simulation(SmartPlugin):

    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION = "1.1.0.4"

    def __init__(self, smarthome,data_file):
        self.logger = logging.getLogger(__name__)
        self.logger.info('Init Simulation release 0.4')
        self._sh = smarthome
        self._datafile=data_file
        self.lastday=''
        smarthome.scheduler.add('midnight', self._midnight, cron='0 0 * *', prio=3)

    def run(self):
        self.logger.info('Starting Simulation')
        self.alive = True
        self._start_record()

        # if you want to create child threads, do not make them daemon = True!
        # They will not shutdown properly. (It's a python bug)

    def stop(self):
        self.logger.info('Exit Simulation')
        try:    
            self.file.close()
        except:
            self.logger.error('No file to close')
        self.alive = False
#--------------------------------- parse_item ----------------------------------
    def parse_item(self, item):
        if 'sim' in item.conf:
            if (item.conf['sim'] == 'message'):
                self._message_item=item
            if (item.conf['sim'] == 'state'):
                self.state=item
            if (item.conf['sim'] == 'control'):
                self.control=item
            if (item.conf['sim'] == 'tank'):
                self.tank=item
            return self.update_item
        else:
            return None

#--------------------------------- parse_logic ---------------------------------
    def parse_logic(self, logic):
        if 'xxx' in logic.conf:
            # self.function(logic['name'])
            pass

#--------------------------------- update_item ---------------------------------
# Callback. Writes the event to the file

    def update_item(self, item, caller=None, source=None, dest=None):
        if (item.conf['sim'] == 'track') and (self.state()==2):
            now = self._sh.now()
            day=now.day
            self.file.write(now.strftime('%a;%H:%M:%S'))
            self.file.write(';')
            self.file.write(item.id())
            self.file.write(';')
            self.file.write('{}'.format(item()))
            self.file.write(';')
            self.file.write(caller)
            self.file.write('\n')
            self.file.flush()
            self._message_item('Last event recorded: {}<br>{}   {}'.format(now.strftime('%H:%M:%S'),item.id(),item(),'Simulation'))
            return None
        if (item.conf['sim'] == 'control') and (caller != 'Simulation'):
            self.state_selector[self.state(),self.control()](self)
            self.control(0,'Simulation')

#----------------------- _start_record ---------------------------
# Called by run() and by the state machine. Compares times 
# and schedules recording accordingly. 

    def _start_record(self):
        tank=self._get_tank()
        self.logger.debug('Tank: {}'.format(tank))
        self.tank(tank)
        now = self._sh.now()
        last_entry = self._lastentry.replace(year=now.year, month=now.month, day=now.day,tzinfo=now.tzinfo)
        self.logger.debug('last entry: {}'.format(last_entry))
        self.logger.debug('now: {}'.format(now))
        now -= timedelta(minutes=15)
        if(now.time() < last_entry.time()):
            self._schedule_recording_start(last_entry)
        else:
            start=last_entry
            start += timedelta(days=1)
            self._schedule_recording_start(start)

#----------------------- _schedule_recording_start ---------------------------
    def _schedule_recording_start(self,time):
        self.state(1,'Simulation')
        self._sh.scheduler.remove('startrecord')
        self._message_item('Recording starts {}'.format(time), caller='Simulation') 
        self.logger.debug('Scheduling record start {}'.format(time))
        self._sh.scheduler.add('startrecord', self._start_recording, next=time)

#----------------------------- _start_recording --------------------------------
    def _start_recording(self):
        self.state(2,'Simulation')
        self._sh.scheduler.remove('startrecord')
        self._message_item('Recording', caller='Simulation') 
        self.logger.debug('starting record')
        self.recording=True
        try:
            self.file=open(self._datafile,'a')
        except IOError as error:
            self.logger.error('Cannot open file {} for writing: {}'.format(self._datafile,error))
            self._message_item('cannot write to file','Simulation') 
            self.state(0,'Smulation')

#----------------------------- _stop_recording ---------------------------------
    def _stop_recording(self):
        self.state(0,'Simulation')
        self._sh.scheduler.remove('startrecord')
        self._message_item('', caller='Simulation') 
        self.logger.debug('stop record')
        try:    
            self.file.close()
        except:
            self.logger.error('Not running')

#----------------------------- _start_playbacl ---------------------------------
    def _start_playback(self):
        self.state(4,'Simulation')
        self.logger.debug('Starting playback')
        try:    
            self.file=open(self._datafile,'r')
            self._wind_until_now()    
            self._set_item()
        except IOError as error:
            self.logger.error('NoFile {}'.format(error))
            self._message_item('No File','Simulation') 
            self.state(0,'Smulation')

#----------------------------- _stop_playback ---------------------------------
    def _stop_playback(self):
        self.state(0,'Simulation')
        self.logger.debug('Stopping playback')
        self._sh.scheduler.remove('simulate')
        self._message_item('Playback stopped','Simulation') 
        try:
            self.file.close()
        except:
            self.logger.error('No fileto close')

#--------------------------------- _set_item -----------------------------------
# Is called by the scheduler. Sets the item, reads the next event and
# schedules it. 

    def _set_item(self, **kwargs):
        target=None
        value=None
        if 'target' in kwargs:
            target = kwargs['target']
        if 'value' in kwargs:
            value = kwargs['value']
        if target!= None and value!= None:
            self.logger.debug('Setting {} to {}'.format(target,value))
            item=self._sh.return_item(target) 
            try:
                item(value, caller='Simulation') 
            except:
                self.logger.error('Skipped unknown item: {}'.format(target))
        entry=self.file.readline()
        if entry =='NextDay\n':
            entry=self.file.readline()
        if entry !='':
            day=entry.split(';')[0]
            time=entry.split(';')[1]
            target=entry.split(';')[2]
            value=entry.split(';')[3]
            hour=int(time.split(':')[0])
            minute=int(time.split(':')[1])
            seconds=int(time.split(':')[2])
            now = self._sh.now()
            next=now.replace(hour=hour, minute=minute,second=seconds)
            dif=next-now
            if (self.lastday != '') and (self.lastday != day):
                self.logger.debug('Found next day {} {} {} shitfing to tomorrow.'.format(target, value, next))
                next=next+timedelta(1)
            self._message_item('Next event: {}<br>{}   {}'.format(time,target,value,'Simulation'))
            self.logger.debug('Scheduling {} {} {}'.format(target, value, next))
            self._sh.scheduler.add('simulate', self._set_item, value={'target': target, 'value': value}, next=next)
            self.lastday=day    
        else:
            self.logger.info('End of file reached, simulation ended')
            self._message_item('Simulation ended','Simulation') 
            self.state(0,'Smulation')

#------------------------------ windnuntil_now --------------------------------
# Reads the events from the file and skips until a time stamp is reached
# that is past the actual time

    def _wind_until_now(self):
        next=0
        now=1
        while next < now:
            pos=self.file.tell()
            entry=self.file.readline()
            if entry == 'NextDay\n':
                entry=self.file.readline()
            if entry != '':
                time=entry.split(';')[1]
                hour=int(time.split(':')[0])
                minute=int(time.split(':')[1])
                seconds=int(time.split(':')[2])
                now = self._sh.now()
                next=now.replace(hour=hour, minute=minute,second=seconds)
                dif=next-now
            else:
                self.logger.info('End of file reached, simulation ended')
                self._message_item('Simulation ended','Simulation') 
                self.state(0,'Smulation')
                return None
        self.file.seek(pos)    

#-------------------------------- do_nothing ----------------------------------
    def _do_nothing(self):
        self.logger.debug('Do nothing state: {} control: {}'.format(self.state(), self.control()))

#-------------------------------- _midnight ----------------------------------
# Called by the scheduler at midnight. It writes the NextDas keyword and 
# removes the first day. 

    def _midnight(self):
        self.logger.debug('Midnight')
        if (self.state()==2):
            self.file.write('NextDay\n')
            self.file.flush()
            if(self.tank()>13):    
                self._remove_first_day()    
            else:
                tank=self.tank()
                self.tank(tank+1)

#-------------------------------- _get_tank ----------------------------------
# Returns the number of days in the  event file

    def _get_tank(self):
        self._lastentry=datetime.strptime('0:0:0','%H:%M:%S')
        try:    
            self.file=open(self._datafile,'r')
        except IOError as error:
            self.logger.error('NoFile {}'.format(error))
            return 0
        entry='bla'
        tank=0;
        while entry != '':
            entry=self.file.readline()
            if entry=='NextDay\n':
                tank=tank+1
            else:
                if entry != '':
                    self._lastentry=datetime.strptime(entry.split(';')[1],'%H:%M:%S')
        self.file.close()
        return tank        

#------------------------------ _remove_first_day ------------------------------
# Removes the forst day from the event file. It is called when the
# 15th day is finioshed at midnight.

    def _remove_first_day(self):
        self.logger.debug('Remove Day')
        self.file.close()
#        try:    
        self.file=open(self._datafile,'r')
#        except IOError as error:
#        self.logger.error('NoFile {}'.format(error))
#        try:    
        self.tempfile=open('/tmp/simulation.tmp','w')
#        except IOError as error:
#        self.logger.error('Canot open tempfile: {}'.format(error))
        entry='bla'    
        while (entry != 'NextDay\n') and (entry!=''):
            entry=self.file.readline()
        while (entry!=''):
            entry=self.file.readline()
            self.tempfile.write(entry)
        self.file.close()
        self.tempfile.close()
        self.tempfile=open('/tmp/simulation.tmp','r')
        self.file=open(self._datafile,'w')
        entry='bla'    
        while (entry!=''):
            entry=self.tempfile.readline()
            self.file.write(entry)
        self.file.close()
        self.tempfile.close()
        self.file=open(self._datafile,'a')





# state_selector state, control
#                       (0,1): _remove_first_day,
    state_selector = { (0,0): _do_nothing,
                       (0,1): _do_nothing,
                       (0,2): _start_playback,
                       (0,3): _start_record,
                       (1,0): _do_nothing,
                       (1,1): _stop_recording,
                       (1,2): _do_nothing,
                       (1,3): _start_recording,
                       (2,0): _do_nothing,
                       (2,1): _stop_recording,
                       (2,2): _start_playback,
                       (2,3): _do_nothing,
                       (4,0): _do_nothing,
                       (4,1): _stop_playback,
                       (4,2): _do_nothing,
                       (4,3): _do_nothing,}
