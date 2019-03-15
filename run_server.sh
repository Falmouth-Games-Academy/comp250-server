#!/bin/bash

PYTHONPATH=. PYTHONUNBUFFERED=TRUE twistd3 -n web --port "tcp:port=80" --wsgi server.app

