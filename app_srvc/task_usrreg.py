from datetime import datetime,timedelta
import time 
import json
import logging
import random
import os
import sys
import traceback
import psycopg2

ipg_host = os.getenv('PG_HOST')
ipg_port = os.getenv('PG_PORT')
ipg_user = os.getenv('PG_USER')
ipg_psw = os.getenv('PG_PSW')
ipg_db = os.getenv('PG_DB')


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

    log("Підлючаюся до БД", label)
    try:
      conn = psycopg2.connect(database=ipg_db,
                          host=ipg_host,
                          user=ipg_user,
                          password=ipg_psw,
                          port=ipg_port)
      log("Відкриваю курсор", label)
      cursor = conn.cursor()
      log("Виконю вставку", label)
      cursor.execute("INSERT INTO test.rusrs (firstname, lastname, login , email, phone) VALUES(%s, %s, %s, %s, %s)", (user_profile["szFirstName"], user_profile["szLastName"], user_profile["szLogin"], user_profile["szEmail"], user_profile["szPhone"]) )
      conn.commit()
      log("Закриваю курсор", label)
      cursor.close()
      log("Відключаюся від БД", label)
      conn.close()
    except Exception as e:
      print(e)   

    log( "======================================================================", label)
    log( "Обробник роботу виконав !!!!", label)
    log( "======================================================================", label)
    return True

