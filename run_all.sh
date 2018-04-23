#!/bin/bash

./run_server.sh >server.log 2>&1 &

for i in {1..3}; do
    python3 -u run_matches.py >match_$i.log 2>&1 &
    echo -n $! >run_matches_$i.pid
done
