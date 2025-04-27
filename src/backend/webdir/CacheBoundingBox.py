
import hashlib
import json



class CacheBoundingBox:
    def __init__(self):
        self.cache = {}
    
    def new(self, regioes, diretorio):
        """Armazena as regiões e o diretório no cache utilizando um hash da chave."""
        chave = self._hash_bbox(regioes)  # Gerar a chave de hash
        self.cache[chave] = diretorio  # Armazenar no cache com a chave e o valor (diretório)
        
    def _hash_bbox(self,regioes, tamanho=12):
        """
        Gera um hash SHA256 a partir da lista de regiões e retorna apenas os primeiros caracteres.
        
        Args:
            regioes (list): Lista de regiões.
            tamanho (int): Quantidade de caracteres do hash retornado (padrão 12).
        
        Returns:
            str: Hash reduzido para usar como chave de cache.
        """
        regioes_json = json.dumps(regioes, sort_keys=True)
        hash_obj = hashlib.sha256(regioes_json.encode('utf-8'))
        hash_completo = hash_obj.hexdigest()
        return hash_completo[:tamanho]

    def get_cache(self, regioes):
        """Busca o diretório associado a um conjunto de regiões no cache."""
        chave = self._hash_bbox(regioes)
        return self.cache.get(chave, None)  # Retorna o diretório ou None se não encontrado
    
    def clear_cache(self):
        """Limpa o cache"""
        self.cache.clear()

cCacheBoundingBox = CacheBoundingBox()

