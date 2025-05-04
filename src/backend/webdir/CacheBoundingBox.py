#!/usr/bin/env python3
"""
    Gerencia o cache de regiões geográficas (bounding boxes) com rotas e comunidades associadas.

    Esta classe fornece funcionalidades para armazenar, recuperar, atualizar e remover entradas de cache
    relacionadas a regiões geográficas consultadas junto ao servidor OSMR. Cada entrada de cache pode conter
    rotas e polilinhas de comunidades associadas, armazenadas em cache secundário específico.

    Funcionalidades principais:
    - Geração de chave hash para identificar regiões geográficas.
    - Armazenamento persistente do cache em disco com compactação (gzip + pickle).
    - Cache auxiliar para rotas (`RouteCache`) e comunidades (`PolylineCache`).
    - Mecanismo debounce para gravações automáticas em segundo plano.
    - Exportação do cache para planilha Excel compactada em .zip.
    - Limpeza automática de entradas antigas com critérios configuráveis.

    Atributos:
        route_cache (RouteCache): Cache de rotas por região.
        comunidades_cache (PolylineCache): Cache de polilinhas de comunidades por região.
        cache (dict): Dicionário contendo os metadados do cache principal.
        ultimaregiao (any): Última região consultada.
        cache_file (Path): Caminho do arquivo de cache persistente no disco.
        _save_timer (threading.Timer): Temporizador de debounce para salvar o cache.
        _debounce_delay (int): Tempo em segundos antes do salvamento automático.
        _lock (threading.Lock): Lock de proteção para acessos concorrentes.

    Métodos principais:
        new(regioes, diretorio): Cria nova entrada de cache.
        get_cache(regioes): Retorna o diretório do cache para a região.
        delete(regioes): Remove uma entrada de cache do disco e da memória.
        clear_cache(): Remove todas as entradas de cache.
        route_cache_get(...) / set(...): Interface para cache de rotas.
        get_comunidades(...) / set_comunidades(...): Interface para cache de comunidades.
        exportar_cache_para_xlsx_zip(path): Exporta conteúdo do cache para planilha compactada.
        clean_old_cache_entries(meses, minimo_regioes): Remove entradas antigas com base em tempo e quantidade mínima.

    Exemplos de uso:
        c = CacheBoundingBox()
        c.new({'norte': -22.1, 'sul': -22.2, 'leste': -43.1, 'oeste': -43.2}, 'regiao-abc')
        dir = c.get_cache({'norte': -22.1, 'sul': -22.2, 'leste': -43.1, 'oeste': -43.2'})
        c.exportar_cache_para_xlsx_zip(Path("/tmp/cache.zip"))
"""


import hashlib
import json
import os
import shutil
import gzip
from datetime import datetime
import threading
from pathlib import Path
import project_folders as pf
import pickle
from datetime import datetime, timedelta
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import zipfile
import os
import route_cache as rc
import PolylineCache as pl
import atexit
import hashlib


# ---------------------------------------------------------------------------------------------------------------
class CacheBoundingBox:
    def __init__(self):
        # Instância global do cache de rotas já pedidas ao servidor OSMR
        # wLog(f"Cache de regioes carregado")
        self.route_cache = rc.RouteCache()  
        self.comunidades_cache = pl.PolylineCache()
        self.areas_urbanas = pl.PolylineCache()
        self.cache = {}
        self.ultimaregiao = None
        self.cache_file = Path(pf.OSMR_PATH_CACHE_DATA) / "cache_boundingbox.bin.gz"
        self._save_timer = None
        self._debounce_delay = 4  # segundos
        self._lock = threading.Lock()
        self._load_from_disk_sync()


    def get_comunidades(self, regioes):
        self.lastrequestupdate(self.ultimaregiao)
        return self.comunidades_cache.get_polylines(regioes)
       
    def set_comunidades(self, regioes, polylinesComunidades): 
        self.lastrequestupdate(self.ultimaregiao)  
        self.comunidades_cache.add_polyline(regioes, polylinesComunidades)

        
    def remover_item_disco(self, caminho):
        if os.path.isdir(caminho):
            shutil.rmtree(caminho)
        elif os.path.isfile(caminho):
            os.remove(caminho)

    def new(self, regioes, diretorio):
        chave = self._hash_bbox(regioes)
        self.ultimaregiao = regioes
        now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        # Gera uma string legível e truncada da região
        regiao_legivel = json.dumps(regioes)
        regiao_legivel = regiao_legivel.replace('\n', '').replace('\r', '')
        if len(regiao_legivel) > 2400:
            regiao_legivel = regiao_legivel[:2397] + '...'

        self.cache[chave] = {
            'regiao': regiao_legivel,
            'diretorio': diretorio,          
            'created': now,
            'lastrequest': now

        }
        self._save_to_disk_sync()


    def chave(self,regioes):
        return self._hash_bbox(regioes)

    def _hash_bbox(self, regioes, tamanho=12):
        regioes_json = json.dumps(regioes, sort_keys=True)
        hash_obj = hashlib.sha256(regioes_json.encode('utf-8'))
        hash_completo = hash_obj.hexdigest()
        return hash_completo[:tamanho]

    
    def get_cache(self, regioes):
            chave = self._hash_bbox(regioes)
            self.ultimaregiao = regioes
            entry = self.cache.get(chave)
            if entry:
                # Atualiza o timestamp de último acesso
                entry['lastrequest'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                self._schedule_save()
                return entry['diretorio']
            return None

    def lastrequestupdate(self, regioes):
            chave = self._hash_bbox(regioes)
            entry = self.cache.get(chave)
            if entry:
                # Atualiza o timestamp de último acesso
                entry['lastrequest'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                self._schedule_save()
                return entry['diretorio']

    def route_cache_get(self, start_lat, start_lon, end_lat, end_lon):
        self.lastrequestupdate(self.ultimaregiao)
        return self.route_cache.get(self.ultimaregiao, start_lat, start_lon, end_lat, end_lon)

    def route_cache_set(self, start_lat, start_lon, end_lat, end_lon, value):
        self.lastrequestupdate(self.ultimaregiao)
        self.route_cache.set(self.ultimaregiao, start_lat, start_lon, end_lat, end_lon, value)

    def route_cache_clear_regioes(self):
        self.route_cache.clear_regioes(self.ultimaregiao)    
        
    def delete(self, regioes):
        self.ultimaregiao = regioes
        self.route_cache_clear_regioes()
        # self.comunidades_cache.clear_regiao(regioes)
        chave = self._hash_bbox(regioes)
        dir = self.cache.get(chave, None)['diretorio']
        if dir:
            self.remover_item_disco(Path(pf.OSMR_PATH_CACHE_DATA) / dir)
        if chave in self.cache:
            del self.cache[chave]
            self._save_to_disk_sync()
            return True
        return False

    def clear_cache(self):
        self.cache.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()


    def _save_in_thread(self):
        """Salvamento real em thread separada."""
        with self._lock:
            thread = threading.Thread(target=self._save_to_disk_sync)
            thread.daemon = True
            thread.start()

    def _schedule_save(self):
        """Inicia ou reinicia o temporizador de salvamento com debounce, com proteção de lock."""
        with self._lock:
            if self._save_timer and self._save_timer.is_alive():
                self._save_timer.cancel()
            self._save_timer = threading.Timer(self._debounce_delay, self._save_in_thread)
            self._save_timer.daemon = True
            self._save_timer.start()


    def _save_to_disk_sync(self):
        data = {
            'cache': self.cache,
            'route_cache': self.route_cache,
            'comunidades_cache': self.comunidades_cache,
            'areas_urbanas': self.areas_urbanas    
        }
        with gzip.open(self.cache_file, 'wb') as f:
             pickle.dump(data, f)
             # f.flush()  # força gravação
        self.exportar_cache_para_xlsx_zip(Path(pf.OSMR_PATH_CACHE_DATA) / "cache_boundingbox.zip")     
        
    def _load_from_disk_sync(self):
        if not self.cache_file.exists():            
            self.cache = {}
            self.route_cache.cache = {}
            self.comunidades_cache.clear_all() 
            self.areas_urbanas.clear_all() 
            return
        with gzip.open(self.cache_file, 'rb') as f:
            data = pickle.load(f)      
        self.cache = data.get('cache', {})
        self.route_cache = data.get('route_cache', {})
        self.comunidades_cache = data.get('comunidades_cache', {})
        self.areas_urbanas = data.get('areas_urbanas', {})
        

    def clean_old_cache_entries(self, meses=12, minimo_regioes=30):
        agora = datetime.now()
        limite = agora - timedelta(days=meses*30)
        
        # Lista de chaves com lastrequest mais antigos que o limite
        chaves_para_remover = []
        for chave, valor in self.cache.items():
            try:
                lastreq = datetime.strptime(valor['lastrequest'], '%d/%m/%Y %H:%M:%S')
                if lastreq < limite:
                    chaves_para_remover.append((chave, lastreq))
            except Exception as e:
                print(f"Erro ao analisar data de {chave}: {e}")

        # Ordena por lastrequest mais antigo primeiro
        chaves_para_remover.sort(key=lambda x: x[1])

        # Só remove se ainda sobrarem pelo menos `minimo_regioes`
        total = len(self.cache)
        removiveis = max(0, total - minimo_regioes)
        chaves_para_remover = chaves_para_remover[:removiveis]

        for chave, _ in chaves_para_remover:
            diretorio = self.cache[chave]['diretorio']
            self.remover_item_disco(Path(pf.OSMR_PATH_CACHE_DATA) / diretorio)
            del self.cache[chave] 
            self.route_cache.clear_regioes_pela_chave(chave)
            self.comunidades_cache.clear_regioes_pela_chave(chave)

        if chaves_para_remover:
            self._save_to_disk_sync()
            # wLog(f"{len(chaves_para_remover)} regiões antigas removidas do cache.",level="debug")
        else:
            # wLog("Nenhuma região antiga removida.",level="debug")
            pass



    def exportar_cache_para_xlsx_zip(self, caminho_zip):
        xlsx_path = caminho_zip.with_suffix('.xlsx')
        wb = Workbook()
        ws = wb.active
        ws.title = "Cache Bounding Box"
        
        # Cabeçalhos
        headers = ['Chave', 'Regiao', 'Diretório', 'Num Rotas Cache', 'Cache Comunidades', 'Criado em', 'Último Acesso']
        ws.append(headers)

        # Inicializa lista de larguras com o comprimento dos cabeçalhos
        col_widths = [len(h) for h in headers]
        
        # Conteúdo do cache
        for chave, dados in self.cache.items():
            numrotascached = len(self.route_cache.cache.get(chave, {}))
            numcomunidadescached = len(self.comunidades_cache.get_by_key(chave))
            row = [
                chave,
                dados.get('regiao', ''),
                dados.get('diretorio', ''),
                str(numrotascached),
                str(numcomunidadescached),
                dados.get('created', ''),
                dados.get('lastrequest', '')
            ]
            ws.append(row)
            # Atualiza larguras máximas
            for i, cell_value in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell_value)))

        # Aplica larguras ajustadas (com margem extra de +2 caracteres, limitando a 200 se necessário)
        for i, width in enumerate(col_widths, 1):
            adjusted_width = width + 2  # Adiciona a margem de 2 caracteres
            if adjusted_width > 50:
                adjusted_width = 50  # Limita a largura a 200 se ultrapassar esse valor
            ws.column_dimensions[get_column_letter(i)].width = adjusted_width
        
        wb.save(xlsx_path)
        # Comprimir para ZIP
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(xlsx_path, arcname=os.path.basename(xlsx_path))
        os.remove(xlsx_path)
 
    def shutdown(self):
        with self._lock:
            if self._save_timer and self._save_timer.is_alive():
                self._save_timer.cancel()
            self._save_to_disk_sync()
        

# ---------------------------------------------------------------------------------------------------------------    

# Instância global
cCacheBoundingBox = CacheBoundingBox()
cCacheBoundingBox.clean_old_cache_entries()
atexit.register(cCacheBoundingBox.shutdown) # evita que o programe termine antes de terminar de salvar o cache