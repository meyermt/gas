# mpcs_run.sh
#
# Copyright (C) 2011-2017 Vas Vasiliadis
# University of Chicago
#
# Runs the GAS web application server
#
##

export MPCS_DEBUG=True
export MPCS_APP_HOST=0.0.0.0
export MPCS_APP_PORT=4433
export MPCS_STATIC_ROOT=./static/
export MPCS_TEMPLATES_ROOT=views/
export MPCS_LOGS_ROOT=./log/
export MPCS_LOG_FILE=mpcs.log

[[ -d ./log ]] || mkdir $MPCS_LOGS_ROOT
if [ ! -e $MPCS_LOGS_ROOT/$MPCS_LOG_FILE ]; then
    touch $MPCS_LOGS_ROOT/$MPCS_LOG_FILE;
fi

python web_server.py
