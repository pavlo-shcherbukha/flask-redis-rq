from datetime import datetime,timedelta
import time 
import json
import logging
import random

logging.basicConfig(filename='worker.log', level=logging.DEBUG)
def log( a_msg='NoMessage', a_label='logger' ):
	dttm = datetime.now()
	ls_dttm = dttm.strftime('%d-%m-%y %I:%M:%S %p')
	logging.info(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)
	print(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)


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
    log( "Зупиняю обробник !!!!", label)
    return True
