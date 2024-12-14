#!/bin/bash
cd webdir
/usr/local/bin/gunicorn -w 4 -b 0.0.0.0:8000 Site:app
