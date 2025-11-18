# Implementação de Verificação de Disponibilidade do Container

## Resumo das Alterações

### Modificações Realizadas

1. **Adicionado import socket**: Para verificação de porta
   ```python
   import socket
   ```

2. **Nova função `is_port_available()`**: 
   - Verifica se a porta está aberta (teste de conexão socket)
   - Testa se OSRM está respondendo no endpoint `/health`
   - Timeout configurável (padrão 3 segundos)

3. **Modificada `get_osrm_matrix_from_local_container()`**:
   - Verifica disponibilidade da porta 5000 **antes** de tentar usar o container
   - Se não disponível, lança exceção imediatamente
   - Fallback automático para `get_osrm_matrix_iterative()`

### Fluxo de Execução

```
get_osrm_matrix_from_local_container()
    ↓
is_port_available(localhost, 5000)
    ↓
Se NÃO disponível → Exception → get_osrm_matrix_iterative()
    ↓
Se disponível → Continua processamento normal
```

### Benefícios

- **Detecção rápida** de indisponibilidade do container
- **Fallback automático** sem delay desnecessário
- **Logs informativos** do processo
- **Timeout configurável** para verificações

### Funções Envolvidas

- `controller()`: Orquestra o processo de roteamento
- `get_osrm_matrix_from_local_container()`: Usa container local (modificada)
- `get_osrm_matrix_iterative()`: Método alternativo via API pública
- `is_port_available()`: Nova função de verificação

### Comandos de Teste

```bash
# Testar com container ativo
uv run src/ucli/webrota_client.py tests/request_shortest\ \(RJ\).json

# Monitorar logs para verificar o comportamento
tail -f logs/*.log
```