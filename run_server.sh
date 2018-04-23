#!/bin/bash

PYTHONPATH=. PYTHONUNBUFFERED=TRUE twistd3 -n web --port "tcp:port=8000" --wsgi server.app

