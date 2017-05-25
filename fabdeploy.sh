#!/bin/bash

fab -i fabfile.py deploy_ty
fab -i fabfile.py remote_deploy
