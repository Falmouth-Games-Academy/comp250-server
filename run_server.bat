set PYTHONPATH=.
twistd -n web --port "tcp:port=80" --wsgi server.app
pause
