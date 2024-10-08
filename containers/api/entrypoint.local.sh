#!/bin/bash

/wait-for-it.sh mysql:3306 --timeout=60
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
