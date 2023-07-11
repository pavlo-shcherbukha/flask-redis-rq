from datetime import datetime,timedelta
import time 
import json
import logging
import random
import requests

import os
import sys
import traceback


import redis
import rq
from rq import Queue, Worker, Connection
from rq.registry import ScheduledJobRegistry


#logging.basicConfig(filename='task.log', level=logging.DEBUG)
logging.basicConfig( level=logging.DEBUG)
def log( a_msg='NoMessage', a_label='logger' ):
	dttm = datetime.now()
	ls_dttm = dttm.strftime('%d-%m-%y %I:%M:%S %p')
	logging.info(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)
	#print(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)

def repeatjob( jobprm ):
    """
        Потр завдання в чергу
    """
    result={}
    label="repeat_job"
    try:
        #iit_distrsrvc_base_url = os.environ.get("IIT_DISTRSRVC_URL")
        #iit_service_name=os.environ.get("IIT_SERVICE_NAME")
        base_url="http://app-srvc-pashakx-dev.apps.sandbox-m2.ll9k.p1.openshiftapps.com"
        req_url= base_url+"/api/wstart"
        req_data=jobprm
        response = requests.post(req_url,  data=json.dumps(req_data) , headers={'Content-Type':  'application/json'} )    

        if response.status_code == 200:
            result['ok']=True
            result["errorCode"]=response.status_code
            result["resText"]=response.text
            result["resBody"]=response.json()
        else: 
            result['ok']=False
            result["error"]=response.text
            result["errorCode"]=response.status_code

        return result  
    except Exception as e:
        ex_type, ex_value, ex_traceback = sys.exc_info()
        trace_back = traceback.extract_tb(ex_traceback)
        stack_trace = list()
        for trace in trace_back:
            stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
        #ex_code=e.code
        ex_name=ex_type.__name__
        ex_dsc=ex_value.args[0]

        result["ok"]=False
        result["error"]=ex_dsc
        result["errorCode"]=ex_name
        result["trace"]=stack_trace 

        return result               





def crttask_sendmsg( message ):
    
    print("start send messge JOB")
    print("input data: " + json.dumps( message ) )
    print("waiting Start")
    print("waiting stop")
    return True

def task_robot( robot_params ):
    
    label="task_robot"
    log("task robot", label)
    log("reobot params = " + json.dumps(robot_params), label) 

    log( "Параметр запуску: timedelta=" + str(robot_params["timedelta"]), label)
    log( "Параметр запуску: records=" + str(robot_params["records"]), label)
    log( "Додаткові параметри: " + robot_params["msg"], label)

    delay=random.randint(5, robot_params["timedelta"])     #robot_params["timedelta"]//2
    log( "Запускаю обробник на (сек)" + str(delay), label)
    time.sleep(delay)
    log( "Перезапускаю завдання", label)
    result = repeatjob(  robot_params )
    log( "Результат перезапуску", label)
    if result['ok']==True:
        log( "Перезапуск успішний " + json.dumps(result), label)
    else:
        log( "Перезапуск НЕЕЕЕ успішний " + json.dumps(result), label)
    log( "Зупиняю обробник !!!!", label)
    return True
