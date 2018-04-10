#!/bin/bash

kill `cat twistd.pid`
./run_server.sh >server.log 2>&1 &
