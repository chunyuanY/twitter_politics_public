TDIR="/home/ubuntu/twitter_politics"

alias tpull="cd $TDIR && git pull origin master && cd -"
alias tdir="cd $TDIR"
alias talert="python $TDIR/longscript/alert_script_progress.py"
alias trun="nohup python $TDIR/twpol/main.py >> $TDIR/twpol/logs/main.log &"

export PYTHONPATH=$PYTHONPATH:$TDIR
export DJANGO_SETTINGS_MODULE=twpol.settings
export PYTHONSTARTUP=$TDIR/python_startup.py

export USE_REMOTE_DB=1
