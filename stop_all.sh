#!/bin/bash

kill `cat twistd.pid`

for f in run_matches*.pid; do
    kill `cat $f`
done

