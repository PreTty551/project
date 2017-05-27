#!/bin/bash

# 上线脚本
# 分四种形式 deploy deploy-ty restart restart-ty
# deploy: 更新代码 pip安装 重启server
# deploy-ty: 更新代码 pip安装 重启server 听云监控
# restart: 重启server
# restart-ty: 重启server 听云监控

# 使用示例
# ./deplay_sh deploy
# ./deplay_sh deploy-ty
# ./deplay_sh restart
# ./deplay_sh restart-ty

WORK=30

_updateCode() {
    git reset --hard HEAD
    git pull origin master
}

_pipInstall() {
    pip3 install -r requirements.txt
    python manage.py migrate
}

_valid() {
  process_num=`ps ax | grep gunicorn | awk '{print $7}' | wc | awk '{print $1}'`
  if [ "$process_num" -lt "$WORK" ]
    then
    echo 1
    return
  fi
  echo 0
}

_restart() {
    kill -HUP `cat /home/mengwei/pa.pid`
    gunicorn gouhuo.wsgi:application -w "$WORK" -b 127.0.0.1:9001 -p /home/mengwei/pa.pid -D
}

_tyRestart() {
    kill `cat /home/mengwei/pa.pid`
    export TING_YUN_CONFIG_FILE=/home/mengwei/tingyun.ini
    tingyun-admin run-program gunicorn gouhuo.wsgi:application -w "$WORK" -b 127.0.0.1:9001 -p /home/mengwei/pa.pid -D
    sleep 2
    if [ `_valid` = 1 ]
      then
      _tyRestart
    fi
}

source /home/mengwei/venv36/bin/activate
cd /home/mengwei/ida-server/

if [ "$1" = "deploy" ]
    then
    _updateCode
    _pipInstall
    _restart
elif [ "$1" = "deploy-ty" ]
    then
    _updateCode
    _pipInstall
    _tyRestart
elif [ "$1" = "restart" ]
    then
    _restart
elif [ "$1" = "restart-ty" ]
    then
    _tyRestart
else
    echo "help information."
    echo "./deplay_sh deploy"
    echo "./deplay_sh deploy-ty"
    echo "./deplay_sh restart"
    echo "./deplay_sh restart-ty"
    echo "For more details, please check code."
fi
