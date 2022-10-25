from display import lcddriver
from keypad import keypad
from gpiozero import LED
from gpiozero import Button
from biometric import pyfingerprint
import time
import os
import sys

class Hardware():
	def __init__(self,display_type,keypad_type,red_led_pin,green_led_pin,buzzer_pin,switch_pin,biometric_type,biometric_port):
		
		self.display_type=display_type
		self.keypad_type=keypad_type
		self.red_led=LED(red_led_pin)
		
		self.green_led_pin=green_led_pin
		self.red_led_pin=red_led_pin
		self.buzzer_pin =buzzer_pin
		self.switch_pin=switch_pin
		
		self.biometric_type=biometric_type
		self.biometric_port=biometric_port
	
	def __del__(self):
		pass 
	

	def restart_code(self):
		arg = 1
		python = sys.executable
		os.execl(python , python , sys.argv[0] , str(arg))

	# print(sys.argv)
	# print(python)
	# os.execl(python,python,*sys.argv,'2')

	def begin_digital_io(self):
		try:
			self.green_led=LED(self.green_led_pin)
			self.buzzer=LED(self.buzzer_pin)
			self.switch = Button(self.switch_pin)
		except Exception as e:
			print("ERror: " +str(e))
	
	def begin_display(self):
		try:
			if self.display_type=='DOT_MATRIX_20X4':
				self.row_count=20
				self.col_count=4
				try:
					lcddriver.ADDRESS=0x27
					self.lcd=lcddriver.lcd()
				except:
					lcddriver.ADDRESS=0X3f
					self.lcd=lcddriver.lcd()
			elif self.display_type=='CMD_LINE':
				print('Command Line Selected')
		except Exception as e:
			print(str(e))
		
	def begin_keypad(self):
		try:
			if self.keypad_type=='KEYPAD_4X4':
				self.kp = keypad.KeypadFactory().create_keypad(repeat=False, repeat_rate=5, key_delay=250)
				self.kp.registerKeyPressHandler(self.get_key)
				self.key_pressed=None
				self.key_value=None
		except Exception as e:
			print(str(e))
			
	def begin_biometric(self):
		try:
			if self.biometric_type=='R30x':
				self.biometric = pyfingerprint.PyFingerprint(self.biometric_port, 57600, 0xFFFFFFFF, 0x00000000)
				if(self.biometric.verifyPassword() == False ):
					raise ValueError('The given fingerprint sensor password is wrong!')
		except Exception as e:
			print(str(e))
			
	def scan_user(self):
		'''
		it should be called continuelsy in order to keep scanning 
		all type of errors should be caught
		returns [index,accuracyScore]
		'''
		if(self.biometric.readImage()==True):
			self.biometric.convertImage(0x01)
			result=self.biometric.searchTemplate()
			# positionNumber=result[0]
			# accuracyScore=result[1]
			return result
		else:
			return None

	def biometric_storage_capacity(self):
		if  self.biometric_type == 'R30x':
			return self.biometric.getStorageCapacity()
	
	def clear_biometric_database(self,index=None):
		'''
		if index=None will clear all database
		otherwise will clear only selected index 
		'''
		if self.biometric_type == 'R30x':
			if index is None:
				return self.biometric.clearDatabase()
			else:
				return deleteTemplate(index)
		
	
	def download_template(self,index):
		if self.biometric_type=='R30x':
			self.biometric.loadTemplate(index)
			template_w=self.biometric.downloadCharacteristics()
			template_w_str=''
			for j in template_w:
				template_w_str=template_w_str+str(j)+','
			return template_w_str
	
	def upload_template(self,index,template_string):
		if self.biometric_type=='R30x':
			template_list = template_string.split(',')
			template_list.pop()
			template_list = map(int,template_list)
			if len(template_list)==512:
				self.biometric.uploadCharacteristics(0x01,template_list)
				self.biometric.storeTemplate(int(index),0x01)
				return True
			else:
				print("Invalid Template Size")
				return None
	
	def get_template_count(self):
			if self.biometric_type=='R30x':
				return self.biometric.getTemplateCount()
	
	def get_template(self,index=0):
		'''
		put finger on the finger print and get template 
		
		'''
		if self.biometric_type=='R30x':
			loop=True
			while loop:
				try:
					self.print_screen('PRESS # to START')
					key =self.waitForCharacter()
					if key=='D':
						loop=False
					self.print_screen("PUT FINGER:")
					self.beep(1)
					while ( self.biometric.readImage() == False ):
						time.sleep(.1)
					self.clear_screen()
					self.print_screen("Wait..:")
					self.biometric.convertImage(0x01)
					self.print_screen("Remove Finger")
					self.beep(2)
					self.print_screen("Put Again ....")
					time.sleep(0.1)
					while ( self.biometric.readImage() == False ):
						time.sleep(.1)
					self.biometric.convertImage(0x02)
					if (self.biometric.compareCharacteristics() == 0 ):
						self.print_screen("ERROR, Try Again")
						time.sleep(1)
						continue
					else:
						self.beep(3)
						self.biometric.createTemplate()
						# self.biometric.storeTemplate(index)
						self.print_screen("SUCCESS")
						# self.biometric.loadTemplate(index)
						template_w=self.biometric.downloadCharacteristics()
						template_w_str=''
						for j in template_w:
							template_w_str=template_w_str+str(j)+','
						return template_w_str
				except Exception as e:
					print(str(e))
					self.print_screen(str(e))
					time.sleep(1)
					self.print_screen('try again')
					time.sleep(1)
					

			
	def red_led_on(self):
		self.red_led.on()
	
	def red_led_off(self):
		self.red_led.off()
	
	def green_led_on(self):
		self.green_led.on()
	
	def green_led_off(self):
		self.green_led.off()
	
	def buzzer_on(self):
		self.buzzer.on()
	
	def buzzer_off(self):
		self.buzzer.off()
	
	def read_switch(self):
		return self.switch.value
	
	def beep(self,n=None):
		if n is None:
			n=1
		for i in range(n):
			self.buzzer_on()
			time.sleep(.1)
			self.buzzer_off()
			time.sleep(0.1)
	
	def get_key(self,key): # from keypad(clall back function of keyypad)
		self.key_pressed=True
		self.key_value=key
		self.beep(1)
		if key=='D':
			self.restart_code()

		# if key=='D':
			
		# print(key)

	def clear_screen(self):
		if self.display_type=='DOT_MATRIX_20X4':
			self.lcd.clear()
		elif self.display_type == 'CMD_LINE':
			print('---------------')
			
	def print_screen(self,str,line=None):
		if str is None:
			return
		if self.display_type=='DOT_MATRIX_20X4':
			if len(str) >self.row_count:
				str = str[0:self.row_count]
			if line==None:
				self.clear_screen()
				self.lcd.prnt(str,1)
			else:
				if (line >=1 and line<=self.col_count):
					self.lcd.prnt(str,line)
		elif self.display_type=='CMD_LINE':
			print(str) # to standard output
	
	def get_no(self,type="Password"):
		user_input_number=[]
		self.clear_screen()
		self.print_screen("Enter "+ type ,1)
		self.print_screen("#:OK, *:DELETE",4)
		while True:
			if(self.key_pressed):
				self.key_pressed=False
				if(self.key_value.isdigit()):
					user_input_number.append(self.key_value)
				elif((len(user_input_number))and(self.key_value=="*")):
					user_input_number.pop()
				elif(self.key_value=="#"):
					print('final password is '+ ''.join(user_input_number))
					return ''.join(user_input_number)
				# print("INPUT: " + ''.join(user_input_number))
				self.print_screen("                    ",2)
				self.print_screen(''.join(user_input_number),2)

	def waitForCharacter(self):
		print("waiting for response")
		self.key_pressed=False
		while(self.key_pressed==False):
			pass
		self.key_pressed=False
		print("wait completed")
		return self.key_value
	
	def check_hardwares(self):
		for i in range(1):
			self.red_led.on()
			self.green_led.off()
			self.buzzer.on()
			time.sleep(.2)
			self.red_led.off()
			self.green_led.on()
			self.buzzer.off()
			time.sleep(.5)
		self.buzzer.off()
		self.red_led.off()
		self.green_led_off()
		self.print_screen("Welcome")
		self.scan_user()
		

		
if __name__=='__main__':
	# hw=Hardware(display_type='DOT_MATRIX_20X4')
	hw=Hardware(display_type='DOT_MATRIX_20X4',keypad_type='KEYPAD_4X4',red_led_pin=18,green_led_pin=23,buzzer_pin=21,switch_pin=24,biometric_type='R30x',biometric_port='/dev/ttyS0')
	hw.begin_digital_io()
	hw.begin_display()
	hw.begin_keypad()
	hw.begin_biometric()
	
	hw.print_screen('it will be printed on the middle because no row no defined ')
	hw.print_screen('it will be concantenated to limited size ',1)
	hw.print_screen('will not be printed if row no gets exceeded ',5) 
	print('get template count',hw.get_template_count())
	print('storage capacity' ,hw.biometric_storage_capacity())
	print('clear biometric database',hw.clear_biometric_database(1))
	
	
	
	# hw.get_no('PASSWORD-1')
	k=hw.waitForCharacter()
	sample_template="3,1,67,28,122,0,255,254,255,254,255,254,225,254,192,254,192,0,192,0,192,0,192,0,192,0,192,0,192," \
					"0,224,0,224,0,224,0,240,2,240,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,92,155,210,126,102,50,212,158," \
					"115,60,147,222,63,191,215,94,88,65,170,158,53,170,25,95,72,182,215,124,26,38,70,125,28,41,69,189," \
					"73,44,171,253,72,186,22,189,72,153,235,250,76,176,22,122,60,48,108,186,58,179,0,122,71,155,219," \
					"27,45,29,220,88,28,48,5,249,103,166,15,246,42,191,223,86,104,193,212,22,114,44,231,14,108,37,206," \
					"117,101,45,38,80,108,157,143,177,84,46,107,173,37,178,2,77,33,185,201,201,0,0,0,0,0,0,0,0,0,0,0," \
					"0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0," \
					"0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,1,79,29,126,0,255,254,255,254,241," \
					"254,224,254,224,126,192,30,192,14,192,14,224,0,224,0,224,0,224,0,224,0,224,0,240,0,240,2,240,6,0," \
					"0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,58,143,76,254,105,40,211,94,58,41,29,62,104,180,20,190,47,62,194," \
					"126,51,66,131,126,30,157,94,255,64,180,217,191,113,56,149,31,54,151,34,157,48,151,225,125,89,28," \
					"33,157,94,158,36,245,96,186,43,253,36,147,32,58,83,59,151,186,40,17,225,251,85,39,154,251,37,176," \
					"134,187,90,183,235,219,75,65,24,24,39,57,132,121,110,63,213,19,105,63,192,16,103,62,149,87,87,37," \
					"128,20,39,182,4,52,71,58,64,181,68,62,128,179,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0," \
					"0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0," \
					"0,0,0,0,0,0,0,0,0,0,0, "
	
	# print('upload template \n',hw.upload_template(1,sample_template))
	# print(hw.download_template(0))
	if k =='D':
		exit(0)
	# hw.beep(2)
	# template=hw.get_template()
	# print(template)
	
	while(True):
		try:
			print(hw.scan_user())
		except Exception as e:
			print("Error: " + str(e))
		# hw.red_led_on()
		# hw.green_led_off()
		# print(hw.read_switch())
		# time.sleep(1)
		# hw.red_led_off()
		# hw.green_led_on()
		time.sleep(.1)

