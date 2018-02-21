#!/bin/bash

PYTHONPATH=. twistd3 -n web --port "tcp:port=8000" --wsgi server.app

