import hashlib
import json
import os
import shutil
import gzip
import pickle
import threading
from pathlib import Path
import project_folders as pf
import route_cache as rc

class CacheBoundingBox:
    def __init__(self):
        # Instância global do cache de rotas já pedidas ao servidor OSMR
        self.route_cache = rc.RouteCache()  
        self.cache = {}
        self.ultimaregiao = None
        self.cache_file = Path(pf.OSMR_PATH_CACHE_DATA) / "cache_boundingbox.json.gz"
        self._save_timer = None
        self._debounce_delay = 10  # segundos
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
        self.cache[chave] = diretorio
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
        return self.cache.get(chave, None)

    def route_cache_get(self, start_lat, start_lon, end_lat, end_lon):
        return self.route_cache.get(self.ultimaregiao, start_lat, start_lon, end_lat, end_lon)

    def route_cache_set(self, start_lat, start_lon, end_lat, end_lon, value):
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
            'route_cache': self.route_cache.cache,
            'cache': self.cache
        }
        with gzip.open(self.cache_file, 'wt', encoding='utf-8') as f:
             json.dump(data, f, ensure_ascii=False, indent=4)
        
    def _load_from_disk_sync(self):
        if not self.cache_file.exists():
            self.route_cache.cache = {}
            self.cache = {}
            return
        with gzip.open(self.cache_file, 'rt', encoding='utf-8') as f:
            data = json.load(f)
            self.route_cache.cache = data.get('route_cache', {})
            self.cache = data.get('cache', {})

# Instância global
cCacheBoundingBox = CacheBoundingBox()
