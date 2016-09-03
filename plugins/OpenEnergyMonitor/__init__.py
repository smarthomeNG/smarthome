#!/usr/bin/env python3

import logging
from datetime import datetime, timedelta

logger = logging.getLogger('OpenEnergyMonitor')

class OpenEnergyMonitor():

	def __init__(self, smarthome, url='',timeout=4, writeApiKey='',inputKey='',nodeId=1):
		logger.info('Init OpenEnergyMonitor')
		self._sh = smarthome
		self.url = url
		self.timeout = timeout
		self.writeApiKey = writeApiKey
		self.inputKey = inputKey
		self.nodeId = nodeId
		if not self.url.endswith('/'):
			self.url += '/'

	def run(self):
		self.alive = True
		# uncomment to execute on startup
		#try:
		#	for item in self._sh.find_items('OpenEnergyMonitor'):
		#		logger.info('DEBUG: calling upload_value on ' + str(item))
		#		self.upload_value(item)
		#except Exception as ex:
		#	import traceback
		#	logger.error('ERROR: ' + traceback.format_exc())

	def stop(self):
		self.alive = False

	def parse_item(self, item):
		if 'OpenEnergyMonitor' in item.conf:
			return self.update_item
		else:
			return None

	def update_item(self, item, caller=None, source=None, dest=None):
		logger.debug('update_item called')
		try:
			self.upload_value(item)
		except Exc as ex:
			import traceback
			logger.error('ERROR: ' + traceback.format_exc())

	def upload_value(self, item):
		try:
			itemInputKey = self.inputKey
			itemNodeId = self.nodeId
			
			# allow overriding the default values
			if 'inputKey' in item.conf:
				logger.debug('Using inputKey from item')
				itemInputKey = item.conf['inputKey']
			if 'nodeId' in item.conf:
				logger.debug('Using nodeId from item')
				itemNodeId = item.conf['nodeId']

			logger.info('Value on ' + str(item) + ' has changed to ' + str(item()) + '. Uploading value as ' + itemInputKey + ' to ' + self.url)
			updateUrl = self.url + 'input/post.json?&apikey=' + self.writeApiKey + '&node=' + str(itemNodeId) + '&json={"' + itemInputKey + '":' + str(item()) + '}'
			logger.debug(updateUrl)
			self._sh.tools.fetch_url(updateUrl,timeout=float(self.timeout))
			logger.debug('upload done')
		except Exception as e:
			import traceback
			logger.error('Error connecting to {}: {}: {}'.format(self.url, e, traceback.format_exc()))
