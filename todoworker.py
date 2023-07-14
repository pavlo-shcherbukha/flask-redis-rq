import sys
import os
import redis
import rq
from rq import Queue, Worker, Connection
from rq.worker_pool import WorkerPool
import logging
from datetime import datetime,timedelta
import time 
import json

import  app_srvc.tasks 


"""
todo worker. This is the worker which is process every todo-s from queue 

"""

irds_host = os.getenv('RDS_HOST')
irds_port = os.getenv('RDS_PORT')
irds_psw = os.getenv('RDS_PSW')
#irdsq_queue = os.getenv('RDSQ_ROBOT')
irdsq_outmsg = os.getenv('RDSQ_OUTMSG')

logging.basicConfig( level=logging.DEBUG)
def log( a_msg='NoMessage', a_label='logger' ):
	dttm = datetime.now()
	ls_dttm = dttm.strftime('%d-%m-%y %I:%M:%S %p')
	logging.info(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)
	#print(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)



def run_worker():
    label="worker_todo"
    red = redis.StrictRedis(irds_host, irds_port, charset="utf-8", password=irds_psw, decode_responses=False)
    listen = [irdsq_outmsg]
    queue = Queue(irdsq_outmsg, connection=red)
    log("running worker", label)
    #with Connection(red):

    log("Create worker", label)
    #worker = Worker(map(Queue, listen))
    workerpool = WorkerPool(  listen , connection=red, num_workers=2)
    #log("Create worker-OK [" + worker.name + "]", label)
    log("Create worker-OK " , label)
    try:
        log("Start worker", label)
        #worker.work(logging_level="DEBUG", with_scheduler=False)
        workerpool.start(logging_level="DEBUG")
        log("Worker is finished", label)
    except Exception as e:
        print(e)   
        
    log('Worker has finished', label)
    #log('Successful jobs: ' + str(worker.successful_job_count), label)
    #log('Failed jobs: ' + str(worker.failed_job_count), label)
    #log('Total working time: '+ str(worker.total_working_time), label) 

if __name__ == '__main__':
    run_worker()
