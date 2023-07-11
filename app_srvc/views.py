from datetime import datetime,timedelta
import flask 
from flask import Flask, render_template, request, jsonify, make_response
from flask.cli import FlaskGroup
import json
import logging
import datetime
import sys
import traceback
import os
import time
import redis
import rq
from rq import Queue, Worker, Connection
from rq.registry import ScheduledJobRegistry
from rq_scheduler import Scheduler


from app_srvc.Errors import AppError, AppValidationError, InvalidAPIUsage
#from app_srvc.tasks import crttask_sendmsg
import app_srvc.tasks

application = Flask(__name__)
cli = FlaskGroup(create_app=application)
app_title="Сервіс асинхронної обробки з Redis "


@application.errorhandler(InvalidAPIUsage)
def invalid_api_usage(e):
    """
        Rest Api Error  handler
    """
    r=e.to_dict()
    return json.dumps(r), e.status_code, {'Content-Type':'application/json'}

"""
    Simple logger
"""
logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
def log( a_msg='NoMessage', a_label='logger' ):
	dttm = datetime.datetime.now()
	ls_dttm = dttm.strftime('%d-%m-%y %I:%M:%S %p')
	logging.info(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)
	print(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)

def add_cors_headers(response):
    """
        CORSA headers
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Content-Type"] = "applicaion/json"
    response.headers["Accept"] = "applicaion/json"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "DELETE,GET,POST"
    return response

@application.route("/")
def home():
    """
        Render main page
    """
    log("render home.html" )
    return render_template("home.html")

@application.route("/about/")
def about():
    """
        Render about pager
    """
    return render_template("about.html")



# Redis Connect

log("Read redis config")    
irds_host = os.getenv('RDS_HOST')
irds_port = os.getenv('RDS_PORT')
irds_psw = os.getenv('RDS_PSW')

irdsq_outmsg = os.getenv('RDSQ_OUTMSG')
irdsq_robot= os.getenv("RDSQ_ROBOT")

i_rpl_job_id = "repeater_job_id"

log('Connec tо redis: ' + 'host=' + irds_host + ' Port=' + irds_port + ' Password: ' + irds_psw )
log("Connect to Redis")
red = redis.StrictRedis(irds_host, irds_port, charset="utf-8", password=irds_psw, decode_responses=False)
log(" Trying PING")
rping=red.ping()
log( str(rping) )
if rping:
    log("redis Connected")
    q = Queue(connection=red)
    q_msg = Queue( name=irdsq_outmsg, connection=red)
    q_robot = Queue(name=irdsq_robot, connection=red)
    red.set(i_rpl_job_id, "NONE")
    log("Q LIST")
else:
    log("redis NOT CONNECTED!!!")    







"""
   ===========================================================================
    *********** Rest API ******************************
    ===========================================================================
"""

@application.route("/api/health", methods=["GET"])
def health():
    """
        health check
    """
    label="health"
    log('Health check', label)
    result={ "ok": True,"app_title":app_title}
    log('Health check return result '+ json.dumps( result ), label)
    return json.dumps( result ), 200, {'Content-Type':'application/json'}

@application.route("/api/sendmsg", methods=["POST"])
def sendmsg():
     """
        Send message to Queue irdsq_outmsg 
     """
     label="sendmsgtoQueue"
     body = request.get_json()
     body_dict = dict(body)
     #idjob=q_msg.enqueue(app_srvc.tasks.crttask_sendmsg)
     try:
        l1=q_msg.get_job_ids()
        log( "поислаю в " + q_msg.name, label)
        log( "num jobs " , label)
        idjob=q_msg.enqueue(app_srvc.tasks.crttask_sendmsg, body_dict)
        print( "jobid"+ idjob.get_id())
        ##idjob=q_msg.enqueue_in( timedelta(seconds=10), app_srvc.tasks.crttask_sendmsg)
        l2=q_msg.get_job_ids()
        #q_msg.run_sync
     except Exception as e:
         print(e)   
     #q = Queue(connection=red)
     res={"ok": True, "idjob": idjob.get_id()}
     return json.dumps(  res ), 200, {'Content-Type':'application/json'}

@application.route("/api/wstart", methods=["post", "get"])
def run_wstart():
    """
        start robot with time in sec and number of  fatchaed records
        request={"timedelta": 15, "records": 20, "msg": "start regular job"}
        response={"ok": true, "idjob": "ewrwqeq", "queue": "name"}
    """
    if request.method=='POST':
        label="POST-Startrobot"
        result={}
        log('PSOT Start Job', label)
        #try:
        body = request.get_json()
        body_dict = dict(body)
        log("Request body is " + json.dumps(body_dict) ,label)
        if not 'timedelta' in body_dict:
            raise InvalidAPIUsage( "InvalidAPIRequestParams",  "No key [timedelta]", target=label,status_code=422, payload = {"code": "NoKey", "description": "Не вказано обов'язковий ключ в запиті" } )

        if not 10 <=  body_dict["timedelta"] <= 360:
            raise InvalidAPIUsage( "InvalidAPIRequestParams",  "Out of Range value in [timedelta]", target=label,status_code=422, payload = {"code": "OutOfRangeValue", "description": "Не допустимий діапазон значень" } )

        if not 'records' in body_dict:
            raise InvalidAPIUsage( "InvalidAPIRequestParams",  "No key [records]", target=label,status_code=422, payload = {"code": "NoKey", "description": "Не вказано обов'язковий ключ в запиті" } )
        
        if not 25 <=  body_dict["records"] <= 200:
            raise InvalidAPIUsage( "InvalidAPIRequestParams",  "Out of Range value in [records]", target=label,status_code=422, payload = {"code": "OutOfRangeValue", "description": "Не допустимий діапазон значень" } )

        if not 'msg' in body_dict:
            raise InvalidAPIUsage( "InvalidAPIRequestParams",  "No key [msg]", target=label,status_code=422, payload = {"code": "NoKey", "description": "Не вказано обов'язковий ключ в запиті" } )

        rpl_job_id=red.get(i_rpl_job_id).decode('UTF-8')

        log("Start robot using queue " + q_robot.name ,label)
        registry = ScheduledJobRegistry(queue=q_robot)
        log("Шукаю в реєстрі JobID = " + rpl_job_id,label)
        job_found=False
        if rpl_job_id != "NONE":
            registry = ScheduledJobRegistry(queue=q_robot)
            job_ids=registry.get_job_ids()
            
            for job_id in job_ids:
                if job_id ==  rpl_job_id:
                    job_found=True
                    log("В реєстрі  вже існує JobID = " + rpl_job_id,label)
                    break

        if job_found:
            raise InvalidAPIUsage( "InvalidAPIRequestParams",  f"Task has allready sheduled [jobid={rpl_job_id} ]", target=label,status_code=422, payload = {"code": "Jobid exists", "description": "ЗАвдання вже поставлено в чергу" } )
        q_robot.fetch_job
        idjob=q_robot.enqueue_in( timedelta(seconds=body_dict["timedelta"]),  app_srvc.tasks.task_robot, body_dict)
        log("В чергу відправлено завдання з jobid=" + idjob.get_id(), label)
        registry = ScheduledJobRegistry(queue=q_robot)
        log("Записую в редіс jobid=" + idjob.get_id(), label)
        red.set(i_rpl_job_id,idjob.get_id() )
        result={"ok": True, "idjob": idjob.get_id(), "queue": q_robot.name}
        return json.dumps(  result ), 200, {'Content-Type':'application/json'}
        #except Exception as e:
        #    ex_type, ex_value, ex_traceback = sys.exc_info()
        #    trace_back = traceback.extract_tb(ex_traceback)
        #    stack_trace = list()
        #    for trace in trace_back:
        #        stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
        #    #ex_code=e.code
        #    ex_name=ex_type.__name__
        #    ex_dsc=ex_value.args[0]

        #    result["ok"]=False
        #    result["error"]=ex_dsc
        #    result["errorCode"]=ex_name
        #    result["trace"]=stack_trace 
        #    return json.dumps(result), 422, {'Content-Type':'application/json'}
    elif request.method=='GET':
        label="GET-Startrobot"
        result={}
        log('GET Start Job', label)
        #try:
        rpl_job_id=red.get(i_rpl_job_id).decode('UTF-8')
        log("Find robot using queue " + q_robot.name ,label)
        registry = ScheduledJobRegistry(queue=q_robot)
        log("Шукаю в реєстрі JobID = " + rpl_job_id,label)
        job_found=False
        if rpl_job_id != "NONE":
            registry = ScheduledJobRegistry(queue=q_robot)
            job_ids=registry.get_job_ids()
            
            for job_id in job_ids:
                if job_id ==  rpl_job_id:
                    job_found=True
                    log("В реєстрі  вже існує JobID = " + rpl_job_id,label)
                    break
        result={"ok": True, "idjob": rpl_job_id, "queue": q_robot.name, "status": "NotFound"}
        if job_found :
            result["status"]="Found"
        return json.dumps(  result ), 200, {'Content-Type':'application/json'}
        #except Exception as e:
        #    ex_type, ex_value, ex_traceback = sys.exc_info()
        #    trace_back = traceback.extract_tb(ex_traceback)
        #    stack_trace = list()
        #    for trace in trace_back:
        #        stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
        #    #ex_code=e.code
        #    ex_name=ex_type.__name__
        #    ex_dsc=ex_value.args[0]

        #    result["ok"]=False
        #    result["error"]=ex_dsc
        #    result["errorCode"]=ex_name
        #    result["trace"]=stack_trace 
        #    return json.dumps(result), 422, {'Content-Type':'application/json'}


@application.route("/api/wstop", methods=["delete"])
def run_wstop():
    """
        stop robot 
    """    
 
    label="Stoprobot"
    result={}
    log('Stop Job', label)
    try:
        job_list=q_robot.get_jobs()
        for job in job_list:
            job.delete()  
        registry = ScheduledJobRegistry(queue=q_robot)
        registry.cleanup()

        log('Stopped all Jobs', label)
        result={"ok": True}
        return json.dumps(  result ), 200, {'Content-Type':'application/json'}

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
        return json.dumps(result), 422, {'Content-Type':'application/json'}


@application.route("/api/wrq", methods=["post"])
def run_wrq():
    """
        start robot with time in sec and number of  fatchaed records
        request={"timedelta": 15, "records": 20, "msg": "start regular job"}
        response={"ok": true, "idjob": "ewrwqeq", "queue": "name"}
    """
    label="RQStartrobot"
    result={}
    log('Start Job', label)
    try:
        body = request.get_json()
        body_dict = dict(body)
        log("Request body is " + json.dumps(body_dict) ,label)
        if not 'timedelta' in body_dict:
            raise InvalidAPIUsage( "InvalidAPIRequestParams",  "No key [timedelta]", target=label,status_code=422, payload = {"code": "NoKey", "description": "Не вказано обов'язковий ключ в запиті" } )

        if not 10 <=  body_dict["timedelta"] <= 360:
            raise InvalidAPIUsage( "InvalidAPIRequestParams",  "Out of Range value in [timedelta]", target=label,status_code=422, payload = {"code": "OutOfRangeValue", "description": "Не допустимий діапазон значень" } )

        if not 'records' in body_dict:
            raise InvalidAPIUsage( "InvalidAPIRequestParams",  "No key [records]", target=label,status_code=422, payload = {"code": "NoKey", "description": "Не вказано обов'язковий ключ в запиті" } )
        
        if not 25 <=  body_dict["records"] <= 200:
            raise InvalidAPIUsage( "InvalidAPIRequestParams",  "Out of Range value in [records]", target=label,status_code=422, payload = {"code": "OutOfRangeValue", "description": "Не допустимий діапазон значень" } )

        if not 'msg' in body_dict:
            raise InvalidAPIUsage( "InvalidAPIRequestParams",  "No key [msg]", target=label,status_code=422, payload = {"code": "NoKey", "description": "Не вказано обов'язковий ключ в запиті" } )

        log("Start robot using queue " + q_robot.name ,label)
        
        scheduler = Scheduler(queue=q_robot, connection=red)
        idjob = scheduler.schedule(scheduled_time=datetime.datetime.utcnow(), func= app_srvc.tasks.task_robot, args=[body_dict], repeat=None, interval=body_dict["timedelta"])
        jobcnt=scheduler.count()
        log("В чергу відправлено завдання з jobid=" + idjob.get_id(), label)
       

        result={"ok": True, "idjob": idjob.get_id(), "queue": q_robot.name}
        return json.dumps(  result ), 200, {'Content-Type':'application/json'}
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
        return json.dumps(result), 422, {'Content-Type':'application/json'}
