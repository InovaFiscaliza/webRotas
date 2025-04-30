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
import route_cache as rc

import hashlib


# ---------------------------------------------------------------------------------------------------------------
class CacheBoundingBox:
    def __init__(self):
        # Instância global do cache de rotas já pedidas ao servidor OSMR
        # wLog(f"Cache de regioes carregado")
        self.route_cache = rc.RouteCache()  
        self.cache = {}
        self.ultimaregiao = None
        self.cache_file = Path(pf.OSMR_PATH_CACHE_DATA) / "cache_boundingbox.bin.gz"
        self._save_timer = None
        self._debounce_delay = 25  # segundos
        self._lock = threading.Lock()
        self._load_from_disk_sync()

    def remover_item_disco(self, caminho):
        if os.path.isdir(caminho):
            shutil.rmtree(caminho)
        elif os.path.isfile(caminho):
            os.remove(caminho)

    def new(self, regioes, diretorio):
        chave = self._hash_bbox(regioes)
        self.ultimaregiao = regioes
        now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.cache[chave] = {
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
        chave = self._hash_bbox(regioes)
        dir = self.cache.get(chave, None)
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
            'route_cache': self.route_cache,
            'cache': self.cache
        }
        with gzip.open(self.cache_file, 'wb') as f:
             pickle.dump(data, f)
             # f.flush()  # força gravação
        
    def _load_from_disk_sync(self):
        if not self.cache_file.exists():
            self.route_cache.cache = {}
            self.cache = {}
            return
        with gzip.open(self.cache_file, 'rb') as f:
            data = pickle.load(f)
        self.route_cache = data.get('route_cache', {})
        self.cache = data.get('cache', {})
        

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
        import webRota as wr
        if chaves_para_remover:
            self._save_to_disk_sync()
            # wLog(f"{len(chaves_para_remover)} regiões antigas removidas do cache.",level="debug")
        else:
            # wLog("Nenhuma região antiga removida.",level="debug")
            pass
            

# ---------------------------------------------------------------------------------------------------------------    

# Instância global
cCacheBoundingBox = CacheBoundingBox()
cCacheBoundingBox.clean_old_cache_entries()
