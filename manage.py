# manage.py


import sys
import os
import redis

from rq import  Worker , Queue, Connection
import app_srvc.tasks 

irds_host = os.getenv('RDS_HOST');
irds_port = os.getenv('RDS_PORT');
irds_psw = os.getenv('RDS_PSW');

irdsq_outmsg = os.getenv('RDSQ_OUTMSG');


def test():
    """Runs the unit tests without test coverage."""
    print("======================")
    print("test command")
    print("======================")
 


def run_worker():
    red = redis.StrictRedis(irds_host, irds_port, charset="utf-8", password=irds_psw, decode_responses=True)
    listen = [irdsq_outmsg, 'default']
    with Connection(red):
        worker = Worker(map(Queue, listen))
        #worker = Worker( queue=irdsq_outmsg )
        worker.work()



if __name__ == '__main__':
    run_worker()