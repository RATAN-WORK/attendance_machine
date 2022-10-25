#!/user/bin/python


'''
serves the resources over http
'''


from system import system
from storage import msql
from softwares.era_server import era_server
from flask import Flask , render_template , redirect , url_for , request
import json
import time

time.sleep(60)

DEBUG = True
PORT = 8080
AUTHORIZED_METHODS = ['GET' , 'POST']

syss = system.System()
app = Flask(__name__)
es = era_server.EraServer()

def _print(s):
	if debug:
		print(s)


def create_json_response(code , message , value):
	"""
	code=0 for undesired response and 1 for desired
	respon message = SUCCESS or ERROR
	response_value = value to return
	"""
	response = {
		'responseCode': code ,
		'responseMessage': message ,
		'responseValue': value
	}
	return json.dumps(response)


def users_log_html(pid =None,start_date =None, end_date=None):
	try:
		users_log = msql.get_users_log('LIST')
		# data = [[]]
		# if pid is None:  # send all data
		# 	for u in users_log:
		# 		row = u.split()
		# 		data.append(row)
		# else:
		# 	for u in users_log:
		# 		row = u.split()
		# 		if pid in row:
		# 			data.append(row)
		# data = users_log
		return render_template('users_log.html' , users_log = users_log)
	except Exception as e:
		_print(str(e))
		return None


@app.route('/queries/<q>' , methods=AUTHORIZED_METHODS)
def queries(q):
	print(q)
	print(request.method)
	print(request.args)
	if request.method in AUTHORIZED_METHODS:
		psw = msql.get_setting_data('password')
		print(psw)
		if psw == request.args['password'] or psw == None: #if password doesn't exist
			if q == 'host_name':
				n = syss.get_host_name()
				if n is not None:
					return create_json_response(1 , 'SUCCESS' , n)
				else:
					return create_json_response(0 , 'ERROR' , n)
			elif q == 'restart_device':
				syss.restart_device()  # will not send any response because of restart
				return create_json_response(1 , "SUCCESS" , "COMMAND SENT")
			elif q == 'change_password':
				new_password = request.args['new_password']
				if new_password is not None:
					if msql.update_settings('password' , new_password):
						return create_json_response(1 , 'SUCCESS' , 'UPDATED NEW PASSWORD: ' + str(new_password))
					else:
						return create_json_response(0 , 'ERROR' , 'DEVICE ERROR')
				else:
					return create_json_response(0 , 'ERROR' , 'NEW PASSWORD REQUIRED')
			elif q == 'users_log':
				log = msql.get_users_log(type='DICT',startdate=None , enddate=None , punchid=None)  # send all data
				if log is not None:
					return create_json_response(1 , 'SUCCESS' , log)
				else:
					return create_json_response(0 , 'ERROR' , 'DEVICE ERROR')
			elif q == 'users_log_html':
				try:
					return  users_log_html()
				except Exception as e:
					return create_json_response(0 , 'ERROR' , str(e))
			elif q == 'user_interface':
				"""
				not working
				to be updated yet
				"""
				ui = user_interface_html()
				if ui is not None:
					return ui
				else:
					return create_json_response(0 , 'ERROR' , 'DEVICE ERROR')
			elif q == 'registration_table':
				"""
				"""
				log = msql.get_registered_table()
				if log is not None:
					return create_json_response(1 , 'SUCCESS' , log)
				else:
					return create_json_response(0 , 'ERROR' , 'DEVICE ERROR')
			elif q == 'clear_registration_table':
				r = msql.clear_registration_table() # clears registration table only
				if r is not None:
					return create_json_response(1 , 'SUCCESS' , 'REGISTRATION TABLE CLEARED')
				else:
					return create_json_response(0 , 'ERROR' , str(r))
			elif q == 'clear_user_logs':
				r = msql.clear_user_logs() # clears
				if r is not None:
					return create_json_response(1 , 'SUCCESS' , 'DATABASE CLEARED')
				else:
					return create_json_response(0 , 'ERROR' , str(r))
			elif q == 'clear_files':
				if syss.remove_directory('/home/pi/database'):
					return create_json_response(1,'SUCCESS','DEVICE MUST BE RESTARTED')
				else:
					return create_json_response(0,'ERROR','TRY AGAIN')
			elif q == 'update_database_table':
				index = request.args['index']  # expected to be -1
				punch_id = request.args['punch_id']
				template = request.args['template']
				msql.update_module_at_startup(True)
				r = msql.log_registration(punch_id , template)
				if r is not None:
					return create_json_response(1 , 'SUCCESS' , 'DEVICE- UPDATED')
				else:
					return create_json_response(0 , 'DEVICE ERROR' , "CHECK FOR DUPLICATE PUNCH ID")
			elif q =='sync_registration_to_server':
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
					es.set_server(server)
					for d in data:
						index = d[0]
						host_name = d[1]
						time_stamp = d[2].strftime("%Y-%m-%d %H:%M:%S")
						punch_id = d[3]
						template = d[4]
						es.update_data_to_server(punch_id , index , template , time_stamp , host_name)
						time.sleep(.25)
					return create_json_response(1,'SUCCESS','UPDATED')
				except Exception as e:
					return create_json_response(0,'ERROR',str(e))
			elif q == 'upload_device_from_file':
				r =msql.update_module_at_startup(True)
				if r:
					create_json_response(1,'SUCCESS','WILL BE UPDATED ON RESTART')
				else:
					create_json_response(0,'ERROR','DB ERROR')
			elif q == 'update_settings':
				if request.args:
					try:
						for d in request.args:
							print ([d , request.args[d]])
							msql.update_settings(d,request.args[d])
						d = msql.get_all_parameters('DICT')
						if d:
							return create_json_response(1,'SUCCESS',str(d))
						else:
							return create_json_response(0,'ERROR','CHECK DATA AGAIN')
					except Exception as e:
						return create_json_response(0,'ERROR',str(e))
			elif q == 'get_settings':
				r = msql.get_all_parameters('DICT')
				if r is not None:
					return create_json_response(1,'DONE',str(r))
				else:
					return create_json_response(0,'ERROR','DEVICE ERROR')
			elif q =='update_crontab':
				from _crontab import crontab_python
				server_sync_interval = msql.get_setting_data('server_updation_interval')
				publish_interval = msql.get_setting_data('publish_identity_interval')

				if None in [server_sync_interval,publish_interval]:
					return create_json_response(0,'ERROR','ERROR GETTING DATA')
				else:
					if str(server_sync_interval).isdigit():
						st = int(server_sync_interval)
					else:
						return create_json_response(0,'ERROR','st not found')
					if str(publish_interval).isdigit():
						pt = int(publish_interval)
					else:
						return create_json_response(0,'ERROR','pt not found')

					if crontab_python.update_crontab(st, pt):
						return create_json_response(1,'SUCCESS',"UPDATED")
					else:
						return create_json_response(0,'ERROR','error updating crontab')
			elif q == 'factory_reset':
				try:
					from _crontab import crontab_python
					msql.delete_tables()
					syss.remove_directory('/home/pi/database')
					crontab_python.update_crontab(15 , 15)
					# time.sleep(5)
					# syss.restart_device()
					return create_json_response(1,'DONE','COMMAND SENT')
				except Exception as e:
					return create_json_response(0,'ERROR',str(e))
			else:
				return create_json_response(0 , 'ERROR' , 'INVALID QUERY')
		else:
			return create_json_response(0 , 'ERROR' , 'INVALID PASSWORD')
	else:
		return create_json_response(0 , 'ERROR' , 'INVALID METHOD')


if __name__ == '__main__':
	app.run(debug=DEBUG , port=PORT , host='0.0.0.0')
