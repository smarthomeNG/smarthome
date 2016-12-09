#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2012-2013 Marcus Popp                         marcus@popp.mx
#########################################################################
#  This file is part of SmartHomeNG.    https://github.com/smarthomeNG//
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.header import Header

logger = logging.getLogger('')


class IMAP():

    def __init__(self, smarthome, host, username, password, cycle=300, port=None, ssl=False):
        self._sh = smarthome
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self.cycle = int(cycle)
        self._mail_sub = {}
        self._mail_to = {}
        self._mail = False
        self._ssl = smarthome.string2bool(ssl)

    def _connect(self):
        if self._ssl:
            if self._port is not None:
                imap = imaplib.IMAP4_SSL(self._host, self._port)
            else:
                imap = imaplib.IMAP4_SSL(self._host)
        else:
            if self._port is not None:
                imap = imaplib.IMAP4(self._host, self._port)
            else:
                imap = imaplib.IMAP4(self._host)
        imap.login(self._username, self._password)
        return imap

    def _cycle(self):
        try:
            imap = self._connect()
        except Exception as e:
            logger.warning("Could not connect to {0}: {1}".format(self._host, e))
            return
        rsp, data = imap.select()
        if rsp != 'OK':
            logger.warning("IMAP: Could not select mailbox")
            imap.close()
            imap.logout()
            return
        rsp, data = imap.uid('search', None, "ALL")
        if rsp != 'OK':
            logger.warning("IMAP: Could not search mailbox")
            imap.close()
            imap.logout()
            return
        uids = data[0].split()
        for uid in uids:
            if not self.alive:
                break
            try:
                rsp, data = imap.uid('fetch', uid, '(RFC822)')
                if rsp != 'OK':
                    logger.warning("IMAP: Could not fetch mail")
                    continue
                mail = email.message_from_bytes(data[0][1])
                to = email.utils.parseaddr(mail['To'])[1]
                fo = email.utils.parseaddr(mail['From'])[1]
                subject, encoding = email.header.decode_header(mail['Subject'])[0]
                if encoding is not None:
                    subject = subject.decode(encoding)
            except Exception as e:
                logger.exception("IMAP: problem parsing message {}: {}".format(uid, e))
                continue
            if subject in self._mail_sub:
                logic = self._mail_sub[subject]
            elif to in self._mail_to:
                logic = self._mail_to[to]
            elif self._mail:
                logic = self._mail
            else:
                logic = False
            if logic:
                logic.trigger('IMAP', fo, mail, dest=to)
                rsp, data = imap.uid('copy', uid, 'Trash')
                if rsp == 'OK':
                    typ, data = imap.uid('store', uid, '+FLAGS', '(\Deleted)')
                    logger.debug("Moving mail to trash. {0} => {1}: {2}".format(fo, to, subject))
                else:
                    logger.warning("Could not move mail to trash. {0} => {1}: {2}".format(fo, to, subject))
            else:
                logger.info("Ignoring mail. {0} => {1}: {2}".format(fo, to, subject))
        imap.close()
        imap.logout()

    def run(self):
        self.alive = True
        self._sh.scheduler.add('IMAP', self._cycle, cycle=self.cycle)

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        pass

    def parse_logic(self, logic):
        if 'mail_subject' in logic.conf:
            self._mail_sub[logic.conf['mail_subject']] = logic
        if 'mail_to' in logic.conf:
            self._mail_to[logic.conf['mail_to']] = logic
        if 'mail' in logic.conf:
            self._mail = logic

    def update_item(self, item, caller=None, source=None, dest=None):
        pass


class SMTP():

    def __init__(self, smarthome, host, mail_from, username=False, password=False, port=25, ssl=False):
        self._sh = smarthome
        self._ssl = smarthome.string2bool(ssl)
        self._host = host
        self._port = int(port)
        self._from = mail_from
        self._username = username
        self._password = password

    def __call__(self, to, sub, msg):
        try:
            smtp = self._connect()
        except Exception as e:
            logger.warning("Could not connect to {0}: {1}".format(self._host, e))
            return
        try:
            msg = MIMEText(msg, 'plain', 'utf-8')
            msg['Subject'] = Header(sub, 'utf-8')
            msg['From'] = self._from
            msg['Date'] = email.utils.formatdate()
            msg['To'] = to
            msg['Message-ID'] = email.utils.make_msgid('SmartHomeNG')
            to = [x.strip() for x in to.split(',')]
            smtp.sendmail(self._from, to, msg.as_string())
        except Exception as e:
            logger.warning("Could not send message {} to {}: {}".format(sub, to, e))
        finally:
            try:
                smtp.quit()
                del(smtp)
            except:
                pass

    def _connect(self):
        smtp = smtplib.SMTP(self._host, self._port)
        if self._ssl:
            smtp.starttls()
        if self._username:
            smtp.login(self._username, self._password)
        return smtp

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        pass

    def parse_logic(self, logic):
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        pass
