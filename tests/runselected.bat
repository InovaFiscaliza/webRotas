cd ..
set WEBROTAS_HOME=%CD%
cd tests

rem uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_contorno.json
rem uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_abrangencia_belem.json
rem uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_visita_ro.json
rem exit

rem uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" criar_cache_grs.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_abrangencia_joaopessoa.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_visita_ro.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_abrangencia_belem.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_abrangencia_salvador.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_abrangencia_goias.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_abrangencia_rj_niteroi_geodesica.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_abrangencia_brasilia_distosmr.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_abrangencia_sp_pesado.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_abrangencia_portoalegre.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_contorno.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_abrangencia_rj_campos.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_visita_saopaulo_cidades_interior.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_visita_portoalegre-belem.json
uv run --project "%WEBROTAS_HOME%" "%WEBROTAS_HOME%\src\ucli\webrota_client.py" exemplo_abrangencia_riodejaneiro_distosmr.json



