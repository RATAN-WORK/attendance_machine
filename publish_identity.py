#!/user/bin/python

""" data will be sent to the live server only"""
from softwares.era_server import era_server
from system import system
from storage import msql
print('publishing identity')
try:
    live_server = msql.get_setting_data('live_server')
    server = None
    if live_server == 'SERVER1':
        server = msql.get_setting_data('api1_server')
    elif live_server == 'SERVER2':
        server = msql.get_setting_data('api2_server')
    elif live_server == 'TEST_SERVER':
        server =msql.get_setting_data('test_server')

    es =era_server.EraServer()
    syss = system.System()
    hostname = syss.get_host_name()
    ip = syss.get_host_ip()
    t =syss.get_cpu_temp()
    uptime = syss.get_uptime()
    es.set_server(server)
    es.publish_identity(hostname,ip,t,uptime)
except Exception as e:
    print(str(e))