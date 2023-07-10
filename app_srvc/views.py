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
irds_host = os.getenv('RDS_HOST');
irds_port = os.getenv('RDS_PORT');
irds_psw = os.getenv('RDS_PSW');

irdsq_outmsg = os.getenv('RDSQ_OUTMSG');

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

@application.route("/api/run", methods=["GET"])
def run_w():


    res={"ok": True}
    return json.dumps(  res ), 200, {'Content-Type':'application/json'}






