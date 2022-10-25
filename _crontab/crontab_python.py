
'''
job3.minute.every(1)
job.hour.every(4)
job.every(2).days()
job.minute.during(5,50).every(5)
job.setall(1, 12, None, None, None)

job2 = cron.new(command='/foo/bar', comment='SomeID')
job2.every_reboot()

cron.remove_all(command='/foo/bar')
cron.remove_all(comment='This command')
cron.remove_all(time='* * * * *')
cron.remove_all()

@reboot 

'''

from crontab import CronTab

def every_midnight(_command,_comment,_user='root'):
	print(' ')
	print('at midnigh')
	my_cron = CronTab(user = _user)
	job1 =my_cron.new(_command,comment=_comment)
	job1.setall(0,0,None, None,None)
	my_cron.write()



def print_existing_jobs(_user ='root'):
	print(' ')
	print('Printing existing jobs------:')
	my_cron = CronTab(user=_user)
	# print(my_qcron)
	for job in my_cron:
		print job
	return my_cron
		
def get_job_by_comment(_comment,_user ='root'):
	print(' ')
	print('Printing jobs with comment: ' + str(_comment) +'--------')
	my_cron = CronTab(user=_user)
	for job in my_cron:
		if job.comment == _comment:
			print job

def update_job_by_comment(_comment,_user ='root'):
	print(' ')
	print('updating job by comment ------:')
	my_cron = CronTab(user=_user)
	for job in my_cron:
		if job.comment == 'reboot at midnight':
			job.hour.every(10)
			my_cron.write()
			print('Cron job modified successfully')

def new_job_per_n_minute(_command,_minute_interval,_comment,_user='root'):
	my_cron =CronTab(user=_user)
	job1 =my_cron.new(_command,comment=_comment)
	job1.minute.every(_minute_interval)
	my_cron.write()
	
def new_job_at_reboot(_command,_comment,_user='root'):
	my_cron =CronTab(user=_user)
	job1 =my_cron.new(_command,comment =_comment)
	job1.every_reboot()
	my_cron.write()
	
def remove_all_jobs(_user='root'):
	my_cron =CronTab(user=_user)
	print(' ')
	print('removing all jobs')
	print('------------------')
	my_cron.remove_all()
	my_cron.write()

# def main():

def update_crontab(server_update_interval,publish_identity_interval):
	# print_existing_jobs()
	remove_all_jobs()
	# every_midnight('sudo reboot ' , 'reboot_at_midnight')
	# new_job_at_reboot('sudo python /home/pi/COMMON_FILES_2/http_server.py >> /home/pi/http_error.txt 2>&1' ,'HTTP-SERVER')
	# new_job_at_reboot('sudo python /home/pi/database/file_ftp.py >> /home/pi/file_ftp.txt 2>&1' ,'FTP-SERVER')
	# new_job_at_reboot('sudo python /home/pi/COMMON_FILES_2/_main.py 30>> /home/pi/main_error.txt 2>&1' , 'MAIN')
	# new_job_per_n_minute('sudo python /home/pi/COMMON_FILES_2/publish_identity.py >> /home/pi/pub_ident.txt 2>&1',int(publish_identity_interval),'IDENTITY')
	# new_job_per_n_minute('sudo python /home/pi/COMMON_FILES_2/update_to_server.py >> /home/pi/send_att_auto.txt 2>&1',int(server_update_interval),'SERVER-UPDATE')
	every_midnight('sudo reboot ' , 'DAILY_REBOOT')
	new_job_at_reboot('sudo python /home/pi/COMMON_FILES_4/http_server.pyc >> /home/pi/http_error.txt 2>&1' , 'HTTP-SERVER')
	new_job_at_reboot('sudo python /home/pi/database/file_ftp.pyc >> /home/pi/file_ftp.txt 2>&1' , 'FTP-SERVER')
	new_job_at_reboot('sudo python /home/pi/COMMON_FILES_4/_main.pyc 30>> /home/pi/main_error.txt 2>&1' , 'MAIN')
	new_job_per_n_minute('sudo python /home/pi/COMMON_FILES_4/publish_identity.pyc >> /home/pi/pub_ident.txt 2>&1' , int(publish_identity_interval) , 'IDENTITY')
	new_job_per_n_minute('sudo python /home/pi/COMMON_FILES_4/update_to_server.pyc >> /home/pi/send_att_auto.txt 2>&1' ,int(server_update_interval) , 'SERVER-UPDATE')
	return True

if __name__ == "__main__":
	update_crontab(15,15)