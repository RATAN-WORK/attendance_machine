import picamera
import time
import datetime
import subprocess

class Capture():
	'''
	capture image, creates timestamp, if user id is provided,
	then appends with that. 
	it also includes device host name
	automatically saves to the default folder
	'''
		
	def __init__(self,folder_path=None):
		if folder_path is not None:
			self.folder_path = folder_path
		else:
			self.folder_path ='/home/pi'
		self.file_type='.jpg'

	def _get_timestamp(self):
		return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

	def _get_host_name(self):
		value = subprocess.check_output(['hostname'])
		return value.split()[0]

	def capture_image(self,user_id=None):
		if user_id is not None:
			self.user_id=user_id
		else:
			self.user_id="NA"

		self.time_stamp =self._get_host_name()
		self.device_id = self._get_timestamp()
		self.banner = str(self.device_id) + '_' +str(user_id)+'_'+str(self.time_stamp)
		self.full_path =str(self.folder_path) + str(self.banner) + str(self.file_type)
		self.camera.annotate_text=self.banner
		# self.camera.resolution = (1024, 768)
		self.camera.capture(self.full_path)
		return [self.banner , self.full_path]
		
	def open_cam(self):
		self.camera = picamera.PiCamera()
		
	def close_cam(self):
		if not self.camera.closed:
			self.camera.close()
			
	def __del__(self):
		self.close_cam()

def capture_now(path,userid):
	try:
		cam = Capture(path)
		cam.open_cam()
		path = cam.capture_image(userid)
		cam.close_cam()
		return path
	except Exception as e:
		print(str(e))
		return None

if __name__ =='__main__':
	path = '/home/pi/'
	userid = '1234'
	for i in range(5):
		print(capture_now(path,userid))
		time.sleep(2)
