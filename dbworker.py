import sys
import os
import redis
import rq
from rq import Queue, Worker, Connection
import logging
from datetime import datetime,timedelta
import time 
import json

import  app_srvc.tasks 

irds_host = os.getenv('RDS_HOST')
irds_port = os.getenv('RDS_PORT')
irds_psw = os.getenv('RDS_PSW')
irdsq_queue = os.getenv('RDSQ_ROBOT')

logging.basicConfig(filename='worker.log', level=logging.DEBUG)
def log( a_msg='NoMessage', a_label='logger' ):
	dttm = datetime.now()
	ls_dttm = dttm.strftime('%d-%m-%y %I:%M:%S %p')
	logging.info(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)
	print(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)



def run_worker():
    label="worker_robot"
    red = redis.StrictRedis(irds_host, irds_port, charset="utf-8", password=irds_psw, decode_responses=False)
    listen = [irdsq_queue]
    queue = Queue(irdsq_queue, connection=red)
    log("running worker", label)
    with Connection(red):
        worker = Worker(map(Queue, listen))
        try:
            #idjob=q_robot.enqueue_in( timedelta(seconds=body_dict["timedelta"]),  app_srvc.tasks.task_robot, body_dict)
            log("getting current job", label)
            curentjob=worker.get_current_job()
            log("running worker " + curentjob.get_id(), label)
            log("running worker " + curentjob.exc_info(), label)
            worker.work(logging_level="DEBUG", with_scheduler=True)
            log("reshedule job", label)
            #queue.enqueue_job(job=curentjob)

            print("resheduled !!!")   
        except Exception as e:
            print(e)   
            
        log('OK', label)
        log(worker.name, label)
        log('Successful jobs: ' + str(worker.successful_job_count), label)
        log('Failed jobs: ' + str(worker.failed_job_count), label)
        log('Total working time: '+ str(worker.total_working_time), label) 

if __name__ == '__main__':
    run_worker()
    #prm={"timedelta": 15, "records": 20, "msg": "start regular job"}
    #app_srvc.tasks.task_robot(prm)