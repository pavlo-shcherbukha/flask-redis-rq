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
import psycopg2


from app_srvc.Errors import AppError, AppValidationError, InvalidAPIUsage
#from app_srvc.tasks import crttask_sendmsg
import app_srvc.tasks
import app_srvc.task_usrreg

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

@application.route("/userreg/")
def ui_user_reg_form():
    """
        Render the user regustration form
    """
    return render_template("user_reg_form.html")


    



# Redis Connect

log("Read redis config")    
irds_host = os.getenv('RDS_HOST')
irds_port = os.getenv('RDS_PORT')
irds_psw = os.getenv('RDS_PSW')

irdsq_outmsg = os.getenv('RDSQ_OUTMSG')
irdsq_robot= os.getenv("RDSQ_ROBOT")
irdsq_usrreg= os.getenv("RDSQ_USRREG")

i_rpl_job_id = "repeater_job_id"
i_rpl_status = "repeater_status"


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
    q_usrreg = Queue(name=irdsq_usrreg, connection=red)
    red.set(i_rpl_job_id, "NONE")
    red.set(i_rpl_status, "STOP")
    log("Q LIST")
else:
    log("redis NOT CONNECTED!!!")    


log("Connect to POSTGRESQL")

ipg_host = os.getenv('PG_HOST')
ipg_port = os.getenv('PG_PORT')
ipg_user = os.getenv('PG_USER')
ipg_psw = os.getenv('PG_PSW')
ipg_db = os.getenv('PG_DB')




@application.route("/userregres/", methods=["POST"])
def ui_user_reg_res():
    """
        User registration 
        Process POST request
        Send user data from http form into queue 
    """
    label="ui_user_reg_res" 
    body={}
    mimetype = request.mimetype
    log("choose right  mimetype", label)
    if mimetype == 'application/x-www-form-urlencoded':
        iterator=iter(request.form.keys())
        for x in iterator:
            body[x]=request.form[x]            
    elif mimetype == 'application/json':
        body = request.get_json()
    else:
        orm = request.data.decode()

    log('Request body is: ' + json.dumps(  body ), label)
    log( "Send the body into queue " + q_usrreg.name, label)
    job=q_usrreg.enqueue(app_srvc.task_usrreg.task_processor, body)
    log( "Message sent into queue with job_id="+ job.get_id())
    log('Вертаю результат: ' )

    return render_template("user_reg_resp.html" , data={ "jobid": job.get_id(), "queue": q_usrreg.name})

@application.route("/userlist/", methods=["GET"])
def ui_user_list():
    label="ui_user_list"
    log("Підлючаюся до БД", label)
    result={}
    try:
        conn = psycopg2.connect(database=ipg_db,
                            host=ipg_host,
                            user=ipg_user,
                            password=ipg_psw,
                            port=ipg_port)
        log("Відкриваю курсор", label)
        cursor = conn.cursor()
        log("Виконю вставку", label)
        cursor.execute("SELECT * FROM test.rusrs")
        log("Отримую всі записи", label)
        userlist=cursor.fetchall()
        log("Закриваю курсор", label)
        cursor.close()
        log("Відключаюся від БД", label)
        conn.close()
        allusers=[]

        for usertup in userlist:
            xuser={}
            for i,  useratt  in enumerate(usertup):
                #(iduser, firstname, lastname, login , email, phone, status, v1,v2,v3, v4,v5,v6)
                #
                if i == 0: 
                    xuser["iduser"]=useratt
                elif i ==1 :
                    xuser["firstname"]=useratt
                elif i ==2 :    
                    xuser["lastname"]=useratt
                elif i ==3 :       
                    xuser["login"]=useratt
                elif i ==4 :
                    xuser["email"]=useratt
                elif i ==5 :
                    xuser["phone"]=useratt
                elif i ==6 :
                    xuser["status"]=useratt
            allusers.append(xuser)
              

        return render_template("user_list.html" , data=allusers )
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
        request={"timedelta": 15, "records": 20, "msg": "start regular job", "rplstatus": "START"}
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

        if 'rplstatus' in body_dict:
            if body_dict["rplstatus"] == "START":
                red.set(i_rpl_status, "START")
                del body_dict["rplstatus"]
            else:
                raise InvalidAPIUsage( "InvalidAPIRequestParams",  "Out of Range value in [rplstatus]", target=label,status_code=422, payload = {"code": "OutOfRangeValue", "description": "Не допустимий діапазон значень rplstatus" } )    
        else:
            rpl_status=red.get(i_rpl_status).decode('UTF-8')
            if rpl_status=="STOP":
                result={"ok": True, "idjob": "0", "queue": "None",  "rplstatus":  "STOP" }
                return json.dumps(  result ), 200, {'Content-Type':'application/json'}

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
            #log("нуда існує", label)
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
        rpl_job_id=red.get(i_rpl_job_id).decode('UTF-8')
        log('Потомчний JOB=' + rpl_job_id, label)
        registry = ScheduledJobRegistry(queue=q_robot)
        log('Отримую JOBS в реєстрі. Зареєстровано = ' + str(registry.count) , label)
        job_ids=registry.get_job_ids()
        log('JOB_ID  поіменно = ' + json.dumps(job_ids)  )
        log("Видаляю jobs з registry", label)
        registry.remove_jobs()
        log("О, віидалив! Залишилося в registry jobs " + str(registry.count) , label)
        
        log('Видаляю JOBS з черги:', label)
        job_list=q_robot.get_jobs()
        for job in job_list:
            log("Видаляю з черги jobid=" + job.get_id(), label)
            job.delete()  
        log('Очищаю ключ поточного JOBS в [' + i_rpl_job_id + ']', label)
        red.set(i_rpl_job_id, "NONE")
        red.set(i_rpl_status, "STOP")


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


