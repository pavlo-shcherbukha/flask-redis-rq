# manage.py


import sys
import os
import redis

from rq import  Worker , Queue, Connection
#from app_srvc.tasks import crttask_sendmsg

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
    # listen = [irdsq_outmsg]
    #workers = Worker.all(connection=red)
    listen = ["default"]
    queue = Queue(irdsq_outmsg, connection=red)

    #for worker in workers:
    #    print("worker=" + worker.name)

    with Connection(red):

        #workers = Worker.all(queue=queue)
        worker = Worker( queue=queue )
        worker.work()
        print('OK')
        print(worker.name)

        print('Successful jobs: ' + str(worker.successful_job_count))
        print('Failed jobs: ' + str(worker.failed_job_count))
        print('Total working time: '+ str(worker.total_working_time)) 

        """
        for worker in workers:
            print('name=' + worker.name)
            worker.work()
            print('OK')
            print(worker.name)

            print('Successful jobs: ' + str(worker.successful_job_count))
            print('Failed jobs: ' + str(worker.failed_job_count))
            print('Total working time: '+ str(worker.total_working_time)) 

        """

if __name__ == '__main__':
    run_worker()