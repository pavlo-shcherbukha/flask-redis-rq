@echo off
call login.cmd
oc project %APP_PROJ%
pause
oc create -f %1
