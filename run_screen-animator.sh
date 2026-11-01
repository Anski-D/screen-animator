#!/usr/bin/env bash
# === USER INPUTS ===
LOG_DIR=logs
LOG_FILE=.screen-animator.log
SCRIPT_BIN=.venv/bin/screen-animator
# ===================

LOG=$LOG_DIR/$LOG_FILE

if [ ! -d $LOG_DIR ]
then
  mkdir $LOG_DIR
fi

echo "=======================" | tee -a $LOG
echo "=== SCREEN-ANIMATOR ===" | tee -a $LOG
echo "=======================" | tee -a $LOG

echo "Starting script" | tee -a $LOG
$SCRIPT_BIN "$@" &
PID=$!
echo $PID > .pid
echo "Running under process $PID" | tee -a $LOG
echo -e "Use $PWD/stop_screen-animator.sh to terminate\n" | tee -a $LOG

exit 0
