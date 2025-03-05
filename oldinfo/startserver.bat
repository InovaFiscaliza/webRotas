call C:\Users\andre\miniconda3\condabin\conda.bat activate webrotas
title WebRota Server
rem python Server.py
waitress-serve --host=0.0.0.0 --port=5001 Server:app



