import requests
from time import sleep

job_data_list = [1,['START',10,10,10,'END'],[0,1,2,3,4]]

#Server URL
server_url_list = 'http://192.168.15.145:5000/add_job_list'

try:
    while True:
        jobID = input()
        response_list = requests.post(server_url_list, json=job_data_list)
        print(response_list.json())
except KeyboardInterrupt:
    print('inturrupted by user')
