cd ..
set WEBROTAS_HOME=%CD%
cd tests

rem uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_abrangencia_rj_niteroi_geodesica.json
rem uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_contorno.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_visita_ro.json
rem uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_visita_saopaulo_cidades_interior.json
rem uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_visita_portoalegre-belem.json
