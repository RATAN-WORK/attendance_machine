import datetime
# import commands #LATERON CHANGE ALL OF ITS funcitons to subprocesss
import os
import subprocess
import time
from gpiozero import CPUTemperature


class System:
    def __init__(self):
        # type: () -> object

        pass

    def __del__(self):
        pass

    def update_hw_clock(self,datetime):
        """
        first it sets the system time
        and then updates the same time to the hw clock.
        datetime format YYYY-DD-MM HH:MM:SS
        """
        try:
            print('updating hw clock')
            subprocess.check_output(['sudo' , 'date' , '-s' , datetime])
            time.sleep(.1)
            subprocess.check_output(['sudo' , 'hwclock' , '-w'])
            return True
        except Exception as e:
            print (str(e))
            return None
    def remove_directory(self,p):
        try:
            subprocess.check_output(['rm','-r',p])
            return True
        except Exception as e:
            print(str(e))
            return None

    def create_directory(self , p):
        try:
            if not os.path.exists(p):
                os.makedirs(p)  # makedirs instead of mkdir to create a
                print("directory created ")
                print(p)
            else:
                print(str(p) + " already exists")
            return p
        except Exception as e:
            print("Error creating dir: " + str(e))
            return None

    def restart_code(self,arg1=None):
        # p("wait....")
        if arg1 is None:
           restart_time = 1
        python = sys.executable
        os.execl(python , python , sys.argv[0] , str(restart_time))  # argument 1 passed to wait for15 seconds

    # print(sys.argv)
    # print(python)
    # os.execl(python,python,*sys.argv,'2')

    def kill_process(self , process_id):
        value = subprocess.check_output(["sudo" , "kill" , process_id])
        return value

    def get_host_name(self):
        try:
            value = subprocess.check_output(['hostname'])
            return value.split()[0]
        except Exception as e:
            return None

    def change_hostname(self , hostname):
        try:
            return subprocess.check_output(["hostname" , hostname])
        except Exception as e:
            return None

    def restart_device(self):
        try:
            subprocess.check_output(["sudo" , "reboot"])
            return True
        except Exception as e:
            return None

    def get_process_id(self):
        try:
            return os.getppid()
        except Exception as e:
            return None

    def get_host_ip(self):
        # value = commands.getoutput('hostname -I')
        try:
            value = subprocess.check_output(["hostname" , "-I"])
            value = value.split()[0]
            return value
        except Exception as e:
            return None

    def get_current_timestamp(self , type):
        """
        :rtype: object
        """
        if type == 0:
            return datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
        elif type == 1:
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif type == 2:
            return datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        elif type == 3:  # fixed length
            now = datetime.datetime.now()
            formated_time = str(now.day).zfill(2) + "-" + str(now.month).zfill(2) + "-" + str(now.year) + " " + str(
                now.hour).zfill(2) + ":" + str(now.minute).zfill(2)
            return formated_time

    def get_cpu_temp(self):
        try:
            cpu_temperature = CPUTemperature().temperature
            return cpu_temperature
        except Exception as e:
            print (str(e))

    def get_uptime(self):
        try:
            up_time = subprocess.check_output(['uptime'])
            return up_time
        except Exception as e:
            print(str(e))

if __name__ == '__main__':
    s =System()
    # s.update_hw_clock('2018-11-18 17:31:33')