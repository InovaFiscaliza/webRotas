import hashlib
import json
import os
import shutil
from pathlib import Path
import project_folders as pf

class CacheBoundingBox:
    def __init__(self):
        self.cache = {}
        self.cache_file = Path(pf.OSMR_PATH_CACHE_DATA) / "cache_boundingbox.json"
        self.load_from_disk()
 
    def remover_item_disco(self, caminho):
        if os.path.isdir(caminho):
            shutil.rmtree(caminho)
        elif os.path.isfile(caminho):
            os.remove(caminho)
           
    def new(self, regioes, diretorio):
        """Armazena as regiões e o diretório no cache utilizando um hash da chave."""
        chave = self._hash_bbox(regioes)
        self.cache[chave] = diretorio
        self.save_to_disk()  # Salva toda vez que adicionar novo item
        
    def _hash_bbox(self, regioes, tamanho=12):
        """Gera um hash SHA256 a partir da lista de regiões."""
        regioes_json = json.dumps(regioes, sort_keys=True)
        hash_obj = hashlib.sha256(regioes_json.encode('utf-8'))
        hash_completo = hash_obj.hexdigest()
        return hash_completo[:tamanho]

    def get_cache(self, regioes):
        """Busca o diretório associado a um conjunto de regiões no cache."""
        chave = self._hash_bbox(regioes)
        return self.cache.get(chave, None)
    
    def delete(self, regioes):
        """Remove do cache o diretório associado a um conjunto de regiões."""
        chave = self._hash_bbox(regioes)
        dir = self.cache.get(chave, None)
        if dir:
            self.remover_item_disco(Path(pf.OSMR_PATH_CACHE_DATA) / dir)
        
        if chave in self.cache:
            del self.cache[chave]
            self.save_to_disk()
            return True
        return False
        
    def clear_cache(self):
        """Limpa o cache e deleta o arquivo de cache."""
        self.cache.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()

    def save_to_disk(self):
        """Salva o cache atual no disco."""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=4)

    def load_from_disk(self):
        """Carrega o cache do disco, se o arquivo existir."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            except Exception as e:
                print(f"Erro ao carregar o cache: {e}")
                self.cache = {}

# Instância global
cCacheBoundingBox = CacheBoundingBox()
