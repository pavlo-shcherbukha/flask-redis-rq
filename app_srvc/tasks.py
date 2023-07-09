import time 
import json

def crttask_sendmsg( message ):
    print("start send messge JOB")
    print("input data: " + json.dumps(message) )
    print("waiting Start")
    time.sleep(  4 )
    print("waiting stop")
    return True
