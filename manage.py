import sys
import os
import redis
import rq
from rq import Queue, Worker, Connection

irds_host = os.getenv('RDS_HOST');
irds_port = os.getenv('RDS_PORT');
irds_psw = os.getenv('RDS_PSW');
irdsq_outmsg = os.getenv('RDSQ_OUTMSG');
def test():
    print("======================")
    print("test command")
    print("======================")
def run_worker():
    red = redis.StrictRedis(irds_host, irds_port, charset="utf-8", password=irds_psw, decode_responses=False)
    listen = [irdsq_outmsg]
    queue = Queue(irdsq_outmsg, connection=red)
    with Connection(red):
        worker = Worker(map(Queue, listen))
        try:
            worker.work(logging_level="DEBUG")
        except Exception as e:
            print(e)   
            
        print('OK')
        print(worker.name)
        print('Successful jobs: ' + str(worker.successful_job_count))
        print('Failed jobs: ' + str(worker.failed_job_count))
        print('Total working time: '+ str(worker.total_working_time)) 

if __name__ == '__main__':
    run_worker()