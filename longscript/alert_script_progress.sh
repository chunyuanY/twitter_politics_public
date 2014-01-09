TDIR="/home/fowlerm/twitter_politics/"
. $TDIR/aliases.sh
DIR="/home/fowlerm/twitter_politics/longscript"
echo $DIR
printenv
python $DIR/alert_script_progress.py >> $DIR/script.log
