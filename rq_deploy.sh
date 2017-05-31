#!/bin/bash

# 头像
ps ax | grep "rqworker avatar" | awk '{print $1}' | xargs kill
sleep 5
nohup python manage.py rqworker avatar &
nohup python manage.py rqworker avatar &


# push
ps ax | grep "rqworker push" | awk '{print $1}' | xargs kill
sleep 1
for i in `seq 50`;do
nohup python manage.py rqworker push &
done


# refresh
ps ax | grep "rqworker refresh" | awk '{print $1}' | xargs kill
sleep 1
for i in `seq 50`;do
nohup python manage.py rqworker refresh &
done


# high
ps ax | grep "rqworker high" | awk '{print $1}' | xargs kill
sleep 1
for i in `seq 30`;do
nohup python manage.py rqworker high &
done
