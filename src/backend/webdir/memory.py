#!/usr/bin/env python3
import psutil
# ----------------------------------------------------------------------------------------------
def percentual_memoria_livre():
    """
    Retorna o percentual de memória física (RAM) livre no sistema.

    Usa a biblioteca `psutil` para acessar informações de uso da memória.

    Returns:
        float: Percentual de memória livre (entre 0 e 100).
    """
    mem = psutil.virtual_memory()
    return mem.available * 100 / mem.total
# ----------------------------------------------------------------------------------------------
def diagnostico_memoria():
    mem = psutil.virtual_memory()
    print(f"Total: {mem.total / 1e9:.2f} GB")
    print(f"Usada: {mem.used / 1e9:.2f} GB")
    print(f"Disponível: {mem.available / 1e9:.2f} GB")
    print(f"Percentual em uso (Windows-style): {mem.percent:.2f}%")
    print(f"Percentual livre (estimado): {100 - mem.percent:.2f}%")
# ----------------------------------------------------------------------------------------------
# Exemplo de uso
if __name__ == "__main__":
    print(f"Memória livre: {percentual_memoria_livre():.2f}%")
    diagnostico_memoria()
