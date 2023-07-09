# Entry point for the application.
from . import views  
from .views import application

import sys
import unittest
import os

import click
import redis
from flask.cli import FlaskGroup
from rq import Connection, Worker

cli = FlaskGroup(application)

irds_host = os.getenv('RDS_HOST');
irds_port = os.getenv('RDS_PORT');
irds_psw = os.getenv('RDS_PSW');

irdsq_outmsg = os.getenv('RDSQ_OUTMSG');


#@application.cli.command("test")
#@click.argument("name")
@cli.command("test")
def test():
    """Runs the unit tests without test coverage."""
    print("======================")
    print("test command")
    print("======================")
 

"""
@cli.command('run_worker')
def run_worker():


    with Connection(redis_connection):
        worker = Worker(app.config['QUEUES'])
        worker.work()
"""

#if __name__ == '__main__':
#    cli()