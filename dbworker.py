import sys
import os
import redis
import rq
from rq import Queue, Worker, Connection

import  app_srvc.tasks 

irds_host = os.getenv('RDS_HOST')
irds_port = os.getenv('RDS_PORT')
irds_psw = os.getenv('RDS_PSW')
irdsq_queue = os.getenv('RDSQ_ROBOT')

def run_worker():
    red = redis.StrictRedis(irds_host, irds_port, charset="utf-8", password=irds_psw, decode_responses=False)
    listen = [irdsq_queue]
    queue = Queue(irdsq_queue, connection=red)
    with Connection(red):
        worker = Worker(map(Queue, listen))
        try:
            worker.work(logging_level="DEBUG", with_scheduler=True)
        except Exception as e:
            print(e)   
            
        print('OK')
        print(worker.name)
        print('Successful jobs: ' + str(worker.successful_job_count))
        print('Failed jobs: ' + str(worker.failed_job_count))
        print('Total working time: '+ str(worker.total_working_time)) 

if __name__ == '__main__':
    run_worker()
    #prm={"timedelta": 15, "records": 20, "msg": "start regular job"}
    #app_srvc.tasks.task_robot(prm)