'''
Copyright (c) <2012> Tarek Galal <tare2.galal@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this 
software and associated documentation files (the "Software"), to deal in the Software 
without restriction, including without limitation the rights to use, copy, modify, 
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to the following 
conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR 
A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

from .Yowsup.Common.utilities import Utilities
from .Yowsup.Common.debugger import Debugger
from .Yowsup.connectionmanager import YowsupConnectionManager
import os
import hashlib
import base64
from .Yowsup.Media.uploader import MediaUploader
import datetime, sys
import logging
#from urllib.request import urlopen
from shutil import copyfileobj
import urllib

logger = logging.getLogger('Whatsapp')

class WhatsappListenerClient:
    
    def __init__(self, smarthome, keepAlive = False, sendReceipts = False, trusted = None, logic = 'Whatsapp'):
        self._sh = smarthome
        self.sendReceipts = sendReceipts
        self._trusted = trusted
        self._logic = logic
        self.autoreconnect = True
        Debugger.enabled =  False
        connectionManager = YowsupConnectionManager()
        connectionManager.setAutoPong(keepAlive)

        self.signalsInterface = connectionManager.getSignalsInterface()
        self.methodsInterface = connectionManager.getMethodsInterface()
        
        self.signalsInterface.registerListener("message_received", self.onMessageReceived)
        self.signalsInterface.registerListener("auth_success", self.onAuthSuccess)
        self.signalsInterface.registerListener("auth_fail", self.onAuthFailed)
        self.signalsInterface.registerListener("disconnected", self.onDisconnected)
        
        self.signalsInterface.registerListener("image_received",self.onImageReceived)
        self.signalsInterface.registerListener("media_uploadRequestSuccess", self.onUploadRequestSuccess)
        self.signalsInterface.registerListener("media_uploadRequestDuplicate", self.onUploadRequestDuplicate)
        self.signalsInterface.registerListener("media_uploadRequestFailed", self.onUploadRequestError)
        self.cm = connectionManager
    
    def login(self, username, password):
        self.username = username
        self.methodsInterface.call("auth_login", (username, password))
        

    def onAuthSuccess(self, username):
        logger.info("Whatsapp: Authed %s" % username)
        self.methodsInterface.call("ready")

    def onAuthFailed(self, username, err):
        logger.error("Whatsapp: Auth Failed!")

    def onDisconnected(self, reason):
        logger.info("Whatsapp: Disconnected because %s" %reason)
        if self.autoreconnect:
            self._sh.whatsapp.createListener()

    def onMessageReceived(self, messageId, jid, messageContent, timestamp, wantsReceipt, pushName, isBroadCast):
        formattedDate = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M')
        logger.info("Whatsapp: %s [%s]:%s"%(jid, formattedDate, messageContent))

        absender = jid.split('@',1)[0]
        self._absender = absender

        if absender in self._trusted:       
            if wantsReceipt and self.sendReceipts:
                self.methodsInterface.call("message_ack", (jid, messageId))

            self._sh.trigger(name=self._logic, value=messageContent, source=absender)
        else:
            logger.warn("Whatsapp: Sender is not trusted: "+absender)

    def sendImage(self,url):
        #Fuer den Preview muesste man das Bild verkleinern, auslesen und dan base64 encodene, das war mir zu stressig, deswegen gibts bei mir nur eine kleine Himbeere als Vorschau ;)
        receiver_jid = self._absender+"@s.whatsapp.net"        
        path = os.path.join(os.path.dirname(__file__), 'rasp.png')
        f=open(path,'rb')
        try:
            stream = base64.b64encode(f.read())
            self.methodsInterface.call("message_imageSend",(receiver_jid, url, "Raspberry Pi", str(os.path.getsize(path)), stream))
        except IOError as e:
            logger.error("Whatsapp: I/O error:"+e.strerror)
        except:
            logger.error("Whatsapp: Unexpected error:"+ sys.exc_info()[0])
            raise
        finally:
            f.close()

    def onUploadSuccess(self, url):
        self.sendImage(url)

    def onError(self):
        logger.error("Whatsapp: Error on sending Image")

    def onUploadRequestSuccess(self, _hash, url, resumeFrom):
        sender_jid = self.username+"@s.whatsapp.net"
        receiver_jid = self._absender+"@s.whatsapp.net"
        MU = MediaUploader(receiver_jid, sender_jid, self.onUploadSuccess, self.onError)
        MU.upload(self.local_path, url)

    def onUploadRequestDuplicate(self,_hash, url):
        self.sendImage(url)

    def onUploadRequestError(self,_hash):
        logger.error("Whatsapp: Error on Upload Image")

    def onImageReceived(self, messageId, jid, preview, url,  size, receiptRequested, isBroadcast):
        logger.info("Whatsapp: img received")
        self.methodsInterface.call("message_send", (jid, "Image received"))
        self.methodsInterface.call("message_ack", (jid, messageId))

    def sendPicture(self, url, username = None, password = None, phoneNumber = None):
        mtype = "image"
        sha1 = hashlib.sha256()
        #localpath = "/usr/smarthome/plugins/whatsapp/img.png"
        localpath = os.path.join(os.path.dirname(__file__), 'whatsappPic.png')
        self.local_path = localpath
        response = None
        if username and password:
            userpw = username+":"+password
            auth_encoded = base64.b64encode(userpw.encode('utf-8')).decode('utf-8')
            req = urllib.request.Request(url)
            req.add_header('Authorization', 'Basic '+auth_encoded)
            #req.add_header('Authorization', b'Basic ' + base64.b64encode(username + b':' + password))
            response = urllib.request.urlopen(req)
        else:
            response = urllib.request.urlopen(url)
        with open(localpath, 'wb') as out:
           copyfileobj(response, out)
        out.close()
        img = open(localpath,'rb')
        sha1.update(img.read())
        img.close()
        hsh = base64.b64encode(sha1.digest())
        self.methodsInterface.call("media_requestUpload", (hsh, "image", os.path.getsize(localpath)))



