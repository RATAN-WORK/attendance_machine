import requests

class EraServer:
	def __init__(self , server=None , debug=True):
		"""
		:type debug: object
		by default , registration server and log server are same,
		registration server may be changed to separate
		"""
		self.server = server
		self.debug = debug

	def _print(self , s):
		# type: (object) -> object
		"""
		:type s: object

		"""
		if self.debug:
			print(s)

	def set_server(self , server_address):
		""" server where user logs will be sent"""
		self.server = server_address

	def post_request(self , url , headers , parameters):
		self._print(url)
		try:
			x = requests.post(url=url , data=parameters , headers=headers)
			return {'status_code': x.status_code , 'response': x.json()}
		except requests.ConnectionError as e:
			self._print("ConnectionError: " + str(e))
			return None
		except requests.Timeout as e:
			self._print("Timeout error " + str(e))
			return None
		except requests.RequestException as e:
			self._print("RequestException error " + str(e))
			return None
		except socket.error as e:
			self._print("socket error" + str(e))
			return None
		except Exception as e:
			self._print("Unknown error " + str(e))
			return None


	def get_server_time(self):
		self._print("getting server time")
		try:
			url = 'http://' + str(self.server) + ':7080/API/DeviceMaster/getDeviceCurrentDateTime'
			headers = {'accessToken': 'F651708E4BED47D7A75D02AA4F9E3589'}
			parameters = {}
			response = self.post_request(url , headers , parameters)
			if response is not None:
				code = response['status_code']
				res = response['response']
				self._print(code)
				self._print(res)
				if code == 200:
					return res['responseValue'][0]['deviceCurrentDateTime']
			return None
		except Exception as e:
			self._print("Error: " + str(e))
			return None

	def add_device_to_database(self , devicename,ip,default_password = None,):
		self._print("adding device to database")
		try:
			if default_password == None:
				default_password = '1234'
			if devicename == 'TEST':
				self._print('device is for evaluation only, not going to be inserted to the database')
				return True
			else:
				url = 'http://' + str(self.server) + ':7080/API/DeviceMaster/addDevice'
				headers = {'accessToken': 'F651708E4BED47D7A75D02AA4F9E3589'}
				parameters = {'deviceName': str(devicename),
							  'password': str(default_password),
							  'currentIPAddress': str(ip)
							  }
				response = self.post_request(url , headers , parameters)
				if response is not None:
					code = response['status_code']
					res = response['response']
					self._print(code)
					self._print(res)
					if code == 200:
						if 'success' in res['responseMessage']:
							self._print('success on server')
							return True
				return None
		except Exception as e:
			self._print("Error: " + str(e))
			return None

	def update_user_log(self , punchID , logDateTime , deviceName,image_url):
		self._print("updating user log")
		try:
			self._print('Update user log to server _')
			url = 'http://' + str(self.server) + ':7080/API/PunchLog/insertPunchLog'
			headers = {'accessToken': 'F651708E4BED47D7A75D02AA4F9E3589'}
			parameters = {'deviceName': str(deviceName) ,
						  'punchID': str(punchID) ,
						  'logDateTime': str(logDateTime) ,
						  'imageUrl':str(image_url)
						  }
			response = self.post_request(url , headers , parameters)
			print('response of update-user-log' ,response)
			if response is not None:
				status_code = response['status_code']
				res = response['response']
				response_message = res['responseMessage']
				response_code = res['responseCode']
				self._print(status_code)
				self._print(res)
				self._print(response_message)
				self._print(response_code)
				if status_code == 200:
					if 'success' in res['responseMessage']:
						self._print('success on server')
						return response_message
			return None
		except Exception as e:
			self._print("Error:== " + str(e))
			return None

	def update_data_to_server(self , punchId , deviceIndex , templete , timestamp , hostname):
		self._print('update data to server')
		# host_name = mu.get_host_name()
		# timestamp = mu.get_current_timestamp(1)
		try:
			url = 'http://' + str(self.server) + ':7080/API/UserMaster/addUser'
			headers = {'accessToken': 'F651708E4BED47D7A75D02AA4F9E3589'}
			parameters = {'punchId': str(punchId) ,
						  'deviceName': str(hostname) ,
						  'deviceIndex': str(deviceIndex) ,
						  'templete': str(templete) ,
						  'registrationDateTime': str(timestamp)
						  }
			response = self.post_request(url , headers , parameters)
			if response is not None:
				code = response['status_code']
				res = response['response']
				self._print(code)
				self._print(res)
				if code == 200:
					if 'success' in res['responseMessage']:
						self._print('success on server')
						return True
			return None
		except Exception as e:
			self._print("Error:== " + str(e))
			return None


	def publish_identity(self,hostname,ip_address,cpu_temp,uptime):
		self._print('publishing identity')
		try:
			url = 'http://' + str(self.server) + ':7080/API/DeviceMaster/updateDeviceIPDetails'
			headers = {'accessToken': 'F651708E4BED47D7A75D02AA4F9E3589'}
			parameters = {'deviceName': str(hostname) ,
						  'currentIPAddress': str(ip_address) ,
						  'deviceTemperture': str(cpu_temp) ,
						  'deviceUpTime': str(uptime)
						  }
			response = self.post_request(url , headers , parameters)
			self._print(response)
			return True
		except Exception as e:
			self._print("Error: " + str(e))
			return None


	def check_existing_user(self , id):
		"""
		:param id:
		checks on the server, if communications gets established,
		then returns, if user exists on the server or not.
		:return:
		"""
		self._print('function check existing user ')
		url = 'http://' + str(self.server) + ':7080/API/UserMaster/checkExistingUser'
		headers = {'accessToken': 'F651708E4BED47D7A75D02AA4F9E3589'}
		parameters = {'punchID': str(id)}
		response = self.post_request(url , headers , parameters)
		code = response['status_code']
		res = response['response']
		self._print(code)
		self._print(res)
		if code == 200:
			return res['responseValue'][0]['isExists']
		else:
			self._print('NETWORK ERROR')
			return None

	def test_api(self , userindex,timestamp=None):
		"""
		this definition is temparory, and it is not recommneded to use as primary api.
		:param userindex:
		:return:
		"""
		self._print("sending data on test api")
		try:
			import datetime
			import commands
			now = datetime.datetime.now()
			terminal = commands.getoutput('hostname')
			url = 'http://' + str(self.server) + ':203/GetLog.asmx/insertAttendance?'
			url = url + 'machineindexid=' + str(userindex)
			if timestamp == None:
				url = url + '&logtime=' + str(now.year) + '-' + str(now.month) + '-' + str(now.day) + ' ' + str(
					now.hour) + ':' + str(now.minute) + ':' + str(now.second)
			else:
				url = url +  '&logtime=' + str(timestamp)
			url = url + '&terminalid=' + str(terminal)
			url = url + '&authtype=1&authresult=1'
			self._print("url:     " + str(url))
			try:
				r = requests.get(url , timeout=2)
				self._print("SERVER RESPONSE====  " + str(r))
				if r.status_code == 200:
					jdata = r.json()
					self._print(jdata)
					user_name = jdata[0]['empname']
					self._print(user_name)
					return user_name
			except requests.ConnectionError as e:
				self._print("ConnectionError: " + str(e))
				return None
			except requests.Timeout as e:
				self._print("Timeout error " + str(e))
				return None
			except requests.RequestException as e:
				self._print("RequestException error " + str(e))
				return None
			except Exception as e:
				self._print("Unknown error " + str(e))
				return None
		except Exception as e:
			self._print("some error in function get_server_response:" + str(e))
			return None


if __name__ == '__main__':
	es = EraServer('192.168.7.13' , True)
	# es.add_device_to_database('TEST')
	# es.add_device_to_database('BMDCL')
	# es.check_existing_user(07041)
	# es.check_existing_user('07041')
	# es.test_api(1)
	print(es.get_server_time())
