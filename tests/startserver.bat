cd ..
set WEBROTAS_HOME=%CD%
cd tests

uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\backend\webdir\server.py" 
