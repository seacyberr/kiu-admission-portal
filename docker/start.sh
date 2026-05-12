#!/bin/bash

# Start nginx in background
nginx -g "daemon on;"

# Start Flask API
cd /app/api
python run.py
