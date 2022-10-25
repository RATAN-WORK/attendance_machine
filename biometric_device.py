#!/user/bin/python

import time
from hardwares import hardware
from softwares.era_server import era_server
from storage import msql
from storage import text_storage
from system import system


class Biometric_device():
	variables = {'password': '1234' ,
				 'setting_mode': False ,
				 'camera_enabled': True ,
				 'process_id': None ,
				 'api1_enabled': True ,
				 'api2_enabled': False ,
				 'mqtt_enabled': True ,
				 'api1_server': '192.168.7.13' ,
				 'api2_server': '192.168.7.13' ,
				 'mqtt_server': '192.168.10.108' ,
				 'test_server': '192.168.7.13' ,
				 'test_api_enabled': False ,
				 'live_server': 'SERVER1' ,  # [[DEFAULT],SERVER1,SERVER2,TEST_SERVER]
				 'host_name': 'TEST' ,
				 'text_file_enabled': True ,
				 'max_users': '999' ,
				 'server_updation_interval': 15 ,  # in minutes will update to server in every n minutes.
				 'offline_registration_enabled': False ,
				 'send_realtime_data': True ,  # data will be sent as soon as punching is done
				 'sync_db_on_start': True ,  # from sqldb to module db
				 'publish_identity_interval': 15 ,  # after every 15 minutes identity is published.
				 'biometric_type': 'R30x' ,  # [R30x,FIM60x]
				 'images_log_path': '/home/pi/database/static/images_logs/' ,
				 'images_database_path': '/home/pi/database/images_database/',
				 'hdmi_enable':False
				 }
	def __init__(self , hw=True , srvr=True , syss=True):

		if syss:
			self.syss = system.System()
		else:
			self.syss = None

		if hw:
			self.hw = hardware.Hardware(display_type='DOT_MATRIX_20X4' , keypad_type='KEYPAD_4X4' , red_led_pin=18 ,
										green_led_pin=23 , buzzer_pin=21 , switch_pin=24 , biometric_type='R30x' ,
										biometric_port='/dev/ttyS0')
			self.hw.begin_digital_io()
			self.hw.begin_display()
			self.hw.begin_keypad()
			self.hw.begin_biometric()
			self.hw.check_hardwares()
		else:
			self.hw = None

		if srvr:
			self.es = era_server.EraServer()
		else:
			self.es = None

		self.txs = text_storage.File_IO()

	def create_default_folders(self):
		try:
			self.update_variables_from_database()
			images_log_folder = Biometric_device.variables['images_log_path']
			images_database_folder = Biometric_device.variables['images_database_path']
			self.syss.create_directory(images_log_folder)
			self.syss.create_directory(images_database_folder)
			return True
		except Exception as e:
			print("Error creating default folders: " + str(e))
			return None

	def __del__(self):
		if self.hw is not None:
			self.hw.print_screen('GOOD BYE')
		time.sleep(1)
		pass

	def update_file_user_log(self , s):
		try:
			ts = self.syss.get_current_timestamp(1)
			full_path ='/home/pi/database/user_logs.txt'
			self.txs.file_writer('\n' + str(ts) + '\n' ,full_path  , 'a')
			self.txs.file_writer(str(s) ,full_path, 'a')
			return True
		except Exception as e:
			print (str(e))

	def update_file_error_log(self , s):
		try:
			ts = self.syss.get_current_timestamp(1)
			full_path = '/home/pi/database/errors.txt'
			self.txs.file_writer('\n' + str(ts) + '\n' ,full_path  , 'a')
			self.txs.file_writer(str(s) , full_path,'a')
			return True
		except Exception as e:
			print (str(e))
			return None

	def update_file_device_log(self , s):
		try:
			ts = self.syss.get_current_timestamp(1)
			full_path ='/home/pi/database/device_logs.txt'
			self.txs.file_writer('\n' + str(ts) + '\n' , full_path , 'a')
			self.txs.file_writer(str(s) ,full_path, 'a')
			return True
		except Exception as e:
			print (str(e))
			return None

	def update_file_registration_log(self , s):
		try:
			ts = self.syss.get_current_timestamp(1)
			full_path ='/home/pi/database/registration.txt'
			self.txs.file_writer('\n' + str(ts) + '\n' , full_path, 'a')
			self.txs.file_writer(str(s) ,full_path, 'a')
			return True
		except Exception as e:
			print (str(e))
			return None

	def reset_data(self , level=0):
		"""
		only settings values will be restored to default.
		after this call , setting variables must be created.

		"""
		if level == 0:
			msql.clear_user_logs()
			return True
		if level == 1:
			msql.clear_registration_table()
			return True
		elif level == 2:
			msql.delete_tables()
			msql.create_tables()
			for key , value in self.variables.items():
				r = msql.create_settting_parameter(key , value)
				if r is None:
					return None
			return True
		elif level == 3:  # everything gets cleared
			msql.delete_tables()
			self.syss.remove_directory('/home/pi/database')
			self.create_default_folders()
			return True
		return None

	def update_variables_from_database(self):
		"""
		returns None if no data is found(may be table doesn't exist)
		should be used to create default parameters,
		should be considered as first start.
		"""
		data = msql.get_all_parameters()
		if data == None:
			return None
		else:
			for key , value in data:
				self.variables[key] = value
			return True

	def get_variables(self):
		return self.variables

	def verify_password(self , attempts=1 , password=None):
		if password is None:
			for i in range(attempts):
				password = self.hw.get_no('PASSWORD')
				if str(password).isdigit():
					if int(password) == int(self.variables['password']):
						return True
		else:
			if int(password) == int(self.variables['password']):
				return True
			else:
				return False

	def register_user(self , punch_id=None):
		"""
		Updates user to the database ,not to module
		after this registration , data must be updated to the module also
		"""
		msql.update_module_at_startup(True)  # no more udpation required
		self.update_variables_from_database()
		offline_registration = int(self.variables['offline_registration_enabled'])
		if offline_registration:
			self.hw.print_screen("OFFLINE ENABLED")
		else:
			self.hw.print_screen("OFFLINE DISABLED")
			self.update_variables_from_database()
			server1 = Biometric_device.variables['api1_server']
			server2 = Biometric_device.variables['api2_server']
			server1_enabled = Biometric_device.variables['api1_enabled']
			server2_enabled = Biometric_device.variables['api2_enabled']
			print(server1 , server2 , server2_enabled , server2_enabled)
			self.hw.print_screen("SERVER:" + str(server1))
			if server1_enabled:
				self.es.set_server(server1)
				self.hw.print_screen("SERVER:" + str(server1))
			elif server2_enabled:
				self.es.set_server(server2)
				self.hw.print_screen("SERVER:" + str(server2))
			else:
				self.hw.print_screen("NO SERVER ENABLED")
				time.sleep(1)
				return None
		time.sleep(2)
		attmpts = 3
		while (attmpts):
			try:
				n = msql.get_no_of_registered_users()
				self.hw.clear_screen()
				self.hw.print_screen("Registered Users: " , 1)
				self.hw.print_screen(str(n) , 2)
				time.sleep(2)

				if (punch_id is None):
					punch_id = self.hw.get_no('PUNCH ID')
					if str(punch_id).isdigit() is not True:
						self.hw.print_screen("INVALID NO")
						return False

				check1 = msql.check_if_user_exists(punch_id)  # local check

				if check1 > 0:
					self.hw.print_screen('ALREADY IN LOCAL DB')
					time.sleep(1)
					return False

				if not offline_registration:
					self.hw.print_screen("CHECKING ON SERVER")
					check2 = self.es.check_existing_user(punch_id)
					time.sleep(1)
					print('check2' , check2)
					if check2 is None:
						self.hw.print_screen("SERVER ERROR")
						self.hw.print_screen("CHECK NETWORK CONNECTION" , 2)
						time.sleep(2)
						return False
					else:
						if check2:
							self.hw.print_screen("USER PRESENT ON SERVER")
							time.sleep(2)
							return False
						else:
							self.hw.print_screen("LOCAL: OK")
							self.hw.print_screen("SERVER: OK")
							time.sleep(2)

				template = self.hw.get_template()
				# print('template: '+ str(len(template)))
				if template is not None:
					r = msql.log_registration(punch_id , template)
					self.update_file_registration_log(str(punch_id) + " " + str(template))
					# print('msql response' + str(r))
					if r is not None:
						self.hw.clear_screen()
						self.hw.print_screen('LOCAL DONE: ' , 1)
						self.hw.print_screen(str(r) , 2)
						n = msql.get_no_of_registered_users()
						self.hw.print_screen('TOTAL: ' + str(n) , 3)
						time.sleep(2)
					# return True
					else:
						self.hw.print_screen("Error, try again")
						time.sleep(2)
						return False
					if not offline_registration:
						self.hw.print_screen("Trying on Server")
						s = self.es.update_data_to_server(punch_id , -1 , template ,
														  self.syss.get_current_timestamp(1) ,
														  self.syss.get_host_name())
						if s is not None:
							self.hw.print_screen("Success on Server")
							self.hw.print_screen("ID:" + str(punch_id) , 2)
							time.sleep(2)
							return True
						else:
							self.hw.print_screen("SERVER ERROR,TRY AGAIN")
							time.sleep(2)
							return False
					else:
						return True
			except Exception as e:
				print("ERROR: " + str(e))
				time.sleep(2)
				self.hw.print_screen("Error, try again" , 1)
				self.hw.print_screen(str(e) , 2)
				time.sleep(2)
				attmpts = attmpts - 1

		return False

	def clear_module(self):
		if self.hw.clear_biometric_database():
			self.hw.print_screen('module db cleared')
			time.sleep(1)
			return True
		else:
			self.hw.print_screen('error clearing module db')
			return False

	def check_user(self):
		"""
		scans and if user exists returns its [index,level,pid]
		must be handled with error exception
		"""
		try:
			user = self.hw.scan_user()
			if user is not None:
				user_index = user[0]
				user_p = user[1]
				if user_index >= 0:
					user_pid = msql.find_pid_from_index(user_index)
					return [user_index , user_p , user_pid]
				else:
					return [user_index , user_p , None]

			else:
				return None
		except Exception as e:
			return None

	def auto_sync_enabled(self):
		self.update_variables_from_database()
		d = Biometric_device.variables['sync_db_on_start']
		# print('auto sync enabled',d)
		if d is None:
			return None
		else:
			return int(d)

	def update_data_from_db_to_module(self):
		self.clear_module()
		n = msql.get_no_of_registered_users()
		print("TOTAL registered users: " + str(n))
		time.sleep(2)
		data = msql.get_registered_table('LIST')  # returns all data from database
		for d in data:
			index = d[0]
			host_name = d[1]
			time_stamp = d[2]
			punch_id = d[3]
			template = d[4]
			template_length = len(template)
			print(index , host_name , time_stamp , punch_id , template_length)
			r = self.hw.upload_template(index , template)
			if r is not None:
				self.hw.clear_screen()
				self.hw.print_screen('DONE' , 1)
				self.hw.print_screen('INDEX: ' + str(index) , 2)
				self.hw.print_screen('PUNCH ID : ' + str(punch_id) , 3)
				self.hw.print_screen('SIZE: ' + str(template_length) , 4)
				time.sleep(.1)
			else:
				self.hw.print_screen("Unknown Error")
				time.sleep(1)
		msql.update_module_at_startup(False)  # no more udpation required
		return True

	def save_users_log(self , index , punch_id , server1_response , server2_response , test_server_response ,
					   image_link):
		self.update_file_user_log( str(index) + " " + str(punch_id) + " " +str(server1_response) + " " + str(server2_response) + " " + str(test_server_response))
		return msql.log_user(index , punch_id , server1_response , server2_response , test_server_response , image_link)

	def set_device_time(self):
		t = self.es.get_server_time()
		if t is not None:
			self.syss.update_hw_clock(t)
		else:
			print('error updating time')

	def home_screen(self):  ## on display
		self.hw.clear_screen()
		self.hw.print_screen('EU ' + str(self.syss.get_host_name()) , 1)
		self.hw.print_screen('--------------------' , 2)
		self.hw.print_screen('IP:' + str(self.syss.get_host_ip()) , 3)
		self.hw.print_screen(str(self.syss.get_current_timestamp(3)) , 4)

	def update_hostname_from_db(self):
		self.update_variables_from_database()
		hostname = Biometric_device.variables['host_name']
		self.syss.change_hostname(hostname)
		return True

	def save_process_id(self):
		msql.update_settings('process_id' , self.syss.get_process_id())
		return True

	def kill_biometric_process(self):
		self.update_variables_from_database()
		process_id = Biometric_device.variables['process_id']
		self.syss.kill_process(process_id)
		return True

	def add_to_server_db(self):
		hn = self.syss.get_host_name()
		ip = self.syss.get_host_ip()
		self.update_variables_from_database()
		server1 = Biometric_device.variables['api1_server']
		server2 = Biometric_device.variables['api2_server']
		server1_enabled = int(Biometric_device.variables['api1_enabled'])
		server2_enabled = int(Biometric_device.variables['api2_enabled'])
		password = Biometric_device.variables['password']

		if server1_enabled:
			self.es.set_server(server1)
		elif server2_enabled:
			self.es.set_server(server2)

		self.es.add_device_to_database(hn ,ip, password)

	def send_registration_data_to_era_server(self):
		try:
			data = msql.get_registered_table('LIST')  # returns all data from database
			live_server = msql.get_setting_data('live_server')
			server = None
			if live_server == 'SERVER1':
				server = msql.get_setting_data('api1_server')
			elif live_server == 'SERVER2':
				server = msql.get_setting_data('api2_server')
			elif live_server == 'TEST_SERVER':
				server = msql.get_setting_data('test_server')
			self.es.set_server(server)
			for d in data:
				index = d[0]
				host_name = d[1]
				time_stamp = d[2].strftime("%Y-%m-%d %H:%M:%S")
				punch_id = d[3]
				template = d[4]
				template_length = len(template)
				if self.hw is not None:
					self.hw.print_screen("index:" + str(index),1)
					self.hw.print_screen("punchid" + str(punch_id),2)
				print(index , host_name , time_stamp , punch_id , template_length)
				self.es.update_data_to_server(punch_id,index,template,time_stamp,host_name)

				# def update_data_to_server(self , punchId , deviceIndex , templete , timestamp , hostname):

				time.sleep(.5)
		except Exception as e:
			print(str(e))

	def send_punch_data_to_era_server(self , user_index , punch_id , image_url ,server='DEFAULT' , time_stamp=None ,
									  device_id=None ):
		"""
		updates data to enabled server only if server is None, otherwiese sends data to selected server only

		@server parameter
		DEFAULT: Sends to enabled servers only
		ALL: Sends to all servers,irrespective of enabled or disabled
		SERVER1 = Sends to server 1 only
		SERVER2 = sends to server 2 only
		TEST_SERVER = sends to test server only


		@time_stamp:
		None: sends current time stamp
		otherwise sends selected time.

		@device_id:
		None: sends hostname of current device
		otherwise sends selected hostname

		@:return
		[RESPONSE1,RESPONSE2,RESPONSE3]

		by default if not selected.
		[NA,NA,NA]

		if selected and data not sent: then return type is None.
		otherwise ret
		urn type is server response.

		for a given server if response is
		NA: not selected
		None: selected but some error from server
		valid_reponse_from_server: is it goes fine. like success, done, ok etc depending on server.


		"""

		if time_stamp is None:
			time_stamp = self.syss.get_current_timestamp(1)

		if device_id is None:
			device_id = self.syss.get_host_name()

		self.update_variables_from_database()
		server1 = Biometric_device.variables['api1_server']
		server2 = Biometric_device.variables['api2_server']
		test_server = Biometric_device.variables['test_server']

		server1_enabled = int(Biometric_device.variables['api1_enabled'])
		server2_enabled = int(Biometric_device.variables['api2_enabled'])
		test_server_enabled = int(Biometric_device.variables['test_api_enabled'])

		print(server1 , server2 , test_server , server1_enabled , server2_enabled , test_server_enabled)

		s1_response = 'NA'
		s2_response = 'NA'
		ts_response = 'NA'

		if server == 'DEFAULT':

			if server1_enabled:
				print('SENDING TO SERVER 1')
				try:
					self.es.set_server(server1)
					s1_response = self.es.update_user_log(punch_id , time_stamp , device_id,image_url)
					if s1_response is None:
						s1_response = 'ERROR'
				except Exception as e:
					print(e)
					s1_response = 'ERROR'

			if server2_enabled:
				print('SENDING DATA TO SERVER 2')
				try:
					self.es.set_server(server2)
					s2_response = self.es.update_user_log(punch_id , time_stamp , device_id,image_url)
					if s2_response is None:
						s2_response = 'ERROR'
				except Exception as e:
					print(e)
					s2_response = 'ERROR'

			if test_server_enabled:
				print('SENDING TO TEST SERVER')
				try:
					self.es.set_server(test_server)
					ts_response = self.es.test_api(user_index,time_stamp)
					print('test response' , ts_response)
					if ts_response is None:
						ts_response = 'ERROR'
				except Exception as e:
					print(e)
					ts_response = 'ERROR'

		elif server == 'SERVER1':
			print('SENDING TO SERVER 1')
			try:
				self.es.set_server(server1)
				s1_response = self.es.update_user_log(punch_id , time_stamp , device_id,image_url)
				if s1_response is None:
					s1_response = 'ERROR'
			except Exception as e:
				print(e)
				s1_response = 'ERROR'
		elif server == 'SERVER2':
			print('SENDING DATA TO SERVER 2')
			try:
				self.es.set_server(server2)
				s2_response = self.es.update_user_log(punch_id , time_stamp , device_id,image_url)
				if s2_response is None:
					s2_response = 'ERROR'
			except Exception as e:
				print(e)
				s2_response = 'ERROR'
		elif server == 'TEST_SERVER':
			print('SENDING TO TEST SERVER')
			try:
				self.es.set_server(test_server)
				ts_response = self.es.test_api(user_index,time_stamp)
				if ts_response is None:
					ts_response = 'ERROR'
			except Exception as e:
				print(e)
				ts_response = 'ERROR'

		return [s1_response , s2_response , ts_response]


if __name__ == '__main__':
	try:
		bd = Biometric_device()
		bd.send_registration_data_to_era_server()
		# resposne = bd.send_punch_data_to_era_server(1,'07041','DEFAULT')
		# print(resposne)
		# time.sleep(2)
		# resposne = bd.send_punch_data_to_era_server(1,'07041','SERVER1')
		# print(resposne)
		# time.sleep(2)
		# resposne = bd.send_punch_data_to_era_server(1,'07041','SERVER2')
		# print(resposne)
		# time.sleep(2)
		# resposne = bd.send_punch_data_to_era_server(1,'1234','TEST_SERVER')
		# print(resposne)

		# bd.syss.remove_directory('/home/pi/database')
		# bd.reset_db()
		# bd.create_default_parameters()
		# print(bd.register_user(1234))
		# print(bd.register_user(2345))
		# bd.clear_module()
		# time.sleep(1)
		# bd.update_data_from_db_to_module()

		# bd.update_variables_from_database()
		# kv=bd.get_variables()
		# for k,v in kv.items():
		# print(k,v)
		# bd.create_default_parameters()
		# kv=bd.get_variables()
		# for k,v in kv.items():
		# print(k,v)

		# print(bd.verify_password(1234))
		# print(bd.verify_password('1234'))
		# print(bd.verify_password(12))
		# print(bd.verify_password())#will take user input  and verify
		# while True:
		# 	result = bd.check_user()
		# 	print(result)
		# 	time.sleep(.1)
		# time.sleep(1)
	except Exception as e:
		print("Error: " + str(e))
