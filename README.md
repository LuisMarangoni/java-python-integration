# Integração Java + Python

[![CI](https://github.com/LuisMarangoni/java-python-integration/actions/workflows/ci.yml/badge.svg)](https://github.com/LuisMarangoni/java-python-integration/actions/workflows/ci.yml)

Aplicação Python que importa chamados de um arquivo CSV para uma API REST desenvolvida com Java e Spring Boot.

Este projeto integra o processamento de dados em Python com o projeto [Sistema de Chamados API](https://github.com/LuisMarangoni/sistema-chamados-api), responsável pela validação final e persistência no PostgreSQL.

## Fluxo da integração

```text
Arquivo CSV
    ↓
Leitura e validação em Python
    ↓
Conversão para JSON
    ↓
Requisição HTTP POST
    ↓
API Java / Spring Boot
    ↓
PostgreSQL
```

Linhas inválidas são registradas como falha sem interromper o processamento das demais linhas.

## Tecnologias

- Python 3.13
- Requests
- pytest
- CSV
- HTTP e JSON
- Logging
- Java 21
- Spring Boot
- PostgreSQL

Java, Spring Boot e PostgreSQL são utilizados pela API consumida.

## Funcionalidades

- Leitura de chamados em CSV
- Verificação das colunas obrigatórias
- Normalização de textos e prioridades
- Validação individual de cada linha
- Conversão de objetos Python para JSON
- Consumo de API REST Java
- Timeout nas requisições
- Tratamento de erros HTTP
- Tratamento de falhas de conexão
- Continuação do processo após linhas inválidas
- Registro de sucessos e falhas em arquivo de log
- Resumo final da importação
- Testes unitários sem dependência da API real

## Estrutura

```text
java-python-integration
├── data
│   └── chamados.csv
├── src
│   ├── __init__.py
│   ├── cliente_api.py
│   ├── importador.py
│   ├── leitor_csv.py
│   └── modelos.py
├── tests
│   ├── test_cliente_api.py
│   ├── test_importador.py
│   ├── test_leitor_csv.py
│   └── test_modelos.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Pré-requisitos

- Python 3.13 ou superior compatível
- Git
- Sistema de Chamados API em execução

Repositório da API Java:

```text
https://github.com/LuisMarangoni/sistema-chamados-api
```

## Ambiente virtual

No PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

Se a ativação for bloqueada, use diretamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Formato do CSV

O arquivo deve possuir as colunas:

```csv
titulo,descricao,prioridade
```

Prioridades aceitas:

```text
BAIXA
MEDIA
ALTA
URGENTE
```

Exemplo:

```csv
titulo,descricao,prioridade
Erro de rede,Usuário sem acesso à internet,ALTA
Impressora offline,Equipamento não imprime documentos,MEDIA
```

O arquivo `data/chamados.csv` contém também linhas inválidas intencionais para demonstrar o tratamento de falhas.

## Executando a API Java

Clone e configure o projeto:

```text
https://github.com/LuisMarangoni/sistema-chamados-api
```

Com o PostgreSQL e a variável `DB_PASSWORD` configurados, execute no projeto Java:

```powershell
.\mvnw.cmd spring-boot:run
```

A API deverá estar disponível em:

```text
http://localhost:8080
```

## Executando a importação

Com a API Java em execução:

```powershell
python -m src.importador
```

O resultado será exibido no terminal e salvo em:

```text
logs/importacao.log
```

A pasta `logs` não é versionada.

## Configuração opcional

A URL da API e o caminho do CSV podem ser modificados por variáveis de ambiente:

```powershell
$env:CHAMADOS_API_URL = "http://localhost:8080"
$env:CAMINHO_CSV = "data/chamados.csv"
```

Valores padrão:

```text
CHAMADOS_API_URL=http://localhost:8080
CAMINHO_CSV=data/chamados.csv
```

## Códigos de saída

| Código | Significado |
|---|---|
| `0` | Todas as linhas foram importadas |
| `1` | O processamento terminou com falhas parciais |
| `2` | O arquivo não pôde ser aberto ou sua estrutura é inválida |

No PowerShell, consulte o código com:

```powershell
$LASTEXITCODE
```

## Testes

Execute:

```powershell
python -m pytest -v
```

A suíte testa:

- normalização de chamados;
- campos obrigatórios;
- prioridades inválidas;
- leitura do CSV;
- ausência de colunas obrigatórias;
- requisição HTTP de criação;
- respostas de erro da API;
- falhas de conexão;
- continuação após uma linha inválida.

Os testes usam mocks e arquivos temporários. Não exigem que a API Java ou o PostgreSQL estejam em execução.

## Decisões técnicas

- `dataclass(frozen=True)` representa entradas imutáveis.
- O leitor aceita arquivos UTF-8 com ou sem BOM.
- Cada linha é validada antes da chamada HTTP.
- O cliente exige `201 Created` para considerar uma criação bem-sucedida.
- Todas as requisições possuem timeout.
- Exceções de rede são convertidas em erros próprios da integração.
- Uma linha inválida não interrompe o lote.
- A sessão HTTP pode ser substituída por mock durante os testes.
- Logs de execução permanecem fora do Git.