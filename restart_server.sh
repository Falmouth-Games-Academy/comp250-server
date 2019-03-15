#!/bin/bash

kill `cat twistd.pid`
rm server.log
./run_server.sh >server.log 2>&1 &
