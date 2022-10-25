import MySQLdb
import datetime
import time
import commands

'''

Note: separate functions have been developed for each operation(See at bottom), because
database gets disconnected after a certain timeout interval.
each function creates a new object and then operates.

it may be solved later, if there is some way to check the connection with db.

'''


class Msql():
	def __init__(self , database_name):
		try:
			self.connection = MySQLdb.connect(host="localhost" , user="root" , passwd="" , db=database_name);
			self.connection.autocommit = True
			self.cur = self.connection.cursor()
		except Exception as e:
			print("error/msql/initialize_db " + str(e))
			return None

	def __del__(self):
		pass

	def _hostname(self):
		return commands.getoutput('hostname')

	def get_tables(self):
		'''
		returns list of tables of the selected database
		'''
		try:
			insert_stmt = ("SHOW TABLES")
			if (self.cur.execute(insert_stmt)):
				data = self.cur.fetchall()
				ddd = []
				for d in data:
					ddd.append(d[0])
				return ddd
		except Exception as e:
			print("Error: userLog : " + str(e))

	def get_version(self):
		'''
		returns the version of the mysqldb
		'''
		try:
			insert_stmt = ('SELECT VERSION()')
			if (self.cur.execute(insert_stmt)):
				data = self.cur.fetchone()
				return data[0]
		except:
			print("ERROR: {}".format(str(e)))
			return None

	def delete_table(self , table_name):  #########delete table arg=string
		try:
			insert_stmt = ("DROP TABLE " + str(table_name))
			self.cur.execute(insert_stmt)
			return True
		except Exception as e:
			print("Error:/msql/delete_table " + str(e))
			return None

	def truncate_table(self , table_name):
		'''
		clears all data from the table , table is not deleted.
		'''
		try:
			insert_stmt = ("TRUNCATE TABLE " + str(table_name))
			self.cur.execute(insert_stmt)
			return True
		except Exception as e:
			print("Error:/msql/truncate_table " + str(e))
			return None

	def delete_all_tables(self):
		try:
			tables = self.get_tables()
			if tables is not None:
				for table in tables:
					if self.delete_table(table) is not None:
						print('{} -deleted '.format(table))
					else:
						print('some error deleting table {}'.format(table))
			return True
		except Exception as e:
			print("error/msql/delete_all_tables " + str(e))
			return None

	def create_settings_table(self):
		try:
			stmt = ('CREATE TABLE settings(setting_name VARCHAR(50) UNIQUE, setting_value VARCHAR(255))')
			x = self.cur.execute(stmt)
			return True
		except Exception as e:
			print("ERror :/msql/create_settings_table " + str(e))
			return None

	def create_registration_table(self):
		try:
			print('creating registration_table')
			stmt = (
				'CREATE TABLE registration_table(indx INT unsigned NOT NULL ,device_id VARCHAR(20),time_stamp DATETIME, punch_id INT unsigned NOT NULL UNIQUE,template TEXT, PRIMARY KEY(indx))')
			x = self.cur.execute(stmt)
			return True
		except Exception as e:
			print("ERROR :/msql/create_registration_table " + str(e))
			return None

	def create_user_logs_table(self):
		try:
			print('creating user log table')
			stmt = (
				'CREATE TABLE user_logs(sno INT unsigned NOT NULL AUTO_INCREMENT,time_stamp DATETIME NOT NULL,indx VARCHAR(20) NOT NULL, punch_id VARCHAR(20) NOT NULL,server1_response VARCHAR(255),server2_response VARCHAR(255),test_server_response VARCHAR(255),image_link VARCHAR(255), PRIMARY KEY(sno))')
			x = self.cur.execute(stmt)
			return True
		except Exception as e:
			print("error create user logs" + str(e))

	def insert_user_log(self , indx , punch_id , server1_response,server2_response,test_server_response,image_link):  #
		try:
			ts = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
			insert_stmt = ("INSERT INTO user_logs(time_stamp,indx,punch_id,server1_response,server2_response,test_server_response,image_link)" "VALUES(%s,%s,%s,%s,%s,%s,%s)")
			data = (ts , indx , punch_id , server1_response,server2_response,test_server_response,image_link)
			print(self.cur.execute(insert_stmt , data))
			self.connection.commit()
			return True
		except Exception as e:
			print("Error/msql/userLogs: userLog : " + str(e))
			return None

	def update_user_logs(self , sno , s1_response,s2_response,test_response ):  #
		'''
		used to change SERVER_RESPONSE value in user logs based on sno as a key
		table name: user_logs
		input= sno 
		value changed: server_response

		'''
		try:
			insert_stmt = "UPDATE user_logs SET server1_response = %s , server2_response= %s , test_server_response = %s WHERE sno = %s"
			data = (s1_response,s2_response,test_response , sno)
			print(self.cur.execute(insert_stmt, data))
			self.connection.commit()
			return True
		except Exception as e:
			print("ERROR/MSQL/update_user_logs: " + str(e))
			return None

	def insert_registration_logs(self , punch_id , template,index=None):  #
		'''
		indx is created automatically
		'''
		try:
			ts = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
			device_id = self._hostname()
			if index is None:
				index = self.count_no_of_rows('registration_table')
				index = index+1
			insert_stmt = (
				"INSERT INTO registration_table(indx,device_id,time_stamp,punch_id,template)" "VALUES(%s,%s,%s,%s,%s)")
			data = (index,device_id , ts , punch_id , template)
			self.cur.execute(insert_stmt , data)
			self.connection.commit()
			return [punch_id]
		except Exception as e:
			# print("Error: userLog -" + str(e))
			print("Error/msql/registration_logs: userLog -" + str(e))
			return None

	def count_no_of_rows(self , table_name):
		'''
		returns tuple of data
		'''
		try:
			insert_stmt = ("SELECT * FROM " + table_name)
			return self.cur.execute(insert_stmt)
			return data
		except Exception as e:
			print("Error: " + str(e))
			return None

	def serach_pid(self , punch_id):
		'''
		checks pid from registration_table if exists return count
		'''
		try:
			insert_stmt = ("SELECT * FROM registration_table where punch_id = %s")
			value = (punch_id ,)
			return self.cur.execute(insert_stmt , value)
			return data
		except Exception as e:
			print("Error: " + str(e))
			return None

	def get_user_logs(self , start_date=None , end_date=None , punch_id=None):  # returns tuple of logs
		try:
			print('getting users log')
			if start_date == None and end_date == None:
				if punch_id == None:
					stmt = ('SELECT * FROM user_logs')
					x = self.cur.execute(stmt)
					data = self.cur.fetchall()
					return data
				else:
					stmt = ('SELECT * FROM user_logs WHERE punch_id = %s')
					data = (punch_id ,)
					x = self.cur.execute(stmt , data)
					data = self.cur.fetchall()
					return data
			else:
				if punch_id == None:
					insert_stmt = ("SELECT *FROM user_logs where time_stamp between %s and %s")
					data = (start_date , end_date)
					self.cur.execute(insert_stmt , data)
					data = self.cur.fetchall()
					return data
				else:
					insert_stmt = ("SELECT *FROM user_logs where time_stamp between %s and %s and punch_id=%s")
					data = (start_date , end_date , punch_id)
					self.cur.execute(insert_stmt , data)
					data = self.cur.fetchall()
					return data
		except Exception as e:
			print("Error /msql/get_user_logs: " + str(e))
			return None

	def create_necessary_tables(self):
		try:
			self.create_user_logs_table()
			self.create_settings_table()
			self.create_registration_table()
			return True
		except Exception as e:
			print("error/msql/create_necessary_tables " + str(e))
			return None

	# def create_necessary_tables_if_not_created(self):
	# '''
	# this is required, because in some devices, tables are present with different parameters
	# '''
	# tables = self.get_tables()
	# print(tables)
	# if tables is None:
	# print('no table found')
	# print('creating new tables')
	# self.create_necessary_tables()
	# else:
	# if 'registration_table' in tables:
	# print('all required tables are supposed to be  existing')
	# else:
	# print('deleting previous tables')
	# self.delete_all_tables()
	# print('creating new tables')
	# self.create_necessary_tables()

	def update_to_settings(self , sett_name , sett_value):
		try:
			insert_stmt = ("UPDATE settings SET setting_value =%s WHERE setting_name=%s")
			data = (sett_value , sett_name)
			self.cur.execute(insert_stmt , data)
			self.connection.commit()
			return True
		# print(str(sett_name)+ " saved  " + str(sett_value))
		except Exception as e:
			print("Error write_to_settings:" + str(e))
			return None

	def write_to_settings(self , sett_name , sett_value):
		try:
			insert_stmt = ("INSERT INTO settings(setting_value,setting_name)" "VALUES(%s ,%s)")
			data = (sett_value , sett_name)
			self.cur.execute(insert_stmt , data)
			self.connection.commit()
			print(str(sett_name) + " saved  " + str(sett_value))
			return True
		except Exception as e:
			print("Error write_to_settings:" + str(e))
			return None

	# def create_default_parameters(self):
	# '''
	# this is not update, this is first time value creation
	# '''
	# self.write_to_settings('password','1234')
	# self.write_to_settings('mode',0)#scanning mode/registration mode
	# self.write_to_settings('process_id','0000')
	# self.write_to_settings('camera_enabled','1')

	# self.write_to_settings('api1_enabled',1)# attendence on api 1
	# self.write_to_settings('api2_enabled',1)# attendence data on api 2
	# self.write_to_settings('mqtt_enabled',1)

	# self.write_to_settings('api1_server','192.168.7.13')
	# self.write_to_settings('api2_server','192.168.7.13')
	# self.write_to_settings('mqtt_server','192.168.10.108')

	# self.write_to_settings('host_name','TEST')
	# self.write_to_settings('sync_db',0)

	# return True

	def show_all_data(self , table_name , parameter=None , parameter_key=None):
		'''
		returns tuple of data
		'''
		try:
			if parameter == None:
				insert_stmt = ("SELECT * FROM " + table_name)
				self.cur.execute(insert_stmt)
				data = self.cur.fetchall()
				return data
			else:
				insert_stmt = ("SELECT * FROM %s WHERE %s = %s")
				insert_value = (table_name , parameter , parameter_key)
				self.cur.execute(insert_stmt , insert_value)
				data = self.cur.fetchall()
				return data
		except Exception as e:
			print("Error: " + str(e))
			return None

	def read_from_settings(self , key=None):
		'''
		reads all values from settings,
		if key is provided, then returns key value only in string format
		if not provided, then returns tuple of key-value 
		'''
		try:
			insert_stmt = ("SELECT * FROM settings")
			self.cur.execute(insert_stmt)
			data = self.cur.fetchall()
			if key == None:
				return data
			else:
				for row in data:
					# print(row[0],row[1])
					if (row[0] == key):
						# print('found:' + row[1])
						return row[1]
		except Exception as e:
			print("Error: " + str(e))
			return None

	def search_user_pid(self , indx):
		try:
			insert_stmt = ("SELECT punch_id FROM registration_table WHERE indx=%s")
			data = (indx ,)
			self.cur.execute(insert_stmt , data)
			data = self.cur.fetchone()
			return str(data[0])
		except Exception as e:
			# print("Error: userLog -" + str(e))
			print("Error/msql_class: serach user pid  -" + str(e))
			return None


def get_no_of_registered_users():
	m = Msql('attendence')
	return m.count_no_of_rows('registration_table')


def create_settting_parameter(name , value):
	m = Msql('attendence')
	m.write_to_settings(name , value)
	return True


def update_global_variables_from_database():
	pass  # to be implemented soon


def log_user(indx , punch_id , server1_response,server2_response,test_server_response,image_link):
	m = Msql('attendence')
	m.insert_user_log(indx , punch_id , server1_response,server2_response,test_server_response,image_link)
	return True


def log_registration(punch_id , template , indx=-1):
	m = Msql('attendence')
	if (int(indx) == -1):
		r = m.insert_registration_logs(punch_id , template)
		return r
	else:
		pass  # create new function to update the registration table, from given index


def get_setting_data(parameter_key):
	try:
		m = Msql('attendence')
		return m.read_from_settings(parameter_key)
	except Exception as e:
		print(str(e))
		return None


# return  m.show_all_data(table_name='settings',parameter='setting_name',parameter_key=parameter_key)


def create_tables():
	'''
	should be called only first time if device booting
	will delete all data forever 
	'''
	m = Msql('attendence')
	m.create_necessary_tables()
	return True


# m.create_default_parameters()

def delete_tables():
	m = Msql('attendence')
	m.delete_all_tables()
	return True


def clear_user_logs():
	m = Msql('attendence')
	m.truncate_table('user_logs')
	return True


def clear_registration_table():
	m = Msql('attendence')
	m.truncate_table('registration_table')
	return True


def get_all_parameters(type =None):
	m = Msql('attendence')
	data = m.read_from_settings()
	if type == 'DICT':
		dic = dict()
		if data is not None:
			for k,v in data:
				dic.__setitem__(k,v)
			return dic
		else:
			return None
	elif type is None:
		return data


def find_pid_from_index(indx):
	m = Msql('attendence')
	return m.search_user_pid(indx)


def check_if_user_exists(pid):
	m = Msql('attendence')
	return m.serach_pid(str(pid))


def update_settings(setting_name , setting_value):
	m = Msql('attendence')
	m.update_to_settings(setting_name , setting_value)
	return True

def update_punch_logs(sno,s1_res,s2_res,test_res):
	m = Msql('attendence')
	m.update_user_logs(sno,s1_res,s2_res,test_res)
	return True

def get_users_log(type='DICT' , startdate=None , enddate=None , punchid=None):
	m = Msql('attendence')
	data = m.get_user_logs(startdate , enddate , punchid)
	if type == 'DICT':
		list_of_dic = []
		for row in data:
			# print(row)
			dic = {
				"sno": row[0] ,
				"time_stamp": row[1].strftime("%Y-%m-%d %H:%M:%S") ,
				"index": row[2] ,
				"punch_id": row[3] ,
				"server1_response": row[4],
				"server2_response": row[5],
				"test_server_response": row[6],
				"image":row[7]
			}
			list_of_dic.append(dic)
		return list_of_dic
	elif type =='LIST':
		d = [[]]
		for row in data:
			r = list()
			for i in row:
				r.append(i)
			d.append(r)
		return d
	else:
		return None

def update_module_at_startup(status=False):
	m=Msql('attendence')
	update_settings('sync_db_on_start',status)
	return True

def get_registered_table(type='DICT'):
	"""
	if index=None,returns all data
	otherwise returns only by index 
	"""
	m = Msql('attendence')
	data = m.show_all_data('registration_table')
	list_of_dict = []
	if type == 'DICT':
		for row in data:
			# print(row)
			dic = {
				"index": row[0] ,
				"hostname": row[1] ,
				"time_stamp": row[2].strftime("%Y-%m-%d %H:%M:%S") ,
				"punch_id": row[3] ,
				"template": row[4]
			}
			list_of_dict.append(dic)
		return list_of_dict
	elif type == 'LIST':
		return data

if __name__ == '__main__':
	msql = Msql('attendence')
	# print('list of tables: ',msql.get_tables())
	# print('get-version',msql.get_version())
	# print('delete table',msql.delete_table('settings'))
	# print('delete all tables ',msql.delete_all_tables())
	# print('create_necessary_tables',msql.create_necessary_tables())
	# print('create_settings_table', msql.create_settings_table())
	# print('create_registration_table',msql.create_registration_table())
	# print('create_user_logs_table',msql.create_user_logs_table())
	# print('insert_user_log',msql.insert_user_log(0,1234,'NA'))
	# print('insert_registration_logs',msql.insert_registration_logs(0,12234,'large template'))
	# print('get_user_logs',msql.get_user_logs())
	# print('update_user_logs',msql.update_user_logs(1,'NA1'))
	# print('create_necessary_tables_if_not_created',msql.create_necessary_tables_if_not_created())
	# print('write_to_settings',msql.write_to_settings('password',1234))
	# print('update_to_settings',msql.update_to_settings('password',1111))
	# print('create_default_parameters',msql.create_default_parameters())
	# print('read all from_settings',msql.read_from_settings())
	# print('read password from_settings',msql.read_from_settings('password'))
	# print('show_all_data',msql.show_all_data('settings'))
	# print('truncate table',msql.truncate_table('settings'))
	# log_user(0,1234,'NA')
	# log_registration(12345,'03835522541252212')
	# print(msql.count_no_of_rows('registration_table'))
	# clear_user_logs()
	# print(msql.search_user_pid(1))
	# print(find_pid_from_index(1))
	# print('users',get_no_of_registered_users())
	# print('check if user exists',check_if_user_exists(55864))
	# print('check if user exists',check_if_user_exists(12345))
	# print('update_to_settings',msql.update_to_settings('offline_registration',False))
	# print('update_to_settings',msql.update_to_settings('host_name','TEST'))
	# print(get_users_log())
	# update_punch_logs('1','ERROR','ERROR','ERROR')
	pass
