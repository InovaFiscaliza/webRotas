cd ..
set WEBROTAS_HOME=%CD%
cd tests

uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_abrangencia_rj_niteroi_geodesica.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_contorno.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_abrangencia_rj_campos.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_visita_ro.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_visita_saopaulo_cidades_interior.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_visita_portoalegre-belem.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_abrangencia_riodejaneiro_distosmr.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_abrangencia_sp_pesado.json

