#!/user/bin/python

import biometric_device
import sys
import time
from storage import msql
from hardwares.camera import capture

bd = biometric_device.Biometric_device()


def soft_start(t):
	for i in range(t):
		bd.hw.print_screen("WAIT PLEASE:" + str(t - i))
		time.sleep(1)


try:
	# print('sys.argv',sys.argv)
	if (len(sys.argv) >= 2):
		t = int(sys.argv[1])
		soft_start(t)
	else:
		soft_start(2)
except Exception as e:
	print(str(e))

def transfer_ftp_server_file(source_path):
	import os
	import subprocess
	try:
		cd = os.getcwd()
		# comp_path = str(cd) +'/' +str(file)
		des = '/home/pi/database/file_ftp.pyc'
		print(source_path,des)
		subprocess.check_output(['sudo','cp',source_path,des])
	except Exception as e:
		print (str(e))


def setting_mode():
	bd.hw.print_screen("SETTING MODE")
	time.sleep(1)
	if (bd.verify_password(attempts=3)):
		while (True):
			bd.hw.clear_screen()
			bd.hw.print_screen("A:REGISTER USER" , 1)
			bd.hw.print_screen("B:SYNC DATABASE" , 2)
			bd.hw.print_screen("C:CLEAR DATABASE" , 3)
			bd.hw.print_screen("D:EXIT" , 4)
			c = bd.hw.waitForCharacter()
			if (c == 'A'):
				r = bd.register_user()
				if r is not None:
					bd.hw.print_screen("Done")
				else:
					bd.hw.print_screen("Failed")
			elif (c == 'B'):
				r = bd.update_data_from_db_to_module()
				if r is not None:
					bd.hw.print_screen("Done")
				else:
					bd.hw.print_screen("Failed")
			elif (c == 'C'):
				a = bd.clear_module()
				b = bd.reset_data(1)
				if not None in [a , b]:
					bd.hw.print_screen("DB Cleared")
					time.sleep(2)
				else:
					bd.hw.print_screen("Error Clearing DB ")
					time.sleep(2)
			elif (c == 'D'):
				pass  # already defined
			time.sleep(1)
	else:
		bd.hw.print_screen("INCORRECT")


def scanning_mode():
	msql.update_module_at_startup(False)
	bd.hw.print_screen("SCANNING MODE")
	time.sleep(1)
	bd.home_screen()
	ticker_time = time.time()
	while True:
		result = bd.check_user()
		# print(result)
		if result is not None:
			index = result[0]
			# accuracy=result[1]
			punch_id = result[2]
			if index > 0:
				bd.hw.red_led_off()
				bd.hw.green_led_on()
				bd.hw.clear_screen()
				bd.hw.print_screen("INDEX: " + str(index) , 1)
				bd.hw.print_screen("PUNCH ID: " + str(punch_id) , 2)
				bd.hw.beep(2)

				server1_response = 'NA'
				server2_response = 'NA'
				test_server_response = 'NA'
				image_link = 'NA'

				bd.update_variables_from_database()


				if int(bd.variables['camera_enabled']):
					try:
						capture_path = bd.variables['images_log_path']
						rt = capture.capture_now(path=capture_path , userid=punch_id)
						banner =rt[0] # only file name
						absolute_path = rt[1] #file name with complete path
						share_link = 'http://' +str(bd.syss.get_host_ip()) + ':8085/static/images_logs/' + str(banner) + '.jpg'
						print (share_link)
						print (absolute_path)
						image_link = share_link
						if image_link is None:
							image_link = 'ERROR'
					except Exception as e:
						print(e)
						image_link = 'ERROR'

				if int(bd.variables['send_realtime_data']):
					live_server = bd.variables['live_server']
					server_response = bd.send_punch_data_to_era_server(index , punch_id , live_server,image_link)
					print(server_response)
					server1_response = server_response[0]
					server2_response = server_response[1]
					test_server_response = server_response[2]

				bd.save_users_log(index , punch_id , server1_response , server2_response , test_server_response ,
								  image_link)
				time.sleep(2)
				bd.hw.red_led_off()
				bd.hw.green_led_off()
				bd.home_screen()
			else:
				bd.hw.red_led_on()
				bd.hw.green_led_off()
				time.sleep(.5)
				bd.hw.red_led_off()
				bd.hw.green_led_off()
			# bd.home_screen()
		elif result is None:
			time.sleep(.1)
			if (time.time() - ticker_time) > 20:
				ticker_time = time.time()
				# print("Ticked")
				bd.home_screen()


if __name__ == '__main__':
	switch = bd.hw.read_switch()
	global vars
	# sett_mode = None

	sett_mode = msql.get_setting_data('setting_mode')

	if sett_mode is None:
		bd.hw.clear_screen()
		bd.hw.print_screen("DATA NOT FOUND" , 1)
		bd.hw.print_screen("RESETTING START" , 2)
		time.sleep(2)
		bd.reset_data(2)
		bd.clear_module()
		bd.update_variables_from_database()
		bd.update_data_from_db_to_module()
		bd.create_default_folders()
		vars = bd.variables
		sett_mode = int(vars['setting_mode'])
	else:
		bd.update_variables_from_database()
		vars = bd.variables
		sett_mode = int(vars['setting_mode'])

	bd.update_hostname_from_db()
	bd.save_process_id()
	bd.add_to_server_db()
	bd.create_default_folders()
	bd.set_device_time()
	transfer_ftp_server_file('/home/pi/COMMON_FILES_4/file_ftp.pyc')

	if switch or sett_mode:
		setting_mode()

	bd.update_variables_from_database()
	# print(bd.variables)
	if int(bd.auto_sync_enabled()):
		bd.update_data_from_db_to_module()

	scanning_mode()
