# -*- coding: utf-8 -*-

from fabric.api import local, run, env, cd

env.hosts = ['mengwei@172.31.0.17:22', 'mengwei@172.31.0.18:22']

PA_PATH = "/home/mengwei/ida-server"


def restart():
    local("./deploy.sh restart")


def restart_ty():
    local("./deploy.sh restart-ty")


def deploy():
    local("./deploy.sh deploy")


def deploy_ty():
    local("./deploy.sh deploy-ty")


def remote_restart():
    with cd(PA_PATH):
        run("./deploy.sh restart")


def remote_deploy():
    with cd(PA_PATH):
        run("./deploy.sh deploy")
