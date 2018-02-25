#!/bin/bash

./run_server.sh >server.log &
python3 run_matches.py >match.log &
