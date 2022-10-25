#!/user/bin/python

""" IT WILL SEND DATA TO THE DEFAULT SERVERS IF ANY ERROR IS FOUND.


POSSIBLE VALUES OF THE CELLS

NA: NOT APPLICABLE,MEANS IT WAS NOT SELECTED TO BE UPDATED DURING LIVE PUNCHING
ERROR: TRIED TO SEND DATA BUT FAILED.
OR ANY OTHER RESPONSE FROM THE SERVER.

"""

import biometric_device
from storage import msql
bd = biometric_device.Biometric_device(hw=False,srvr=True,syss=True)

try:
    user_logs = msql.get_users_log(type ='DICT')
    s1_en = int(msql.get_setting_data('api1_enabled'))
    s2_en = int(msql.get_setting_data('api2_enabled'))
    ts_en = int(msql.get_setting_data('test_api_enabled'))

    for row in user_logs:
        # print (row)
        sno = row['sno']
        time_stamp = row['time_stamp']
        indx = row['index']
        punch_id = row['punch_id']
        server1_response = row['server1_response']
        server2_response = row['server2_response']
        test_server_response = row['test_server_response']
        image_link = row['image']
        print(sno)

        print('previous response:',server1_response,server2_response,test_server_response)
        if s1_en:
            if 'ERROR' in [server1_response] or 'NA' in [server1_response]:
                print ('ERROR AT SNO  = {}'.format(sno))
                print ('data will be updated to the server-1')
                response = bd.send_punch_data_to_era_server(indx,punch_id,image_link,'SERVER1',time_stamp)
                server1_response = response[0]
                print('SERVER1 RESPONSE: {}'.format(server1_response))
                print('NEW RESPONSE: {},{},{}'.format(server1_response , server2_response , test_server_response))

                if msql.update_punch_logs(sno , server1_response , server2_response , test_server_response):
                    print('DATA UPDATED 1 ')
                else:
                    print('NOT DONE 1')

        if s2_en:
            if 'ERROR' in [server2_response] or 'NA' in [server2_response]:
                print ('ERROR AT SNO  = {}'.format(sno))
                print ('data will be updated to the server2')
                response = bd.send_punch_data_to_era_server(indx , punch_id ,image_link,'SERVER2' , time_stamp)
                server2_response = response[1]
                print('SERVER2 RESPONSE: {}'.format(server2_response))
                print('NEW RESPONSE: {},{},{}'.format(server1_response , server2_response , test_server_response))

                if msql.update_punch_logs(sno , server1_response , server2_response , test_server_response):
                    print('DATA UPDATED 2 ')
                else:
                    print('NOT DONE 2')

        if ts_en:
            if 'ERROR' in [test_server_response] or 'NA' in [test_server_response]:
                print ('ERROR AT SNO  = {}'.format(sno))
                print ('data will be updated to the test_server')
                response = bd.send_punch_data_to_era_server(indx , punch_id , image_link,'TEST_SERVER' , time_stamp)
                test_server_response = response[2]
                print('TEST SERVER RESPONSE: {}'.format(test_server_response))
                print('NEW RESPONSE: {},{},{}'.format(server1_response , server2_response , test_server_response))

                if msql.update_punch_logs(sno , server1_response , server2_response , test_server_response):
                    print('DATA UPDATED TEST')
                else:
                    print('NOT DONE TEST')


except Exception as e:
    print(str(e))

