import sys
import os
import redis
import rq
from rq import Queue, Worker, Connection
import logging
from datetime import datetime,timedelta
import time 
import json
import  app_srvc.task_usrreg 

"""
 worker  для реєстрації користувача

"""

irds_host = os.getenv('RDS_HOST')
irds_port = os.getenv('RDS_PORT')
irds_psw = os.getenv('RDS_PSW')
irdsq_outmsg = os.getenv('RDSQ_USRREG')

logging.basicConfig( level=logging.DEBUG)
def log( a_msg='NoMessage', a_label='logger' ):
	dttm = datetime.now()
	ls_dttm = dttm.strftime('%d-%m-%y %I:%M:%S %p')
	logging.info(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)
	#print(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)



def run_worker():
    label="worker_user_registration"
    red = redis.StrictRedis(irds_host, irds_port, charset="utf-8", password=irds_psw, decode_responses=False)
    listen = [irdsq_outmsg]
    queue = Queue(irdsq_outmsg, connection=red)
    log("running worker", label)
    with Connection(red):
        log("Create worker", label)
        worker = Worker(map(Queue, listen))
        log("Create worker-OK [" + worker.name + "]", label)
        try:
            log("Start worker", label)
            worker.work(logging_level="DEBUG", with_scheduler=False)
            log("Worker is finished", label)
        except Exception as e:
            print(e)   
            
        log('Worker has finished', label)
        log('Successful jobs: ' + str(worker.successful_job_count), label)
        log('Failed jobs: ' + str(worker.failed_job_count), label)
        log('Total working time: '+ str(worker.total_working_time), label) 

if __name__ == '__main__':
    run_worker()
    ##param={"szFirstName": "Nocolo", "szLastName": "Paganini", "szLogin": "PANIC", "szEmail": "PANIC@GMAIL.COM", "szPhone": "+380501112233"}
    ##app_srvc.task_usrreg.task_processor(param)
