#!/bin/bash

./run_server.sh >server.log 2>&1 &
python3 -u run_matches.py >match.log 2>&1 &
echo -n $! >run_matches.pid
