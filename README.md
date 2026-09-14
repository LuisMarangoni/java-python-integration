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
Sistema de Chamados API
    ↓
Users API: autenticação JWT e validação do solicitante
    ↓
Persistência do chamado no PostgreSQL
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
- Validação da resposta de criação: objeto JSON com ID inteiro positivo
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
- Users API e seu PostgreSQL em execução
- Conta de integração ativa na Users API, com perfil `SUPORTE` ou `ADMIN`

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
titulo,descricao,prioridade,solicitante_id
```

A coluna `solicitante_id` deve conter o ID numérico positivo de um usuário ativo cadastrado na Users API. O valor `1` nos exemplos é apenas ilustrativo: substitua-o pelo ID real do usuário antes de executar a importação. O Python envia esse campo à API Java como `solicitanteId`.

Prioridades aceitas:

```text
BAIXA
MEDIA
ALTA
URGENTE
```

Exemplo:

```csv
titulo,descricao,prioridade,solicitante_id
Erro de rede,Usuário sem acesso à internet,ALTA,1
Impressora offline,Equipamento não imprime documentos,MEDIA,1
```

O arquivo `data/chamados.csv` contém também linhas inválidas intencionais para demonstrar o tratamento de falhas.

## Preparando as APIs

Configure primeiro a [Users API](https://github.com/LuisMarangoni/users-api), seguindo o README desse projeto. Ela deve estar acessível na porta `8081`, com seu banco ligado.

A conta usada pelo Sistema de Chamados para consultar usuários deve estar ativa e possuir o perfil `SUPORTE` (suficiente para a integração) ou `ADMIN`. O cadastro padrão com perfil `USUARIO` não permite essa consulta. Após alterar perfis, faça um novo login para obter um token atualizado.

Depois configure o Sistema de Chamados API:

```text
https://github.com/LuisMarangoni/sistema-chamados-api
```

No `.env` desse projeto, configure `DB_PASSWORD`, `USERS_API_EMAIL` e `USERS_API_PASSWORD`. As duas últimas variáveis são as credenciais de login da conta de integração, não as credenciais do PostgreSQL. Não versione o `.env` nem tokens.

Com o Docker Desktop ligado, execute na pasta do Sistema de Chamados:

```powershell
docker compose up -d --build
```

O Compose conecta a API em container à Users API no host por `http://host.docker.internal:8081`. Aguarde a inicialização da aplicação. O Sistema de Chamados deverá estar disponível em:

```text
http://localhost:8080
```

Se alterar as credenciais da integração ou seus perfis durante os testes, recrie o container da API para carregar o ambiente atualizado e descartar o token em memória:

```powershell
docker compose up -d --force-recreate api
```

O importador Python não precisa receber o token: o Sistema de Chamados realiza o login na Users API. O `solicitante_id` do CSV identifica o usuário ativo vinculado ao chamado; não precisa ser a mesma conta usada para autenticar a integração.

## Executando a importação

Com as duas APIs e seus bancos em execução:

```powershell
python -m src.importador
```

O resultado será exibido no terminal e salvo em:

```text
logs/importacao.log
```

A pasta `logs` não é versionada.

Com o CSV de exemplo de quatro registros e IDs de solicitantes ativos ajustados ao seu banco, o resultado esperado é **2 sucessos e 2 falhas de validação** (título vazio e prioridade inválida), com código de saída `1`. Os registros válidos são gravados no banco local; repetir a importação cria novos chamados.

## Respostas inválidas e repetição da importação

Uma criação só é contabilizada como sucesso quando a API retorna `201 Created` e um objeto JSON com `id` inteiro positivo. Respostas `null`, listas, valores simples, objetos sem ID ou com ID inválido são tratadas como falhas de integração. Valores booleanos não são aceitos como IDs.

O importador registra a falha e continua processando as próximas linhas. Isso não desfaz uma criação que já tenha ocorrido no servidor: um timeout ou uma resposta inválida pode impedir a confirmação mesmo que o chamado tenha sido gravado. Antes de repetir uma linha nessa situação, confira o banco ou consulte a API. Não há repetição automática nem garantia de idempotência; reenviar pode gerar duplicados.

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
- rejeição de JSON nulo ou com formato inesperado;
- rejeição de ID ausente, nulo, não inteiro, booleano ou não positivo;
- falhas de conexão;
- continuação após uma linha inválida;
- continuação do lote após resposta inválida da API, usando o cliente real com a sessão HTTP simulada.

Os testes usam mocks e arquivos temporários. Não exigem que a API Java ou o PostgreSQL estejam em execução.

## Decisões técnicas

- `dataclass(frozen=True)` representa entradas imutáveis.
- O leitor aceita arquivos UTF-8 com ou sem BOM.
- Cada linha é validada antes da chamada HTTP.
- O cliente exige `201 Created` e um objeto JSON com ID inteiro positivo para confirmar uma criação bem-sucedida.
- Todas as requisições possuem timeout.
- Exceções de rede são convertidas em erros próprios da integração.
- Uma linha inválida não interrompe o lote.
- A sessão HTTP pode ser substituída por mock durante os testes.
- Logs de execução permanecem fora do Git.
