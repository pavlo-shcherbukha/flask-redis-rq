@echo off
call ..\login.cmd
oc project %APP_PROJ%
pause

set fltempl=async-worker-templ.yaml 
set fldepl=async-repeater-depl.yaml 


set DATABASE_SERVICE_NAME=redis
set APP_SERVICE_NAME=rqrepeater
set APP_NAME=async-app-srvc
set GIT_BRANCH=main
set GIT_URL=https://github.com/pavlo-shcherbukha/flask-redis-rq.git
set DOCKER_PTH=./Dockerfile
set WORKER_RUNNER=/opt/app-root/lib/python3.9/site-packages/rq_scheduler/scripts/rqscheduler.py -b True -H redis -p 6379 -d 0 -P qq

oc delete -f %fldepl%
pause
oc process -f %fltempl%  --param=NAMESPACE=%APP_PROJ% --param=DATABASE_SERVICE_NAME=%DATABASE_SERVICE_NAME% --param=APP_SERVICE_NAME=%APP_SERVICE_NAME% --param=APP_NAME=%APP_NAME% --param=GIT_BRANCH=%GIT_BRANCH% --param=GIT_URL=%GIT_URL% --param=DOCKER_PTH=%DOCKER_PTH% --param=WORKER_RUNNER=%WORKER_RUNNER% -o yaml > %fldepl% 
pause
oc create -f %fldepl%
pause
 