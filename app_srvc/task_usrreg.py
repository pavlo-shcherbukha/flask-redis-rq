from datetime import datetime,timedelta
import time 
import json
import logging
import random
import os
import sys
import traceback

def log( a_msg='NoMessage', a_label='logger' ):
	dttm = datetime.now()
	ls_dttm = dttm.strftime('%d-%m-%y %I:%M:%S %p')
	#logging.info(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)
	print(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)


def task_processor( user_profile ):
    """
      Демо процесор для форми реєсрації користувача
    """
    label="task_processor"
    log("task processor", label)
    log("Обробляю запис " + json.dumps( user_profile ), label)
    delay=random.randint(5, 15) 
    log( "Запускаю затримку оброника на (сек)" + str(delay), label)
    time.sleep(delay)

    log( "======================================================================", label)
    log( "Обробник роботу виконав !!!!", label)
    log( "======================================================================", label)
    return True

