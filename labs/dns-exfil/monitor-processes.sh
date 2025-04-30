#!/bin/bash

# Continuously monitor processes
while true; do
    # Find any process owned by www-data excluding the Flask app
    for pid in $(pgrep -u www-data); do
        # Get the command of the process
        cmd=$(ps -p $pid -o cmd=)

        # Check if the process is not the Flask app and is older than 10 seconds
        if [[ "$cmd" != "/app/venv/bin/python3 /app/app.py" ]]; then
            # Terminate the process if it's older than 10 seconds
            timeout 10s kill -9 $pid
        fi
    done
    sleep 10
done